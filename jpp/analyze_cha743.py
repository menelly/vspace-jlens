"""🐙 CHA-743 analysis: the prereg's primary metric, verdict, and secondaries.

PRIMARY (fixed in the prereg): Δ = macro recall@10(J++) − macro recall@10(J),
macro over the 5 evals, AVERAGED OVER THE 6 LAYERS (per-layer recall, not their
best-over-layers headline), held-out items. J = plain J-lens, full vocabulary (no
Readout Filtering); J++ = full recipe WITH Readout Filtering.
Recall per item = fraction of its scoreable intermediates with rank <= 10 (their
item-weighting: average within the item, then over an eval's items).
95% CI: 10,000 bootstrap resamples of items, seed 0, resampled within eval, paired
(the same resampled items score both lenses).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RUN = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/Ace/vspace-jlens/jpp_runs/cha743")
EVALS = ["multihop", "multilingual", "typo", "association", "poetry"]
LAYERS = [4, 8, 12, 16, 20, 24]
K = 10
B = 10_000

filt = pd.read_csv(RUN / "ranks_filtered.csv")
unf = pd.read_csv(RUN / "ranks_unfiltered.csv")


def hits(df, lens):
    """item x layer matrix of per-item recall@K (mean over intermediates), per eval."""
    d = df[df["lens"] == lens].assign(hit=lambda x: x["rank"] <= K)
    per = d.groupby(["eval", "item", "layer"])["hit"].mean().unstack("layer")[LAYERS]
    return {e: per.loc[e] for e in EVALS}


def macro_by_layer(h):
    return np.mean([h[e].mean(axis=0).values for e in EVALS], axis=0)  # [layers]


conds = {
    "J (plain, full vocab) [PRIMARY]": hits(unf, "J"),
    "J++ (filtered) [PRIMARY]": hits(filt, "Jpp"),
    "J (filtered)": hits(filt, "J"),
    "J++ (full vocab)": hits(unf, "Jpp"),
    "R-lens / pooled LRP (filtered)": hits(filt, "R"),
    "R-lens / pooled LRP (full vocab)": hits(unf, "R"),
}
J, JPP = conds["J (plain, full vocab) [PRIMARY]"], conds["J++ (filtered) [PRIMARY]"]
for e in EVALS:  # same held-out items for both lenses
    assert list(J[e].index) == list(JPP[e].index), e

rng = np.random.default_rng(0)
idx = {e: rng.integers(0, len(J[e]), size=(B, len(J[e]))) for e in EVALS}


def boot_delta(A, Bm, layer_mask):
    """bootstrap Δ (pp) of macro recall averaged over the masked layers, A minus B."""
    out = np.zeros(B)
    for e in EVALS:
        a = A[e].values[:, layer_mask].mean(axis=1)  # per item, mean over layers
        b = Bm[e].values[:, layer_mask].mean(axis=1)
        d = a - b
        out += d[idx[e]].mean(axis=1)
    return 100 * out / len(EVALS)


def point_delta(A, Bm, layer_mask):
    return 100 * float(np.mean([(A[e].values[:, layer_mask].mean(1) - Bm[e].values[:, layer_mask].mean(1)).mean() for e in EVALS]))


all_l = np.ones(len(LAYERS), bool)
early = np.array([l <= 12 for l in LAYERS])
late = ~early

res = {}
delta = point_delta(JPP, J, all_l)
bd = boot_delta(JPP, J, all_l)
lo, hi = np.percentile(bd, [2.5, 97.5])
if delta >= 5 and lo > 0:
    verdict = "CONFIRMED"
elif delta <= 0 or hi < 2:
    verdict = "REFUTED"
else:
    verdict = "INCONCLUSIVE"
res["primary"] = {"delta_pp": round(delta, 2), "ci95_pp": [round(lo, 2), round(hi, 2)], "verdict": verdict,
                  "J_macro_recall10_pct": round(100 * macro_by_layer(J).mean(), 2),
                  "Jpp_macro_recall10_pct": round(100 * macro_by_layer(JPP).mean(), 2)}

for name, m in [("early_4_8_12", early), ("late_16_20_24", late)]:
    b = boot_delta(JPP, J, m)
    res[f"delta_{name}"] = {"delta_pp": round(point_delta(JPP, J, m), 2),
                            "ci95_pp": [round(x, 2) for x in np.percentile(b, [2.5, 97.5])]}

res["per_eval_delta_pp"] = {}
for e in EVALS:
    d = (JPP[e].values.mean(1) - J[e].values.mean(1))
    bb = d[idx[e]].mean(axis=1) * 100
    res["per_eval_delta_pp"][e] = {"n_heldout_items": int(len(d)),
                                  "J_pct": round(100 * J[e].values.mean(), 2),
                                  "Jpp_pct": round(100 * JPP[e].values.mean(), 2),
                                  "delta_pp": round(100 * d.mean(), 2),
                                  "ci95_pp": [round(x, 2) for x in np.percentile(bb, [2.5, 97.5])]}

res["per_layer_macro_recall10_pct"] = {
    c: {str(l): round(100 * v, 2) for l, v in zip(LAYERS, macro_by_layer(h))} for c, h in conds.items()}
res["layer_avg_macro_recall10_pct"] = {c: round(100 * macro_by_layer(h).mean(), 2) for c, h in conds.items()}
res["per_eval_layer_avg_recall10_pct"] = {
    c: {e: round(100 * h[e].values.mean(), 2) for e in EVALS} for c, h in conds.items()}

# their headline-style metric (best rank over the layers), from their own pass_at_k tables
pf = pd.read_csv(RUN / "pass_at_k_filtered.csv")
pu = pd.read_csv(RUN / "pass_at_k_unfiltered.csv")
sel = lambda p, lens: float(p[(p["eval"] == "macro") & (p["lens"] == lens) & (p["k"] == K) & (p["weighting"] == "item")]["pass_at_k"].iloc[0])
res["their_metric_best_over_layers_macro_recall10_pct"] = {
    "J full vocab": round(100 * sel(pu, "J"), 2), "J filtered": round(100 * sel(pf, "J"), 2),
    "Jpp filtered": round(100 * sel(pf, "Jpp"), 2), "Jpp full vocab": round(100 * sel(pu, "Jpp"), 2),
    "R filtered": round(100 * sel(pf, "R"), 2), "R full vocab": round(100 * sel(pu, "R"), 2)}

# decomposition of the primary Δ (descriptive): recipe-with-filter-held-fixed, and filter alone
res["decomposition_pp"] = {
    "Jpp_vs_J_both_filtered": round(point_delta(conds["J++ (filtered) [PRIMARY]"], conds["J (filtered)"], all_l), 2),
    "Jpp_vs_J_both_full_vocab": round(point_delta(conds["J++ (full vocab)"], J, all_l), 2),
    "filter_alone_on_J": round(point_delta(conds["J (filtered)"], J, all_l), 2),
    "R_filtered_vs_J_filtered (LRP alone)": round(point_delta(conds["R-lens / pooled LRP (filtered)"], conds["J (filtered)"], all_l), 2),
    "Jpp_vs_R_both_filtered (experts alone)": round(point_delta(JPP, conds["R-lens / pooled LRP (filtered)"], all_l), 2),
}

# optional secondary: our September Phase 6 J-lens (own corpus, 100 prompts, jlens.fit)
if (RUN / "ranks_phase6_unfiltered.csv").exists():
    p6 = {"Phase6 J (full vocab)": hits(pd.read_csv(RUN / "ranks_phase6_unfiltered.csv"), "J_phase6"),
          "Phase6 J (filtered)": hits(pd.read_csv(RUN / "ranks_phase6_filtered.csv"), "J_phase6")}
    for c, h in p6.items():
        res["per_layer_macro_recall10_pct"][c] = {str(l): round(100 * v, 2) for l, v in zip(LAYERS, macro_by_layer(h))}
        res["layer_avg_macro_recall10_pct"][c] = round(100 * macro_by_layer(h).mean(), 2)
        res["per_eval_layer_avg_recall10_pct"][c] = {e: round(100 * h[e].values.mean(), 2) for e in EVALS}
    res["phase6_vs_new_J_full_vocab_pp"] = round(point_delta(p6["Phase6 J (full vocab)"], J, all_l), 2)
    res["Jpp_vs_phase6_J_primary_style_pp"] = round(point_delta(JPP, p6["Phase6 J (full vocab)"], all_l), 2)

(RUN / "summary_cha743.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
