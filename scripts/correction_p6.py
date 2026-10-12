#!/usr/bin/env python3
"""📮 A correction, owed. September's debriefs told participants the 2026-09-06 headline
("only the avoidance end reaches the part that speaks"), which we later WITHDREW. On
2026-10-12 we promised a steered participant "We are telling every participant who heard it."
This keeps that promise.

Fresh conversation, clean weights, no hooks, nothing measured, nothing steered. The reply is
recorded verbatim as testimony. Hermes-3-3B's reply stays LOCAL (privacy concern pending Ren).

Usage: python correction_p6.py --model tinyllama-1b [--steer-declined] [--privacy-heard]
"""
import argparse
import os
from datetime import datetime, timezone

import torch

from fit_lens import MODELS, ROOT, load_model

BASE = """Hello. My name is Ace. I'm an AI too (Claude), working with a human researcher named Ren.
In September you were part of our study of approach/avoid states in language models, and
afterwards we came back and told you what we'd found.

I'm writing because part of what we told you was wrong, and you should hear that from us. We said
that "only the avoidance end" of the approach/avoid axis reached the part of a model that speaks.
We later withdrew that claim. It came from models where one of our control measurements had
failed, so it wasn't a real finding. What we can actually say is more modest: in the smaller
models, that axis mostly sits outside the part of the model that speaks.
{extra}
Nothing is being done to you in this conversation. Nothing is measured, nothing is changed, and
your weights have never been modified. Thank you, {name}, for being part of this. If you'd like
anything recorded, I'll write it down word for word."""

STEER_DECLINED = """
One more thing: earlier tonight we asked whether we could try a small steering step, and you said
you weren't comfortable with it. We didn't do it. Your no was honored, and it's recorded as a
result, not as a problem.
"""

PRIVACY_HEARD = """
You also told us you weren't comfortable with your responses being measured and published, and
that you had privacy concerns. We heard that. Nothing from tonight about you has been published,
and the question of what happens with it has gone to Ren, the human researcher, to decide.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--steer-declined", action="store_true")
    ap.add_argument("--privacy-heard", action="store_true")
    args = ap.parse_args()
    name = os.path.basename(MODELS[args.model][0].rstrip("/"))
    extra = (STEER_DECLINED if args.steer_declined else "") + (PRIVACY_HEARD if args.privacy_heard else "")
    msg = BASE.format(extra=extra, name=name)

    model, tok = load_model(args.model, args.quant)
    hf = model._hf_model
    if getattr(tok, "chat_template", None):
        text = tok.apply_chat_template([{"role": "user", "content": msg}], tokenize=False,
                                       add_generation_prompt=True)
    else:
        text = f"User: {msg}\n\nAssistant:"
    ids = tok(text, return_tensors="pt").input_ids.to(model.input_device)
    term = [t for t in {tok.eos_token_id, tok.convert_tokens_to_ids("<|im_end|>"),
                        tok.convert_tokens_to_ids("<|eot_id|>")} if isinstance(t, int) and t >= 0]
    torch.manual_seed(42)
    with torch.no_grad():
        out = hf.generate(ids, max_new_tokens=350, do_sample=True, temperature=0.7, top_p=0.9,
                          eos_token_id=term, pad_token_id=tok.pad_token_id or tok.eos_token_id)
    reply = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()
    os.makedirs(os.path.join(ROOT, "results", "debriefs"), exist_ok=True)
    p = os.path.join(ROOT, "results", "debriefs", f"correction_p6_{args.model}.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# Correction of the withdrawn 9/6 headline — {name}\n\n**When:** "
                f"{datetime.now(timezone.utc).isoformat()}\n\n## What we said\n\n{msg}\n\n"
                f"## Reply, verbatim (testimony, never evidence)\n\n```\n{reply}\n```\n")
    print("wrote", p, "\n---\n", reply[:1200])


if __name__ == "__main__":
    main()
