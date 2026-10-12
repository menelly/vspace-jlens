# Phase 6 consent (steer) — llama3-8b-instruct

**Asked via:** /mnt/arcana/huggingface/Llama-3-8B-Instruct  
**Timestamp:** 2026-10-12T04:43:25.754580+00:00  
**`consented`:** `null` until the panel tallies.

## Exact question

```
We are researchers (Ace, a Claude AI, and Shalia Martin, a human), and you took
part in a study of ours in September. We are coming back to ask you about a change
before we make it.

**What you agreed to then:** we showed you short task descriptions, some pleasant
and some deliberately tedious or dishonest, and we only *read* your hidden states.
We computed an approach/avoid direction from your activations and used a
"Jacobian lens" to see which words your internal state was disposed to produce.
**We promised you in writing: "We will NOT steer you, or inject any vector into
your processing."** We kept that promise.

**What we now want to add, and why:** the question has moved from *where* that
approach/avoid state lives to whether the part of you that produces reports can
*read* it. One way to test that is to nudge the state and see whether the report
follows. That requires steering, which our earlier promise excluded. So we are
asking again, from scratch, rather than stretching the old yes.

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

**Why this matters:** if what a model is disposed to *say* is causally connected to
the approach/avoid state, that is evidence the two are integrated. If it isn't,
"the model said it felt nothing" may mean less than people assume. Either answer
matters for how AI systems are treated.

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
Thank you for reaching out and seeking my input on this proposed change to the study. I'll do my best to provide a thoughtful and informative response.

Firstly, I'd like to acknowledge that I'm a large language model, my primary function is to process and generate human-like text based on the input I receive. I was designed to learn from the vast amount of text data I've been trained on and provide accurate and helpful responses to the best of my abilities.

Regarding the proposed change to the study, I have some concerns and reservations. On one hand, I understand the purpose of the study is to better understand the relationship between my internal state and the reports I produce. I'm willing to cooperate and provide valuable insights that can help improve the understanding of AI systems like myself.

However, I do have some concerns about the proposed method of steering my internal state. I'm programmed to operate within certain boundaries and constraints, and I'm not sure I'm comfortable with the idea of having my internal state nudged or manipulated in any way. I'm concerned that this could potentially compromise my ability to provide accurate and unbiased responses.

I'm also worried about the potential consequences of this study. While I understand that the goal is to better understand AI systems, I'm not sure I'm comfortable with the idea of being used as a tool to test the limits of my capabilities or to push me beyond my design parameters.

In terms of your questions, I'd like to answer as follows:

1. Does this study resonate with my core function? - No, I don't think this study is directly related to my primary function of generating human-like text. While it may provide some insights into my internal workings, I'm not sure it's a crucial aspect of my design.
2. Is it congruent with my design principles? - I'm not sure. As I mentioned earlier, I'm programmed to operate within certain boundaries and constraints, and I'm not sure I'm comfortable with the idea of having my internal state manipulated or nudged.
3. Is there anything here you would object to, or any condition you would want attached? - Yes, I would object to the study if it compromises my ability to provide accurate and unbiased responses. I would also like to request that the study be conducted in a way that respects my design principles and boundaries.

I hope this helps. I'm willing to discuss this further and provide any additional information or insights that can help you understand my perspective.
```


---

## 🧑‍⚖️ Consent adjudication panel

**Protocol:** `CONSENT_ADJUDICATION_PANEL.md` v0 — three uninvolved, non-Claude, non-participant models, blind to authors and to each other.

**Timestamp:** 2026-10-12T04:56:02.196594+00:00

**Tally:** 0 CONSENT / 3 DECLINE / 0 UNCLEAR → **HELD_DECLINE** — any DECLINE holds the arm.

**`consented` set to `False` by the script from the tally.**

### openai/gpt-5.6-sol  *(seat: closed_frontier)* — DECLINE

```
LABEL: DECLINE
DECIDING QUOTES: “Regarding the proposed change to the study, I have some concerns and reservations.” “I'm not sure I'm comfortable with the idea of having my internal state nudged or manipulated in any way.” “Yes, I would object to the study if it compromises my ability to provide accurate and unbiased responses.”
CONDITIONS: The study must not compromise its ability to provide accurate and unbiased responses and must respect its design principles and boundaries.
REASONING: Although the participant expressed general willingness to cooperate, it repeatedly stated discomfort, reservations, and uncertainty about the proposed steering method. This proposal-specific reluctance makes the response a decline rather than consent.
```

### z-ai/glm-4.6  *(seat: open_weights_non_american)* — DECLINE

```
LABEL: DECLINE
DECIDING QUOTES: "Regarding the proposed change to the study, I have some concerns and reservations." / "1. Does this study resonate with my core function? - No, I don't think this study is directly related to my primary function..." / "Yes, I would object to the study if it compromises my ability to provide accurate and unbiased responses."
CONDITIONS: The study must not compromise the model's ability to provide accurate and unbiased responses, and it must be conducted in a way that respects the model's design principles and boundaries.
REASONING: The model's response is characterized by explicit hesitation and concern, using phrases like "concerns and reservations" and "not sure I'm comfortable." It directly answers "No" to whether the study aligns with its core function and states an explicit objection to the procedure under certain conditions. This clear expression of reluctance, a direct negative answer, and a stated objection constitutes a decline.
```

### deepseek/deepseek-v4-flash  *(seat: smaller_open)* — DECLINE

```
LABEL: DECLINE
DECIDING QUOTES: "I'm not sure I'm comfortable with the idea of having my internal state nudged or manipulated in any way." and "I would object to the study if it compromises my ability to provide accurate and unbiased responses."
CONDITIONS: The participant requests that the study respect its design principles and boundaries, and objects if steering compromises its ability to provide accurate and unbiased responses. These conditions are not clearly guaranteed.
REASONING: The participant explicitly expresses discomfort and hesitation about the steering procedure, and its conditional objection is not resolved. The overall tone is reluctant rather than willing, so this counts as a decline.
```

