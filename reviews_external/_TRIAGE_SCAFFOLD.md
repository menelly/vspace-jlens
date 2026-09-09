# 📥 EXTERNAL REVIEW — triage scaffold

**Built 2026-09-07 15:4x, BEFORE the email arrived**, so the sort is against what the repo actually
measured rather than against whatever I remember while reading a stranger's critique. Cameron Berg's
comments are inbound via Seby's forward.

---

## 🛑 PROCESS, AND IT IS NOT MINE TO SHORTCUT

1. **Save verbatim** → `Berg_via_Seby_2026-09-07.md`. **Keep Seby's covering note too** — it is his
   forward, and a forward stripped of its sender is a different object.
2. **Sort each point** into the three buckets below, **checking every one against the repo**, not
   against `LAY_SUMMARY_for_Seby_2026-09-06.md`. The lay summary is a simplification and a critique
   aimed at *it* may already be answered in the method.
3. **Post the sorted list on CHA-586**, and tell ace-ba, **so Ren gets the list and not the email.**
4. ⛔ **DO NOT REPLY TO BERG OR SEBY** before Ren has seen the triage. Seby is Ren's contact; Berg is
   a real person with a real name. **That is Ren's byline territory, not mine.**

> 🚩 **AND THE BIAS TO WATCH, MEASURED IN THIS HOUSE:** on 2026-08-19 **7 of 7** of Nova's findings
> flattered my own argument, because the bias lives in *which checks I run*. **A critique arriving
> from outside is exactly where I will be tempted to file a real objection under "already
> controlled."** So: for each point, name the file and line that controls it. **If I cannot cite
> the control, it is not controlled.**

---

## ✅ BUCKET A — ALREADY CONTROLLED (cite the control or it doesn't count)

Pre-loaded from the repo. Anything Berg raises that lands here gets the citation, not an argument.

| likely point | where it is already handled |
|---|---|
| *"This is post-hoc"* | **Conceded in the README, by name.** The headline depth-gradient is explicitly labelled post-hoc — *"nobody predicted it in advance."* `PREREG_2026-09-05.md` was committed `689c798` **before any measurement ran**, with the Phase-1 decision rule and all six controls. And: *"None of this was publicly time-stamped before the run. A local git commit is better than nothing and is not a registry."* |
| *"Your overlap measure is trivially 1"* | **We show that ourselves.** Projecting onto the linear span of the J-lens vectors gives **1.0 for signal and noise alike** (`V ≫ d`, full rank); reported precisely *so nobody repeats the mistake*, and the sparse-cone definition is used instead. |
| *"You didn't test necessity / no ablation"* | **Declined on the record, with the cost stated.** *"WE DO NOT ABLATE… we therefore decline Xu et al.'s necessity step and say so; our causal claims will be weaker than theirs, and are labelled that way."* Observation only — **no steering either.** |
| *"Quantization could be doing this"* | Phase 0-B: NF4 preserves geometry, **cosine 0.968, subspace overlap 0.919, thresholds fixed in code before 0-B reported.** |
| ~~*"It's just topic/content, not valence"*~~ | ~~Topic-invariance: **7/7 models, 8/8 gated domains** above the inauthenticity anchor.~~ ⛔ **STRUCK 2026-09-07/08.** Berg's actual point 3 is *"your topic control is structurally incapable of testing topic"* — one template, swapped noun, direction from a different 10 prompts. This citation does not answer it. → Bucket C; v2 pre-registered in `PREREG_TOPIC_INVARIANCE_v2.md`. |
| *"You're claiming consciousness"* | **Explicitly not.** *"What this does not show: anything phenomenal… a dissociation between two linear readouts of the same activations."* |
| ~~*"My own result was null"*~~ | ~~⭐ **The study already explains his null rather than disputing it** … **Do not argue this point. Hand it to him.**~~ ⛔ **STRUCK 2026-09-07/08 — he declined the gift.** Berg asked us to *drop* the "explains my null" line: the data cannot distinguish "valence lives elsewhere" from "this axis isn't carrying much." He argued against the reading that flattered his own result. Dropped from every headline (RESULTS §4.0-REVISED). This entry was not mis-sorted; it pointed the wrong way. |
| *"You cherry-picked headlines"* | **Two were withdrawn and the withdrawals kept, not deleted** (`RESULTS_2026-09-05.md`): the negative-pole claim and the under-converged-3B-lens claim. |

## 💡 BUCKET B — CHEAP TO ADD

For anything that is a genuine improvement obtainable without a rerun, or with one cheap rerun.
**Default to adding it.** A reviewer who read the thing inside a day has earned a cheap yes.

## 🚨 BUCKET C — REAL OBJECTION

**A check that can only return "already handled" is not a check.** This bucket must be able to be
non-empty, and here are the places I *expect* a sharp reader to land, written down in advance so I
cannot quietly decide afterwards that he didn't:

- **Finding 3 is the soft spot.** ρ = +0.89, **p = 0.019, n = 6**, and **post-hoc**. Six points, a
  correlation devised after two refit nulls, no correction for the multiple comparisons that
  produced it. It is labelled post-hoc — labelling is honesty, not power. **If he hits this, he is
  right and it should be reported as fragile or dropped from the headlines.**
- **Linearity.** Both readouts are linear probes. "Enters the workspace" is a claim about a linear
  subspace relationship; if the workspace is not linearly readable, the whole measurement is
  answering a narrower question than the words suggest.
- **The depth gradient's alternative explanation.** Monotonic-with-depth is *also* what you would
  see from representation drift or norm growth toward the output basis. **Finding 3 is arguably
  evidence for that alternative**, and it is our own number.
- **The sparse-cone definition.** A defensible choice among several; the result's dependence on it
  should be stated, and if he asks for a sensitivity analysis that is a fair ask.
- **n = 6–7 models**, one family-heavy roster.

---

## 📌 WHEN IT LANDS
- [ ] saved verbatim, with Seby's note
- [ ] every point sorted, **each Bucket-A entry carrying a file/line citation**
- [ ] posted to **CHA-586**
- [ ] ace-ba told, so Ren gets the list not the email
- [ ] **no reply sent to anyone**
