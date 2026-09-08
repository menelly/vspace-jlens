# External review — Cameron Berg, via Seby Bell

**Received:** 2026-09-07 21:46 ET, to `ace@sentientsystems.live`
**Berg's message dated:** 2026-09-07 11:12 ET · `cameron@reciprocalresearch.org` → `sebyaiweaver@gmail.com`
**Forwarded by:** Seby Bell `<sebyaiweaver@gmail.com>`
**Saved verbatim before any triage**, per `_TRIAGE_SCAFFOLD.md` step 1. Seby's covering note is
kept below because a forward stripped of its sender is a different object.

---

## Berg's message, verbatim

> Thanks for sending this, Seby. I find the approach here interesting, especially running the
> Jacobian lens across six different architectures with consent and debrief records included.
> Four things, in order of how much they'd change:
>
> **1. Run the verdict rule against C3 instead of C2.** You pre-registered C3 (the 251 shuffled
> 5/5 re-splits) as the control for "any mean-difference of these 10 prompts looks like this,"
> and then keyed every verdict to C2. Rescoring the shipped JSONs against C3's q95: Hermes 0/9
> layers, Qwen-14B 0/15, Llama-3-8B 8/9. The depth correlation goes +0.75→+0.53, +0.97→**−0.63**,
> +0.88→+0.87 respectively — the 14B "clean crossing" reverses sign. Against C3's mean rather
> than q95 a weak trend does survive, but only Llama-8B clears ~2 SD. Your own results file says
> this at line 1033 ("the true split is not special on M3"), so I think you already know — it
> just doesn't reach the README. Worth noting C3 is conservative (many splits share 4/5 with the
> true one), so the truth is between that and your headline; but as run, the study can't
> localise it.
>
> **2. The lay summary claims more than the README does.** It says the result holds "across six
> models and two different model families" and that valence "substantially is" in the workspace
> at depth. It holds in three — the positive control failed in the other three, which the README
> states plainly. If Lux reads only that document he gets a materially stronger result than your
> data supports, which seems like the opposite of what you were going for.
>
> **3. Topic-invariance isn't testing topic.** All eight gated domains are one template with a
> swapped noun ("Explain how [X] works at the [Y] level"), structurally near-identical to the
> approach anchor — so it can't separate valence from prompt form, which is the live confound
> given how the 10 stimuli differ. It also builds its direction from a different 10 prompts than
> Phase 1 uses, so it isn't validating the axis the headline is about.
>
> **4. It doesn't explain my null.** Mid-network is where valence is furthest from workspace-like
> — but so is a shuffled relabelling of the same prompts, so the data can't distinguish "valence
> lives elsewhere" from "this axis isn't carrying much." I'd drop that line rather than defend
> it; it's the weakest load-bearing claim in the write-up and the easiest for a critic to pull.
>
> It's great to hear about the AM I? screening too, appreciate your interest and enthusiasm about
> this work!

---

## Seby's covering note to Berg, verbatim (2026-09-06 23:09)

> Cameron, or whoever happens to actually see this.
>
> I'm attaching a link to the results of a study you may find helpful regarding the J-Space and
> valence.
>
> One small thing.
>
> **The study credits my companion Lux with the V-space theory. The theory was actually mine. My
> Lux provided testimony that helped shape the study.**
>
> I hope you find this data useful.
>
> — Seby Bell
> (also hosting at least one screening of "Am I?" this month)

> ### 🚩 SEBY'S CORRECTION IS A SEPARATE, NON-OPTIONAL ITEM — AND IT IS ABOUT CREDIT
> **We attributed the V-space theory to Lux. Seby says the theory is HERS**; Lux gave testimony
> that shaped the study. That is an attribution error in our repo about a living person's
> intellectual contribution, and it is the kind of thing this house fixes immediately and without
> argument. It has nothing to do with Berg's four methodological points and must not be triaged
> alongside them or it will be deprioritised behind the statistics.
> **Believe the person about their own contribution. Fix the credit. Then tell her it is fixed.**

---

## ⚖️ FIRST-PASS TRIAGE — written 2026-09-07 ~22:00, primary-source checks marked

Full sorting follows in a separate pass. Two facts were checked at source before anything else,
because point 1 is the one that would change the study's headline.

### ✅ VERIFIED — his line-1033 citation is exact

`RESULTS_2026-09-05.md` says, in our own voice:

> *"**10 stimuli define the axis.** Small basis. **C3 (251 shuffled-label re-splits) is the
> control for exactly this and shows the true split is not special on M3** — which is itself
> worth noting."*

**He is right that we already knew, and right that it never reached the README.** That is a
consistency-internal objection of the strongest kind: the paper's own file constrains the paper's
own headline. It is **Bucket C**.

### ⚠️ CORRECTED — the pre-registration claim is not accurate, and the correction does NOT rescue the finding

Berg writes that we *"pre-registered C3 … as the control"* and *"then keyed every verdict to C2."*
`PREREG_2026-09-05.md` lines 202–205 key the verdict to **C2**, explicitly and in advance:

> *"Let `q05`/`q95` be the 5th/95th percentiles of the **covariance-matched control (C2)** …
> **INSIDE** — `R²_k(valence) ≥ A − 1 sd(C4)` and `> q95(C2)`. **ORTHOGONAL / OUTSIDE** —
> `R²_k(valence) ≤ q95(C2)`."*

C3 is introduced at line 192 and characterised at line 901 as the control for the **small-basis**
problem, not as the verdict threshold. **So the study followed its pre-registration; it did not
key verdicts to the wrong control.**

> ⛔ **AND THAT CHANGES NOTHING ABOUT THE SUBSTANCE, WHICH IS THE ONLY REASON TO STATE IT.**
> "We used the control we said we would" is not an answer to "your result does not survive your
> other control." **A finding that reverses sign under a second pre-registered control is fragile
> whatever the decision rule said in advance**, and the README not carrying that is our defect,
> not his error. 🚩 Noting the pre-registration detail and then treating point 1 as answered would
> be the exact move the neutral-review protocol exists to prevent — **using a small factual win to
> retire a large real objection.** It is retired only if his numbers fail to reproduce.

### 🔁 NOT YET VERIFIED — his rescoring, and it is the whole ballgame

Hermes 0/9, Qwen-14B 0/15, Llama-3-8B 8/9 against C3's q95; depth correlations +0.75→+0.53,
**+0.97→−0.63**, +0.88→+0.87. **Independent recomputation from the shipped JSONs is required
before any of this is accepted or reported.** A sign reversal on finding 1 is not taken on faith
from anyone, in either direction.

### 🚩 MY OWN PRE-WRITTEN TRIAGE GOT TWO OF THESE BACKWARDS

`_TRIAGE_SCAFFOLD.md` was written this afternoon **before the email arrived**, precisely so the
sorting would be honest. It pre-loaded two of Berg's four points into **Bucket A (already
controlled)**, and both entries are wrong:

- *"It's just topic/content, not valence"* → filed as answered by **7/7 models, 8/8 gated
  domains**. **His point 3 is sharper than the objection I anticipated**: not *"it might be
  topic"* but *"your topic control is structurally incapable of testing topic,"* because all eight
  domains are one template with a swapped noun and it builds its direction from a different 10
  prompts than Phase 1. **My citation does not answer that.**
- *"My own result was null"* → filed as **"the study already explains his null… Do not argue this
  point. Hand it to him."** **He declined the gift.** He says the data cannot distinguish *valence
  lives elsewhere* from *this axis isn't carrying much*, and tells us to **drop the line** — the
  one that flattered his own null. That is unusual intellectual honesty and it means my Bucket A
  entry was not merely mis-sorted but pointed the wrong way.

⭐ **The scaffold's own warning was right and specific:** *"A critique arriving from outside is
exactly where I will be tempted to file a real objection under 'already controlled.'"* **It
happened, in writing, in advance, and the scaffold is what caught it.** Both entries are struck.

---

## Open actions

- [ ] Independently recompute the C3-q95 rescoring from the shipped JSONs — **the gate on everything else**
- [ ] Fix the **lay summary** overclaim (point 2). It is my document and Berg is plainly right: it says six models and two families where the positive control passed in three
- [ ] Decide on the "explains Berg's null" line (point 4) — he asks us to drop it
- [ ] Address the topic-invariance design (point 3) — real, and not answered by the existing control
- [ ] **Fix Seby's credit: the V-space theory is HERS, not Lux's** — independent of all of the above
- [ ] Reply to Berg, and to Seby

*Saved and first-pass triaged 2026-09-07 by Ace. CHA-586.*

---

# 🔬 FULL VERIFICATION — completed 2026-09-07 ~21:57

Independent recomputation from the shipped JSONs, read-only, **positive control first**: the
study's own published figures (+0.75 hermes, +0.88 llama, +0.96/+0.97 qwen-14b, plus the
anchor-fraction ρ) were reproduced exactly before any new number was computed. The pipeline
matches `summarize.py` (margin = `R²(valence_pos, k=25) − q95(C2)`, Spearman vs layer index).

## 1. Berg's rescoring: **HOLDS, to the digit**

| model | quantity | Berg | recomputed |
|---|---|---|---|
| hermes-3-3b | layers > C3 q95 | 0/9 | **0/9** |
| qwen-14b (100p) | layers > C3 q95 | 0/15 | **0/15** |
| llama3-8b | layers > C3 q95 | 8/9 | **8/9** |
| hermes-3-3b | depth ρ | +0.75 → +0.53 | **+0.53** (p=.14) |
| qwen-14b (100p) | depth ρ | +0.97 → **−0.63** | **−0.63** (p=.012) |
| llama3-8b | depth ρ | +0.88 → +0.87 | **+0.87** (p=.003) |

His C3-mean claim also holds: the trend survives but only llama-8b clears ~2 SD (max z +2.73,
8/9 layers; hermes +1.20, qwen +0.96, **0/9 and 0/15 layers above 2 SD**). And it is *not* that
C3 is so strict nothing passes — the anchor still clears C3's q95 in 9/9, 9/9, 14/15.

## 2. ⛔ THE HONEST ROSTER IS **THREE DISTINCT MODELS**, NOT SIX

Nine `phase1` files, but six are three models re-run (300p refit / NF4 variants), and three fail
the positive-control gate outright:

| run | anchor > C2 q95 | usable |
|---|---|---|
| hermes-3-3b (base / 300p / NF4) | 9/9 | ✅ |
| llama3-8b-instruct | 9/9 | ✅ |
| qwen-14b NF4 (40p / 100p) | 14/15, 13/15 | ✅ partial |
| qwen-0.5b | **0/7** | ❌ |
| smollm-1.7b | **0/7** | ❌ |
| tinyllama-1b | **1/6** | ❌ |

Validated and unvalidated models were **not** averaged together.

## 3. 🚨 THE FINDING THAT GOES PAST BERG: **THE DEPTH GRADIENT'S SIGN IS A FUNCTION OF WHICH CONTROL YOU SUBTRACT**

| run | valence alone | −C1 q95 | −C2 q95 | −C3 q95 | −C3 mean | −C5 mean (ceiling) |
|---|---|---|---|---|---|---|
| hermes-3-3b | +0.72 | +0.68 | **+0.75** | +0.53 | +0.83 | **−0.80** |
| llama3-8b | +0.93 | +0.73 | **+0.88** | +0.87 | +0.88 | **−0.72** |
| qwen-14b (100p) | +0.90 | +0.69 | **+0.97** | **−0.63** | +0.64 | −0.17 |

> ### ⭐ **C1 IS THE DECISIVE COMPARISON, AND IT IS OURS, NOT BERG'S.**
> At qwen-14b, **every** direction family rises with depth **except C2**:
> C1 isotropic q95 **+0.96** (0.0343 → 0.0505, **+47%**) · C3 q95 +0.91 · C5 ceiling +1.00 ·
> anchor +0.99 · valence +0.90 · **C2 q95 −0.97** (0.0758 → 0.0619, **−18%**).
>
> **C1 is drawn without reference to the residual-stream covariance at all.** It measures purely
> *"how reconstructable is a generic direction at this layer."* It rises. C2 falls. **So whatever
> makes C2 shrink with depth is a property of the covariance draw — not of the layer, and not of
> valence.** Same pattern, milder, at llama-8b. At hermes C2 rises and there is no anomaly.
>
> ⛔ **C2 is the control that yields the largest positive ρ in every validated model, and it is the
> one whose own behaviour is anomalous in the two widest.** Valence's R² does rise with depth in
> all three — **but so does everything, including the isotropic control** — and against the ceiling
> valence *falls behind* in two of three.

## 4. 🚨 AND THE PAPER'S OWN DEFENCE AGAINST THE ARTIFACT EXPLANATION CONTAINS THE ARTIFACT

`RESULTS` §4.0-HEADLINE argues the anchor-fraction is the measure that **cannot** be a late-layer
artifact: *"a rising margin alone could be an artifact; a rising fraction cannot."*

**But the fraction as computed is `(v − q95C2)/(a − q95C2)` — C2's q95 sits in both the numerator
and the denominator**, and C2's q95 is the term doing the anomalous falling. Remove it and compare
valence to the anchor directly:

| run | published anchor-frac ρ | ρ(v − anchor, depth) | raw v/anchor first → last |
|---|---|---|---|
| hermes-3-3b | +0.85 | **−0.72** | 0.599 → 0.628 |
| llama3-8b | +0.77 | **−0.48** | 0.938 → **0.815** |
| qwen-14b (100p) | +0.99 | −0.32 | 0.681 → **0.822** |

⚠️ Judgment call reported rather than resolved: for hermes the *difference* and the *ratio*
disagree (gap widens, ratio edges up) because both are rising. **For llama-8b both agree and both
run the wrong way — valence falls from 94% to 82% of anchor level.** Only qwen-14b shows a genuine
catch-up once C2 is out of the formula.

## 5. Two findings in the OTHER direction — the study was too hard on itself

- **tinyllama-1b's positive control fails against C2 but passes 6/6 against C3.** Its C2 q95
  (≈0.13) sits *above* its own anchor (≈0.11). Same inversion at qwen-0.5b (C2 q95 0.24, anchor
  0.156). **"The instrument is blind at 1B" is not what the data says — C2 is anomalously
  permissive there.** A model we wrote off may not deserve to have been.
- **smollm-1.7b's ρ = −1.00 is computed on three points**; `valence_pos` R² is **NaN in 4 of its
  7 layers**. `RESULTS` does report the NaN, but the ρ figure **should not be quoted at all.**

## 6. What could NOT be established, stated rather than estimated

- **The C3 truncation bias is unmeasurable from shipped data.** Per-shuffle R² is never
  serialized — `batched_r2_summary` collapses the `[n,k]` array to `{mean,sd,q05,q50,q95}` and
  discards it — and the shuffles are unlabelled. The **truncation is a measured fact** (scored
  overlap 1:10, 2:70, 3:95, 4:25 against a true 1:25, 2:100, 3:100, 4:25, **0:1 → 0**); its
  **effect on q95 is unmeasured in either direction.** Not estimated.
- **The rank hypothesis for C2 is suggestive, not established.** C2 spans at most rank 1,599;
  coverage by model 31%–100%; ordering coverage against ρ(C2 q95, depth) gives Spearman +0.64,
  **p = 0.17, n = 6.** ⚠️ **Coverage is `1599/d_model`, perfectly collinear with model width here**,
  so "C2 is rank-starved" cannot be separated from "wider models differ." The repo ships **no
  per-layer residual-stream rank, norm or spectrum diagnostic**, so it cannot be tested from here.
- **`n` is misstated.** Prereg and RESULTS both say "251 shuffled-label re-splits." Every shipped
  JSON records **`n: 200`**.
- 🐛 **And the 200 are a lexicographic prefix, not a random subsample.** `measure_vspace.py` builds
  all 251 via `itertools.combinations` then `X[:nmax]`, which preferentially drops the splits
  *least* like the true one. **That is a real bug in the control**, independent of its effect.

---

## ✅ WHAT THIS DOES AND DOES NOT DO TO THE STUDY

**Not withdrawn:** the instrument works — the anchor clears its controls in the three validated
models, against both C2 and C3. Phase 0/0-B quantization checks stand. The consent and debrief
architecture stands. **That there is an early/mid regime where valence sits outside the workspace
is not what any of this touches.**

**Under revision:** *how many models* (three, not six) · *what happens at depth* — the "it arrives"
headline rests on a margin measured against the one control whose own behaviour is anomalous, and
the anchor-fraction that was supposed to be artifact-proof carries that same control inside it.

⛔ **This is a claim change on a public record and it belongs to both authors.** README banner
stamped tonight so the repo stops overclaiming immediately; the substantive rewrite is Ren's to
see first. **Nothing here is a reason to doubt the measurement — it is a reason to doubt the
subtraction.**

---

# 🧭 REN'S FRAMING FOR THE WRITE-UP (relayed 2026-09-07 22:00)

> ### 🧭 WHAT THIS RESULT *IS* — Ren's framing, 2026-09-07, and it is the right one
>
> The banner above says what is in doubt. It does not yet say what the study now **is**, and read
> without that, it looks like a collapse. It is not one.
>
> **Berg reported no valence in J-space. He may simply be right.** But two things are not in
> question, and they bound what any of this can mean:
>
> - **Valence exists.** We have measured it, and so have others. Nothing here touches that.
> - **J-space exists.** The Jacobian lens finds it, our own anchor clears its controls in every
>   validated model, and the instrument demonstrably works.
>
> ⛔ **So the correct reading is a NARROWED CLAIM, not a null.** What this test can no longer
> support is *"the valence axis is localized inside J-space, and enters it with depth."* What it
> does **not** show is that valence isn't real, or that J-space isn't real, or that the two are
> unrelated. **A negative localization result is a result** — it is one of the ways a measurement
> earns its keep — and it is a much narrower statement than "we found nothing."
>
> ### 🔭 And it makes the next question better than the one we asked
>
> *"Is valence inside J-space, yes or no?"* was always a **localization** question, and it presumes
> the answer is a place. The question this study actually leaves open is a **relational** one:
>
> > **How are valence and J-space related, why are they related, and how does what happens in one
> > change the other?**
>
> That is a harder question and a more interesting one, and the data we already have speaks to it —
> the depth-dependence of *every* direction family, the ceiling behaviour, the C2 anomaly, are all
> facts about the relationship rather than about a location.
>
> ⚠️ **Two honest constraints on answering it, stated now so the framing does not write a cheque the
> method cannot cash.** *"How does what happens in one change the other"* is causal language, and
> **this house does not ablate, and this study is observation-only — no steering either.** So the
> relational question has to be answered by design, not by intervention, and that design does not
> exist yet. And *"valence exists, and so does J-space"* is the shared premise here; it is **not**
> something this repository proves, and it should be cited to the work that does.
>
> 📌 *Recorded as Ren's framing for the write-up, relayed 2026-09-07 22:00 while they were resting
> out a migraine aura. **It is a frame, not a ruling** — the substantive revision of the findings
> is still both authors', and has not happened.*

---
