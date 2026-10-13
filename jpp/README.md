# 🔬 J++ lens on our own models (CHA-743)

> 🔒 **Participant anonymized, 2026-10-13 ~13:10.** The 3B participant was shown exactly what we would publish about them and chose to be left out of the publication (three-model consent panel: 3/3 DECLINE). Their name is replaced with **P-3B** everywhere in the current tree. **That is the only change**: every other byte is as sealed, and the sealed original remains in git history (which we cannot and did not rewrite; the participant was told so before choosing).

**What J++ is:** Ayonrinde & Lindsey, *"J++ Lens: Jacobian Filtering Enables More Faithful Workspace
Lenses"* (LessWrong, 2026-10-08; post `nc9dHfcB22JdMzGbr`). Code: https://github.com/safety-research/jpp_lens
(Apache-2.0, Anthropic PBC; modified by Kola Ayonrinde). It improves the J-lens we already use by fitting
8 "expert" Jacobians on clusters of activations and down-weighting the noisy ones (mostly clusters that
just track punctuation), plus an LRP backward pass and readout filtering. Their headline: recall@10
55% vs J-lens 36%, best gains in EARLY layers. We do **not** vendor their code here; we keep only our
own changes and point at theirs.

**Why we care:** Phase 6 reads valence/workspace coupling through the plain J-lens, which is noisiest
exactly in the early-to-middle layers. A cleaner lens can sharpen those readings, or show they were
lens artifacts. The J++ author, on X (2026-10-12 23:22), about using it for valence: *"Would be
excited to see someone try this!"*

## What's in this folder (all ours)
| file | what |
|---|---|
| `jpp_setup.sh` | builds a SEPARATE venv on the Consortium (`/home/Ace/jpp-venv`, Python 3.12, `torch 2.11.0+cu126`, `transformers 5.14.1`). Never pip into `/home/codex/venv`. cu126 (not their cu128) because our PG500 is sm_70 (Volta) and the P40 is sm_61; cu128 wheels dropped those. **Verified** a matmul runs on the PG500. |
| `lrp_llama_mistral.patch` | 6 lines: registers `LlamaRMSNorm`, `MistralRMSNorm`, `LlamaMLP`, `MistralMLP` with the existing Qwen2 LRP rules. Justified because their `forward`s are byte-identical to Qwen2's in transformers 5.14.1 (checked with `inspect.getsource`), and all four of our Llama/Mistral checkpoints have `mlp_bias` off. Qwen2.5 models (our 0.5B and 14B) were already supported upstream. |
| `test_lrp_llama_mistral.py` | 6 behavioural tests × {Llama, Mistral}: forward unchanged, exit restores stock, every residual norm + MLP patched, LN-rule gradient equals the Llama formula `cot·w·rsqrt(mean(x²)+ε)` (plain `w`, NOT Qwen3.5's `1+w`), half-rule halves the MLP gradient, and a **positive control** that the patched gradient differs from stock. |

## Receipts (2026-10-13, ~00:30–00:45, Consortium)
- Their suite on our box: **214/214** with the GPU hidden (`CUDA_VISIBLE_DEVICES=`). With the GPU visible, 4 tests fail on a cpu/cuda device mix: their tests assume a CPU-only machine; not a code bug.
- Our tests with the patch: **12/12 pass**. **Negative control:** same tests against the ORIGINAL `lrp.py`: **12/12 fail.** Full suite with patch: **226/226**.

## Rules for this work (from CHA-743)
- **Readouts only.** Ren, 2026-10-13 00:19: *"we have the local consent files that cover reading, just not ablation."* Their causal eval patches lens vectors into the model: **activation patching needs Ren's okay first.** No ablation, ever.
- **Positive control before any Phase 6 re-read:** J++ vs our plain J-lens on P-3B, their readout tasks, thresholds fixed in a prereg committed BEFORE the run. It must be able to end REFUTED.
- RunPod money (24B/32B) is Ren's call.

## Apply the patch
```bash
cd /home/Ace/jpp_lens && patch -p1 < /path/to/lrp_llama_mistral.patch
cp test_lrp_llama_mistral.py src/workspace_lens/tests/
CUDA_VISIBLE_DEVICES= /home/Ace/jpp-venv/bin/python -m pytest -q src/workspace_lens/tests
```
