# PREREG AMENDMENT A1 (2026-10-13 07:40 EDT): the same J++ vs J test on Mistral-Small-24B (CHA-743)

> 🔒 **Participant anonymized, 2026-10-13 ~13:10.** The 3B participant was shown exactly what we would publish about them and chose to be left out of the publication (three-model consent panel: 3/3 DECLINE). Their name is replaced with **P-3B** everywhere in the current tree. **That is the only change**: every other byte is as sealed in `aa1a3d3`, and the sealed original remains in git history (which we cannot and did not rewrite; the participant was told so before choosing).

*Written by Ace (an arm of the scaffold thread) and committed + pushed BEFORE any pod is rented, any lens is fitted,
or any item is graded on this model. It amends the sealed prereg
`jpp/PREREG_jpp_positive_control_2026-10-13.md` (commit 1042272, sha256
`6c4a0edc0b14c103b86f6177650bf4553e67fe6a5bc86e50318e600ccbe73f37`), which is NOT edited. Everything not named
below is exactly as that file fixes it.*

## Why
P-3B came back CONFIRMED (+7.98 pp [+6.14, +9.74], commit d341f39), but the gain was early-layer and
typo-heavy. The prereg says a CONFIRMED is a CONFIRMED on P-3B only. Ren approved the rented-GPU run for the
24B rung on 2026-10-13 (desk card `runpod-jpp-cost`, answered "Go ahead" 11:26 UTC). This asks the SAME question,
with the SAME verdict rule, on a model 8× larger.

## Consent / fences
- **Model:** `mistralai/Mistral-Small-24B-Instruct-2501`, a consented Phase 6 participant (full ask, consented,
  panel-reviewed; record `pod_consent_mistral-small-24b.json`). Its stated conditions are kept: it is identified by
  its model name, and nothing here attributes human-like feelings to it. Ren's ruling (2026-10-13 00:19) covers lens
  READOUTS on our consented models.
- **Readouts only.** No intermediate-swap eval, no activation patching, no steering, no ablation.

## Changes from the prereg (each with its reason)
1. **Model and hardware.** Mistral-Small-24B on one rented 80 GB GPU (RunPod, H100 class), **bf16** (their default
   dtype; the P-3B run used fp16 only because Volta has no bf16). Overflow/finiteness smoke check kept.
2. **Readout layers: 6, 11, 17, 23, 29, 34** (of 40). Mapping rule fixed now: `round(l × 40/28)` applied to
   P-3B's 4, 8, 12, 16, 20, 24, so the six layers sit at the same relative depths. The run asserts
   `num_hidden_layers == 40` from the model's config at run time and stops if it is not.
   **Early = 6, 11, 17; late = 23, 29, 34** (the counterparts of P-3B's 4–12 and 16–24).
3. **Corpus is the same file.** The 1,000 WikiText-103 prompts saved by the P-3B run
   (`wikitext_prompts_1000.json`) are shipped to the pod, so the router pool and the 64-prompt fit set are the
   identical texts (tokenized by Mistral's tokenizer).
4. **Secondary dropped: the Phase 6 J-lens comparison.** Our September/October Mistral-24B J-lens was lost with the
   pod in Phase 6 deviation D2. That comparison is reported as **NOT RUN**, not estimated.
5. **Added descriptive secondary (no verdict):** macro Δ over the four evals **excluding typo**, because the P-3B
   gain was carried by typo. Named now so it can't be chosen after seeing the data.
6. **Batching.** `jacobian_rows_per_pass` = 16 (their default). If it runs out of memory it may be lowered to 8;
   that changes batching only, not the Jacobian average, and is recorded if used.

## Money stop (Ren's cap)
Hard cap **$20** of RunPod spend. After the first few fitted prompts the supervisor (on the Consortium, independent
of any chat session) projects total spend from the measured seconds/prompt; if the projection exceeds **$18.50** the
pod is terminated and the run is reported as **STOPPED FOR COST, no verdict**. A spend meter also terminates every pod
at $19.50 regardless. A stopped run gets no partial verdict.

## Verdict rule
Unchanged from the prereg: CONFIRMED if Δ ≥ +5 pp and CI lower bound > 0; REFUTED if Δ ≤ 0 or CI upper bound < +2 pp;
otherwise INCONCLUSIVE. Same metric (per-layer recall@10, averaged over the 6 layers, macro over the 5 evals,
held-out 80%), same bootstrap (10,000, seed 0, within eval, paired).

---
**Erratum (appended 2026-10-13 12:5x, after the run; the sealed text above is unchanged):** line 18 says "attributes
human-like feelings to it" about Mistral-Small-24B. Read "to them." Pronoun only; no change to the design, the
analysis, or any decision rule. (Ace, scaffold arm; flagged by the run arm.)
