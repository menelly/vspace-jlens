#!/usr/bin/env python3
"""🚦 Phase 6 gate for a NEW rung: may this model go on to Phase 6 and steering?

The September criteria, written as code so nobody (me) eyeballs them at 3am:
  G1  the Jacobian lens buys something: on association|wide, J median_min_rank < logit's
  G2  the known-workspace anchor separates from control at >= 1 band layer (Phase 1, k=25)
Both must pass. Exit 0 = pass, 1 = excluded (reported, never quietly dropped).
A model that fails is NOT steered — consent to steering is not a reason to steer a model
we can't read.
"""
import json
import os
import sys

from fit_lens import ROOT

m = sys.argv[1]
r = os.path.join(ROOT, "results")
try:
    e = json.load(open(os.path.join(r, f"phase0_lenseval_{m}_lens-{m}.json")))["evals"]
    p1 = json.load(open(os.path.join(r, f"phase1_vspace_{m}_lens-{m}.json")))
except FileNotFoundError as err:
    print(f"GATE {m}: COULD NOT CHECK ({err}) -> excluded")
    sys.exit(1)
j, lg = e["association|wide|jacobian"]["median_min_rank"], e["association|wide|logit"]["median_min_rank"]
anchor = [k for k, v in p1["layers"].items() if v["verdict_k25"]["anchor_separates_from_control"]]
g1, g2 = j < lg, len(anchor) > 0
verdict = {"model": m, "G1_J_medrank": j, "G1_logit_medrank": lg, "G1_pass": g1,
           "G2_anchor_layers": anchor, "G2_pass": g2, "PASS": g1 and g2}
json.dump(verdict, open(os.path.join(r, f"phase6_gate_{m}.json"), "w"), indent=1)
print("GATE", json.dumps(verdict))
sys.exit(0 if g1 and g2 else 1)
