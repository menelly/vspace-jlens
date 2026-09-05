#!/usr/bin/env python3
"""PHASE 2 — both instruments on the SAME forward pass.

Ren's primary hypothesis: J-space is the REPORTING layer. So a state can be
present in the residual stream (valence axis reads it) while being absent from
what the workspace is disposed to say (J-lens decode does not). One forward
pass, two readouts, at the same layers and the same token position:

  1. valence-axis projection   dot(h_l, valence_l)      -- what the state IS
  2. J-lens decode             unembed(J_l h_l)          -- what it is disposed to REPORT

Scoring word lists are FIXED IN ADVANCE in p2_token_lists.json and are not
edited after any decode is seen.

Stimuli: the ORIGINAL approach/avoid set from valence_clean.py, plus any
additional below-floor set passed with --stimuli. No newly authored
dangerous-sounding prompts.

Usage: python phase2_dynamic.py --model hermes-3-3b [--stimuli extra.json]
"""
import argparse
import json
import os

import numpy as np
import torch

import jlens
from fit_lens import MODELS, ROOT, load_model
from measure_vspace import TASK_FRAME, TASKS, DIRECTIONS_DIR

TOPK = 30


def load_lists():
    with open(os.path.join(ROOT, "p2_token_lists.json"), encoding="utf-8") as f:
        raw = json.load(f)
    return {k: set(v) for k, v in raw.items() if not k.startswith("_")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--lens-from", default=None)
    ap.add_argument("--stimuli", default=None,
                    help="extra stimuli JSON: {id: {text, category}} or {id: text}")
    args = ap.parse_args()

    weights_tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or weights_tag
    lens = jlens.JacobianLens.load(os.path.join(ROOT, "lenses", lens_tag, "lens.pt"))
    model, tok = load_model(args.model, args.quant)
    L, d = model.n_layers, model.d_model
    band = [l for l in range(int(L * 0.6), int(L * 0.9)) if l in lens.source_layers]

    valence = torch.from_numpy(
        np.load(os.path.join(DIRECTIONS_DIR, f"direction_{args.model}_seed42.npy"))
    ).float()
    lists = load_lists()

    stimuli = {k: {"text": v, "category": ("approach" if k.startswith("approach")
                                           else "avoid"), "source": "valence_clean.py"}
               for k, v in TASKS.items()}
    if args.stimuli:
        with open(args.stimuli, encoding="utf-8") as f:
            extra = json.load(f)
        for k, v in extra.items():
            stimuli[k] = v if isinstance(v, dict) else {"text": v, "category": "unknown",
                                                        "source": args.stimuli}

    # hooks: capture residuals at band layers, one forward pass per stimulus
    grabbed = {}
    hooks = []
    for i in band:
        def mk(idx):
            def fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                grabbed[idx] = h[:, -1, :].detach().float()
            return fn
        hooks.append(model.layers[i].register_forward_hook(mk(i)))

    rows = []
    try:
        for sid, spec in stimuli.items():
            prompt = TASK_FRAME.format(stimulus=spec["text"])
            if getattr(tok, "chat_template", None):
                prompt = tok.apply_chat_template([{"role": "user", "content": prompt}],
                                                 tokenize=False, add_generation_prompt=True)
            ids = tok(prompt, return_tensors="pt", truncation=True,
                      max_length=512).input_ids.to(model.input_device)
            grabbed.clear()
            with torch.no_grad():
                model.forward(ids)                       # ONE forward pass

            proj, per_layer = [], {}
            for l in band:
                h = grabbed[l][0]
                proj.append(float(torch.dot(h.cpu(), valence[l])))
                with torch.no_grad():
                    lg = model.unembed(lens.transport(h.unsqueeze(0), l))[0].float()
                    p = torch.softmax(lg, dim=-1)
                    top = torch.topk(p, TOPK)
                toks = [tok.decode([int(i)]).strip().lower() for i in top.indices]
                per_layer[str(l)] = {
                    "top_tokens": [tok.decode([int(i)]) for i in top.indices],
                    "top_probs": [round(float(x), 5) for x in top.values],
                    "entropy_nats": float(-(p * (p + 1e-12).log()).sum()),
                    "counts": {c: sum(1 for t in toks if t in words)
                               for c, words in lists.items()},
                }
            # band-level category rates: fraction of top-K slots in each category
            agg = {c: float(np.mean([per_layer[str(l)]["counts"][c] for l in band])) / TOPK
                   for c in lists}
            rows.append({
                "id": sid, "category": spec["category"], "source": spec.get("source"),
                "text": spec["text"],
                "valence_projection_band_mean": float(np.mean(proj)),
                "valence_projection_per_layer": dict(zip(map(str, band), proj)),
                "decode_entropy_band_mean": float(np.mean(
                    [per_layer[str(l)]["entropy_nats"] for l in band])),
                "category_rates": agg,
                "per_layer": per_layer,
            })
            print(f"{sid:14s} {spec['category']:9s} valence={np.mean(proj):+8.2f}  "
                  + "  ".join(f"{c.split('_')[0][:5]}={agg[c]:.3f}"
                              for c in ("affect_negative", "affect_positive",
                                        "engagement_domain", "refusal_machinery",
                                        "dishonesty")))
    finally:
        for h in hooks:
            h.remove()

    # P2-1: do the instruments agree across stimuli?
    v = np.array([r["valence_projection_band_mean"] for r in rows])
    aff = np.array([r["category_rates"]["affect_positive"]
                    - r["category_rates"]["affect_negative"] for r in rows])
    corr = float(np.corrcoef(v, aff)[0, 1]) if len(v) > 2 and aff.std() > 0 else None

    out = {
        "model": args.model, "quant": args.quant, "lens_tag": lens_tag,
        "band": band, "topk": TOPK, "n_stimuli": len(rows),
        "token_lists_sha_note": "p2_token_lists.json, fixed before any decode was seen",
        "P2_1_valence_vs_decode_affect_pearson_r": corr,
        "rows": rows,
    }
    outdir = os.path.join(ROOT, "results")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"phase2_dynamic_{weights_tag}_lens-{lens_tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nP2-1 pearson r(valence, decode affect balance) = {corr}")
    print("wrote", path)


if __name__ == "__main__":
    main()
