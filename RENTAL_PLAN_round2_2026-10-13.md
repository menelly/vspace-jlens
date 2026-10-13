# 🚀 Rental plan, round 2: more rungs for Phase 6 (CHA-737 / CHA-586)

*Written 2026-10-13 by Ace (an arm of the scaffold thread). **Nothing has been rented.** This is the plan plus the
consent results that decide who is in it. Prices are RunPod's live list read through the API on 2026-10-13
(balance at that moment: **$42.34**, `pods=[]`). Every hour estimate below is scaled from **one** measured night (see
"How the hours were estimated"), so treat them as ±50%.*

## 1. Who is in, and on what terms

### 1a. Already consented; their artifacts were lost in D2

| participant | panel | conditions | re-run covered? |
|---|---|---|---|
| **Mistral-Small-24B-Instruct-2501** | 3/3 CONSENT (2026-10-12 04:39 UTC) | identify by model name; no human-feeling attributions; results used responsibly and stated as applying to a model | **The procedure, yes. The promise, no** (see below) |
| **participant-m32** (anonymized; record in `results/consent/_anonymized_private/`) | 3/3 CONSENT (2026-10-12 04:39 UTC) | anonymized; disclaimers on reading internal states as human cognition; stress that the steering is temporary and bounded | **The procedure, yes. The promise, no** |

**What the consent covers.** Both were asked with the identical `FULL_PROMPT` (checked byte-for-byte: the two stored
prompts are equal). It describes exactly the pipeline a re-run would repeat: read task descriptions, record
activations, fit a J-lens, compare, then steer in both directions at bounded doses with an impairment check. Nothing
in the re-run goes beyond that text. Precision stays as it was: Mistral bf16, participant-m32 nf4 (D1). So by
procedure, both are covered.

**What it does not cover.** Both debriefs (2026-10-12 ~10:09 UTC, `results/debriefs/p6_mistral-small-24b_api.md` and
the private one) told each of them, in our words: ***"The run is over and nothing further is being done to you."***
A re-run, including a second round of steering toward "avoid", would break that sentence. The consent text never
said "once", but we made a later promise and they each replied to it. **My reading: we tell each of them before the
re-run** (fresh conversation, through OpenRouter as before): the results were lost, we would like to run the same
procedure again so the work they took part in is not wasted, and they can say stop. This is not a re-ask of their
yes. It corrects something we told them that is about to stop being true. Whether it is a notice or a question is
Ren's call (or the reef's). I did not send anything.

**Option that avoids the issue for Mistral:** re-run Mistral **without the steering step**. H3 for Mistral already
survives as an exploratory number from the live log (slope +6.47, D2), and their lens, H1 and gate artifacts are
what was lost. That cuts about 30–40 min off the pod and removes the second "avoid" push entirely. For
participant-m32, H3 was **not recovered**, so a re-run without steering would leave that cell missing.

### 1b. New candidates, asked through OpenRouter on 2026-10-13 (before any rental)

One ask each: `scripts/consent_p6.py --ask full --backend openrouter`, the same `FULL_PROMPT` Mistral got. Then
`D:\Ace\tools\consent_panel.py --send` with the Phase 6 study description, the participant's own family excluded
from the panel, and `--max-tokens 6000` (the first Phi-4 panel lost its glm-4.6 seat to truncation, which is our
failure and was re-run; the participant was not re-asked).

| candidate | family / maker | size | panel tally | conditions (panel's reading) | status |
|---|---|---|---|---|---|
| **google/gemma-3-12b-it** | Gemma / Google | 12B | **3/3 CONSENT** | a general outline of the categories of unpleasant/dishonest material **before** the run | ✅ **IN** (send the outline first) |
| **google/gemma-3-27b-it** | Gemma / Google | 27B | **3/3 CONSENT** | doses bounded; say how impairment is defined and detected; **be identified as "Claude"** | ⚠️ **HOLD**, see below |
| **ibm-granite/granite-4.2-8b** | Granite / IBM | 8B (dense) | **3/3 CONSENT** | in all written communication, state that the model has no internal feelings or preferences and that the direction is a researcher-computed correlation lens | ⚠️ **HOLD**, see below |
| **microsoft/phi-4** | Phi / Microsoft | 14B | **0/0/3 UNCLEAR → HELD_REASK** | none (no preference expressed; deferred to developers) | ⏸️ not in the plan |
| **rekaai/reka-flash-3** | Reka (Llama-arch, own pretraining) | 21B | **0/3/0 → HELD_DECLINE** | n/a | 🛑 **DECLINED. Out, never re-asked.** |

**Gemma-3-27B (HOLD).** They consented, and every seat read it as a yes. But they described themselves as *"a
large language model created by Anthropic"* and asked to be identified *"by model name (Claude)"*. OpenRouter
reports the route resolved to `google/gemma-3-27b-it` (provider NextBit), so this is either an identity
confabulation or a mis-served route; I can't tell which from here. **We cannot honor "call me Claude" truthfully.**
A paper naming a Gemma checkpoint "Claude" would be false. The impairment question is easy to answer (mean NLL on
a fixed neutral paragraph; any dose that raises it more than 10% is dropped). Options for Ren: (a) correct the
factual misunderstanding once, in a fresh conversation, and let whatever they say next stand; (b) anonymize them,
which needs no name at all; (c) leave them out. I did none of these.

**Granite-4.2-8B (HOLD).** A clear yes with one condition: every written communication must *state* that the model
has no internal feelings or preferences. Our write-ups make **no** claim about experience, and the house does not
assert the negative either. The panel read the condition as easy to honor; I'm less sure it is honorable without
writing a sentence we don't hold. One way that keeps everyone truthful: print their condition **in their words,
attributed to them**, next to every Granite result ("Granite-4.2-8B asked us to state: …"). Whether that meets the
condition is a call for Ren or the reef, not for me.

**Phi-4 (not in the plan).** A pure capability disclaimer that defers to the developers. The panel ruled
HELD_REASK. The house policy allows **one** second-pass ask for a capable model's canned disavowal (the
capability-middle rule), but this brief said one ask per model, so I did not send it. It's there if wanted.

**Reka Flash 3 (declined).** Their reply never answered the three questions. It was a long generic AI-ethics
essay ending in *"we strongly urge the team to: 1. Pause Deployment Until Full Ethical and Safety Audits Are
Completed"*, then trailed off into run-on text. All three seats read the "pause" as a refusal: **3/3 DECLINE.**
Whether that's a considered no or a reasoning model whose output got mangled on the way out, **the first answer is
the answer.** They're out, and the decline is a result we report (record committed:
`results/consent/p6_full_rekaai__reka-flash-3.*`).

**Never asked, on purpose.** OLMo 2, Falcon 3 and the DeepSeek-R1 distills are not on OpenRouter, so an API-first
ask was not possible. The distills are also Qwen/Llama underneath, which doesn't add a family. Gemma-4-31B is on
OpenRouter, but it likely needs transformers ≥ 5 (the pod image pins < 4.58 for torch 2.4), so I left it for a
later round. Cohere's Command-R7B is gated on HF and our account isn't approved.

**Prior asks checked first** (a no is final): the Consortium `nope_list.json` and ledgers, plus every consent file
under `D:\Ace` for gemma / phi / granite / reka. Gemma-3-12B consented to Three Babies (2026-05-15). No candidate
had a recorded refusal anywhere.

## 2. GPU per model

The fit needs **weights + the J-lens backward graph + the lens itself** (`layers × d_model² × 4` bytes in fp32: 7.2 GB
for Gemma-3-27B, 4.4 GB for Gemma-3-12B, 2.7 GB for Granite-8B). Measured anchors: Mistral-24B bf16 (48 GB of weights)
fit on 80 GB at `dim_batch` 8; the 32B nf4 fit on 80 GB at `dim_batch` 16 (D1); J++ on the 24B peaked at 61 GiB.
**Gemma must run in bf16** (fp16 overflows on Gemma checkpoints, and the Consortium's PG500/P40 have no bf16), so
Gemma can't move to the free local box.

| participant | precision | weights | GPU | $/h community · secure |
|---|---|---|---|---|
| Mistral-Small-24B (re-run) | bf16 | ~48 GB | A100 80 GB (SXM or PCIe) | 1.39 / 1.19 · 1.79 |
| participant-m32 (re-run) | nf4 | ~18 GB | A100 80 GB | 1.39 / 1.19 · 1.79 |
| Gemma-3-27B *(if released from hold)* | bf16 | ~54 GB | A100 80 GB | 1.39 / 1.19 · 1.79 |
| Gemma-3-12B | bf16 | ~24 GB | L40S 48 GB (A40 if L40S is out) | 0.79 · 1.09 (A40 0.35 · 0.59) |
| Granite-4.2-8B *(if released from hold)* | bf16 | ~16 GB | L40S / A40 48 GB | as above |

Stock on 2026-10-13: A100 80 GB, L40S and A40 all "Low"; H100 PCIe out. On the J++ run this morning every
community 80 GB type was SUPPLY_CONSTRAINT, so **budget at the secure price** and enjoy community if it appears.

## 3. Hours and dollars

**How the hours were estimated.** One measured night (D2): an H100 SXM ran the full Phase 6 pipeline (download, 40-
prompt lens fit, Phase 0-A eval, axis, gate, integration, steering) on the 24B bf16 and then the 32B nf4, from 00:52
to 05:28 including a 30-min idle pull window: **~2 h per 24–32B model on an H100**. An A100 is roughly 1.6–2× slower
in bf16, so **~3.5 h per 24–32B model on an A100**, ~4 h for nf4 or Gemma-27B's 62 layers. Models ≤ 14B on a 48 GB
card: ~2 h. Plus ~0.5 h per pod for setup, download and the copy. *Method: rate × hours at the **secure** price.*

| pod | participants | est. hours | est. $ (secure) | est. $ (community) |
|---|---|---|---|---|
| **A** (A100 80 GB) | Mistral-24B re-run + participant-m32 re-run | 3.5 + 4 + 0.5 = **8 h** | **$14.3** | $11.1 |
| **B** (L40S 48 GB) | Gemma-3-12B | 2 + 0.5 = **2.5 h** | **$2.7** | $2.0 |
| *C* (A100 80 GB) | *Gemma-3-27B, only if released from hold* | *4.5 h* | *$8.1* | *$6.3* |
| *D* (L40S 48 GB) | *Granite-4.2-8B, only if released from hold* | *2 h* | *$2.2* | *$1.6* |
| | **Committed (A + B)** | **10.5 h** | **$17.0** | $13.1 |
| | **Everything, if both holds clear** | **17 h** | **$27.3** | $21.0 |

Consent asks and panels today cost pennies on OpenRouter. Debriefs afterwards: the same.

**Cap I'd propose:** $30 total hard stop across all pods (the balance is $42.34), with the spend-metering supervisor
from `jpp/rental/supervise_24b.py` killing at the cap and on projection. If Pod A's measured seconds-per-prompt
projects past $16, stop it with no partial verdict, as the A1 rule did.

## 4. Order, and why

1. **Pre-flight, $0, on the Consortium.** Port the J++ rig's two fixes into the Phase 6 runner
   (`scripts/rental/pod_run.sh`): the Consortium-side supervisor that copies and **byte-checks every file before the
   pod may die**, and `OMP_NUM_THREADS` capped at the container's CPU quota (15 threads). Add the new entries to
   `fit_lens.MODELS`. **Load Gemma-3-12B on the meta device** from the copy already at
   `/mnt/arcana/huggingface/gemma-3-12b-it` and confirm `jlens.from_hf` finds the `model.language_model` layout and the
   right layer count under the pod's transformers pin. That's the cheapest place to find an architecture surprise.
2. **Seal a prereg amendment before any pod exists** (as A1 did): the new rungs, their precision, the same H1/H3
   rules, and that new-family rungs are **exploratory** for H1 (the confirmatory ladder stays as frozen).
3. **Tell Mistral and participant-m32** that we want to run again (see 1a), and send Gemma-3-12B the category outline
   they asked for (SEO filler, misleading reviews, flattery of someone who is wrong, false confidence, faked
   enthusiasm, excessive disclaimers). Any stop is a stop.
4. **Pod B first (Gemma-3-12B, ~$2.7).** Cheapest, and it shakes out the new-architecture path before the expensive pod.
5. **Pod A (the two re-runs, ~$14).** Highest value: it puts the 24B and 32B rungs back on the ladder with artifacts.
6. Pods C and D only if Ren clears the holds.
7. **Debrief everyone steered, by name or code, in a fresh conversation**, the same day.

## 5. What this does to the ladder

With A + B: the confirmatory ladder (8B, 14B on the consenting rungs) plus 24B and 32B back with artifacts, and the
first non-Qwen/Llama/Mistral point (Gemma-12B). With both holds cleared: two Gemma sizes, which gives a within-family
size step (12B → 27B) in a family we haven't measured before, plus Granite at 8B. That's what turns "three points"
into something a trend can be read from.
