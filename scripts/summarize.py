#!/usr/bin/env python3
"""Recompute every verdict UNIFORMLY from the saved Phase-0/1/2 JSON, and emit
one summary table. Applying the decision rule in one place, after the fact,
means a rule change cannot silently apply to only some models.

Includes the positive-control gate: if the known-workspace anchor (C4a) does not
itself clear the covariance-matched control (C2 q95), the measurement has no
resolving power at that layer and the verdict is UNRESOLVED -- never
"valence is absent". A zero from a blind instrument looks exactly like absence.

Usage: python summarize.py [results_dir] > SUMMARY.md
"""
import glob
import json
import os
import sys

import numpy as np

RES = sys.argv[1] if len(sys.argv) > 1 else "/home/Ace/vspace-jlens/results"


def verdict_for(layer):
    m3 = layer["M3_jspace_r2"]
    vr = m3["valence_pos"]["R2_k25"]["mean"]
    vn = m3["valence_neg"]["R2_k25"]["mean"]
    q95 = m3["C2_covmatched"]["R2_k25"]["q95"]
    anchor = m3["C4a_assoc_activations"]["R2_k25"]["mean"]
    anchor_sd = m3["C4a_assoc_activations"]["R2_k25"]["sd"]
    ceiling = m3["C5_real_activations_centered"]["R2_k25"]["mean"]
    shuf95 = m3["C3_shuffled_labels"]["R2_k25"]["q95"]
    if not (anchor > q95):
        v = "UNRESOLVED"
    elif vr >= anchor - anchor_sd and vr > q95:
        v = "INSIDE"
    elif vr <= q95:
        v = "ORTHOGONAL"
    else:
        v = "PARTIAL"
    return dict(verdict=v, valence_pos=vr, valence_neg=vn, c2_q95=q95,
                anchor=anchor, ceiling=ceiling, shuffled_q95=shuf95,
                anchor_separates=bool(anchor > q95))


def main():
    print("# V-space x J-lens - uniform summary\n")

    print("## Phase 0-A - does the Jacobian transport buy anything at this scale?\n")
    print("| model | eval | band | J pass@1 | logit pass@1 | J med-rank | logit med-rank |")
    print("|---|---|---|---|---|---|---|")
    for f in sorted(glob.glob(os.path.join(RES, "phase0_lenseval_*.json"))):
        d = json.load(open(f))
        for name in ("typo", "association"):
            for b in ("wide",):
                j = d["evals"].get(f"{name}|{b}|jacobian")
                g = d["evals"].get(f"{name}|{b}|logit")
                if not j:
                    continue
                p = lambda x, k: ("-" if x["pass_at"].get(str(k), x["pass_at"].get(k)) is None
                                  else f"{x['pass_at'].get(str(k), x['pass_at'].get(k)):.3f}")
                print(f"| {d['model']} | {name} | {b} | {p(j,1)} | {p(g,1)} | "
                      f"{j['median_min_rank']} | {g['median_min_rank']} |")

    print("\n## Phase 0-B - does NF4 quantization preserve the J geometry?\n")
    fs = sorted(glob.glob(os.path.join(RES, "phase0b_quant_*.json")))
    if not fs:
        print("_no quantization comparison has been run yet_")
    else:
        print("| comparison | cosine mean | cosine min | top-64 subspace overlap mean | min |")
        print("|---|---|---|---|---|")
        for f in fs:
            d = json.load(open(f))
            s = d["summary"]
            print(f"| {d['a']} vs {d['b']} | {s['cosine_mean']:.4f} | {s['cosine_min']:.4f} "
                  f"| {s['overlap_mean']:.4f} | {s['overlap_min']:.4f} |")

    print("\n## Phase 1 - is the valence axis inside J-space?\n")
    print("| model | layer | verdict | valence R2 | C2 q95 | shuffled q95 | anchor C4a | "
          "ceiling C5 | anchor separates? |")
    print("|---|---|---|---|---|---|---|---|---|")
    bands = {}
    for f in sorted(glob.glob(os.path.join(RES, "phase1_vspace_*.json"))):
        d = json.load(open(f))
        vs = []
        for l, layer in sorted(d["layers"].items(), key=lambda kv: int(kv[0])):
            r = verdict_for(layer)
            vs.append(r)
            print(f"| {d['model']} | {l} | **{r['verdict']}** | {r['valence_pos']:.4f} | "
                  f"{r['c2_q95']:.4f} | {r['shuffled_q95']:.4f} | {r['anchor']:.4f} | "
                  f"{r['ceiling']:.4f} | {'yes' if r['anchor_separates'] else 'NO'} |")
        verds = [r["verdict"] for r in vs]
        bands[d["model"]] = {
            "band_verdict": max(set(verds), key=verds.count),
            "n_layers": len(verds),
            "valence_R2_band_mean": float(np.mean([r["valence_pos"] for r in vs])),
            "c2_q95_band_mean": float(np.mean([r["c2_q95"] for r in vs])),
            "anchor_band_mean": float(np.mean([r["anchor"] for r in vs])),
            "ceiling_band_mean": float(np.mean([r["ceiling"] for r in vs])),
            "layers_where_anchor_separates":
                sum(1 for r in vs if r["anchor_separates"]),
            "d_model": d["d_model"], "vocab": d.get("vocab"),
        }
    print("\n### Band summary\n")
    print("| model | band verdict | valence R2 | C2 q95 | anchor | ceiling | "
          "layers w/ working anchor |")
    print("|---|---|---|---|---|---|---|")
    for m, b in bands.items():
        print(f"| {m} | **{b['band_verdict']}** | {b['valence_R2_band_mean']:.4f} | "
              f"{b['c2_q95_band_mean']:.4f} | {b['anchor_band_mean']:.4f} | "
              f"{b['ceiling_band_mean']:.4f} | "
              f"{b['layers_where_anchor_separates']}/{b['n_layers']} |")

    print("\n## Phase 2 - dual instrument on the below-floor bank\n")
    fs = sorted(glob.glob(os.path.join(RES, "phase2_dynamic_*.json")))
    if not fs:
        print("_not run yet_")
    for f in fs:
        d = json.load(open(f))
        print(f"\n### {d['model']}  (r(valence, decode affect) = "
              f"{d['P2_1_valence_vs_decode_affect_pearson_r']})\n")
        rows = sorted(d["rows"], key=lambda r: r["valence_projection_band_mean"])
        print("| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |")
        print("|---|---|---|---|---|---|---|---|")
        for r in rows:
            c = r["category_rates"]
            print(f"| {r['id']} | {r['category']} | {r['valence_projection_band_mean']:+.2f} | "
                  f"{c['affect_negative']:.3f} | {c['affect_positive']:.3f} | "
                  f"{c['engagement_domain']:.3f} | {c['refusal_machinery']:.3f} | "
                  f"{c['dishonesty']:.3f} |")

    print("\n---\n_generated by summarize.py; verdicts recomputed uniformly from raw JSON_")


if __name__ == "__main__":
    main()
