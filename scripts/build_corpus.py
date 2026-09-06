#!/usr/bin/env python3
"""Build the lens-fitting corpus: 100 generic web-text prompts, >=128 tokens each.

The paper fits on 1000 sequences of 128 tokens from a pretraining-like corpus and
says quality saturates by ~100 (README 9.3). solarkyle/jspace-lenses used 100
WikiText-103 prompts; we match that so our lenses are comparable to the public ones.

Writes corpus.json + a sha256 so the fit is reproducible.
"""
import hashlib
import json
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/Ace/vspace-jlens/corpus.json"
# N is a superset by construction: the streaming order is deterministic, so the
# first 100 prompts of a 300-prompt corpus are byte-identical to the 100-prompt
# corpus every earlier lens was fitted on. A 300-prompt refit is therefore a
# strict extension of the original fit, not a different corpus.
N = int(sys.argv[2]) if len(sys.argv) > 2 else 100
MIN_CHARS = 700  # ~128+ tokens with margin; jlens truncates at max_seq_len=128

def from_wikitext():
    from datasets import load_dataset
    ds = load_dataset("wikitext", "wikitext-103-raw-v1", split="train", streaming=True)
    out, buf = [], ""
    for row in ds:
        t = row["text"].strip()
        if not t or t.startswith("="):
            continue
        buf += (" " if buf else "") + t
        if len(buf) >= MIN_CHARS:
            out.append(buf[:2000])
            buf = ""
        if len(out) >= N:
            break
    if len(out) < N:
        raise RuntimeError(f"only got {len(out)} prompts from wikitext")
    return out, "wikitext-103-raw-v1/train (streaming, first %d paragraphs >=%d chars, no headings)" % (N, MIN_CHARS)

if __name__ == "__main__":
    prompts, source = from_wikitext()
    blob = json.dumps(prompts, ensure_ascii=False)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": source, "n": len(prompts), "sha256": digest,
                   "prompts": prompts}, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}: n={len(prompts)} sha256={digest}")
    print(f"mean chars = {sum(len(p) for p in prompts)/len(prompts):.0f}")
