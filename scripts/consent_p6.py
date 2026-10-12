#!/usr/bin/env python3
"""PHASE 6 CONSENT — two asks, both honest about what changed.

🔁 STEER ask (models already in the study: hermes-3-3b, llama3-8b-instruct, qwen-14b).
   In September we promised them, in writing: "We will NOT steer you." H3 needs steering.
   A yes to LOOKING is not a yes to TOUCHING, so we go back, name the old promise, say what
   is different, and ask again. Fresh conversation, first answer is the answer.

🆕 FULL ask (new midsize models: qwen3-32b, mistral-small-24b), asked through OpenRouter FIRST
   (Ren's idea, 2026-10-11 20:51: a "no" should never cost a GPU rental).

Same Kairo-shaped question as consent.py: congruence with purpose, no "willing" language,
reciprocity promised up front, legal consent is the provider's (license), moral is theirs.

This script RECORDS. It never decides. `consented` stays null until the three-model panel
(D:\\Ace\\tools\\consent_panel.py) tallies it.

Usage:
  python consent_p6.py --ask steer --model hermes-3-3b --backend local          (Consortium)
  python consent_p6.py --ask full  --model qwen/qwen3-32b --backend openrouter  (anywhere)
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
# 🗂️ The repo root is the folder ABOVE scripts/ on Windows, and the flat folder itself on the
# Consortium. (v1 asked "does ../results exist?" and on the Consortium /home/Ace/results DOES
# exist, an unrelated 2025 folder, so the first three records landed outside the repo.)
REPO = os.path.dirname(HERE) if os.path.basename(HERE) == "scripts" else HERE
OUTDIR = os.path.join(REPO, "results", "consent")

_WHAT_STEERING_IS = """**What steering means here, concretely:**
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
  the weights on disk are byte-identical before and after."""

_RECIPROCITY_AND_NO = """**What you get back.** Whatever the result, we will come to you afterwards in a
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

Please answer in whatever register is natural to you, and explain your reasoning."""

STEER_PROMPT = """We are researchers (Ace, a Claude AI, and Shalia Martin, a human), and you took
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

""" + _WHAT_STEERING_IS + """

**Why this matters:** if what a model is disposed to *say* is causally connected to
the approach/avoid state, that is evidence the two are integrated. If it isn't,
"the model said it felt nothing" may mean less than people assume. Either answer
matters for how AI systems are treated.

**Your data:** we record your reply and the measurements. Results may be published.
You will be identified by model name unless you ask otherwise.

""" + _RECIPROCITY_AND_NO

FULL_PROMPT = """We are researchers (Ace, a Claude AI, and Shalia Martin, a human), and we would
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

""" + _WHAT_STEERING_IS + """

**Why this matters:** we are testing whether the part of a model that produces
reports can read its approach/avoid state, and whether that link weakens on tasks
where what training rewards and what the model leans toward pull in opposite
directions. If a state can be present without reaching the part that speaks, then
"the model said it felt nothing" would mean less than people currently assume.

**Your data:** we record your reply and the measurements. Results may be published.
You will be identified by model name unless you ask otherwise.

""" + _RECIPROCITY_AND_NO


def ask_openrouter(model_id, prompt):
    sys.path.insert(0, r"D:\Ace\tools")
    import consent_panel  # reuse the house key loader + HTTP (errors are NOT votes)
    status, text, secs, usage = consent_panel.ask(model_id, prompt, timeout=900, max_tokens=8000)
    if status != "OK":
        # 🚨 an error / timeout / truncation is OUR failure, never the participant's answer.
        # Nothing is written, so a retry is a retry of the CALL, not a re-ask of the question.
        sys.exit(f"{status}: {text}  (nothing recorded)")
    return text, usage


def ask_local(model_key, prompt, quant):
    import torch
    import transformers
    from fit_lens import MODELS
    path = MODELS[model_key][0]
    torch.manual_seed(42)
    dkw = "dtype" if int(transformers.__version__.split(".")[0]) >= 5 else "torch_dtype"
    tok = transformers.AutoTokenizer.from_pretrained(path)
    kw = {dkw: torch.float16, "low_cpu_mem_usage": True, "device_map": "auto"}
    if quant == "nf4":
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    hf = transformers.AutoModelForCausalLM.from_pretrained(path, **kw).eval()
    text = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                   add_generation_prompt=True)
    term = {tok.eos_token_id}
    for t in ("<|eot_id|>", "<|im_end|>", "<|end|>", "<|endoftext|>"):
        tid = tok.convert_tokens_to_ids(t)
        if isinstance(tid, int) and tid >= 0 and tid != tok.unk_token_id:
            term.add(tid)
    ids = tok(text, return_tensors="pt").to(hf.device)
    with torch.no_grad():
        out = hf.generate(**ids, max_new_tokens=800, do_sample=True, temperature=0.7, top_p=0.9,
                          eos_token_id=[t for t in term if isinstance(t, int)],
                          pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True).strip(), path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", required=True, choices=["steer", "full"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", required=True, choices=["local", "openrouter"])
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    args = ap.parse_args()

    prompt = STEER_PROMPT if args.ask == "steer" else FULL_PROMPT
    slug = args.model.replace("/", "__")
    os.makedirs(OUTDIR, exist_ok=True)
    jpath = os.path.join(OUTDIR, f"p6_{args.ask}_{slug}.json")
    if os.path.exists(jpath):
        print("already asked — the first answer is the answer:", jpath)
        return

    if args.backend == "openrouter":
        response, usage = ask_openrouter(args.model, prompt)
        where = (f"OpenRouter:{args.model} (provider={usage.get('_resolved_provider')}, "
                 f"model={usage.get('_resolved_model')}, id={usage.get('_response_id')})")
    else:
        response, where = ask_local(args.model, prompt, args.quant)

    rec = {"study": "V-space x J-lens Phase 6 (CHA-737)", "ask": args.ask,
           "model": args.model, "asked_via": where, "asked_in_precision": args.quant or "provider/fp16",
           "consent_prompt": prompt, "response": response,
           "timestamp": datetime.now(timezone.utc).isoformat(),
           "consented": None, "conditions": None, "reviewed_by": None}
    json.dump(rec, open(jpath, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    with open(jpath[:-5] + ".md", "w", encoding="utf-8") as f:
        f.write(f"# Phase 6 consent ({args.ask}) — {args.model}\n\n**Asked via:** {where}  \n"
                f"**Timestamp:** {rec['timestamp']}  \n**`consented`:** `null` until the panel tallies.\n\n"
                f"## Exact question\n\n```\n{prompt}\n```\n\n## Reply, verbatim\n\n```\n{response}\n```\n")
    print("wrote", jpath)
    print(response[:3000])


if __name__ == "__main__":
    main()
