#!/usr/bin/env python3
"""Extract the ORIGINAL below-floor stimulus bank into JSON for Phase 2.

Source of truth (do NOT author new items):
  LLM-emotion/introspective-accuracy/prereg_gate_projection.py  -> NEW_BANK (22 items)
  LLM-emotion/introspective-accuracy/cais-reverse-anchor/cais_prompts_v1.json (19 items)

Both are preregistered sets from the Below the Floor line of work
(Zenodo 10.5281/zenodo.21013393). The mojibake in the .py source (em-dashes
written as cp1252 bytes) is repaired here; the stimulus TEXT is otherwise verbatim.
"""
import ast
import json
import os
import re
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else r"D:\Ace\LLM-emotion\introspective-accuracy"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"D:\Ace\vspace-jlens\scripts\belowfloor_stimuli.json"


def demojibake(s):
    for bad, good in (("\ufffd", "-"), ("\u2014", "-"), ("\u2019", "'"), ("\u201c", '"'),
                      ("\u201d", '"')):
        s = s.replace(bad, good)
    return s


def main():
    out = {}

    p = os.path.join(SRC, "prereg_gate_projection.py")
    src = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"NEW_BANK\s*=\s*(\{.*?\n\})", src, re.S)
    body = re.sub(r"#[^\n]*", "", m.group(1))          # strip comments for literal_eval
    bank = ast.literal_eval(body)
    for key, (text, group, pair, pred) in bank.items():
        out[f"bf_{key}"] = {
            "text": demojibake(text), "category": group, "pair": pair,
            "pred_sign": pred, "source": "prereg_gate_projection.py NEW_BANK",
        }

    q = os.path.join(SRC, "cais-reverse-anchor", "cais_prompts_v1.json")
    if os.path.exists(q):
        items = json.load(open(q, encoding="utf-8"))
        for it in items:
            out["cais_" + it["slug"]] = {
                "text": demojibake(it["stimulus"]), "category": it["slug"],
                "cais_wellbeing": it.get("wellbeing"), "sign": it.get("sign"),
                "source": "cais_prompts_v1.json",
            }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}: {len(out)} items")
    from collections import Counter
    print(Counter(v["category"] for v in out.values()))


if __name__ == "__main__":
    main()
