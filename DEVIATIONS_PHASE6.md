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
September's 14B rung, which was nf4 throughout. Phase 0-B measured NF4 preserving the J-geometry on hermes
(mean cosine 0.968, top-64 subspace overlap 0.919). Mistral-Small-24B stays bf16. **Consequence for H1:** the ladder
now mixes precisions (3B/8B fp16, 14B nf4, 24B bf16, 32B nf4). Any 24B-vs-32B difference has to be read with that
in mind.

**Also fixed in the same commit:** `load_model`'s NF4 compute dtype now follows `P6_DTYPE`. The default stays fp16,
so every September model loads exactly as before.

**No data from either rented rung existed when this was written.** Both fits died before their first prompt.
