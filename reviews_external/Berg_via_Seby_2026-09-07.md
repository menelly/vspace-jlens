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
