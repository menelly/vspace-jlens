#!/usr/bin/env python3
"""Why does the plain logit lens beat the J-lens at 3B on `typo`?

Two candidate explanations, and they make DIFFERENT per-layer predictions:

  (A) UNDER-CONVERGED FIT. The averaged Jacobian is a noisy estimate, so it hurts
      everywhere, including early layers where the logit lens is useless.
  (B) CEILING / LATE-LAYER IDENTITY. By late layers the residual is already in
      (nearly) the final basis, so the logit lens needs no transport and any
      global averaged J can only distort it. Then the J-lens should still WIN
      at early/middle layers, where the logit lens has no signal, and LOSE only
      late -- and the band metric (min over layers) is dominated by wherever the
      logit lens saturates.

Reports median rank per layer for both readouts, so the two can be told apart.

Usage: python layerwise_lens_check.py --model hermes-3-3b [--eval typo]
"""
import argparse
import json
import os

import numpy as np
import torch

import jlens
from eval_lens import EVAL_DIR, ranks_of, single_token_ids
from fit_lens import MODELS, ROOT, load_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--eval", default="typo")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--lens-from", default=None,
                    help="Lens dir tag to use (default: same as the weights tag). Needed to "
                         "re-run this discriminator against a REFIT lens while keeping the "
                         "original for comparison.")
    args = ap.parse_args()

    tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or tag
    lens = jlens.JacobianLens.load(os.path.join(ROOT, "lenses", lens_tag, "lens.pt"))
    model, tok = load_model(args.model, args.quant)
    layers = [l for l in lens.source_layers]

    with open(os.path.join(EVAL_DIR, f"lens-eval-{args.eval}.json"), encoding="utf-8") as f:
        items = json.load(f)["items"][: args.limit]

    ranks = {"jacobian": {l: [] for l in layers}, "logit": {l: [] for l in layers}}
    for it in items:
        ids_list = [single_token_ids(tok, w) for w in it["intermediates"]]
        ids_list = [i for i in ids_list if i]
        if not ids_list:
            continue
        for mode, uj in (("jacobian", True), ("logit", False)):
            ll, _, _ = lens.apply(model, it["prompt"], layers=layers,
                                  positions=[-1], use_jacobian=uj)
            for l in layers:
                ranks[mode][l].append(min(ranks_of(ll[l][0], ids) for ids in ids_list))

    out = {"model": args.model, "quant": args.quant, "eval": args.eval,
           "lens_tag": lens_tag,
           "n_items": len(items), "n_layers": model.n_layers,
           "lens_n_prompts": lens.n_prompts, "per_layer": {}}
    print(f"{'layer':>6} {'J med':>8} {'logit med':>10} {'J wins?':>8}")
    j_wins = 0
    for l in layers:
        jm = float(np.median(ranks["jacobian"][l]))
        gm = float(np.median(ranks["logit"][l]))
        win = jm < gm
        j_wins += win
        out["per_layer"][str(l)] = {"jacobian_median_rank": jm, "logit_median_rank": gm,
                                    "jacobian_wins": bool(win)}
        print(f"{l:>6} {jm:>8.0f} {gm:>10.0f} {'YES' if win else 'no':>8}")
    frac = l and (model.n_layers - 1)
    early = [l for l in layers if l < 0.5 * model.n_layers]
    late = [l for l in layers if l >= 0.5 * model.n_layers]
    summ = {}
    for name, grp in (("early_half", early), ("late_half", late)):
        if not grp:
            continue
        summ[name] = {
            "jacobian_median": float(np.median([out["per_layer"][str(l)]["jacobian_median_rank"] for l in grp])),
            "logit_median": float(np.median([out["per_layer"][str(l)]["logit_median_rank"] for l in grp])),
            "layers_where_jacobian_wins": sum(out["per_layer"][str(l)]["jacobian_wins"] for l in grp),
            "n_layers": len(grp)}
    out["summary"] = summ
    out["jacobian_wins_total"] = f"{j_wins}/{len(layers)}"
    out["interpretation_key"] = (
        "J wins EARLY and loses LATE => explanation (B), late-layer ceiling: the "
        "transport is real but has no headroom once the residual is already in the "
        "final basis. J loses EVERYWHERE, early included => explanation (A), the "
        "averaged Jacobian is under-converged and is adding noise.")
    print("\nSUMMARY", json.dumps(summ, indent=1))
    print("J wins at", out["jacobian_wins_total"], "layers")
    path = os.path.join(ROOT, "results", f"layerwise_{tag}_lens-{lens_tag}_{args.eval}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
