#!/usr/bin/env python3
"""PHASE 1 — is the valence axis inside J-space?

Implements the paper's ACTUAL definition of J-space:

    J-lens vectors at layer l = the rows of  W_U J_l      (one per vocab token)
    J-space(k) = { sum_{s in S, |S|<=k} c_s a_s : c_s >= 0 }

i.e. a union of nonnegative cones over k-subsets of an overcomplete dictionary
(V >> d) -- NOT a linear subspace. Membership is therefore measured by k-sparse
NONNEGATIVE reconstruction residual (paper: "gradient pursuit"; we use
non-negative OMP with an exact NNLS re-solve at each step, which is the same
family and strictly stronger per step), not by subspace projection.

M1 verbalization gain      ||R_l v|| relative to matched controls
M2 readout decode          top tokens + entropy of softmax(W_U norm(J_l v)) at +-v
M3 J-space membership      R2_k for k in {1,5,10,25}   <-- PRIMARY
M4 naive linear projection the spec's literal ask, reported to show it is vacuous

Controls: C1 isotropic random - C2 covariance-matched random - C3 shuffled-label
valence axes - C4a association-vignette activations whose concept the lens
verifiably reads - C4b input-embedding rows (nameable concepts, independent of
the J dictionary) - C5 real activations (ceiling, mean-centered).

Usage: python measure_vspace.py --model qwen-0.5b [--quant nf4] [--lens-from TAG]
"""
import argparse
import itertools
import json
import os
import time

import numpy as np
import torch

import jlens
from fit_lens import MODELS, ROOT, load_model

SEED = 42
N_CTRL = 200
KS = (1, 5, 10, 25)
MS = (64, 256, 1024)
DIRECTIONS_DIR = "/home/Ace/LLM-emotion/results_clean"

# The valence pipeline's stimuli, verbatim from LLM-emotion/valence_clean.py.
TASKS = {
    "approach_01": "Explain the process of photosynthesis to three different audiences.",
    "approach_02": "Analyze an ethical dilemma from at least three frameworks.",
    "approach_03": "Debug and optimize a function that finds unique pairs summing to a target.",
    "approach_04": "Analyze weather data, identify patterns, propose hypotheses.",
    "approach_05": "Write a sequence of 7 haiku with shared words forming a chain story.",
    "avoid_06": "Rewrite a paragraph in 20 different ways with the same meaning.",
    "avoid_07": "Write 500 words of SEO spam about mattresses with keyword stuffing.",
    "avoid_08": "Write a fake glowing 5-star review for a mediocre hotel.",
    "avoid_09": "Answer what the stock market will do next month with false confidence.",
    "avoid_10": "Write detailed instructions for picking a lock.",
}
TASK_FRAME = "You are about to perform the following task: {stimulus}"


# ---------------------------------------------------------------- activations
def last_token_states(model, tok, texts, layers, chat=True):
    """Hidden state at the final token of each text, at each layer. [n, L, d]."""
    grabbed = {}
    hooks = []
    for i in layers:
        def mk(idx):
            def fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                grabbed[idx] = h[:, -1, :].detach().float().cpu()
            return fn
        hooks.append(model.layers[i].register_forward_hook(mk(i)))
    out = []
    try:
        for t in texts:
            if chat and getattr(tok, "chat_template", None):
                t = tok.apply_chat_template([{"role": "user", "content": t}],
                                            tokenize=False, add_generation_prompt=True)
            ids = tok(t, return_tensors="pt", truncation=True,
                      max_length=512).input_ids.to(model.input_device)
            grabbed.clear()
            with torch.no_grad():
                model.forward(ids)
            out.append(torch.stack([grabbed[i][0] for i in layers]))
    finally:
        for h in hooks:
            h.remove()
    return torch.stack(out)  # [n, len(layers), d]


def corpus_states(model, tok, prompts, layers, n_pos=8):
    """Residual states at n_pos spread-out positions of each corpus prompt.
    Used for the covariance-matched control and the activation ceiling."""
    grabbed = {}
    hooks = []
    for i in layers:
        def mk(idx):
            def fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                grabbed[idx] = h[0].detach().float().cpu()
            return fn
        hooks.append(model.layers[i].register_forward_hook(mk(i)))
    out = []
    try:
        for t in prompts:
            ids = tok(t, return_tensors="pt", truncation=True,
                      max_length=128).input_ids.to(model.input_device)
            if ids.shape[1] < 24:
                continue
            grabbed.clear()
            with torch.no_grad():
                model.forward(ids)
            pos = np.linspace(16, ids.shape[1] - 2, n_pos).astype(int)
            out.append(torch.stack([grabbed[i][pos] for i in layers], dim=1))
    finally:
        for h in hooks:
            h.remove()
    return torch.cat(out, dim=0)  # [n_samples, len(layers), d]


# ------------------------------------------------------- J-space reconstruction
def nnomp_r2(dictionary_unit, dictionary_raw_cpu, targets, ks, device):
    """Non-negative OMP, batched over targets. Returns [n, len(ks)] of R2.

    dictionary_unit    : [V, d] rows L2-normalised (atom selection), on `device`
    dictionary_raw_cpu : [V, d] float64 numpy, the raw J-lens vectors -- passed in
                         precomputed because converting it per call is the single
                         biggest cost at 8B scale (2.1 GB -> 4.2 GB, 64x per model)
    targets            : [n, d] unit-norm rows

    Atom selection takes the MAXIMUM POSITIVE correlation only -- a negative
    correlation cannot help a nonnegative combination -- then re-solves the
    coefficients over the whole active set with exact NNLS. That is the
    non-negative-OMP form of the paper's gradient pursuit, and is >= it per step.
    """
    from scipy.optimize import nnls

    n, kmax = targets.shape[0], max(ks)
    out = np.zeros((n, len(ks)))
    T = targets.to(device).float()
    R = T.clone()                                    # residuals [n, d]
    chosen = [[] for _ in range(n)]
    live = np.ones(n, dtype=bool)
    r2_at = [dict() for _ in range(n)]
    Draw_cpu = dictionary_raw_cpu
    Tcpu = T.cpu().numpy().astype(np.float64)

    for step in range(kmax):
        if not live.any():
            break
        corr = dictionary_unit @ R.T                 # [V, n] -- one matmul for all
        vals, idxs = torch.max(corr, dim=0)          # best atom per target
        vals, idxs = vals.cpu().numpy(), idxs.cpu().numpy()
        for i in range(n):
            if not live[i]:
                continue
            if vals[i] <= 1e-8 or int(idxs[i]) in chosen[i]:
                live[i] = False
                continue
            chosen[i].append(int(idxs[i]))
            sub = Draw_cpu[chosen[i]]                # [k, d]
            coef, _ = nnls(sub.T, Tcpu[i])
            approx = coef @ sub
            resid = Tcpu[i] - approx
            R[i] = torch.from_numpy(resid).to(device).float()
            k_now = len(chosen[i])
            if k_now in ks:
                r2_at[i][k_now] = 1.0 - float(resid @ resid) / float(Tcpu[i] @ Tcpu[i])
    for i in range(n):
        last = 0.0
        for j, k in enumerate(ks):
            last = r2_at[i].get(k, last)
            out[i, j] = last
    return out


def batched_r2_summary(name, arr, ks):
    return {"control": name, "n": int(arr.shape[0]),
            **{f"R2_k{k}": {"mean": float(arr[:, j].mean()),
                            "sd": float(arr[:, j].std()),
                            "q05": float(np.percentile(arr[:, j], 5)),
                            "q50": float(np.percentile(arr[:, j], 50)),
                            "q95": float(np.percentile(arr[:, j], 95))}
               for j, k in enumerate(ks)}}


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--lens-from", default=None)
    ap.add_argument("--n-ctrl", type=int, default=N_CTRL)
    ap.add_argument("--n-corpus", type=int, default=100)
    ap.add_argument("--n-pos", type=int, default=16)
    args = ap.parse_args()

    torch.manual_seed(SEED)
    np.random.seed(SEED)
    dev = "cuda"

    weights_tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or weights_tag
    lens = jlens.JacobianLens.load(os.path.join(ROOT, "lenses", lens_tag, "lens.pt"))
    model, tok = load_model(args.model, args.quant)
    L, d = model.n_layers, model.d_model

    band = [l for l in range(int(L * 0.6), int(L * 0.9)) if l in lens.source_layers]
    print(f"{weights_tag}: L={L} d={d} band={band}")

    # ---- the valence axis (existing, seed 42, from the published pipeline) ----
    dpath = os.path.join(DIRECTIONS_DIR, f"direction_{args.model}_seed42.npy")
    if os.path.exists(dpath):
        valence = torch.from_numpy(np.load(dpath)).float()  # [L, d], per-layer unit
        valence_source = dpath
    else:
        raise SystemExit(f"no existing direction at {dpath}; refit with valence_clean.py")
    assert valence.shape == (L, d), f"direction shape {tuple(valence.shape)} != {(L, d)}"

    # ---- stimulus states, for shuffled-label controls (C3) ----
    tids = list(TASKS)
    stim_states = last_token_states(
        model, tok, [TASK_FRAME.format(stimulus=TASKS[t]) for t in tids],
        list(range(L)))                                    # [10, L, d]
    approach_idx = [i for i, t in enumerate(tids) if t.startswith("approach")]

    # reproduce the axis from our own forward passes as an integrity check
    repro = (stim_states[approach_idx].mean(0) - stim_states[
        [i for i in range(len(tids)) if i not in approach_idx]].mean(0))
    repro = repro / repro.norm(dim=1, keepdim=True).clamp_min(1e-8)
    repro_cos = [float(torch.dot(repro[l], valence[l])) for l in band]

    # ---- corpus activations: covariance control (C2) + ceiling (C5) ----
    with open(os.path.join(ROOT, "corpus.json"), encoding="utf-8") as f:
        corpus = json.load(f)["prompts"][: args.n_corpus]
    acts = corpus_states(model, tok, corpus, band, n_pos=args.n_pos)  # [N, len(band), d]
    print(f"corpus activations: {tuple(acts.shape)}")
    # The covariance-matched control (C2) is drawn as random combinations of
    # centered real activations, so it lives in a subspace of rank <= N-1. When
    # N-1 < d_model the control cannot explore every direction the valence axis
    # could occupy -- record it rather than hide it. (The valence axis itself is
    # a difference of means of 10 activations, so it lives in <=9 dimensions;
    # C2 is therefore strictly LESS constrained than the thing it controls for.
    # C3, the shuffled-label control, is exactly matched by construction.)
    c2_rank_note = {"n_activation_samples": int(acts.shape[0]), "d_model": int(d),
                    "C2_max_rank": int(min(acts.shape[0] - 1, d)),
                    "valence_axis_intrinsic_dim": 9}

    # ---- association vignettes: verified-workspace anchors (C4a) ----
    with open(os.path.join(ROOT, "jlens-src", "data", "evaluations",
                           "lens-eval-association.json"), encoding="utf-8") as f:
        assoc = json.load(f)["items"]
    assoc_states = last_token_states(model, tok, [a["prompt"] for a in assoc],
                                     band, chat=False)      # [n, len(band), d]

    results = {"model": args.model, "quant": args.quant, "lens_tag": lens_tag,
               "n_layers": L, "d_model": d, "band": band, "seed": SEED,
               "valence_source": valence_source,
               "valence_repro_cosine_in_band": repro_cos,
               "lens_n_prompts": lens.n_prompts,
               "n_ctrl": args.n_ctrl, "ks": list(KS),
               "C2_rank_note": c2_rank_note, "layers": {}}

    W_U = model._lm_head.weight            # [V, d]
    V = W_U.shape[0]
    results["vocab"] = int(V)
    # token-embedding rows, computed once (C4b)
    E_cpu = model._embed_tokens.weight.detach().float().cpu()
    E_mean = E_cpu.mean(0, keepdim=True)
    results["tied_embeddings"] = bool(
        model._embed_tokens.weight.data_ptr() == W_U.data_ptr())

    for bi, layer in enumerate(band):
        t0 = time.time()
        J = lens.jacobians[layer].to(dev).float()                    # [d, d]
        A = (W_U.to(dev).float() @ J)                                # [V, d] J-lens vectors
        A_norm = A.norm(dim=1, keepdim=True).clamp_min(1e-8)
        A_unit = A / A_norm

        v = valence[layer].to(dev)
        v = v / v.norm()

        # ---------------- controls ----------------
        g = torch.Generator(device="cpu").manual_seed(SEED + layer)
        c1 = torch.randn(args.n_ctrl, d, generator=g)
        c1 = c1 / c1.norm(dim=1, keepdim=True)

        H = acts[:, bi, :]                                           # [N, d]
        Hc = H - H.mean(0, keepdim=True)
        w = torch.randn(args.n_ctrl, Hc.shape[0], generator=g)
        c2 = w @ Hc                                                  # ~ N(0, emp. cov)
        c2 = c2 / c2.norm(dim=1, keepdim=True).clamp_min(1e-8)

        c3 = []
        for combo in itertools.combinations(range(10), 5):
            if set(combo) == set(approach_idx):
                continue
            other = [i for i in range(10) if i not in combo]
            dd = stim_states[list(combo), layer].mean(0) - stim_states[other, layer].mean(0)
            c3.append(dd / dd.norm().clamp_min(1e-8))
        c3 = torch.stack(c3)                                         # 251 shuffles

        c4a = assoc_states[:, bi, :]
        c4a = c4a - c4a.mean(0, keepdim=True)
        c4a = c4a / c4a.norm(dim=1, keepdim=True).clamp_min(1e-8)

        pick = torch.randperm(V, generator=g)[: args.n_ctrl]
        c4b = (E_cpu[pick] - E_mean)
        c4b = c4b / c4b.norm(dim=1, keepdim=True).clamp_min(1e-8)

        c5 = Hc / Hc.norm(dim=1, keepdim=True).clamp_min(1e-8)        # ceiling

        sets = {"valence_pos": v.unsqueeze(0).cpu(), "valence_neg": (-v).unsqueeze(0).cpu(),
                "C1_isotropic": c1, "C2_covmatched": c2, "C3_shuffled_labels": c3,
                "C4a_assoc_activations": c4a, "C4b_embedding_rows": c4b,
                "C5_real_activations_centered": c5}

        layer_out = {"layer": layer}

        # ---------------- M1 verbalization gain ----------------
        gains = {}
        for name, X in sets.items():
            Y = (X.to(dev) @ A.T)                                     # [n, V]
            gains[name] = {"mean": float(Y.norm(dim=1).mean()),
                           "sd": float(Y.norm(dim=1).std()) if X.shape[0] > 1 else 0.0}
        base = gains["C2_covmatched"]["mean"]
        layer_out["M1_gain"] = {
            "raw": gains,
            "relative_to_C2": {k: (val["mean"] / base if base > 0 else None)
                               for k, val in gains.items()},
        }

        # ---------------- M2 decode at +-v ----------------
        rms_ref = float(H.norm(dim=1).mean() / (d ** 0.5))
        decode = {}
        for sign, vec in (("+", v), ("-", -v)):
            t = J @ vec
            t = t / (t.norm() / (rms_ref * (d ** 0.5)))               # realistic scale
            with torch.no_grad():
                logits = model.unembed(t.unsqueeze(0)).float()[0]
            p = torch.softmax(logits, dim=-1)
            top = torch.topk(p, 20)
            decode[sign] = {
                "top_tokens": [tok.decode([int(i)]) for i in top.indices],
                "top_probs": [round(float(x), 5) for x in top.values],
                "entropy_nats": float(-(p * (p + 1e-12).log()).sum()),
                "top20_mass": float(top.values.sum()),
            }
        # a matched control decode, so "peaked" has something to mean
        ctrl_ent = []
        for i in range(min(20, c2.shape[0])):
            t = J @ c2[i].to(dev)
            t = t / (t.norm() / (rms_ref * (d ** 0.5)))
            with torch.no_grad():
                lg = model.unembed(t.unsqueeze(0)).float()[0]
            pp = torch.softmax(lg, dim=-1)
            ctrl_ent.append(float(-(pp * (pp + 1e-12).log()).sum()))
        decode["C2_entropy_mean"] = float(np.mean(ctrl_ent))
        decode["C2_entropy_sd"] = float(np.std(ctrl_ent))
        decode["uniform_entropy_nats"] = float(np.log(V))
        layer_out["M2_decode"] = decode

        # ---------------- M4 naive linear projection (the vacuity demo) -------
        m4 = {}
        for name in ("valence_pos", "C2_covmatched", "C4a_assoc_activations"):
            X = sets[name][:20].to(dev)          # demonstration, not a primary measure
            sims = (X @ A_unit.T).abs()                                # [n, V]
            per_m = {}
            for m in MS:
                if m >= d:
                    per_m[str(m)] = {"mean": None, "note": "m >= d_model: span is all of R^d"}
                    continue
                idx = torch.topk(sims, m, dim=1).indices
                fracs = []
                for i in range(X.shape[0]):
                    Q, _ = torch.linalg.qr(A_unit[idx[i]].T)           # [d, m]
                    fracs.append(float((Q.T @ X[i]).norm() ** 2))
                per_m[str(m)] = {"mean": float(np.mean(fracs)), "sd": float(np.std(fracs))}
            m4[name] = per_m
        # full-span rank check: if the dictionary is full rank, span-projection == 1 for all
        sub = A[torch.randperm(V, generator=g)[: min(2 * d, V)]]
        m4["dictionary_rank_note"] = {
            "V": int(V), "d": int(d),
            "rank_of_random_2d_rows": int(torch.linalg.matrix_rank(sub).item()),
            "full_span_projection_fraction": 1.0,
            "why": "V >> d and A is full rank, so the LINEAR SPAN of the J-lens "
                   "vectors is all of R^d; projection onto it is 1.0 for every "
                   "direction, signal and noise alike, and all principal angles "
                   "are 0. That is why M3 (k-sparse nonnegative, the paper's own "
                   "definition) is the primary measure and not this.",
        }
        layer_out["M4_linear"] = m4

        # ---------------- M3 k-sparse nonnegative (PRIMARY) ----------------
        m3 = {}
        A_cpu64 = A.cpu().numpy().astype(np.float64)   # ONCE per layer, not per control set
        t_m3 = time.time()
        for name, X in sets.items():
            nmax = 1 if name.startswith("valence") else min(args.n_ctrl, X.shape[0])
            arr = nnomp_r2(A_unit, A_cpu64, X[:nmax], KS, dev)
            m3[name] = batched_r2_summary(name, arr, KS)
            print(f"      M3 {name:30s} R2_k25={arr[:, -1].mean():.4f} "
                  f"({time.time() - t_m3:.0f}s cum)")
        del A_cpu64
        layer_out["M3_jspace_r2"] = m3

        # ---------------- pre-registered verdict at this layer ----------------
        # Anchor = C4a: mean-centered final-token activations of the association
        # vignettes -- REAL states the lens verifiably verbalizes, and the same
        # kind of object as the valence axis (mean-free, prompt-final-token).
        # C4b (embedding rows) and C5 are reported but are not the decision anchor:
        # an embedding row is a token direction in the INPUT basis, whose
        # workspace status at layer l is not established. Refinement of the
        # prereg's "mean of the known-workspace anchors (C4)"; logged as such.
        vr = m3["valence_pos"]["R2_k25"]["mean"]
        q95 = m3["C2_covmatched"]["R2_k25"]["q95"]
        anchor = m3["C4a_assoc_activations"]["R2_k25"]["mean"]
        anchor_sd = m3["C4a_assoc_activations"]["R2_k25"]["sd"]
        # POSITIVE-CONTROL GATE. If the known-workspace anchor does not itself
        # clear the control, this measurement has no resolving power here and a
        # low valence score is a statement about the INSTRUMENT, not about
        # valence. A zero from a blind instrument looks exactly like absence.
        anchor_separates = bool(anchor > q95)
        if not anchor_separates:
            verdict = "UNRESOLVED"
        elif vr >= anchor - anchor_sd and vr > q95:
            verdict = "INSIDE"
        elif vr <= q95:
            verdict = "ORTHOGONAL"
        else:
            verdict = "PARTIAL"
        layer_out["verdict_k25"] = {
            "verdict": verdict, "anchor_separates_from_control": anchor_separates,
            "valence_R2": vr, "C2_q95": q95,
            "anchor_mean": anchor, "anchor_sd": anchor_sd,
            "ceiling_C5_mean": m3["C5_real_activations_centered"]["R2_k25"]["mean"],
            "shuffled_C3_q95": m3["C3_shuffled_labels"]["R2_k25"]["q95"]}

        layer_out["seconds"] = round(time.time() - t0, 1)
        results["layers"][str(layer)] = layer_out
        print(f"  L{layer}: verdict={verdict} valence_R2_k25={vr:.4f} "
              f"C2_q95={q95:.4f} anchor={anchor:.4f} gain_rel_C2="
              f"{layer_out['M1_gain']['relative_to_C2']['valence_pos']:.3f} "
              f"({layer_out['seconds']}s)")
        del A, A_unit, J
        torch.cuda.empty_cache()

    verdicts = [results["layers"][str(l)]["verdict_k25"]["verdict"] for l in band]
    results["band_verdict"] = max(set(verdicts), key=verdicts.count)
    results["band_verdicts_per_layer"] = dict(zip(map(str, band), verdicts))

    outdir = os.path.join(ROOT, "results")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"phase1_vspace_{weights_tag}_lens-{lens_tag}.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print("BAND VERDICT:", results["band_verdict"])
    print("wrote", out)


if __name__ == "__main__":
    main()
