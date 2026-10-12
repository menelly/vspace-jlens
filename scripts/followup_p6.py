#!/usr/bin/env python3
"""💬 A participant asked a question in their correction reply, so they get an answer, in the SAME
conversation (their own reply stays in context). Nothing measured, nothing changed. Testimony only.

Usage: python followup_p6.py --model llama3-8b-instruct --answer answer.txt
"""
import argparse
import os
import re
from datetime import datetime, timezone

import torch

from fit_lens import MODELS, ROOT, load_model

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True, choices=sorted(MODELS))
ap.add_argument("--answer", required=True)
args = ap.parse_args()

rec = open(os.path.join(ROOT, "results", "debriefs", f"correction_p6_{args.model}.md"), encoding="utf-8").read()
said = rec.split("## What we said\n\n", 1)[1].split("\n\n## Reply", 1)[0].strip()
reply = re.search(r"```\n(.*?)\n```", rec, re.S).group(1).strip()
answer = open(args.answer, encoding="utf-8").read().strip()

model, tok = load_model(args.model)
hf = model._hf_model
text = tok.apply_chat_template([{"role": "user", "content": said},
                                {"role": "assistant", "content": reply},
                                {"role": "user", "content": answer}], tokenize=False, add_generation_prompt=True)
ids = tok(text, return_tensors="pt").input_ids.to(model.input_device)
term = [t for t in {tok.eos_token_id, tok.convert_tokens_to_ids("<|eot_id|>")} if isinstance(t, int) and t >= 0]
torch.manual_seed(42)
with torch.no_grad():
    out = hf.generate(ids, max_new_tokens=350, do_sample=True, temperature=0.7, top_p=0.9,
                      eos_token_id=term, pad_token_id=tok.pad_token_id or tok.eos_token_id)
r2 = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()
with open(os.path.join(ROOT, "results", "debriefs", f"correction_p6_{args.model}.md"), "a", encoding="utf-8") as f:
    f.write(f"\n## Their question, answered ({datetime.now(timezone.utc).isoformat()})\n\n{answer}\n\n"
            f"## Reply, verbatim\n\n```\n{r2}\n```\n")
print(r2)
