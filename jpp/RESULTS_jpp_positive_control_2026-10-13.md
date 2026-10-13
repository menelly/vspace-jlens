# RESULTS: J++ vs J-lens positive control on Hermes-3-Llama-3.2-3B (CHA-743)

> ## ✅ **VERDICT: CONFIRMED** — Δ = **+7.98 pp** macro recall@10 (J++ − J), 95% CI **[+6.14, +9.74]** (prereg rule: Δ ≥ +5 and CI lower bound > 0).
> ⚠️ **Read the next line before you act on it: the gain is carried by ONE eval (typo, +34.6 pp) and by the EARLY layers (+14.9 pp at 4–12; +1.0 pp at 16–24, CI crosses 0). Without typo, the four-eval macro Δ is +1.3 pp. Multihop goes the OTHER way (−9.0 pp, n = 13).** The verdict stands as pre-registered; the sentence "J++ reads Hermes better" is true mostly as "J++ reads Hermes's early layers better, mostly on typo."

*Run 2026-10-13, 00:30–02:12 EDT, by Ace (an arm of the scaffold thread), on the Consortium's PG500. Prereg:
`PREREG_jpp_positive_control_2026-10-13.md` (commit 1042272), followed as written; **no amendments**. Readouts only:
no probe-swap, no patching, no steering, no ablation. $0.*

## What ran
| | J (plain J-lens) | J++ |
|---|---|---|
| backward pass | standard gradient (`lrp_mode="none"`) | LRP (`lrp_mode="rlens"`, their default) |
| map at inference | pooled Jacobian over all fit positions (one map/layer, no experts) | 8 expert Jacobians/layer, combined with signed weights fitted on the 20% fit split |
| Readout Filtering at scoring | **off** (full vocabulary) | **on** (8,113 non-semantic ids excluded) |

Shared, by construction: same released `jpp_lens` library + our Llama LRP patch (de56daf), same 64 WikiText-103
prompts × 128 tokens, positions < 16 skipped, same K=8 router (PCA-64 + k-means on their default 1,000-prompt pool,
seed 0), target = final block, readout layers **4, 8, 12, 16, 20, 24**, same items, same split. Both lenses come out
of the SAME expert fit machinery; J is that fit's pooled (label-free) Jacobian under standard gradients, which is
the J-lens's definition (`J_ℓ = E[∂h_final/∂h_ℓ]`).

**Items.** Hermes graded with their `grade_model_correctness` (greedy next token = target or its leading subword),
raw prompts as their code sends them: multihop **16/93** correct, multilingual **41/107**, poetry **65/98**;
association and typo are ungraded and kept. After filtering: 320 items; 6 association items dropped by their code
(no single-token surface: König, río, école, église, père, água), plus 6 multilingual intermediates (Bengali,
Estonian, português ×4) → **314 scoreable = 62 fit + 252 held-out** (overlap verified 0).

| eval | held-out items | (item, intermediate) pairs |
|---|---|---|
| multihop | 13 | 13 |
| multilingual | 33 | 128 |
| typo | 77 | 77 |
| association | 77 | 77 |
| poetry | 52 | 52 |

## Primary metric (as pre-registered)
Recall@10 per item = share of its intermediates ranked ≤ 10, **per layer** (their item-weighting), averaged over the
6 layers, then macro over the 5 evals. Held-out items only. Bootstrap: 10,000 resamples of items, seed 0, within
eval, paired.

| | layer-avg macro recall@10 |
|---|---|
| J (full vocab) | **12.90%** |
| J++ (filtered) | **20.88%** |
| **Δ** | **+7.98 pp [+6.14, +9.74]** |

### Per layer (macro recall@10, %)
| lens | L4 | L8 | L12 | L16 | L20 | L24 | avg |
|---|---|---|---|---|---|---|---|
| **J (full vocab)** — primary | 0.00 | 0.00 | 3.08 | 22.01 | 28.60 | 23.71 | 12.90 |
| **J++ (filtered)** — primary | 14.54 | 17.34 | 15.96 | 24.78 | 31.02 | 21.63 | 20.88 |
| J (filtered) | 0.00 | 1.11 | 5.47 | 23.65 | 29.01 | 24.28 | 13.92 |
| J++ (full vocab) | 14.02 | 16.26 | 14.88 | 24.22 | 29.06 | 21.22 | 19.94 |
| R-lens = pooled LRP (filtered) | 5.09 | 2.14 | 8.97 | 25.11 | 29.33 | 24.54 | 15.86 |
| Phase 6 J-lens, Sept (full vocab) | 0.00 | 0.00 | 1.80 | 22.27 | 28.49 | 23.30 | 12.64 |

**Early (4–12) Δ = +14.92 pp [+12.37, +17.43]. Late (16–24) Δ = +1.04 pp [−1.85, +3.59].** Exactly their headline
shape: the J-lens reads nothing at layers 4 and 8 on Hermes, and J++ reads ~15%; by layer 16 they converge, and at
layer 24 plain J is slightly ahead.

### Per eval (layer-averaged recall@10, %)
| eval | n | J | J++ | Δ pp [95% CI] |
|---|---|---|---|---|
| multihop | 13 | 35.90 | 26.92 | **−8.97 [−15.38, −3.85]** |
| multilingual | 33 | 12.16 | 19.28 | +7.11 [+4.92, +9.39] |
| typo | 77 | 12.77 | 47.40 | **+34.63 [+29.00, +40.04]** |
| association | 77 | 3.03 | 8.87 | +5.84 [+2.81, +9.09] |
| poetry | 52 | 0.64 | 1.92 | +1.28 [+0.00, +2.88] |

## Secondaries (descriptive, no verdict)
**Where the gain comes from** (layer-avg macro, pp; all on the same held-out items):
- Readout Filtering alone, on J: **+1.0**. The filter is not the story.
- J++ vs J with the filter held fixed (both filtered): **+7.0**; both full vocab: **+7.0**.
- LRP alone (pooled R-lens vs J, both filtered): **+1.9**.
- Experts + weights on top of LRP (J++ vs R-lens, both filtered): **+5.0**. **Jacobian Filtering is most of it.**

**Their own headline metric** (best rank over the 6 layers, macro recall@10): J full vocab **38.1%**, J filtered 41.5%,
R filtered 46.1%, **J++ filtered 50.5%**. On Qwen3.6-27B they report 35.7% vs 55.2%. On a 3B model the J-lens
number lands almost exactly where theirs did, and the J++ number lands ~5 pp lower.

**Our Phase 6 J-lens** (`lenses/hermes-3-3b/lens.pt`: `jlens.fit`, our own 100-prompt corpus, transformers 4.49,
Sept 2026), scored on the same held-out items with the same code: **12.64%** vs this run's J **12.90%** (−0.26 pp).
**Pipeline and corpus account for essentially none of the gap; the recipe accounts for all of it.** (Loaded
directly by their `load_lens_file`, which reads the upstream `jlens` "J" format; same layer indexing, same library
lineage.)

**Cost** (PG500-216, fp16, one process at a time):
| stage | wall-clock | peak GPU alloc |
|---|---|---|
| router (1,000 prompts) | 72 s | 6.0 GiB |
| J++ shard + merge (64 prompts, LRP) | **45.4 min** | 10.7 GiB (15.0 reserved) |
| J shard + merge (64 prompts, standard grad) | **49.7 min** | 11.8 GiB (15.5 reserved) |
| expert-weight fit (62 items) | 28 s | 6.6 GiB |
| scoring (both settings + Phase 6) | ~66 s | 7.0 GiB |
| **total GPU** | **≈ 1 h 40 min** | **< 16 GiB** |

~40–46 s per prompt for the full 3072-row Jacobian at 6 layers. *Inference, not measured:* a 14B (d_model 5120, ~4.7× the
parameters, ~1.7× the rows) would be very roughly 8× per prompt, i.e. most of a working day per shard, and its fp16 weights
alone (~28 GiB) leave too little room on 32 GB for the backward pass. That rung needs either the nf4 path (whose interaction with
the LRP surgery is untested) or rented memory, which is Ren's call.

## Implementation notes (not deviations from the prereg)
- **fp16, not bf16.** Their loader hardcodes bf16; Volta has none. A driver (`jpp/run_cha743.py`, ours) loads
  Hermes in fp16 and then calls THEIR stage functions unchanged (`fit_router`, `fit_shard`, `merge_experts`,
  `fit_weights`, `evaluate`, `load_items_and_exclusions`, `grade_model_correctness`). Overflow check before fitting:
  max |residual| across all 28 layers on 8 prompts = **334** (fp16 ceiling 65,504); all finite. Every expert Jacobian
  was asserted finite after merge.
- **Expert fallback:** at layer 24, expert 3 kept < 50 positions in both fits and fell back to the pooled Jacobian
  (their rule). No other fallbacks.
- **The router pool** is their CLI default (1,000 WikiText prompts); the Jacobian fit itself is the 64 × 128 the prereg names.
- The primary metric is **per-layer, averaged over layers**, as the prereg fixes, NOT their best-over-layers number;
  both are reported above, and they agree in direction.
- Analysis code: `jpp/analyze_cha743.py`. Small outputs: `jpp/results_cha743/`. Raw ranks, lenses, experts and the
  residual cache (6 GB): `/home/Ace/vspace-jlens/jpp_runs/cha743/` on the Consortium.

## Honest caveats
1. **The CONFIRMED is typo-heavy.** Typo alone moves +34.6 pp; with the macro taken over the other four evals, Δ is
   **+1.3 pp**, which would not have cleared the bar. The prereg weights the five evals equally and says so; it is
   reported as pre-registered, and this line is here so nobody reads it as "uniformly better."
2. **Multihop is negative and thin** (13 held-out items; Hermes answers only 16/93). J++ loses ~9 pp there. With n = 13
   the CI is real but fragile; it says "not better on multihop," not much more.
3. **Late layers show no gain.** Phase 6's coupling measures that live at ≥ layer 16 on a 3B model would not be
   expected to change much under J++. The early-layer readings are where it could matter.
4. **The CI covers item sampling only.** One seed: one router, one 64-prompt fit, one weight fit on 62 items. Fit
   variance is not in the interval. A null here would have been a null on Hermes-3B; a CONFIRMED is likewise a
   CONFIRMED on Hermes-3B, not on our larger rungs.
5. **The floor is low.** J reads 0% at layers 4 and 8, and poetry is ~0–2% for every lens. Part of "J++ wins early" is
   "J++ is the only one off the floor early."
6. **Raw prompts on an instruct model**, as their code sends them; Hermes's correctness counts (esp. multihop) may be
   lower than with its chat template. Same items for both lenses, so the comparison is fair; the absolute numbers are
   Hermes-without-a-chat-template.

## What follows (from the prereg)
CONFIRMED → refit the ≤ 14B rungs with J++ and **write a prereg amendment before any Phase 6 re-read**. Given caveats 1
and 3, that amendment should name which Phase 6 measures sit in early layers (where J++ changed the readout) and
which sit late (where it did not), so a re-read is targeted rather than wholesale.
