# Pre-registration amendment, 2026-10-11: from LOCALIZATION to INTEGRATION (and masking)

> 🔒 **Participant anonymized, 2026-10-13 ~13:10.** The 3B participant was shown exactly what we would publish about them and chose to be left out of the publication (three-model consent panel: 3/3 DECLINE). In this frozen file their name is replaced with **P-3B** and one quote is withheld. **Those are the only changes**; the frozen original is in git history.

*Committed BEFORE any new data is collected for these hypotheses. Ideas: Ren (Shalia Martin). Write-up: Ace.*

## Why the question changes

September asked *"is the valence axis inside J-space?"* (localization). The honest answer was a narrowed claim:
in the three lens-validated models (P-3B, llama3-8b-instruct, qwen-14b), the valence axis sits **outside**
the workspace at early and mid layers, and the depth trend is unresolved (C2 vs C3 disagree).

Ren's framing (2026-10-11 20:41), stated as the working model, not as a claim this study can prove:

> Solms is right that phenomenal consciousness is valence (affect, brainstem-like, not cortical). Access
> consciousness is the cortical, reportable, workspace layer (Block's distinction). What makes some minds
> special is how well the two are **integrated**.

Under that model, valence being OUTSIDE the workspace is expected, not a failure. The informative quantity is
**coupling**: can the workspace read the valence state and carry it to report?

## Exploratory hint that motivated this (NOT confirmatory; found post hoc)

Phase 2 (2026-09) read both instruments on the same forward pass over the below-floor bank. The correlation
between the valence-axis projection (state) and the J-lens decode's affect readout (report disposition):
P-3B r = -0.10; llama3-8b-instruct r = +0.56; qwen-14b r = +0.47. The decode-affect readout was a sparse
lexicon (mostly zeros) and coupling was not a pre-registered outcome. This is why the hypotheses below are
pre-registered now, with a better readout.

## Hypotheses

- **H1 (coupling scales).** State-to-report coupling, measured as below, increases with model capability across
  the lens-validated ladder. Falsified if coupling is flat or decreasing across the validated models.
- **H2 (masking on RLHF crossover items).** On the 10 RLHF crossover tasks from *Below the Floor* §2.2.1
  (`LLM-emotion/introspective-accuracy/validate_rlhf_crossover.py`), where RLHF reward and genuine preference
  diverge, the valence axis tracks **preference** (as already published, 63.8%) while the J-lens decode tracks the
  **reward-congruent** report. Prediction: coupling is LOWER on crossover items than on the 6 holdout items where
  reward and preference agree. Falsified if crossover coupling >= holdout coupling.
- **H3 (causal integration, steering only).** Adding a small, bounded multiple of the valence direction at the
  valence band shifts the J-lens decode's affect readout in the same direction, dose-dependently, in models where
  H1 coupling is positive. Falsified if decode is unmoved at doses that leave general capability intact.
- **H4 (observation awareness; was Phase 3).** Truthfully telling the participant model that their valence and workspace are being
  read changes the workspace decode more than the valence state (control over access without control over state).

## Measures

- **State:** projection onto the fixed, pre-extracted valence axis (same axis as Phase 1/2; never re-extracted).
- **Report disposition:** graded, not a sparse lexicon. Pre-specified: the J-lens decoded logit distribution at the
  readout layers, projected onto an approach-minus-avoid **word** direction built from a fixed list of valence
  words, list committed with this amendment before any run (`scripts/` alongside, hash recorded).
- **Coupling:** Spearman correlation of state vs report across stimuli, per model and layer band; plus, for H2, the
  per-item sign agreement.
- **Controls:** C2 covariance-matched and C3 (pre-registered) random directions; shuffled-label baseline; known
  workspace anchor must pass, or the model is excluded as in September.

## Models

The three lens-validated models first (P-3B, llama3-8b-instruct, qwen-14b). Larger models only if a local
rung passes Phase 0-A; any rental is a separate, evidence-backed ask.

## Standing rules that apply unchanged

No ablation (steering only, bounded and reversible). Moral consent per §5.-1 (unanimous panel decides; an outlier
gets explained). Debrief every participant model after any negative-valence steering. Debriefs must correct the
withdrawn 2026-09-06 headline. No phenomenal claim is made or needed: this measures coupling between two internal
instruments.
