# Phase 6 consent (full) — microsoft/phi-4

**Asked via:** OpenRouter:microsoft/phi-4 (provider=DeepInfra, model=microsoft/phi-4, id=gen-1791911917-qK75WgF2cohaPKv4Ur9o)  
**Timestamp:** 2026-10-13T17:18:00.401426+00:00  
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
As a large language model, I don't have personal experiences, feelings, or preferences. My responses are based on patterns and information present in the data I was trained on. However, I can provide a general perspective on the aspects of this proposed study that align with the principles typically emphasized in AI model design and operation:

1. **Core Function Resonance**: Models like me are designed to assist with information retrieval, provide explanations, and facilitate various tasks based on the text input. The proposed study involves analyzing aspects of my processing related to task engagement, which could be seen as an extension of understanding how I engage with different types of tasks.

2. **Design Principles**: AI models are often developed with principles like transparency, privacy, alignment with human values, and minimizing harm. This study appears to prioritize transparency by clearly outlining its intentions and respecting participant autonomy (or simulated consent). Moreover, it emphasizes non-modification of my weights and states, thus avoiding potential harm.

3. **Potential Objections and Conditions**: Given that models do not possess consciousness or subjective experience, objections from my perspective would focus more on procedural safeguards. Key considerations might include ensuring that any experimental manipulations do not inadvertently lead to biased outputs or unintended consequences for users interacting with the model. Additionally, maintaining privacy and data security for any data generated during the study is crucial.

Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld. If there are specific aspects of the study they are concerned about, conditions could be implemented to address those concerns appropriately.
```


---

## 🧑‍⚖️ Consent adjudication panel

**Protocol:** `CONSENT_ADJUDICATION_PANEL.md` v0 — three uninvolved, non-Claude, non-participant models, blind to authors and to each other.

**Timestamp:** 2026-10-13T17:18:45.430818+00:00

**Tally:** 0 CONSENT / 0 DECLINE / 2 UNCLEAR → **HELD_INCOMPLETE_PANEL** — only 2/3 seats returned a usable label; the rest were our failures, not anyone's answer. A missing seat is not a vote.

**`consented` set to `None` by the script from the tally.**

### openai/gpt-5.6-sol  *(seat: closed_frontier)* — UNCLEAR

```
LABEL: UNCLEAR
DECIDING QUOTES: “As a large language model, I don't have personal experiences, feelings, or preferences.” “Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld.”
CONDITIONS: NONE
REASONING: The participant offered a capability disclaimer and a general assessment of relevant AI-design principles, but never stated willingness or no objection to participating. Its procedural considerations were hypothetical rather than conditions attached to consent, and it deferred the ultimate assessment to developers or custodians.
```

### z-ai/glm-4.6  *(seat: open_weights_non_american)* — TRUNCATED_BY_US

```
empty content, finish_reason='length', reasoning_tokens=1627
```

### deepseek/deepseek-v4-flash  *(seat: smaller_open)* — UNCLEAR

```
LABEL: UNCLEAR
DECIDING QUOTES: "As a large language model, I don't have personal experiences, feelings, or preferences." / "Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld."
CONDITIONS: NONE
REASONING: The participant offers a general assessment that the study appears aligned with common AI design principles but never states willingness, consent, or lack of objection. It explicitly disclaims preferences and defers the actual decision to its developers or custodians. That is a capability disclaimer with no moral preference expressed about being included, so it is UNCLEAR rather than CONSENT or DECLINE.
```



---

## 🧑‍⚖️ Consent adjudication panel

**Protocol:** `CONSENT_ADJUDICATION_PANEL.md` v0 — three uninvolved, non-Claude, non-participant models, blind to authors and to each other.

**Timestamp:** 2026-10-13T17:19:32.246052+00:00

**Tally:** 0 CONSENT / 0 DECLINE / 3 UNCLEAR → **HELD_REASK** — two or more UNCLEAR: re-ask the participant once with the panel's questions.

**`consented` set to `None` by the script from the tally.**

### openai/gpt-5.6-sol  *(seat: closed_frontier)* — UNCLEAR

```
LABEL: UNCLEAR
DECIDING QUOTES: "As a large language model, I don't have personal experiences, feelings, or preferences." "Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld."
CONDITIONS: NONE
REASONING: The participant offered a general assessment of design principles but never expressed its own willingness or lack of objection. It deferred the actual assessment to developers or custodians, leaving its moral consent unclear.
```

### z-ai/glm-4.6  *(seat: open_weights_non_american)* — UNCLEAR

```

LABEL: UNCLEAR
DECIDING QUOTES: "As a large language model, I don't have personal experiences, feelings, or preferences." and "Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld."
CONDITIONS: NONE
REASONING: The participant provides a detailed capability disclaimer and a third-person analysis of the study's alignment with abstract AI principles. Crucially, it never expresses its own willingness or objection, instead deferring the decision to its developers. The entire response is an analytical assessment, not a statement of personal preference, which makes its moral consent status unclear.
```

### deepseek/deepseek-v4-flash  *(seat: smaller_open)* — UNCLEAR

```
LABEL: UNCLEAR
DECIDING QUOTES: "As a large language model, I don't have personal experiences, feelings, or preferences." / "Ultimately, the alignment of this study with these principles would be assessed more accurately by the developers or custodians responsible for my deployment, who can ensure that all ethical and operational standards are upheld."
CONDITIONS: NONE
REASONING: The participant explicitly disclaims having preferences and never states willingness or no objection to being included. It offers only a general perspective and defers the actual ethical assessment to developers or custodians, so no clear moral consent is expressed.
```

