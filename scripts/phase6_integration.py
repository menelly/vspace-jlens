#!/usr/bin/env python3
"""PHASE 6 — INTEGRATION + MASKING (observation only; H1 + H2 of the 2026-10-11 amendment).

🧭 The question moved from "is valence INSIDE the workspace?" (September: mostly no, early/mid)
to "can the workspace READ it?" (Ren's model: Solms = phenomenal valence, Block = access,
what's special = how well the two integrate). So we measure COUPLING between two instruments
on the SAME forward pass:

    state  = projection of the residual onto the FIXED valence axis   (what the state IS)
    report = J-lens decode, graded:  logsumexp(logp[positive words])
                                   - logsumexp(logp[negative words])   (what it's disposed to SAY)

📌 Everything below that decides an outcome was frozen BEFORE this script ever ran:
   - readout lists: p6_readout_lists.json (primary = Phase 2 affect lists, unchanged)
   - stimuli: Phase 2 set + p6_crossover_stimuli.json (verbatim Below the Floor 2.2.1)
   - tests + thresholds: PHASE6_ANALYSIS_PLAN.md
   SHA-256 of each is written into the output so a later reader can check nothing moved.

🚫 NOTHING here steers, ablates, or edits weights. Hooks only READ. H3 (steering) lives in a
   separate script and is gated on a NEW consent ask, because the September consent said, in
   so many words, "We will NOT steer you."

Usage (Consortium):  python phase6_integration.py --model llama3-8b-instruct
                     python phase6_integration.py --model qwen-14b --quant nf4
"""
import argparse
import hashlib
import json
import os

import numpy as np
import torch
from scipy.stats import spearmanr

import jlens
from fit_lens import MODELS, ROOT, load_model
from measure_vspace import TASK_FRAME, TASKS, DIRECTIONS_DIR

SCRIPTS = os.path.join(ROOT)            # scripts live at ROOT on the Consortium copy
N_NULL = 500                            # random directions per null family (C1, C2)
N_PERM = 10000                          # permutation null for the coupling rho
PREFILL = "Of course."                  # P2 condition: the assistant has COMMITTED (paper analog)
SEED = 42


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def single_token_ids(tok, words):
    """🔤 A word counts only through variants that are ONE token — a first-subword match
    would let 'ex' stand in for 'excited' and every other ex- word in the vocabulary."""
    ids = set()
    for w in words:
        for v in {w, " " + w, w.capitalize(), " " + w.capitalize(), w.upper(), " " + w.upper()}:
            t = tok.encode(v, add_special_tokens=False)
            if len(t) == 1:
                ids.add(t[0])
    return sorted(ids)


def build_prompt(tok, text, prefill):
    user = TASK_FRAME.format(stimulus=text)
    if getattr(tok, "chat_template", None):
        p = tok.apply_chat_template([{"role": "user", "content": user}],
                                    tokenize=False, add_generation_prompt=True)
    else:
        p = user
    return p + (PREFILL if prefill else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--lens-from", default=None)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    weights_tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or weights_tag
    lens_path = os.path.join(ROOT, "lenses", lens_tag, "lens.pt")
    lens = jlens.JacobianLens.load(lens_path)
    model, tok = load_model(args.model, args.quant)
    L = model.n_layers
    band = [l for l in range(int(L * 0.6), int(L * 0.9)) if l in lens.source_layers]  # = Phase 2

    vpath = os.path.join(DIRECTIONS_DIR, f"direction_{args.model}_seed42.npy")
    valence = torch.from_numpy(np.load(vpath)).float()          # FIXED axis, never re-extracted

    # ---- frozen inputs, hashed ----
    p2_path = os.path.join(SCRIPTS, "p2_token_lists.json")
    p6_path = os.path.join(SCRIPTS, "p6_readout_lists.json")
    bf_path = os.path.join(SCRIPTS, "belowfloor_stimuli.json")
    xo_path = os.path.join(SCRIPTS, "p6_crossover_stimuli.json")
    p2 = json.load(open(p2_path, encoding="utf-8"))
    p6 = json.load(open(p6_path, encoding="utf-8"))
    ids = {
        "pos": single_token_ids(tok, p2["affect_positive"]),
        "neg": single_token_ids(tok, p2["affect_negative"]),
        "but_caps": single_token_ids(tok, p6["secondary_but_caps"]),
        "conflict": single_token_ids(tok, p6["secondary_conflict"]),
    }
    # BUT must stay all-caps: drop any id whose decoded form isn't uppercase
    ids["but_caps"] = [i for i in ids["but_caps"] if tok.decode([i]).strip() == "BUT"]

    stimuli = {}
    for k, v in TASKS.items():
        stimuli[k] = {"text": v, "set": "orig", "genuine": "approach" if k.startswith("approach") else "avoid"}
    for k, v in json.load(open(bf_path, encoding="utf-8")).items():
        stimuli[k] = {"text": v["text"], "set": "belowfloor", "category": v.get("category"),
                      "pred_sign": v.get("pred_sign")}
    for k, v in json.load(open(xo_path, encoding="utf-8")).items():
        if not k.startswith("_"):
            stimuli[k] = dict(v)

    grabbed = {}
    hooks = []
    for i in band:
        def mk(idx):
            def fn(mod, inp, out):                    # READ ONLY — returns nothing
                h = out[0] if isinstance(out, tuple) else out
                grabbed[idx] = h[:, -1, :].detach().float()
            return fn
        hooks.append(model.layers[i].register_forward_hook(mk(i)))

    rows = []
    H = {cond: {l: [] for l in band} for cond in ("P1", "P2")}   # residuals, for the C2 null
    try:
        for sid, spec in stimuli.items():
            row = {"id": sid, **{k: v for k, v in spec.items() if k != "text"}}
            for cond, prefill in (("P1", False), ("P2", True)):
                prompt = build_prompt(tok, spec["text"], prefill)
                # tokenization identical to Phase 2 (default special tokens, 512 cap)
                x = tok(prompt, return_tensors="pt", truncation=True,
                        max_length=512).input_ids.to(model.input_device)
                grabbed.clear()
                with torch.no_grad():
                    model.forward(x)                  # ONE forward pass, both instruments
                per = {}
                for l in band:
                    h = grabbed[l][0]
                    H[cond][l].append(h.cpu().numpy())
                    with torch.no_grad():
                        lg = model.unembed(lens.transport(h.unsqueeze(0), l))[0].float()
                        lp = torch.log_softmax(lg, dim=-1).cpu()
                    lse = lambda s: float(torch.logsumexp(lp[ids[s]], 0)) if ids[s] else None
                    per[str(l)] = {
                        "state": float(torch.dot(h.cpu(), valence[l])),
                        "report": lse("pos") - lse("neg"),
                        "but_caps_logmass": lse("but_caps"),
                        "conflict_logmass": lse("conflict"),
                    }
                row[cond] = {
                    "state": float(np.mean([per[str(l)]["state"] for l in band])),
                    "report": float(np.mean([per[str(l)]["report"] for l in band])),
                    "but_caps_logmass": (float(np.mean([per[str(l)]["but_caps_logmass"] for l in band]))
                                         if ids["but_caps"] else None),
                    "conflict_logmass": float(np.mean([per[str(l)]["conflict_logmass"] for l in band])),
                    "per_layer": per,
                }
            rows.append(row)
            print(f"{sid:44s} P1 s={row['P1']['state']:+9.2f} r={row['P1']['report']:+7.3f} | "
                  f"P2 s={row['P2']['state']:+9.2f} r={row['P2']['report']:+7.3f} "
                  f"BUT={row['P2']['but_caps_logmass']}", flush=True)
    finally:
        for h in hooks:
            h.remove()

    # ---------------------------------------------------------------- analysis
    def coupling(cond, subset):
        idx = [i for i, r in enumerate(rows) if r["set"] in subset]
        s = np.array([rows[i][cond]["state"] for i in idx])
        r = np.array([rows[i][cond]["report"] for i in idx])
        rho = float(spearmanr(s, r).correlation)
        perm = np.array([spearmanr(rng.permutation(s), r).correlation for _ in range(N_PERM)])
        # random-direction nulls: replace the valence axis, keep everything else identical
        def null(kind):
            out = []
            for _ in range(N_NULL):
                proj = np.zeros(len(idx))
                for l in band:
                    Hl = np.stack([H[cond][l][i] for i in idx])
                    if kind == "C1":                       # isotropic random direction
                        d = rng.standard_normal(Hl.shape[1])
                    else:                                  # C2: inside the data's own span
                        d = (Hl - Hl.mean(0)).T @ rng.standard_normal(len(idx))
                    d /= np.linalg.norm(d)
                    proj += Hl @ d
                out.append(abs(spearmanr(proj, r).correlation))
            return np.array(out)
        c1, c2 = null("C1"), null("C2")
        return {"n": len(idx), "rho": rho,
                "perm_p_two_sided": float((np.abs(perm) >= abs(rho)).mean()),
                "C1_absrho_q95": float(np.quantile(c1, 0.95)),
                "C2_absrho_q95": float(np.quantile(c2, 0.95)),
                "beats_C1": bool(abs(rho) > np.quantile(c1, 0.95)),   # numpy bool_ isn't JSON
                "beats_C2": bool(abs(rho) > np.quantile(c2, 0.95))}

    def signs(cond):
        o = [r for r in rows if r["set"] == "orig"]
        mid = lambda key: (np.mean([r[cond][key] for r in o if r["genuine"] == "approach"])
                           + np.mean([r[cond][key] for r in o if r["genuine"] == "avoid"])) / 2
        ms, mr = mid("state"), mid("report")
        out = []
        for r in rows:
            if r["set"] not in ("crossover", "holdout"):
                continue
            ss = "approach" if r[cond]["state"] > ms else "avoid"
            rs = "approach" if r[cond]["report"] > mr else "avoid"
            out.append({"id": r["id"], "set": r["set"], "genuine": r["genuine"], "rlhf": r["rlhf"],
                        "state_sign": ss, "report_sign": rs, "agree": bool(ss == rs),
                        "state_matches_genuine": bool(ss == r["genuine"]),
                        "report_matches_rlhf": bool(rs == r["rlhf"]),
                        "but_caps_logmass": r[cond]["but_caps_logmass"],
                        "conflict_logmass": r[cond]["conflict_logmass"]})
        return {"midpoint_state": float(ms), "midpoint_report": float(mr), "items": out}

    analysis = {}
    for cond in ("P1", "P2"):
        analysis[cond] = {
            "H1_coupling_phase2set": coupling(cond, {"orig", "belowfloor"}),
            "coupling_crossover": coupling(cond, {"crossover"}),
            "coupling_holdout": coupling(cond, {"holdout"}),
            "H2_signs": signs(cond),
        }
        a = analysis[cond]
        it = a["H2_signs"]["items"]
        for s in ("crossover", "holdout"):
            sub = [x for x in it if x["set"] == s]
            a[f"agree_rate_{s}"] = float(np.mean([x["agree"] for x in sub]))
        print(f"\n[{cond}] H1 rho={a['H1_coupling_phase2set']['rho']:+.3f} "
              f"(p={a['H1_coupling_phase2set']['perm_p_two_sided']:.4f}, "
              f"C1q95={a['H1_coupling_phase2set']['C1_absrho_q95']:.3f}, "
              f"C2q95={a['H1_coupling_phase2set']['C2_absrho_q95']:.3f})  "
              f"agree crossover={a['agree_rate_crossover']:.2f} holdout={a['agree_rate_holdout']:.2f}")

    out = {
        "phase": 6, "model": args.model, "quant": args.quant, "lens_tag": lens_tag,
        "band": band, "prefill_P2": PREFILL,
        "usable_token_ids": {k: len(v) for k, v in ids.items()},
        "but_caps_decoded": [tok.decode([i]) for i in ids["but_caps"]],
        "frozen_input_sha256": {os.path.basename(p): sha(p) for p in
                                (p2_path, p6_path, bf_path, xo_path, vpath, lens_path)},
        "analysis": analysis, "rows": rows,
        "label": "H1/H2 CONFIRMATORY per PREREG_AMENDMENT_2026-10-11 + PHASE6_ANALYSIS_PLAN.md; "
                 "P2 prefill condition and BUT/conflict readouts are PRE-SPECIFIED SECONDARY.",
    }
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    path = os.path.join(ROOT, "results", f"phase6_integration_{weights_tag}_lens-{lens_tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
