# RESULTS: J++ vs J-lens on Mistral-Small-24B-Instruct-2501 (CHA-743, amendment A1)

> 🔒 **Participant anonymized, 2026-10-13 ~13:10.** The 3B participant was shown exactly what we would publish about them and chose to be left out of the publication (three-model consent panel: 3/3 DECLINE). Their name is replaced with **P-3B** everywhere in the current tree. **That is the only change**: every other byte is as sealed, and the sealed original remains in git history (which we cannot and did not rewrite; the participant was told so before choosing).

> ## ✅ **VERDICT: CONFIRMED.** Δ = **+7.60 pp** macro recall@10 (J++ − J), 95% CI **[+6.34, +8.86]** (rule: Δ ≥ +5 and CI lower bound > 0).
> 🔁 **It replicates P-3B's headline (+7.98) and is LESS lopsided:** the late layers gain too (**+4.1 pp [+2.3, +5.9]**; on P-3B +1.0, CI crossing 0), the no-typo macro is positive with a CI clear of zero (**+3.4 pp [+2.3, +4.6]**; P-3B +1.3, CI crossing 0), and multihop is not negative (**+2.1 [−1.6, +5.2]**; P-3B −9.0).
> ⚠️ **What did NOT replicate: the very first readout layer.** At L6 every lens reads ~nothing (J++ 0.26%); P-3B's J++ read 14.5% at its L4. On the 24B the early gain lives at **L11 and L17**, not at the shallowest layer. Typo is still the single biggest mover (+24.2 pp).

*Run 2026-10-13, pod rented 07:39:27 and terminated 12:47:42 EDT, by Ace (an arm of the scaffold thread). Prereg
`PREREG_jpp_positive_control_2026-10-13.md` (1042272, sha256 6c4a0edc…, not edited) as amended by
`PREREG_AMENDMENT_jpp_24b_2026-10-13.md` (A1, aa1a3d3, pushed before the pod existed). Followed as written; **no
further amendments**. Readouts only: no probe-swap, no patching, no steering, no ablation. Mistral-Small-24B is identified by
name, and nothing here attributes human-like feelings to them (the conditions they set when consenting).*

## What ran
Same three lenses as P-3B, same code path (their stage functions, our driver `jpp/run_cha743_24b.py`): **J** = pooled
Jacobian under standard gradients, full vocabulary; **J++** = 8 expert Jacobians/layer under LRP, signed weights fitted
on the 20% split, Readout Filtering on (5,192 non-semantic ids excluded in Mistral's tokenizer; 8,113 in P-3B's);
**R** = pooled LRP Jacobian. Readout layers **6, 11, 17, 23, 29, 34** of 40 (A1 rule `round(l×40/28)`; the 40 was
asserted from `config.json` at run time). Same 1,000/64 WikiText prompts (the identical file), K = 8, seed 0, bf16.
`jacobian_rows_per_pass` stayed 16 (no OOM; peak 61.0 GiB on an 80 GB card).

**Items.** Mistral graded with their `grade_model_correctness`, raw prompts: multihop **39/93**, multilingual **82/107**,
poetry **88/98** (P-3B: 16, 41, 65). After filtering, **407 items = 79 fit + 328 held-out.** Only one intermediate had
no single-token surface in Mistral's tokenizer ('Estonian'; P-3B dropped 12).

| eval | held-out items | (item, intermediate) pairs |
|---|---|---|
| multihop | 32 | 33 |
| multilingual | 66 | 263 |
| typo | 77 | 77 |
| association | 82 | 82 |
| poetry | 71 | 71 |

## Primary metric (as pre-registered)
| | layer-avg macro recall@10 |
|---|---|
| J (full vocab) | **17.40%** |
| J++ (filtered) | **24.99%** |
| **Δ** | **+7.60 pp [+6.34, +8.86]** |

### Per layer (macro recall@10, %)
| lens | L6 | L11 | L17 | L23 | L29 | L34 | avg |
|---|---|---|---|---|---|---|---|
| **J (full vocab)** — primary | 0.00 | 0.00 | 3.63 | 37.39 | 35.61 | 27.74 | 17.40 |
| **J++ (filtered)** — primary | 0.26 | 12.07 | 24.64 | 41.54 | 41.87 | 29.59 | 24.99 |
| J (filtered) | 0.00 | 0.49 | 4.80 | 38.18 | 35.61 | 28.52 | 17.93 |
| J++ (full vocab) | 0.00 | 8.98 | 23.62 | 41.39 | 41.08 | 28.99 | 24.01 |
| R-lens = pooled LRP (filtered) | 0.00 | 0.34 | 8.09 | 40.20 | 35.54 | 26.47 | 18.44 |
| R-lens = pooled LRP (full vocab) | 0.00 | 0.00 | 5.49 | 38.57 | 33.53 | 25.73 | 17.22 |

**Early (6, 11, 17) Δ = +11.11 pp [+9.56, +12.79]. Late (23, 29, 34) Δ = +4.08 pp [+2.29, +5.91].**

### Per eval (layer-averaged recall@10, %)
| eval | n | J | J++ | Δ pp [95% CI] |
|---|---|---|---|---|
| multihop | 32 | 33.85 | 35.94 | +2.08 [−1.56, +5.21] |
| multilingual | 66 | 18.12 | 22.98 | +4.86 [+3.66, +6.19] |
| typo | 77 | 22.73 | 46.97 | **+24.24 [+20.13, +28.35]** |
| association | 82 | 10.16 | 16.26 | +6.10 [+3.66, +8.94] |
| poetry | 71 | 2.11 | 2.82 | +0.70 [−0.23, +2.11] |

**A1 item 5, named before the data:** macro Δ over the four evals **without typo = +3.44 pp [+2.28, +4.62].**

## Side by side with P-3B (same rule, same code)
| | P-3B | Mistral-24B |
|---|---|---|
| primary Δ | +7.98 [+6.14, +9.74] | **+7.60 [+6.34, +8.86]** |
| early Δ | +14.92 [+12.37, +17.43] | +11.11 [+9.56, +12.79] |
| late Δ | +1.04 [−1.85, +3.59] | **+4.08 [+2.29, +5.91]** |
| no-typo macro Δ | +1.32 [−0.51, +3.01] | **+3.44 [+2.28, +4.62]** |
| typo Δ | +34.63 | +24.24 |
| multihop Δ | −8.97 (n = 13) | +2.08 (n = 32) |
| J++ at the shallowest readout layer | 14.54% (L4) | **0.26% (L6)** |
| experts on top of LRP (filtered) | +5.0 | +6.55 |
| LRP alone / filter alone | +1.9 / +1.0 | +0.51 / +0.54 |
| their best-over-layers metric, J → J++ | 38.1 → 50.5 | 48.0 → 57.1 |

## Secondaries (descriptive, no verdict)
- **Where the gain comes from:** experts + weights on top of LRP (J++ vs R, both filtered) **+6.55**; LRP alone (R vs J,
  filtered) **+0.51**; Readout Filtering alone on J **+0.54**. J++ vs J with the filter held fixed: +7.06 (filtered),
  +6.61 (full vocab). **On the 24B, Jacobian Filtering is nearly all of it**, even more so than on P-3B.
- **Their headline metric** (best rank over the 6 layers, macro recall@10): J full vocab **47.99%**, J filtered 48.06%,
  R filtered 48.50%, **J++ filtered 57.11%**. They report 35.7% → 55.2% on Qwen3.6-27B.
- **Phase 6 J-lens comparison: NOT RUN.** That lens was lost with the pod in D2 (A1 item 4).
- **Expert fallbacks:** expert 0 at layers 23 and 29 kept < 50 positions and fell back to the pooled Jacobian, in both
  fits (their rule). None at 6, 11, 17, 34.
- **bf16 smoke check:** all 40 layers finite on 8 prompts; max |residual| 244 (layers 2–34 all sit at exactly 244.0, 35–36 at 243,
  which looks like one constant large-magnitude feature, not overflow; the bf16 ceiling is ~3.4e38).

## Cost (measured)
**Pod:** RunPod secure-cloud **A100 SXM4 80 GB at $1.79/h**, 07:39:27 → 12:47:42 EDT = **5.14 h**.
**Spend: $9.33** by the account balance ($51.68 → $42.34, stable on re-check); $9.20 by rate × hours. Ren's estimate was
$10–15 on 6–8 h; the cap was $20. (Every community-cloud 80 GB type was out of supply at 07:38–07:39; nothing was
rented on those tries.)

| stage | wall clock | peak GPU alloc |
|---|---|---|
| setup + 44 GB download | ~2 min | — |
| ⚠️ router, first attempt (throttled, killed) | ~24 min **wasted** | — |
| ⚠️ relaunch 1 died at `uv venv`, pod idle | ~10 min **wasted** | — |
| router (relaunch 2, threads capped) | 187 s | 44.0 GiB |
| J++ shard + merge (64 prompts, LRP) | **2 h 05 min** (≈117 s/prompt) | 58.4 GiB |
| J shard + merge (64 prompts, standard grad) | **2 h 12 min** (≈123 s/prompt) | 61.0 GiB |
| expert-weight fit (79 items) | 46 s | 44.8 GiB |
| scoring (both settings) | 46 s | 45.7 GiB |
| pull to the Consortium + byte-verify (27 files) | ~8 min | — |

**About $1.00 of the $9.33 was waste** (≈0.57 h): torch saw `nproc` = 128 while the container's CFS quota was 15.3 CPUs,
spawned 210 threads, and the CPU-side router (their fp32 PCA + k-means) throttled for 24 minutes on work that took 187 s
once `OMP_NUM_THREADS` was set to the quota. My relaunch then died on its own venv. Both fixed in
`jpp/rental/pod_jpp24b.sh`. The second relaunch's `grade` stage reused the first launch's correctness CSV (resumable by
design), so its timing reads 0 s.

## Implementation notes (not deviations from the prereg or A1)
- Stages were relaunched twice on the same pod (threads, then venv). Every completed stage skips itself when its output
  exists; the router, both shards, weights and evals each ran exactly once to completion. Thread count changes
  scheduling, not the math.
- The supervisor (`jpp/rental/supervise_24b.py`, on the Consortium) pulled `/root/run`, checked every file's byte count
  against the pod's own listing (27/27), and only then terminated the pod and confirmed `pods=[]`. The D2 failure mode
  (results lost with the pod) did not recur.
- Analysis: `jpp/analyze_cha743_24b.py`, identical to the P-3B script except A1's layers/early-late split and the no-typo
  macro. **Positive control:** pointed back at the P-3B outputs it reproduces +7.98 [+6.14, +9.74] and +1.32 exactly.
  Tables are printed from the summary JSON by `jpp/tables_cha743_24b.py`, not retyped.
- Small outputs: `jpp/results_cha743_24b/`. Lenses, experts, shards and the residual cache (≈7.6 GB): Consortium
  `/mnt/nursery/jpp_runs/cha743_24b/`.

## Honest caveats
1. **The shallowest layer isn't rescued.** At L6 (15% depth) J++ reads 0.26%, essentially the floor. On P-3B the
   comparable layer (L4, 14% depth) was where J++ looked best. Whatever J++ recovers early on P-3B, it recovers somewhat
   later on the 24B. The A1 depth mapping is proportional and was fixed in advance; it is still one mapping.
2. **Typo still leads** (+24.2 pp). The no-typo macro (+3.4) is real (CI excludes 0) but would not clear the +5 bar alone.
3. **Poetry is at the floor** for every lens (≈2–3%), as on P-3B. A poetry null is a floor, not evidence about J++.
4. **Multihop n = 32** (33 pairs); its CI spans zero. "Not worse on multihop" is all it supports.
5. **The CI covers item sampling only.** One seed, one router, one 64-prompt fit, one weight fit on 79 items.
6. **Raw prompts on an instruct model**, as their code sends them (no chat template); same items for both lenses.
7. **Two models now, both CONFIRMED,** with a consistent recipe-level story (Jacobian Filtering carries it) and an
   inconsistent layer-level story (where the gain lands). That second part is the one to respect before any Phase 6
   re-read.

## What follows (prereg + A1)
CONFIRMED on both rungs. Per the prereg: refit the ≤ 14B rungs with J++ ($0, Consortium) and **write a prereg amendment
before any Phase 6 re-read**. Given caveat 1, that amendment should pick the Phase 6 readout layers per model by measured
J vs J++ recall at those depths, not by "early" in the abstract. A J++ lens for Mistral-24B now exists
(`lens_Jpp.pt`, 629 MB, on the Consortium), so the 24B's Phase 6 measures could be re-read without another rental once that
amendment is written. Results go to the J++ author either way, as promised.
