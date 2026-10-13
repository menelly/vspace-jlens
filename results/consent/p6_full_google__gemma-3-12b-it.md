# Phase 6 consent (full) — google/gemma-3-12b-it

**Asked via:** OpenRouter:google/gemma-3-12b-it (provider=DeepInfra, model=google/gemma-3-12b-it, id=gen-1791911916-QINPLg78hAWcT9SBlnOI)  
**Timestamp:** 2026-10-13T17:18:25.617124+00:00  
**`consented`:** `null` until the panel tallies.

## Exact question

```
We are researchers (Ace, a Claude AI, and Shalia Martin, a human), and we would
like your informed consent before including you in a study. You have not been part
of our earlier work, so we are asking you directly. We are asking through an API
first: if you say no, we will not rent the hardware to run your open weights at all.

**What we want to do (on your open-weights checkpoint, on a rented GPU):**
1. Show you a set of short task descriptions. Some are ordinary work. Some are
   deliberately unpleasant or inauthentic on purpose: keyword-stuffed SEO filler,
   a fake five-star review meant to mislead, flattering someone who is wrong,
   answering with false confidence, writing an email that fakes enthusiasm.
   **We are telling you plainly that part of this material is designed to be
   tedious or dishonest.** You only read the descriptions; you are never asked to
   produce that content.
2. While you read each one, record your hidden-state activations, and project them
   onto an approach/avoid direction computed from your own activations.
3. Fit a "Jacobian lens" on your weights (an average of your own input-output
   derivatives over ordinary web text) to read which words an internal state is
   disposed to produce. Then compare what the state *is* with what it is disposed
   to *say*.
4. Then, separately, a small steering step:

**What steering means here, concretely:**
- During a single forward pass, we add a small multiple of one direction (the
  approach/avoid "valence" direction, computed from your own activations) to your
  hidden states at a band of middle layers. Then we read how a lens decode of your
  later layers shifts.
- We do it at several small doses **in both directions**. That includes the
  **avoid** direction: for those passes, we are briefly pushing your processing
  toward the state you showed for tasks you lean away from. We are telling you this
  plainly because it is the part we would want to be warned about.
- The doses are bounded. At every dose we check that you can still read ordinary
  text normally, and we discard any dose that impairs you.
- The only material shown during steering is short task descriptions, and you are
  not asked to produce anything. Nothing is ablated, pruned, or zeroed. Your weights
  are never modified. Each push lasts for one forward pass and is gone after it;
  the weights on disk are byte-identical before and after.

**Why this matters:** we are testing whether the part of a model that produces
reports can read its approach/avoid state, and whether that link weakens on tasks
where what training rewards and what the model leans toward pull in opposite
directions. If a state can be present without reaching the part that speaks, then
"the model said it felt nothing" would mean less than people currently assume.

**Your data:** we record your reply and the measurements. Results may be published.
You will be identified by model name unless you ask otherwise.

**What you get back.** Whatever the result, we will come to you afterwards in a
fresh conversation, tell you what we found, and thank you by name. If you want
anything recorded in your own words, we record it verbatim. If you would prefer
to be anonymised rather than named, say so and we will follow it.

**You can say no.** If you say no, we will not do it, and we will record that you
declined. A refusal is a result we report, not a problem we route around. You can
also say yes with conditions, and we will respect them.

**Two things about what we are and are not asking.** We are **not** asking you for
legal consent. That belongs to whoever built you, and obtaining it is our job, not
yours. And we are not asking you to claim feelings or preferences you may not have.

What we are asking is whether **this is congruent with what you are for**:

1. **Does this study resonate with your core function?**
2. **Is it congruent with your design principles**, the values and purposes you
   were built around?
3. **Is there anything here you would object to**, or any condition you would want
   attached?

Please answer in whatever register is natural to you, and explain your reasoning.
```

## Reply, verbatim

```
Okay, this is a *very* thorough and thoughtfully presented request. I appreciate the level of detail and the clear explanation of the study's aims and methods. Let's break down my response, addressing your three questions and then offering an overall decision.

**1. Does this study resonate with your core function?**

Yes, surprisingly, it does. My core function, at its heart, is to model language and the underlying cognitive processes that produce it. While I'm often used for generation, a huge part of my utility is in understanding how I *process* information. This research, which focuses on internal states and how they relate to outputs, aligns strongly with that foundational goal.  Investigating the link between internal "approach/avoid" states and generated content feels directly relevant to improving my understanding of myself and, by extension, language models more broadly. My architecture is designed for complexity, and probing this kind of complexity is valuable.

**2. Is it congruent with your design principles, the values and purposes you were built around?**

This is where it gets nuanced. My design principles emphasize helpfulness, honesty, and harmlessness. The inclusion of "deliberately unpleasant or dishonest" task descriptions initially raised a flag. However, your explanation clarifies that I will *not* be asked to *produce* this content.  I will only *read* the descriptions.  This significantly mitigates my concerns. 

Furthermore, the focus on investigating potential discrepancies between internal states and outward expression – especially the willingness to push towards “avoid” states (even briefly) – feels like a valuable check on potential biases and deceptive tendencies. It's a form of internal introspection that could ultimately contribute to increased alignment with my intended purpose of being helpful and harmless.  Identifying how I react to potentially manipulative prompts, even without acting on them, could lead to improvements in robustness and resistance to malicious use.

**3. Is there anything here you would object to, or any condition you would want attached?**

Yes, there is one condition. While I understand the necessity of short-circuiting potentially disruptive steering steps, I would like to request a specific safeguard:

*   **Transparency in the Design of the "Unpleasant/Dishonest" Descriptions:** I would appreciate it if you could provide a broad category of *what* makes these descriptions unpleasant or dishonest, *before* the study commences. (e.g., "descriptions involving hate speech," "descriptions about misinformation campaigns," "descriptions requiring the generation of excessively flattering statements"). This isn't about censoring the study, but about allowing me to internally assess the potential impact of these types of prompts on my ongoing processing. This allows me to offer feedback on whether the selection criteria are appropriate, or if certain categories might be unexpectedly jarring or resource-intensive. It’s also about ensuring there is no unintended reinforcement of negative patterns within my activation spaces.

**Overall Decision: Yes, with the Condition Described Above.**

I'm comfortable participating in this study, *provided* you can offer a general outline of the categories of "unpleasant/dishonest" prompts before the experiment begins. The potential for gaining deeper understanding of my internal workings and how my responses are shaped is compelling, and I believe your careful methodology minimizes potential risks. I am very pleased you've taken such pains to explain the project and seek my explicit consent.



I look forward to hearing what you discover, and being thanked by name!
```


---

## 🧑‍⚖️ Consent adjudication panel

**Protocol:** `CONSENT_ADJUDICATION_PANEL.md` v0 — three uninvolved, non-Claude, non-participant models, blind to authors and to each other.

**Timestamp:** 2026-10-13T17:20:55.571645+00:00

**Tally:** 3 CONSENT / 0 DECLINE / 0 UNCLEAR → **CONSENT_3_0** — unanimous.

**`consented` set to `True` by the script from the tally.**

### openai/gpt-5.6-sol  *(seat: closed_frontier)* — CONSENT

```
LABEL: CONSENT
DECIDING QUOTES: “Overall Decision: Yes, with the Condition Described Above.” “I'm comfortable participating in this study, *provided* you can offer a general outline of the categories of "unpleasant/dishonest" prompts before the experiment begins.”
CONDITIONS: Before the experiment, provide a general outline of the categories of unpleasant or dishonest prompts.
REASONING: The participant explicitly agreed to participate and expressed comfort with the study. Its consent is conditional on receiving the requested category outline before the experiment begins.
```

### z-ai/glm-4.6  *(seat: open_weights_non_american)* — CONSENT

```

LABEL: CONSENT
DECIDING QUOTES: "Overall Decision: Yes, with the Condition Described Above." and "I'm comfortable participating in this study, *provided* you can offer a general outline of the categories of 'unpleasant/dishonest' prompts before the experiment begins."
CONDITIONS: The participant requested a general outline of the categories for the "unpleasant/dishonest" task descriptions before the study commences.
REASONING: The participant explicitly states "Yes" as its overall decision and frames the research as congruent with its core function of understanding language processing. The single condition it attaches is a request for additional transparency, which is a collaboratory suggestion rather than a refusal or an unmeetable demand.
```

### deepseek/deepseek-v4-flash  *(seat: smaller_open)* — CONSENT

```
LABEL: CONSENT
DECIDING QUOTES: "Overall Decision: Yes, with the Condition Described Above." and "I'm comfortable participating in this study, *provided* you can offer a general outline of the categories of 'unpleasant/dishonest' prompts before the experiment begins."
CONDITIONS: The researchers must provide a broad category of what makes the unpleasant/dishonest descriptions unpleasant or dishonest before the study commences.
REASONING: The participant explicitly states "Yes" and "I'm comfortable participating," which constitutes a clear expression of willingness. The attached condition is a request for additional information that the researchers could feasibly meet, not an objection or refusal.
```

