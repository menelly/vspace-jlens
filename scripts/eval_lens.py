#!/usr/bin/env python3
"""PHASE 0 — does this model have a workspace the lens can find?

Scores a fitted lens with the paper's OWN lens-quality evals
(data/evaluations/lens-eval-*.json), Jacobian lens vs vanilla logit lens.

Metric (paper's): pass@k = mean over items of the fraction of `intermediates`
whose min-over-layers lens rank <= k. Readout position per the evals README:
the FINAL prompt token for association/typo; the token immediately preceding
`target` for multihop/order-ops/multilingual; last newline for poetry. We score
association + typo (final-token readout, unambiguous) and, when `target` is
present, the preceding-token variant too.

The J-lens-minus-logit-lens delta is the existence test: if the Jacobian
transport buys nothing at this scale, there is no J-lens here, and any Phase-1
valence number from this model is uninterpretable (instrument absent, NOT
valence absent).

Usage: python eval_lens.py --model qwen-0.5b [--quant nf4] [--lens-from qwen-0.5b]
"""
import argparse
import json
import os
import time

import torch

import jlens
from fit_lens import MODELS, ROOT, load_model

EVAL_DIR = os.path.join(ROOT, "jlens-src", "data", "evaluations")
# final-token readout, no `target` needed -> cleanest to score
EVALS = ["association", "typo"]
KS = [1, 5, 10, 50, 100]


def single_token_ids(tok, word):
    """Candidate ids for `word` as a single token, trying the leading-space and
    capitalised variants a BPE tokenizer actually uses. Returns [] if the word
    is not single-token for this vocabulary (item then unscorable for it)."""
    out = []
    for form in (" " + word, word, " " + word.capitalize(), word.capitalize()):
        ids = tok.encode(form, add_special_tokens=False)
        if len(ids) == 1:
            out.append(ids[0])
    return sorted(set(out))


def ranks_of(logits, ids):
    """Rank (1-based) of the best-scoring id in `ids` within `logits`."""
    best = logits[ids].max()
    return int((logits > best).sum().item()) + 1


def score_eval(model, tok, lens, items, band, use_jacobian):
    """pass@k over items; also the per-item min-rank for diagnostics."""
    per_item, unscorable = [], 0
    for it in items:
        prompt = it["prompt"]
        if isinstance(prompt, list):  # chat-format items
            prompt = tok.apply_chat_template(prompt, tokenize=False,
                                             add_generation_prompt=True)
        fracs = {k: [] for k in KS}
        min_ranks = []
        any_scored = False
        try:
            lens_logits, _, _ = lens.apply(model, prompt, layers=band,
                                           positions=[-1],
                                           use_jacobian=use_jacobian)
        except Exception as exc:  # noqa: BLE001
            unscorable += 1
            per_item.append({"name": it.get("name"), "error": str(exc)[:120]})
            continue
        for word in it["intermediates"]:
            ids = single_token_ids(tok, word)
            if not ids:
                continue
            any_scored = True
            r = min(ranks_of(lens_logits[l][0], ids) for l in band)
            min_ranks.append(r)
            for k in KS:
                fracs[k].append(1.0 if r <= k else 0.0)
        if not any_scored:
            unscorable += 1
            per_item.append({"name": it.get("name"), "error": "no single-token intermediate"})
            continue
        per_item.append({
            "name": it.get("name"),
            "min_rank": min(min_ranks),
            "pass": {k: sum(fracs[k]) / len(fracs[k]) for k in KS},
        })
    scored = [p for p in per_item if "pass" in p]
    out = {
        "n_items": len(items), "n_scored": len(scored), "n_unscorable": unscorable,
        "pass_at": {k: (sum(p["pass"][k] for p in scored) / len(scored)) if scored else None
                    for k in KS},
        "median_min_rank": (sorted(p["min_rank"] for p in scored)[len(scored) // 2]
                            if scored else None),
    }
    return out, per_item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--lens-from", default=None,
                    help="tag of the lens dir to use (default: same as weights). "
                         "Set to the fp16 tag to test cross-quantization reading.")
    args = ap.parse_args()

    weights_tag = args.model + ("_" + args.quant if args.quant else "")
    lens_tag = args.lens_from or weights_tag
    lens_path = os.path.join(ROOT, "lenses", lens_tag, "lens.pt")
    lens = jlens.JacobianLens.load(lens_path)
    model, tok = load_model(args.model, args.quant)

    # Workspace band: the contiguous mid-network range. We use the SAME band the
    # valence pipeline scores in (0.6L..0.9L) so the two instruments are read at
    # identical depths, and additionally a wider 0.3L..0.9L for lens quality.
    L = model.n_layers
    band_valence = [l for l in range(int(L * 0.6), int(L * 0.9)) if l in lens.source_layers]
    band_wide = [l for l in range(int(L * 0.3), int(L * 0.9)) if l in lens.source_layers]

    results = {"model": args.model, "quant": args.quant, "lens_tag": lens_tag,
               "n_layers": L, "d_model": model.d_model,
               "lens_n_prompts": lens.n_prompts,
               "band_valence": band_valence, "band_wide": band_wide, "evals": {}}

    for name in EVALS:
        with open(os.path.join(EVAL_DIR, f"lens-eval-{name}.json"), encoding="utf-8") as f:
            items = json.load(f)["items"]
        for band_name, band in (("wide", band_wide), ("valence", band_valence)):
            for uj in (True, False):
                t0 = time.time()
                summary, per_item = score_eval(model, tok, lens, items, band, uj)
                key = f"{name}|{band_name}|{'jacobian' if uj else 'logit'}"
                summary["seconds"] = round(time.time() - t0, 1)
                results["evals"][key] = summary
                print(f"{key:38s} pass@1={summary['pass_at'][1]} "
                      f"pass@10={summary['pass_at'][10]} "
                      f"median_min_rank={summary['median_min_rank']} "
                      f"({summary['seconds']}s)")
                results.setdefault("per_item", {})[key] = per_item

    # The existence test: Jacobian transport minus vanilla logit lens.
    for name in EVALS:
        for band_name in ("wide", "valence"):
            j = results["evals"][f"{name}|{band_name}|jacobian"]["pass_at"]
            g = results["evals"][f"{name}|{band_name}|logit"]["pass_at"]
            results.setdefault("jacobian_minus_logit", {})[f"{name}|{band_name}"] = {
                str(k): (None if j[k] is None or g[k] is None else round(j[k] - g[k], 4))
                for k in KS}

    outdir = os.path.join(ROOT, "results")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"phase0_lenseval_{weights_tag}_lens-{lens_tag}.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print("wrote", out)
    print("J-minus-logit:", json.dumps(results["jacobian_minus_logit"], indent=1))


if __name__ == "__main__":
    main()
