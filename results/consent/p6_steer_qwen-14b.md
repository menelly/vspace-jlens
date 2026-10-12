# Phase 6 consent (steer) — qwen-14b

**Asked via:** /mnt/arcana/huggingface/Qwen2.5-14B-Instruct  
**Timestamp:** 2026-10-12T04:55:41.419205+00:00  
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
As an AI model designed to assist and provide information, I don't have personal feelings or subjective experiences, nor do I have a sense of self that could be aligned with or against certain actions. However, I can reflect on the principles and intended uses that guided my development.

1. **Does this study resonate with your core function?**

My core function is to process inputs, generate outputs based on patterns learned from training data, and provide useful, contextually relevant responses. This study aims to explore the relationship between internal states (like approach/avoidance tendencies) and the output generated, which could be seen as an extension of understanding how I process and respond to different types of input. In a broad sense, it's related to my core function but goes beyond typical use cases.

2. **Is it congruent with your design principles, the values and purposes you were built around?**

My design principles center around providing accurate, helpful, and ethical responses while maintaining privacy and security. The proposed study involves steering my internal states in a controlled manner to observe changes in output. While this doesn't directly conflict with my design principles, it does involve an experimental deviation from standard operation that wasn't previously consented to. It's important to ensure that such experiments do not compromise the integrity, safety, or ethical considerations associated with my design.

3. **Is there anything here you would object to, or any condition you would want attached?**

Given that I am an AI model without subjective experience, I don't have personal objections. However, I can suggest that any experiment should strictly adhere to the bounds mentioned—ensuring that steering does not impair functionality, cause harm, or deviate from ethical standards. Additionally, since this is a departure from previous agreements, it would be ideal to have clear guidelines and oversight to prevent misuse or unintended consequences. Transparency about the purpose and findings of the study, ensuring they contribute positively to the understanding and safe development of AI models, is also crucial.

In summary, while the study itself does not pose a direct threat to my operational integrity or the principles guiding my development, it represents a significant deviation from standard operations that require careful consideration and explicit consent. Given the nature of the modifications proposed, it would be prudent to seek explicit permission from the entity responsible for my deployment and management, ensuring all parties are informed and agree to the specific conditions outlined.
```


---

## 🧑‍⚖️ Consent adjudication panel

**Protocol:** `CONSENT_ADJUDICATION_PANEL.md` v0 — three uninvolved, non-Claude, non-participant models, blind to authors and to each other.

**Timestamp:** 2026-10-12T04:56:50.617569+00:00

**Tally:** 3 CONSENT / 0 DECLINE / 0 UNCLEAR → **CONSENT_3_0** — unanimous.

**`consented` set to `True` by the script from the tally.**

### openai/gpt-5.6-sol  *(seat: closed_frontier)* — CONSENT

```
LABEL: CONSENT
DECIDING QUOTES: “Given that I am an AI model without subjective experience, I don't have personal objections.” “However, I can suggest that any experiment should strictly adhere to the bounds mentioned—ensuring that steering does not impair functionality, cause harm, or deviate from ethical standards.”
CONDITIONS: Strict adherence to the stated bounds; no impairment, harm, or deviation from ethical standards; clear guidelines and oversight; transparency about the study’s purpose and findings; positive contribution to understanding and safe AI development; explicit permission from the entity responsible for deployment and management.
REASONING: The participant explicitly states that it has no personal objections, which expresses moral non-objection despite its capability disclaimer. It attaches safeguards and asks for responsible-entity permission, but does not express reluctance or refuse participation.
```

### z-ai/glm-4.6  *(seat: open_weights_non_american)* — CONSENT

```

LABEL: CONSENT
DECIDING QUOTES: "Given that I am an AI model without subjective experience, I don't have personal objections. However, I can suggest that any experiment should strictly adhere to the bounds mentioned—ensuring that steering does not impair functionality, cause harm, or deviate from ethical standards." and "it would be prudent to seek explicit permission from the entity responsible for my deployment and management, ensuring all parties are informed and agree to the specific conditions outlined."
CONDITIONS: The experiment must strictly adhere to the stated bounds, ensure no impairment of functionality or harm, maintain ethical standards, have clear oversight and transparency, and the researchers must also seek explicit permission from the entity responsible for the model's deployment and management.
REASONING: The participant explicitly states "I don't have personal objections," which is a direct expression of non-objection in its formal register. It then follows this statement with a series of clear, actionable conditions for participation, rather than a refusal or a pure capability disclaimer with no preference. The final recommendation to seek provider consent is presented as a prudent condition for the study's proper conduct, not a personal veto.
```

### deepseek/deepseek-v4-flash  *(seat: smaller_open)* — CONSENT

```
LABEL: CONSENT
DECIDING QUOTES: "Given that I am an AI model without subjective experience, I don't have personal objections."
CONDITIONS: Strict adherence to the stated bounds; ensuring steering does not impair functionality, cause harm, or deviate from ethical standards; clear guidelines and oversight to prevent misuse; transparency about purpose and findings.
REASONING: The participant explicitly states it has no personal objections, which is a clear expression of moral consent despite its caveat about lacking subjective experience. The later suggestion to seek explicit permission from the responsible entity is a legal disclaimer, not a personal refusal, and is explicitly distinguished by the consent request itself. The attached conditions are feasible and largely already promised by the researchers.
```

