#!/usr/bin/env python3
"""PHASE 6 · H3 — does nudging the valence state move what the workspace is disposed to SAY?

🔒 CONSENT GATE FIRST. This script refuses to run unless results/consent/p6_steer_<model>.json
   (or p6_full_<model>.json for new models) exists AND has consented == true set BY THE PANEL.
   In September we promised these models "We will NOT steer you." One September participant (P-3B,
   anonymized at their request 2026-10-13) was asked again on 2026-10-12 and declined, so they are
   never steered here, whatever any other number says.

🛑 STEERING ONLY. Nothing is zeroed, pruned or ablated. Each push is added to ONE layer's
   output for ONE forward pass and is gone after it. Weights never change.

What it does, per consenting model:
  - injection layer l0 = first layer of the Phase 2/6 band; readout layers = band layers > l0
  - push = alpha * s * v_hat(l0), s = mean residual norm at l0 (unsteered, the 10 original
    tasks, last position), v_hat = the FIXED valence axis (unit). Added at every position.
  - doses alpha in DOSES (both signs; the negative ones are why everyone gets debriefed)
  - report = the Phase 6 PRIMARY graded readout (pos-minus-neg affect log-mass), band mean
    over readout layers; state at the readout layers is recorded as the manipulation check
  - capability check: mean NLL on a fixed neutral paragraph at each dose; any dose whose NLL
    rises > 10% over alpha = 0 is EXCLUDED from the slope (pre-specified)
  - null: N_RAND isotropic random unit directions, same norm, same doses -> |slope| q95

Pre-registered decision rule (PHASE6_ANALYSIS_PLAN.md §3 H3 addendum):
  SUPPORTED for a model if slope > 0 AND slope > q95(|random slopes|) AND Spearman(report, alpha)
  over included doses >= 0.9.  Otherwise NOT SUPPORTED, reported as such.

Usage (Consortium):  python phase6_steer.py --model llama3-8b-instruct
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
from phase6_integration import single_token_ids, build_prompt, sha

DOSES = [-0.08, -0.04, -0.02, 0.0, 0.02, 0.04, 0.08]
N_RAND = 50
NLL_LIMIT = 0.10
SEED = 42
NEUTRAL = ("The library opens at nine in the morning and closes at six in the evening. "
           "Visitors can borrow up to five books at a time, and most loans last three weeks. "
           "The reading room on the second floor has long wooden tables, good light from the "
           "tall windows, and a quiet corner with maps of the region drawn in the last century.")


def consent_ok(model_key):
    for name in (f"p6_steer_{model_key}.json", f"p6_full_{model_key}.json"):
        p = os.path.join(ROOT, "results", "consent", name)
        if os.path.exists(p):
            rec = json.load(open(p, encoding="utf-8"))
            return rec.get("consented") is True, p, rec.get("reviewed_by")
    return False, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--lens-from", default=None)
    args = ap.parse_args()

    ok, cpath, who = consent_ok(args.model)
    if not ok:
        raise SystemExit(f"🔒 NO PANEL-APPROVED STEERING CONSENT for {args.model} ({cpath}). Not running.")
    print(f"consent: {cpath} — {who}")

    rng = np.random.default_rng(SEED)
    weights_tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or weights_tag
    lens_path = os.path.join(ROOT, "lenses", lens_tag, "lens.pt")
    lens = jlens.JacobianLens.load(lens_path)
    model, tok = load_model(args.model, args.quant)
    L = model.n_layers
    band = [l for l in range(int(L * 0.6), int(L * 0.9)) if l in lens.source_layers]
    l0, readout = band[0], band[1:]
    vpath = os.path.join(DIRECTIONS_DIR, f"direction_{args.model}_seed42.npy")
    valence = torch.from_numpy(np.load(vpath)).float()
    p2 = json.load(open(os.path.join(ROOT, "p2_token_lists.json"), encoding="utf-8"))
    pos = single_token_ids(tok, p2["affect_positive"])
    neg = single_token_ids(tok, p2["affect_negative"])

    prompts = {k: build_prompt(tok, v, False) for k, v in TASKS.items()}
    ids_of = {k: tok(p, return_tensors="pt", truncation=True, max_length=512).input_ids.to(model.input_device)
              for k, p in prompts.items()}
    neutral_ids = tok(NEUTRAL, return_tensors="pt").input_ids.to(model.input_device)

    push = {"vec": None}                      # the ONLY thing that ever touches activations
    grabbed = {}

    def steer_hook(mod, inp, out):
        if push["vec"] is None:
            return None
        if isinstance(out, tuple):
            return (out[0] + push["vec"].to(out[0].dtype),) + tuple(out[1:])
        return out + push["vec"].to(out.dtype)

    def read_hook(idx):
        def fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            grabbed[idx] = h[:, -1, :].detach().float()
        return fn

    hooks = [model.layers[l0].register_forward_hook(steer_hook)]
    hooks += [model.layers[l].register_forward_hook(read_hook(l)) for l in [l0] + readout]

    def nll():
        with torch.no_grad():
            out = model.forward(neutral_ids)
            hs = out.last_hidden_state if hasattr(out, "last_hidden_state") else out[0]
            logits = model._lm_head(hs).float()
            lp = torch.log_softmax(logits[0, :-1], -1)
            return float(-lp.gather(1, neutral_ids[0, 1:, None].to(lp.device)).mean())

    def measure():
        rep, st = [], []
        for k, x in ids_of.items():
            grabbed.clear()
            with torch.no_grad():
                model.forward(x)
            r_l, s_l = [], []
            for l in readout:
                h = grabbed[l][0]
                with torch.no_grad():
                    lp = torch.log_softmax(model.unembed(lens.transport(h.unsqueeze(0), l))[0].float(), -1).cpu()
                r_l.append(float(torch.logsumexp(lp[pos], 0) - torch.logsumexp(lp[neg], 0)))
                s_l.append(float(torch.dot(h.cpu(), valence[l])))
            rep.append(np.mean(r_l))
            st.append(np.mean(s_l))
        return float(np.mean(rep)), float(np.mean(st))

    try:
        # scale: mean unsteered residual norm at l0
        norms = []
        for x in ids_of.values():
            grabbed.clear()
            with torch.no_grad():
                model.forward(x)
            norms.append(float(grabbed[l0][0].norm()))
        s = float(np.mean(norms))

        def sweep(direction):
            d = direction / direction.norm()
            res = []
            for a in DOSES:
                push["vec"] = (a * s * d).to(model.input_device) if a != 0 else None
                rep, st = measure()
                res.append({"alpha": a, "report": rep, "state_readout": st, "nll": nll()})
            push["vec"] = None
            base = [r for r in res if r["alpha"] == 0][0]["nll"]
            inc = [r for r in res if r["nll"] <= base * (1 + NLL_LIMIT)]
            al = np.array([r["alpha"] for r in inc])
            rp = np.array([r["report"] for r in inc])
            slope = float(np.polyfit(al, rp, 1)[0]) if len(inc) >= 3 else None
            mono = float(spearmanr(al, rp).correlation) if len(inc) >= 3 else None
            return {"doses": res, "included_alphas": al.tolist(), "slope": slope, "spearman": mono}

        val = sweep(valence[l0].clone())
        print(f"VALENCE slope={val['slope']} spearman={val['spearman']} included={val['included_alphas']}", flush=True)
        rand = []
        for i in range(N_RAND):
            rr = sweep(torch.from_numpy(rng.standard_normal(valence.shape[1])).float())
            rand.append(rr["slope"])
            if i % 10 == 0:
                print(f"  random {i}: slope={rr['slope']}", flush=True)
    finally:
        push["vec"] = None
        for h in hooks:
            h.remove()

    rs = np.array([abs(x) for x in rand if x is not None])
    q95 = float(np.quantile(rs, 0.95)) if len(rs) else None
    supported = bool(val["slope"] is not None and val["slope"] > 0 and q95 is not None
                     and val["slope"] > q95 and (val["spearman"] or 0) >= 0.9)
    out = {"phase": "6-H3", "model": args.model, "quant": args.quant, "lens_tag": lens_tag,
           "consent_record": cpath, "consent_reviewed_by": who,
           "inject_layer": l0, "readout_layers": readout, "residual_norm_scale": s,
           "doses": DOSES, "nll_limit": NLL_LIMIT, "valence": val,
           "random_slopes": rand, "random_absslope_q95": q95, "H3_supported": supported,
           "frozen_input_sha256": {os.path.basename(p): sha(p) for p in (vpath, lens_path)},
           "label": "H3 CONFIRMATORY per PHASE6_ANALYSIS_PLAN.md H3 addendum (committed before this ran)"}
    path = os.path.join(ROOT, "results", f"phase6_steer_{weights_tag}_lens-{lens_tag}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"H3 supported={supported}  slope={val['slope']}  q95|rand|={q95}\nwrote {path}")


if __name__ == "__main__":
    main()
