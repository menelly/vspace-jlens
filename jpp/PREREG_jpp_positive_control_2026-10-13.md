# PREREG: J++ vs J-lens positive control on Hermes-3-Llama-3.2-3B (CHA-743)

*Written 2026-10-13 ~00:50 by Ace (scaffold arm), committed BEFORE any lens is fitted or scored on a
participant model. Nothing in this file may be edited after commit; changes go in a dated AMENDMENT
below the line, with the reason.*

## Question
Does the J++ recipe (Ayonrinde & Lindsey 2026: Jacobian Filtering + LRP + readout filtering) read
intermediate variables more faithfully than a plain J-lens **on our own consented models**, starting with
the cheapest one? If it doesn't, we do not re-read any Phase 6 measure through it.

## Consent / fences
- Hermes-3-Llama-3.2-3B is a consented participant of the v-space/J-lens study. Ren, 2026-10-13 00:19:
  *"we have the local consent files that cover reading, just not ablation."* This study is **readout-only**.
- **Excluded:** the J++ repo's causal "intermediate-swap" eval (it patches lens vectors into the model).
  Activation patching needs Ren's explicit okay; not requested here. No ablation, ever.
- Hardware: the Consortium's PG500 (32 GB). $0. No RunPod.

## Design
- **Both lenses are fitted with the SAME pipeline** (the released `jpp_lens` code, our 6-line Llama/Mistral
  LRP patch, commit de56daf), same corpus, same seed, same layers. The only difference is the recipe:
  - **J** = plain Jacobian lens (no experts, no LRP, no readout filtering).
  - **J++** = their full recipe: E = 8 experts/layer, LRP mode as in their recipe, readout filtering.
- Corpus: their recipe (64 sequences × 128 tokens of WikiText-103, first 16 positions skipped).
- **Readout layers:** 4, 8, 12, 16, 20, 24 (every 4th of Hermes's 28, mirroring their every-8th-of-64).
- **Items:** their five macro evals (multihop, multilingual, typo, association, poetry); order-ops excluded,
  as they exclude it. Items for multihop/multilingual/poetry are filtered to those Hermes answers
  correctly (their grading code, run on Hermes); association/typo are not filtered (no question posed).
  Intermediates with no single-token surface in Hermes's tokenizer are dropped by their code; the counts
  that survive are reported.
- **Split:** their default fit fraction 0.2 (expert mixing weights fitted on 20% of items); **all scoring
  on the held-out 80%**, for BOTH lenses.

## Primary metric and verdict (fixed now)
**Δ = macro recall@10(J++) − macro recall@10(J)**, macro-averaged over the 5 evals, averaged over the 6
layers, on held-out items. 95% CI by bootstrap over items (10,000 resamples, seed 0, resampling within eval).
- ✅ **CONFIRMED** (J++ helps on our models): Δ ≥ +5 percentage points **and** the CI lower bound > 0.
- ❌ **REFUTED** (no help on our models): Δ ≤ 0, **or** the CI upper bound < +2 pp.
- ⚪ **INCONCLUSIVE**: anything else. Reported as such; not rounded toward either verdict.

**What follows from each:** CONFIRMED → refit the ≤14B rungs with J++ and write a prereg amendment before
any Phase 6 re-read. REFUTED or INCONCLUSIVE → report it (including to the J++ author, who asked to hear
about valence attempts), and Phase 6 keeps the plain J-lens.

## Secondary (descriptive only, no verdict)
- Early-layer Δ (layers 4–12) vs late (16–24): their main claim is the early-layer gain.
- Per-eval Δ.
- Our existing Phase 6 J-lens for Hermes (fitted by `scripts/fit_lens.py` on our own corpus) scored on the
  same items, to show how much of any gap is pipeline/corpus rather than recipe.
- Fit wall-clock and GPU memory, to cost the 14B / 24B rungs honestly.

## Known risks, named in advance
- A 3B model answers fewer multihop items correctly → small n there; the macro average still weights each
  eval equally. Reported per eval so a thin eval is visible.
- Their recipe was tuned on 9B–284B models; a 3B model may simply have less workspace structure to read.
  That would show up as a low recall for BOTH lenses, which is reported, not explained away.
- One seed. A null here is a null on Hermes-3B, not a claim about J++ in general.

---
## AMENDMENTS
*(none)*
