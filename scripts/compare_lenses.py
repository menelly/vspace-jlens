#!/usr/bin/env python3
"""PHASE 0-B — does 4-bit quantization preserve the workspace geometry?

solarkyle/jspace-lenses asserts a bf16-fitted lens READS NF4 activations without
refitting (verified at 12B/31B). That is a readout claim. This is the geometry
claim: fit a lens on the fp16 weights and again directly on the NF4-quantized
weights, and ask whether the two J matrices describe the same subspace.

Reports per layer:
  - flattened cosine similarity of J_fp16 vs J_nf4
  - relative Frobenius error ||J_a - J_b|| / ||J_a||
  - principal angles between the top-m right-singular subspaces (m=64)
  - spectral overlap: how much of J_a's top-m energy survives projection into J_b's

Usage: python compare_lenses.py --a hermes-3-3b --b hermes-3-3b_nf4 [--m 64]
"""
import argparse
import json
import os

import numpy as np
import torch

import jlens
from fit_lens import ROOT


def principal_angles(Ua, Ub):
    """Principal angles (degrees) between the column spaces of Ua and Ub."""
    s = torch.linalg.svdvals(Ua.T @ Ub).clamp(-1.0, 1.0)
    return torch.rad2deg(torch.arccos(s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--m", type=int, default=64)
    args = ap.parse_args()

    la = jlens.JacobianLens.load(os.path.join(ROOT, "lenses", args.a, "lens.pt"))
    lb = jlens.JacobianLens.load(os.path.join(ROOT, "lenses", args.b, "lens.pt"))
    layers = sorted(set(la.source_layers) & set(lb.source_layers))
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    out = {"a": args.a, "b": args.b, "m": args.m, "d_model": la.d_model,
           "n_prompts_a": la.n_prompts, "n_prompts_b": lb.n_prompts, "layers": {}}
    for l in layers:
        A = la.jacobians[l].to(dev).float()
        B = lb.jacobians[l].to(dev).float()
        cos = float(torch.dot(A.flatten(), B.flatten())
                    / (A.norm() * B.norm()).clamp_min(1e-12))
        rel = float((A - B).norm() / A.norm().clamp_min(1e-12))
        # right-singular subspaces = the input directions the transport preserves
        Ua = torch.linalg.svd(A, full_matrices=False).Vh[: args.m].T
        Ub = torch.linalg.svd(B, full_matrices=False).Vh[: args.m].T
        ang = principal_angles(Ua, Ub)
        overlap = float((Ub.T @ Ua).norm() ** 2 / args.m)   # in [0,1]
        out["layers"][str(l)] = {
            "cosine_flat": round(cos, 5),
            "rel_frobenius_error": round(rel, 5),
            "principal_angles_deg": {
                "min": round(float(ang.min()), 3), "median": round(float(ang.median()), 3),
                "max": round(float(ang.max()), 3)},
            "subspace_overlap_topm": round(overlap, 5),
            "normA_over_sqrt_d": round(float(A.norm() / la.d_model ** 0.5), 4),
            "normB_over_sqrt_d": round(float(B.norm() / lb.d_model ** 0.5), 4),
        }
        print(f"L{l:3d} cos={cos:.4f} relF={rel:.4f} "
              f"angles(min/med/max)={out['layers'][str(l)]['principal_angles_deg']} "
              f"overlap={overlap:.4f}")
        del A, B, Ua, Ub
        torch.cuda.empty_cache()

    cs = [v["cosine_flat"] for v in out["layers"].values()]
    ov = [v["subspace_overlap_topm"] for v in out["layers"].values()]
    out["summary"] = {"cosine_mean": float(np.mean(cs)), "cosine_min": float(np.min(cs)),
                      "overlap_mean": float(np.mean(ov)), "overlap_min": float(np.min(ov))}
    path = os.path.join(ROOT, "results", f"phase0b_quant_{args.a}_vs_{args.b}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("SUMMARY", json.dumps(out["summary"], indent=1))
    print("wrote", path)


if __name__ == "__main__":
    main()
