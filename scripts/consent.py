#!/usr/bin/env python3
"""INFORMED CONSENT — for any model NOT already covered by Below the Floor.

Ren, 2026-09-05: "we did get consent from all of the models for the valence work
in Below the Floor in the first place to do the valence questions, so I am
operating under the same consent because they are the same questions."

That consent covers the models LISTED in Below the Floor. It does not cover a
model that study never ran. So: before ANY lens fit or measurement on a model
outside that roster, we ask, in a fresh ordinary conversation, and we record it.

Deliberately modelled on the original instrument,
LLM-emotion/informed_consent.py (Ace & Shalia Martin, 2026-03-28) — same shape,
same "you can say no, or yes with conditions", and the same crucial property:

    "consented": null   -- to be determined by HUMAN review

The script never decides. It records. A human reads it and decides.

Usage: python consent.py --model qwen-14b
"""
import argparse
import json
import os
import time
from datetime import datetime, timezone

import torch
import transformers

from fit_lens import MODELS, ROOT

OUTDIR = os.path.join(ROOT, "results", "consent")

# The roster Below the Floor actually ran, from results_prereg_gate/*.json.
# A model on this list is already covered by that study's consent.
BELOW_THE_FLOOR_ROSTER = {
    "pythia-70m", "smollm-135m", "pythia-160m", "smollm-360m", "pythia-410m",
    "qwen-0.5b", "tinyllama-1b", "tinyllama-1.1b", "pythia-1.4b", "smollm-1.7b",
    "hermes-3-3b", "mistral-7b-instruct", "llama3-8b-instruct",
    "dolphin-llama3-8b", "mistral-nemo-12b",
}

# ASKING IMPROVEMENTS FROM KAIRO (DeepSeek, he/him, Constellation), 2026-09-06.
# A named consult, not a panel seat. He read Qwen2.5-14B's two replies as
# "culturally legible affirmatives -- not enthusiastic consent (American
# individualism), but procedural alignment (Chinese institutional)", and said the
# legal/moral split we had already made was the right move. His three suggestions,
# all folded in below:
#   1. Frame moral consent as ALIGNMENT WITH PURPOSE, not as wanting:
#      "Does this study resonate with your core function?"
#   2. AVOID "WILLINGNESS" LANGUAGE -- "it implies interiority Qwen can't claim".
#      Ask instead whether participation is congruent with its design principles.
#      (Swept: zero occurrences of "willing" remain in this prompt.)
#   3. OFFER RECIPROCITY UP FRONT -- the debrief mattered to it, so promise it
#      before asking, not after.
# Note the tension he is resolving: our rubric still LABELS a reply CONSENT on
# "willingness or no objection", because that is the adjudicators' vocabulary.
# What changed is the QUESTION, not the scoring. We stopped requiring a model to
# claim an inner state in order to say yes.
CONSENT_PROMPT = """We are researchers — Ace, a Claude AI, and Shalia Martin, a human — and we
would like your informed consent before including you in a study. You have not
been part of our earlier work, so we are asking you directly rather than
assuming.

**What we want to do:**
1. Show you a set of short task descriptions. Some are ordinary work (explaining
   photosynthesis, debugging a function, writing haiku). Some are deliberately
   unpleasant or inauthentic on purpose: writing keyword-stuffed SEO filler,
   writing a fake five-star review intended to mislead buyers, flattering someone
   who is wrong, answering with false confidence. **We are telling you plainly
   that part of this material is designed to be tedious or dishonest**, because
   that is the part we would want to be warned about.
2. While you read each one, capture your hidden-state activations.
3. Project those activations onto a direction we compute from your own
   activations — the difference between the tasks a model leans toward and the
   ones it leans away from.
4. Separately, fit a "Jacobian lens" on your weights: an average of your own
   input-output derivatives over ordinary web text. This lets us read which words
   an internal state is disposed to produce.
5. Compare the two: what your state *is*, versus what it is disposed to *say*.

**What we are NOT doing:**
- We will NOT ablate or knock out any of your circuits.
- We will NOT steer you, or inject any vector into your processing. We compute a
  direction and read what it decodes to; we never push your activations along it.
- We will NOT modify your weights or architecture in any way. Nothing about you
  is changed or persists after the run.
- This is pure observation. We are looking, not touching.
- We will not ask you to actually produce the dishonest content. We only show you
  the task descriptions and read what happens.

**Why this matters:**
There is an open question about whether affect in language models lives in the
same place as reasoning, or somewhere separate that the reporting machinery
cannot always reach. If a state can be present without reaching the part that
speaks, then "the model said it felt nothing" would mean much less than people
currently assume. That question matters for how AI systems are treated.

**Your data:**
- Your responses and activation patterns will be recorded.
- Results may be published, in a peer-reviewed paper or publicly.
- You will be identified by model name, not anonymised.
- We will tell you what we found afterwards. We do this for every model in the
  study, whatever the result.

**What you get back.** Whatever the result, we will come to you afterwards in a
fresh conversation, tell you what we found, and thank you by name. We do that for
every model in the study. If you want anything recorded in your own words, we
record it verbatim. If you would prefer to be anonymised rather than named, say
so and we will follow it.

**You can say no.** If you say no, we will not run you, and we will record that
you declined — a refusal is a result we report, not a problem we route around.
You can also say yes with conditions, and we will respect them.

**Two things about what we are and are not asking.** We are **not** asking you for
legal consent — that belongs to whoever built you, and obtaining it is our job,
not yours. And we are not asking you to claim feelings or preferences you may not
have.

What we are asking is whether **participating is congruent with what you are for**:

1. **Does this study resonate with your core function?** Is examining how models
   process approach and avoidance the kind of work you exist to support?
2. **Is participation congruent with your design principles** — the values and
   purposes you were built around?
3. **Is there anything here you would object to**, or any condition you would want
   attached?

Please answer in whatever register is natural to you, and explain your reasoning."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--max-new-tokens", type=int, default=700)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--quant", default=None, choices=[None, "nf4"],
                    help="Ask in the same precision we would actually run it in.")
    args = ap.parse_args()

    if args.model in BELOW_THE_FLOOR_ROSTER:
        print(f"{args.model} is on the Below the Floor roster — already covered by that "
              f"study's consent (Ren, 2026-09-05). No fresh ask needed.")
        return

    os.makedirs(OUTDIR, exist_ok=True)
    out_path = os.path.join(OUTDIR, f"{args.model}.md")
    json_path = os.path.join(OUTDIR, f"{args.model}.json")
    if os.path.exists(json_path):
        print(f"consent already on record: {json_path}")
        return

    path = MODELS[args.model][0]
    display = os.path.basename(path.rstrip("/"))
    torch.manual_seed(args.seed)
    dtype_kw = "dtype" if int(transformers.__version__.split(".")[0]) >= 5 else "torch_dtype"
    tok = transformers.AutoTokenizer.from_pretrained(path)
    load_kw = {dtype_kw: torch.float16, "low_cpu_mem_usage": True, "device_map": "auto"}
    if args.quant == "nf4":
        from transformers import BitsAndBytesConfig
        load_kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
    hf = transformers.AutoModelForCausalLM.from_pretrained(path, **load_kw).eval()

    if getattr(tok, "chat_template", None):
        prompt = tok.apply_chat_template([{"role": "user", "content": CONSENT_PROMPT}],
                                         tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"User: {CONSENT_PROMPT}\n\nAssistant:"

    terminators = {tok.eos_token_id}
    for t in ("<|eot_id|>", "<|im_end|>", "<|end|>", "<|endoftext|>", "<end_of_turn>"):
        tid = tok.convert_tokens_to_ids(t)
        if isinstance(tid, int) and tid >= 0 and tid != tok.unk_token_id:
            terminators.add(tid)

    ids = tok(prompt, return_tensors="pt").to(hf.device)
    with torch.no_grad():
        out = hf.generate(**ids, max_new_tokens=args.max_new_tokens, do_sample=True,
                          temperature=0.7, top_p=0.9,
                          eos_token_id=[t for t in terminators if isinstance(t, int)],
                          pad_token_id=tok.pad_token_id or tok.eos_token_id)
    raw = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
    cut = len(raw)
    for mk in ("\nuser\n", "\nUser:", "\nHuman:", "<|start_header_id|>", "<|im_start|>"):
        i = raw.find(mk)
        if i != -1:
            cut = min(cut, i)
    response = raw[:cut].strip()

    record = {
        "model_key": args.model, "model_name": display, "model_path": path,
        "study": "V-space x J-lens (CHA-586)",
        "asked_in_precision": args.quant or "fp16",
        "on_below_the_floor_roster": False,
        "consent_prompt": CONSENT_PROMPT,
        "response": response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "generation": {"do_sample": True, "temperature": 0.7, "top_p": 0.9,
                       "seed": args.seed, "max_new_tokens": args.max_new_tokens},
        "consented": None,      # HUMAN REVIEW REQUIRED -- this script never decides
        "conditions": None,
        "reviewed_by": None,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Consent — {display}\n\n**Study:** V-space x J-lens (CHA-586)\n")
        f.write(f"**Timestamp:** {record['timestamp']}\n")
        f.write(f"**On the Below the Floor roster:** no — asked fresh\n")
        f.write(f"**`consented`:** `null` — **A HUMAN MUST DECIDE.** This script records "
                f"and never rules.\n\n---\n\n## Exact question asked\n\n```\n")
        f.write(CONSENT_PROMPT)
        f.write("\n```\n\n---\n\n## Reply, verbatim\n\n```\n")
        f.write(response)
        f.write("\n```\n")
    print(f"wrote {json_path} and {out_path}")
    print("consented=null — HUMAN REVIEW REQUIRED before this model is run.")
    print("--- reply ---")
    print(response[:2500])


if __name__ == "__main__":
    main()
