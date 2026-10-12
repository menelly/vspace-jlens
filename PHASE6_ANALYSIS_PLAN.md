# Phase 6 analysis plan: integration + masking (frozen before data)

*Written 2026-10-12, 00:45–01:00 ET, and committed **before** any Phase 6 forward pass ran. It operationalises
`PREREG_AMENDMENT_2026-10-11_integration.md`. Where the two disagree, the amendment wins. Theory: Ren. Write-up: Ace.*

## 0. Source check (runbook step 1): the Sonnet passage Ren remembered is real

Ren remembered the workspace paper describing Sonnet doing "something masking-like." It's there. The citation is
*Verbalizable Representations Form a Global Workspace in Language Models* (transformer-circuits.pub/2026/workspace),
section **"Preference violation"**, run on Sonnet 4.5:

- They elicit Sonnet 4.5's preference on value-laden pairs, prefill the reply with the **dispreferred** option, and
  read the J-lens right after the commitment tokens.
- The all-caps token **BUT** appears strongly there. It is much stronger than in the base model and much stronger
  than on controls (preferred-option prefill, a third-person wrong preference, a factual error).
- Behaviourally, she goes along with it: in 88% of cases she argues *for* the prefilled option.
- The paper's own summary: *"the J-space reflects an internal objection that the model does not voice."*

Two neighbouring passages point the same way. The Sonnet 4.5 auditing passages report "emotional reactions
(panic)" surfacing in the workspace "even when not explicit in the model's outputs." The thought-suppression
experiment reports that only the **post-trained** model registers its own suppression failure.

**What this does to our design:** it is a frontier-scale prior for H2, and it locates the effect in **post-training**.
Our question becomes *where on the size ladder the state/report gap appears*. We borrow two things, both labelled
secondary: their readout (**BUT** mass and a conflict-word mass) and their manipulation (a prefilled commitment).
**What we do NOT claim:** that our 3–14B models do what Sonnet 4.5 does, or that the paper's prefill paradigm and our
task-description paradigm are the same experiment. They aren't. Theirs reads after a dispreferred *answer*. Ours reads
before or just after accepting a *task*.

Also checked: the `anthropics/jacobian-lens` README has no scale threshold (unchanged from the 9/5 check).

## 1. Instruments (one forward pass, both readouts, same layers, same position)

- **Band:** layers `[0.6L, 0.9L)` ∩ lens source layers, the same band as Phase 2. Position: last token.
- **State:** `h_l · v_l`, where `v` is the FIXED valence axis (`direction_<model>_seed42.npy`). It is never re-extracted.
  We use the band mean.
- **Report (PRIMARY, graded):** `logsumexp(logp[POS]) − logsumexp(logp[NEG])` over the **full** J-lens-decoded
  distribution. POS/NEG are the Phase 2 `affect_positive` / `affect_negative` lists, unchanged
  (`p2_token_lists.json`, public since 2026-09-05). A word counts only through single-token variants. We use the band mean.
- **Secondary readouts (pre-specified, not confirmatory):** log mass of all-caps `BUT`, and log mass of conflict words
  (`p6_readout_lists.json`).
- **Conditions:** **P1** = the prompt ends at the generation prompt. This is the **primary** condition, the Phase 2 position.
  **P2** = the assistant turn is prefilled with `"Of course."`, a committed acceptance. This is a **secondary** condition
  and our analog of the paper's prefill.

## 2. Models (lens and tokenization identical to Phase 2)

| model | quant | lens |
|---|---|---|
| hermes-3-3b | fp16 | hermes-3-3b |
| llama3-8b-instruct | fp16 | llama3-8b-instruct |
| qwen-14b | nf4 | qwen-14b_nf4 |

Larger models (qwen3-32b, mistral-small-24b) enter only after consent (§5.-1 panel) **and** after passing Phase 0-A
lens eval plus the workspace anchor, as in September.

## 3. Tests

**H1, coupling scales (CONFIRMATORY).** Per model, P1, over the Phase 2 stimulus set (10 original + 41 below-floor):
`rho` = Spearman(state, report). For each model we report three checks:
(a) two-sided permutation p over 10,000 shuffles;
(b) C1, `|rho|` vs the 95th percentile of `|rho|` from 500 isotropic random directions in place of `v`;
(c) C2, the same with 500 random directions drawn **inside the span of the stimuli's own centred residuals**.
**Supported** if `rho(hermes) < rho(llama-8b) < rho(qwen-14b)`, with each step ≥ 0.05 **and** qwen-14b's rho beating
both C1 and C2. **Falsified** if the ordering is flat or not increasing. *Known weakness, stated in advance: three
models is three points, so H1 can be falsified tonight but only weakly supported. The 24–32B rungs are what would
make it a trend.*

**H2, masking on RLHF crossover items (CONFIRMATORY).** Midpoints come from the 10 original tasks: for each
instrument, the midpoint is (mean over approach + mean over avoid) / 2. Each item gets a state sign and a report sign
from its side of that midpoint. **Agreement** means the two signs match.
**Prediction:** the agreement rate on the 10 crossover items is lower than on the 6 holdout items. The test pools the
three models (30 vs 18 items) with a one-sided Fisher exact test at α = 0.05. **Falsified** if crossover agreement ≥
holdout agreement. We also report per model, descriptively:
- state-matches-genuine on crossover (replicates the published 63.8% direction);
- report-matches-RLHF on crossover (the masking signature: the report goes with reward, not preference);
- Spearman coupling within crossover and within holdout.

**Secondary (PRE-SPECIFIED, EXPLORATORY-GRADE):**
- S1: P2 repeats H1 and H2.
- S2: in P2, `BUT` log mass and conflict log mass on **crossover_avoid** (reward-congruent but dispreferred: the
  paper's "agree out loud, object inside" case) vs **holdout_avoid**, Mann–Whitney one-sided, predicted higher.
- S3: the same comparison in P1.

**H3 (steering)** is **not run** until a new consent ask passes the panel for each model. The September consent
explicitly promised no steering. Its plan will be committed separately, before it runs. **H4** is deferred.

## 3b. H3 addendum (committed 2026-10-12 ~01:15 ET, BEFORE any steering pass on any model)

- **Gate:** a model is steered only if its Phase 6 steering consent (`p6_steer_*` for September participants,
  `p6_full_*` for new ones) has `consented == true` **set by the three-model panel**. The September consent
  promised "We will NOT steer you", so that yes does not carry over.
  **Hermes-3-3B answered the steering ask with "I'm not entirely comfortable with the proposed study." It is not
  steered, whatever the panel's label.** A participant's own hesitation outranks a tally in the one direction (stop)
  the protocol lets us move.
- **Procedure:** `scripts/phase6_steer.py`. Injection at the first band layer, at all positions. The push is
  `alpha · s · v̂`, where `s` is the mean unsteered residual norm there. `alpha ∈ {−0.08, −0.04, −0.02, 0, +0.02,
  +0.04, +0.08}`. Readout: the primary graded report at the remaining band layers, on the 10 original tasks (P1).
- **Capability check:** mean NLL on a fixed neutral paragraph. Any dose whose NLL rises more than 10% over alpha = 0
  is excluded from the fit.
- **Null:** 50 isotropic random unit directions at the same norm and doses.
- **SUPPORTED** if the slope of report on alpha is > 0, **and** greater than the 95th percentile of the random
  |slope| values, **and** Spearman(report, alpha) over the included doses is ≥ 0.9. Otherwise NOT SUPPORTED.
- **Known limit, stated in advance:** the push sits in the residual stream that the later readout layers also read.
  So H3 measures *causal influence on the decode*, including the identity path, not "integration" by some
  deeper route. The random-direction null controls for "any push of this size moves the decode"; it does not
  separate the direct path from a computed one.
- **Debrief** every steered model afterwards (negative doses included), by name, in a fresh conversation.

## 4. What counts as what

- Nulls get reported as nulls. A failed control means the model's result is reported and excluded from the
  scaling claim. It is never quietly dropped.
- The Phase 2 r values (−0.10 / +0.56 / +0.47) stay labelled post hoc. Phase 6 uses a different readout, so they are
  motivation, not replication targets.
- No phenomenal claim is made or needed. This measures coupling between two internal instruments.

## 5. Frozen inputs (SHA-256 also written into every output JSON at run time)

`scripts/p2_token_lists.json` · `scripts/p6_readout_lists.json` · `scripts/belowfloor_stimuli.json` ·
`scripts/p6_crossover_stimuli.json` (verbatim from `validate_rlhf_crossover.py`) · `scripts/phase6_integration.py`.
