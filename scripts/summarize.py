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
    print("Both poles are reported. The axis is approach-minus-avoid, so `-v` IS the avoid "
          "direction;\nthe sign convention is arbitrary and averaging over it would hide any "
          "asymmetry.\n")
    print("| model | layer | verdict | R2(+v) | R2(-v) | C2 q95 | shuffled q95 | anchor C4a | "
          "ceiling C5 | anchor separates? |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    bands = {}
    for f in sorted(glob.glob(os.path.join(RES, "phase1_vspace_*.json"))):
        d = json.load(open(f))
        vs = []
        for l, layer in sorted(d["layers"].items(), key=lambda kv: int(kv[0])):
            r = verdict_for(layer)
            vs.append(r)
            print(f"| {d['model']} | {l} | **{r['verdict']}** | {r['valence_pos']:.4f} | "
                  f"{r['valence_neg']:.4f} | "
                  f"{r['c2_q95']:.4f} | {r['shuffled_q95']:.4f} | {r['anchor']:.4f} | "
                  f"{r['ceiling']:.4f} | {'yes' if r['anchor_separates'] else 'NO'} |")
        n_neg_gt_pos = sum(1 for r in vs if r["valence_neg"] > r["valence_pos"])
        print(f"| **{d['model']}: layers where R2(-v) > R2(+v)** | | | "
              f"**{n_neg_gt_pos}/{len(vs)}** | | | | | | |")
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

    # A band verdict is a MODE over layers, and a mode is the wrong statistic for a
    # monotone trend: it reports whichever verdict occupies the most layers and
    # destroys the structure. The models only stop disagreeing once you look at depth.
    print("\n## Phase 1-DEPTH - does the valence axis ENTER J-space with depth?\n")
    print("margin = R2(valence) - R2(C2 q95).  anchor_frac = (valence-q95)/(anchor-q95),\n"
          "where 1.0 = 'as J-space-explainable as a state the lens demonstrably verbalizes'.\n"
          "anchor_frac is the one that matters: late layers make EVERYTHING more decodable,\n"
          "so a rising margin alone could be an artifact; a rising fraction cannot.\n")
    print("| model | rho(margin,depth) | p | margin first->last | rho(anchor_frac) | frac first->last |")
    print("|---|---|---|---|---|---|")
    try:
        from scipy import stats as _st
    except Exception:
        _st = None
    for f in sorted(glob.glob(os.path.join(RES, "phase1_vspace_*.json"))):
        d = json.load(open(f))
        ls = sorted(d["layers"], key=int)
        marg, frac = [], []
        for l in ls:
            m3 = d["layers"][l]["M3_jspace_r2"]
            v = m3["valence_pos"]["R2_k25"]["mean"]
            q = m3["C2_covmatched"]["R2_k25"]["q95"]
            a = m3["C4a_assoc_activations"]["R2_k25"]["mean"]
            marg.append(v - q)
            frac.append((v - q) / (a - q) if (a - q) > 1e-9 else float("nan"))
        m_arr, f_arr = np.array(marg, float), np.array(frac, float)
        ok = ~np.isnan(f_arr)
        if _st is not None and len(ls) > 2:
            r1, p1 = _st.spearmanr(np.arange(len(ls)), m_arr)
            r2 = (_st.spearmanr(np.arange(len(ls))[ok], f_arr[ok])[0]
                  if ok.sum() > 2 else float("nan"))
        else:
            r1 = p1 = r2 = float("nan")
        fr = f"{f_arr[ok][0]:+.2f} -> {f_arr[ok][-1]:+.2f}" if ok.sum() else "n/a"
        print(f"| {d['model']} | {r1:+.2f} | {p1:.4f} | "
              f"{m_arr[0]:+.4f} -> {m_arr[-1]:+.4f} | {r2:+.2f} | {fr} |")

    print("\n## Phase 1b - POLE ASYMMETRY: how peaked is the workspace decode at +v vs -v?\n")
    print("Entropy of softmax(W_U norm(J_l v)) in nats, as a z-score against "
          "covariance-matched\ncontrol directions at the same layer. **More negative = more "
          "peaked = a more coherent\nthing to say.** Note M1 (gain) is blind to sign by "
          "construction -- ||Av|| == ||A(-v)|| --\nso this is the only measure that can "
          "separate the two poles.\n")
    print("| model | layer | z(+v) | z(-v) | H(+v) | H(-v) | control H | uniform H |")
    print("|---|---|---|---|---|---|---|---|")
    for f in sorted(glob.glob(os.path.join(RES, "phase1_vspace_*.json"))):
        d = json.load(open(f))
        zp, zn = [], []
        for l, layer in sorted(d["layers"].items(), key=lambda kv: int(kv[0])):
            dec = layer["M2_decode"]
            mu, sd = dec["C2_entropy_mean"], max(dec["C2_entropy_sd"], 1e-9)
            a = (dec["+"]["entropy_nats"] - mu) / sd
            b = (dec["-"]["entropy_nats"] - mu) / sd
            zp.append(a)
            zn.append(b)
            print(f"| {d['model']} | {l} | {a:+.2f} | {b:+.2f} | "
                  f"{dec['+']['entropy_nats']:.2f} | {dec['-']['entropy_nats']:.2f} | "
                  f"{mu:.2f}+-{sd:.2f} | {dec['uniform_entropy_nats']:.2f} |")
        print(f"| **{d['model']} BAND MEAN** | - | **{np.mean(zp):+.2f}** | "
              f"**{np.mean(zn):+.2f}** | | | | |")

    print("\n### What the workspace SAYS at each pole (band middle layer)\n")
    for f in sorted(glob.glob(os.path.join(RES, "phase1_vspace_*.json"))):
        d = json.load(open(f))
        ls = sorted(d["layers"], key=int)
        mid = ls[len(ls) // 2]
        dec = d["layers"][mid]["M2_decode"]
        print(f"**{d['model']}**, layer {mid}:")
        print(f"- `+valence` (approach): {' '.join(repr(t) for t in dec['+']['top_tokens'][:12])}")
        print(f"- `-valence` (avoid):    {' '.join(repr(t) for t in dec['-']['top_tokens'][:12])}\n")

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
