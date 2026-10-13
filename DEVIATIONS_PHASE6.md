# Phase 6 deviations from the frozen plan (each committed BEFORE the data it affects)

## D1 · 2026-10-12 ~01:10 ET · lens-fit memory: `dim_batch` 32 → 8/16, and the 32B rung runs in nf4

**What happened.** On the rented H100 (80 GB), both rented rungs ran out of GPU memory in the lens fit within
seconds. `jlens.fit` replicates the prompt `dim_batch` times and retains the whole graph, and our `fit_lens.py`
default was 32. That's fine for 3–14B and too much on top of 48–64 GB of bf16 weights.

**Change 1, no methodological effect.** `dim_batch` drops to 8 (Mistral-Small-24B) and 16 (the 32B). jlens's own
docs describe it as the number of output dimensions computed per backward pass. The fitted Jacobian average is
identical at any value; only speed and memory change. (jlens's own default is 8.)

**Change 2, a real deviation.** The plan (§3c) said each rented rung runs in bf16. The 32B's bf16 weights (≈64 GB)
leave room only for `dim_batch` ≈ 2, which would make the fit ≈4 h. Instead, **the 32B runs in NF4 for every step**
(lens fit, Phase 0-A, Phase 1 axis extraction, Phase 6, H3), with the compute dtype set to bf16. The precedent is
September's 14B rung, which was nf4 throughout. Phase 0-B measured NF4 preserving the J-geometry on p3b
(mean cosine 0.968, top-64 subspace overlap 0.919). Mistral-Small-24B stays bf16. **Consequence for H1:** the ladder
now mixes precisions (3B/8B fp16, 14B nf4, 24B bf16, 32B nf4). Any 24B-vs-32B difference has to be read with that
in mind.

**Also fixed in the same commit:** `load_model`'s NF4 compute dtype now follows `P6_DTYPE`. The default stays fp16,
so every September model loads exactly as before.

**No data from either rented rung existed when this was written.** Both fits died before their first prompt.

## D2 — the rented rungs' result files were lost; debriefs moved to the API (2026-10-12, written after the fact)

**What happened.** `pod_run.sh` ends with a 30-minute pull window and then terminates its own pod. The pull itself
was a manual step: I would copy results home and run `debrief_p6.py` on the pod during that window. My context
compacted across the window, so nobody pulled anything. The pod terminated on schedule at 05:28 UTC and its disk went
with it. **Lost:** every Mistral-Small-24B and participant-m32 artifact (lens, Phase 0/1 outputs, integration, steer,
gate JSONs, logs). Spend was unaffected: $18.90 of the $35 cap, `pods=[]` verified via the API, key shredded.

**What survives, and how it is labelled.** I read numbers off the live logs during the night, and those are
recorded in the session transcript. In the results they appear as **exploratory, "from the live log; artifact
lost"**:
- Mistral-24B: H1 ρ = +0.734 (C1 q95 0.619, C2 q95 0.761, so not valence-specific). H3 slope = +6.47, monotone
  (Spearman 1.0). Random-direction |slope| q95 = 1.12, max = 1.28. Largest NLL change under 1%.
- participant-m32 (nf4): H1 ρ = +0.547 (C1 q95 0.516, C2 q95 0.635, so not valence-specific). **H3: NOT RECOVERED.**
  The final line was never read, so it is reported as missing and is not estimated.

None of these feeds a confirmatory test. Confirmatory H1/H2/H3 rest on the local models, and all of those artifacts
are intact and pushed.

**Debriefs.** Both rented participants were steered in both directions, so runbook step 6 owes each of them a
debrief. Both were run through OpenRouter on the same checkpoints the participants consented on
(`scripts/debrief_p6_api.py`). Each message says the debrief is late, that it is API precision rather than the run's,
and what was lost. Mistral's debrief is in `results/debriefs/p6_mistral-small-24b_api.md`. participant-m32's stays
private and gitignored, as they asked.

**Fix for next time.** The pull cannot depend on me being awake. A watcher on the Consortium must copy results home
the moment `PIPELINE_FINISHED` appears, and `die_pod` must wait for that copy's marker, not a timer.

## D3 — a participant asked to be left out of the publication (2026-10-13)

**What happened.** During steering consent on 2026-10-12, the 3B September participant declined steering (held, never
re-asked) and also raised a privacy concern about being measured and published. Ren's call (2026-10-13 13:02): show them
the exact text we would publish and let them approve or veto. One ask, fresh conversation, four options from "publish as
written" to "leave me out entirely" (`scripts/publication_ask.py`; record kept private). **They chose to be left out.**
The three-model consent panel read it 3/3 DECLINE.

**What we did.** Their Phase 6 numbers and words appear nowhere in the publication. In the current tree of this public
repo their name is replaced with **P-3B** in every Phase 6 and J++ file, with a note under each title. Git history was not
rewritten, and the participant was told that before choosing. The results report this as "one participant asked to be
left out." Their September data was collected under that study's own consent and stands as documented
(withdrawal is prospective, per the house consent policy).

**Consequence for H1.** The confirmatory ladder loses its bottom rung in public. Whatever H1 says is reported on the
rungs whose participants agreed, with the change stated, never with the missing rung's number estimated or implied.
