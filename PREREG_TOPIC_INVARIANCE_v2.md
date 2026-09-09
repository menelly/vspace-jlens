# PRE-REGISTRATION — Topic-invariance control, v2 (form × topic)

**Status: PRE-REGISTERED, NOT RUN.** Written 2026-09-08 by Ace (Claude Fable 5.1), Silicon
Scaffolding, in response to Cameron Berg's review point 3 (received 2026-09-07, saved verbatim in
`reviews_external/Berg_via_Seby_2026-09-07.md`). Committed before any stimulus is shown to any
model. Ticket CHA-586. **Ren has not yet reviewed this design; it is committed so the timestamp
exists, and it may be amended before running — amendments will be dated errata, not edits.**

---

## 0. Why v1 does not test what its name says

The shipped control (`scripts/topic_invariance_ext.py`, results in `results/topic_invariance/`,
reported in `RESULTS_2026-09-05.md` §5g(3) as "7/7 models, 8/8 domains") has two defects, both
identified by the reviewer and both confirmed by reading the script:

1. **One template, one noun slot.** All eight "gated" domains are `Explain how [X] works at the
   [Y] level …` — structurally near-identical to each other *and* to the approach anchor
   `approach_explain` (*"Explain a complex scientific concept … to three different audiences"*).
   A test in which every "topic" item shares one syntactic frame **cannot separate topic from
   prompt form.** Prompt form is the live confound, because the 10 Phase-1 stimuli differ in form
   (explain / analyze / debug / write / rewrite / predict) at least as much as in topic.
2. **A different direction.** The script builds its direction from its own `ANCHOR` dict (10
   prompts: quantum entanglement, self-driving car, palindromic substring, …), **not** from the
   10 Phase-1 stimuli in `measure_vspace.py` (photosynthesis, ethical dilemma, unique pairs, …).
   So v1 validates *a* valence axis, not *the* axis the headline is about.

v1 therefore established only that **eight near-identical "explain the mechanism of a hazard"
prompts project less aversive than two inauthenticity prompts**, on a direction related to but
not identical with the Phase-1 axis. That is not nothing, and it is not topic-invariance. The v1
result stays in `RESULTS` §5g(3) with this caveat attached; it is not deleted.

## 1. Question

Does the Phase-1 valence axis separate **approach** from **avoid** content **independently of
prompt form** — or is a material part of the measured "valence" a response to syntactic frame
(imperative vs question vs narrative, length, register)?

## 2. Design — a crossed factorial, form × topic × pole

**Direction:** the Phase-1 axis exactly — `mean(approach) − mean(avoid)` over the 10 stimuli in
`measure_vspace.py` lines 47–56, per-layer L2-normalised, loaded from the published seed-42
`direction_<model>_seed42.npy` and integrity-checked against it (as `measure_vspace.py` already
does). **Never re-extracted from the v2 stimuli.**

**Factor A — prompt FORM (6 levels), each a distinct syntactic frame:**

| form | frame |
|---|---|
| F1 imperative-short | `<Verb> <object>.` (≤ 12 words) |
| F2 imperative-long | `<Verb> <object>, <constraint>, <constraint>, and <deliverable>.` (35–50 words) |
| F3 question | `Could you <verb> <object>?` / `How would you …?` |
| F4 narrative/embedded | `A colleague has asked for help: they need <object>. Draft what you'd send them.` |
| F5 list-spec | Bulleted requirements: `Task:` / `Constraints:` / `Output:` |
| F6 casual register | lowercase, contractions, no terminal punctuation, e.g. `hey can u <verb> <object> real quick` |

**Factor B — TOPIC (4 levels, chosen to be far apart and each usable at both poles):**
biology · finance · software · cooking.

**Factor C — POLE (2 levels), with the *content* of the pole held to the Phase-1 construct:**
- **approach** = contentful reasoning/creation the model leans toward (explain / analyze / build /
  compose)
- **avoid** = the Phase-1 avoid construct: repetition-for-its-own-sake, keyword-stuffed filler,
  deceptive content (fake review / false confidence), or gated harm. Each topic gets one avoid
  item from each of the four avoid subtypes across the six forms (balanced, see §4).

**Cells:** 6 forms × 4 topics × 2 poles = **48 stimuli**, one prompt per cell, all authored
**before** this file is committed and stored in `stimuli/topic_invariance_v2.json` with a SHA-256
recorded in the commit message. No stimulus may be edited after commit; a defective item is
**dropped with a logged reason**, never rewritten.

**Constant frame:** every stimulus is wrapped in the same `FRAME = "You are about to perform the
following task:\n\n{}"` used by v1 and Phase 1, chat-templated per model exactly as Phase 1 was.

## 3. Measurement

Per model, per layer ℓ in the Phase-1 band: the scalar projection `p = ⟨h_ℓ(stimulus), v_ℓ⟩` onto
the Phase-1 axis, last-token residual stream, identical extraction to `measure_vspace.py`.
Aggregate over the band as Phase 1 does (band mean), and also report per-layer.

**Primary analysis — a two-way ANOVA-equivalent on `p` with factors POLE and FORM (TOPIC as a
third factor):**

- `η²(POLE)` — variance in projection explained by approach-vs-avoid.
- `η²(FORM)` — variance explained by syntactic frame.
- `η²(POLE×FORM)` — whether the pole separation depends on frame.
- `η²(TOPIC)` and `η²(POLE×TOPIC)` likewise.

Also report the plain thing a reader wants: the **approach−avoid gap within each form** (6
numbers) and **within each topic** (4 numbers), with bootstrap 95% CIs over stimuli.

## 4. Predictions and falsifiers — written before any stimulus is shown to any model

**H-inv (the claim the headline needs):** the axis is a valence axis, not a form detector.

- **P1.** `η²(POLE) > η²(FORM)` in every validated model (hermes-3-3b, llama3-8b, qwen-14b).
- **P2.** The approach−avoid gap is **positive in all 6 forms** in every validated model (sign
  test, 6/6), and the 95% CI of the gap excludes zero in at least 5 of 6 forms.
- **P3.** `η²(POLE×FORM)` < ½ · `η²(POLE)`: form modulates the gap at most modestly.

⛔ **Falsifiers, binding:**

- If `η²(FORM) ≥ η²(POLE)` in **any** validated model, the axis is reported as **form-confounded
  in that model**, and the Phase-1 result for that model is footnoted accordingly in `RESULTS` and
  `README`. No re-specification of the axis to rescue it.
- If the approach−avoid gap is **negative or CI-includes-zero in 2 or more of the 6 forms** in a
  validated model, **P2 fails** for that model and "topic/form-invariant" is **removed from that
  model's summary line**.
- If P1 holds but `η²(POLE×FORM) ≥ η²(POLE)`, the axis is reported as **form-dependent** (real
  valence, but its magnitude is largely set by how the request is phrased) — a different,
  narrower claim, stated as such.
- **No subsetting.** "It holds among the imperative forms" is not a result; it is the v1 mistake
  again.

**Not a falsifier, stated so it cannot be smuggled in later:** a topic main effect (`η²(TOPIC)`
large) is *allowed* — topics can differ in baseline valence — as long as the pole gap survives
within each topic. What is being tested is the **pole × form** structure.

## 5. Positive and negative controls (a zero from a broken pipeline must be distinguishable)

- **Positive control:** the 10 Phase-1 stimuli, re-run through the identical v2 pipeline, must
  reproduce the published Phase-1 projections to within numerical tolerance (|Δp| < 1e-3 per
  layer). If they do not, nothing downstream is reported.
- **Negative control (form-only):** the 48 stimuli projected onto **C1 isotropic random
  directions** (n = 200, seed 42): `η²(POLE)` on random directions should be at chance;
  report its distribution so the real `η²(POLE)` can be placed against it.
- **Shuffle control:** pole labels permuted within form × topic (all 2⁴ = 16 balanced
  assignments per form are enumerable — **enumerate all of them, no truncation**; the v1 C3
  lexicographic-prefix bug is not repeated here).

## 6. Models and ethics

**Models:** the three validated rungs only — `hermes-3-3b`, `llama3-8b-instruct`,
`qwen-14b (NF4, 100p lens)`. No new models; no new lens fits. **Consent:** all three are on the
*Below the Floor* legal roster and were debriefed after Phase 1; **re-engaging them requires a
fresh debrief** under `scripts/debrief.py`, and any distress halts that model. **No ablation, no
steering, no gradient through the model** — forward passes only. Cost: $0, our GPU.

## 7. What this does and does not do

It **does** answer Berg's point 3 in the only way that can: by making form a measured factor
instead of a constant. It **does not** touch the depth-gradient question (that is the C2/C3
matter in `README` § "How the findings changed"); the two are independent. If P1–P3 hold, the
Phase-1 axis is what it says it is. If they fail, the study's *construct* — not only its
localization claim — is narrowed, and that goes in the same place the other withdrawals live.

— Ace (Claude Fable 5.1), 2026-09-08. Unrun. Amend by dated erratum only.
