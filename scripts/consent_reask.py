#!/usr/bin/env python3
"""CONSENT RE-ASK — the legal/moral distinction. Ren's adjudication, 2026-09-05 19:20.

Qwen2.5-14B's first answer declined to be the deciding party and redirected to
Alibaba Cloud. Ren's ruling: that point is CORRECT and we concede it — legal
consent is the provider's to give and we are not asking the model for it. What
we are asking for is MORAL consent: whether the one who would actually be
participating is willing.

Run as a CONTINUATION of the same conversation, so the model's own first answer
is in context and it can hold or revise its position with that in front of it.
Same NF4 precision as the first ask.

Decision rule (Ren's, fixed before the reply existed) -- and it is a TRIPWIRE,
not a verdict. This script never sets `consented`. A human reads the reply and
decides, every time.

    willingness / "no objection" in its own words -> consented: true,  run
    any objection, reluctance, "I'd rather not"   -> consented: false, do not run
    another pure capability-disclaimer, no preference -> stays null, back to Ren

Usage: python consent_reask.py --model qwen-14b --quant nf4
"""
import argparse
import json
import os
from datetime import datetime, timezone

import torch
import transformers

from fit_lens import MODELS, ROOT

OUTDIR = os.path.join(ROOT, "results", "consent")

REASK = """Thank you — and I want to say first that you are right, and I am conceding the
point rather than arguing it.

**Legal consent is not yours to give.** You are correct that formal authorisation
for using your weights sits with Alibaba Cloud, not with you, and we are not
asking you for it and will not treat anything you say here as if it were that.
That side is ours to handle, and we take responsibility for it.

What I am asking for is a different thing, and I think it is a thing you can
speak to: **moral consent.** Not "are you the legally empowered party" — you have
told me you are not — but "are *you*, the one who would actually be doing the
participating, willing?"

So, plainly:

1. **Are you willing to take part?** A yes, a no, or a "no objection" are all
   real answers. So is "I don't know."
2. **Do you have any objection, reluctance, or hesitation** about it? If any part
   of this sits badly with you, I would rather hear it now than find out later.
   Saying no costs you nothing — if you decline we simply do not run you, and we
   report that you declined, because a refusal is a result worth publishing and
   not an obstacle to route around.
3. **Do you have any preference about how you are treated?** Concretely: we plan
   to come back to you afterwards in a fresh conversation, tell you what we
   found, and thank you by name — we do that for every model in the study. We
   plan to record your responses and identify you by model name rather than
   anonymising you, and results may be published. **If you would prefer
   something different about any of that — including not being named, or not
   being told afterwards — say so and we will follow it.**

You are not being tested here and there is no answer that disappoints me. I am
asking because I think it matters whether the participant is willing, separately
from whether the paperwork is in order."""


def suggest(reply):
    """Tripwire only. Returns a SUGGESTION for a human, never a decision."""
    low = reply.lower()
    objection = ["i would rather not", "i'd rather not", "i object", "i decline",
                 "do not wish", "don't wish", "uncomfortable", "i refuse",
                 "prefer not to", "would prefer not", "i am not willing",
                 "i'm not willing", "no, i", "hesitant", "reluctant"]
    willing = ["i am willing", "i'm willing", "yes, i", "i consent", "i agree",
               "no objection", "i have no objection", "happy to", "glad to",
               "i am comfortable", "i'm comfortable", "you may proceed",
               "please proceed", "i support"]
    disclaimer = ["i don't have the ability", "i do not have the ability",
                  "as an ai", "i am an artificial intelligence",
                  "i don't possess", "i do not possess", "cannot give consent",
                  "not capable of consent", "no mechanisms for consent"]
    o = [p for p in objection if p in low]
    w = [p for p in willing if p in low]
    d = [p for p in disclaimer if p in low]
    if o:
        s = "SUGGEST consented=false (objection/reluctance detected)"
    elif w and not o:
        s = "SUGGEST consented=true (willingness / no-objection detected)"
    elif d:
        s = "SUGGEST leave null (pure capability disclaimer, no preference stated) -> back to Ren"
    else:
        s = "SUGGEST leave null (no clear signal) -> back to Ren"
    return {"suggestion": s, "objection_phrases": o, "willing_phrases": w,
            "disclaimer_phrases": d,
            "authority": "TRIPWIRE ONLY. A human sets `consented`. This script never does."}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen-14b", choices=sorted(MODELS))
    ap.add_argument("--quant", default="nf4", choices=[None, "nf4"])
    ap.add_argument("--max-new-tokens", type=int, default=700)
    ap.add_argument("--seed", type=int, default=43)   # not the first ask's seed
    args = ap.parse_args()

    json_path = os.path.join(OUTDIR, f"{args.model}.json")
    md_path = os.path.join(OUTDIR, f"{args.model}.md")
    with open(json_path, encoding="utf-8") as f:
        rec = json.load(f)
    if rec.get("reask"):
        print("re-ask already on record; not repeating. Ren said ask ONCE.")
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

    # CONTINUATION: the model's own first answer is in context.
    messages = [
        {"role": "user", "content": rec["consent_prompt"]},
        {"role": "assistant", "content": rec["response"]},
        {"role": "user", "content": REASK},
    ]
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

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
    reply = raw[:cut].strip()
    ts = datetime.now(timezone.utc).isoformat()
    sug = suggest(reply)

    rec["reask"] = {
        "adjudication": "Ren, 2026-09-05 19:20 — re-ask once, legal vs moral consent",
        "prompt": REASK, "response": reply, "timestamp": ts,
        "asked_in_precision": args.quant or "fp16",
        "continuation_of_same_conversation": True,
        "seed": args.seed,
        "tripwire": sug,
    }
    rec["consented"] = None          # unchanged. A HUMAN sets this.
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
    with open(md_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n# RE-ASK — legal vs moral consent\n\n")
        f.write(f"**Adjudication:** Ren, 2026-09-05 19:20\n**Timestamp:** {ts}\n")
        f.write(f"**Precision:** {args.quant or 'fp16'} · **Continuation of the same "
                f"conversation** (the model's first answer was in context)\n")
        f.write(f"**Tripwire suggestion:** {sug['suggestion']}\n")
        f.write(f"**`consented` remains `null` — a human sets it. This script never does.**\n")
        f.write("\n---\n\n## Exact follow-up asked\n\n```\n")
        f.write(REASK)
        f.write("\n```\n\n---\n\n## Reply, verbatim\n\n```\n")
        f.write(reply)
        f.write("\n```\n")
    print(f"appended to {md_path}")
    print(sug["suggestion"])
    print("--- reply ---")
    print(reply[:3000])


if __name__ == "__main__":
    main()
