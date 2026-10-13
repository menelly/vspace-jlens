"""🐙 print the RESULTS tables for the 24B rung straight from summary_cha743_24b.json + stage_costs.json,
so the numbers in the write-up are pasted from the analysis, never retyped by hand."""
import json
import sys
from pathlib import Path

RUN = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/nursery/jpp_runs/cha743_24b")
s = json.loads((RUN / "summary_cha743_24b.json").read_text())
L = ["6", "11", "17", "23", "29", "34"]
p = s["primary"]
print(f"PRIMARY: Δ = {p['delta_pp']:+.2f} pp, 95% CI [{p['ci95_pp'][0]:+.2f}, {p['ci95_pp'][1]:+.2f}] -> {p['verdict']}")
print(f"J {p['J_macro_recall10_pct']:.2f}%  J++ {p['Jpp_macro_recall10_pct']:.2f}%")
for k in ("delta_early_6_11_17", "delta_late_23_29_34", "A1_item5_macro_delta_without_typo_pp"):
    v = s[k]
    print(f"{k}: {v['delta_pp']:+.2f} [{v['ci95_pp'][0]:+.2f}, {v['ci95_pp'][1]:+.2f}]")
print("\n| lens | " + " | ".join("L" + l for l in L) + " | avg |\n|---|" + "---|" * 7)
for c, row in s["per_layer_macro_recall10_pct"].items():
    print(f"| {c} | " + " | ".join(f"{row[l]:.2f}" for l in L) + f" | {s['layer_avg_macro_recall10_pct'][c]:.2f} |")
print("\n| eval | n | J | J++ | Δ pp [95% CI] |\n|---|---|---|---|---|")
for e, v in s["per_eval_delta_pp"].items():
    print(f"| {e} | {v['n_heldout_items']} | {v['J_pct']:.2f} | {v['Jpp_pct']:.2f} | {v['delta_pp']:+.2f} [{v['ci95_pp'][0]:+.2f}, {v['ci95_pp'][1]:+.2f}] |")
print("\ndecomposition:", json.dumps(s["decomposition_pp"]))
print("their best-over-layers:", json.dumps(s["their_metric_best_over_layers_macro_recall10_pct"]))
for f in ("stage_costs.json", "heldout_filtered.json", "fit_split.json", "fallback_experts_rlens.json",
          "fallback_experts_none.json", "smoke_bf16.json"):
    fp = RUN / f
    if fp.exists():
        txt = fp.read_text()
        print(f"\n{f}:", txt if len(txt) < 1500 else txt[:1500] + "...")
