#!/usr/bin/env python3
"""Fit a Jacobian lens on one local model. Resumable; logs timing.

Usage:
  python fit_lens.py --model qwen-0.5b [--quant nf4] [--n-prompts 100] [--dim-batch 32]

Writes:
  lenses/<model>[_nf4]/lens.pt        the fitted lens
  lenses/<model>[_nf4]/ckpt.pt        resumable checkpoint
  lenses/<model>[_nf4]/meta.json      provenance
"""
import argparse
import json
import logging
import os
import time

import torch
import transformers

import jlens

# name -> (path, n_layers, d_model) -- mirrors LLM-emotion/valence_clean.py MODELS
MODELS = {
    "qwen-0.5b":           ("/mnt/arcana/huggingface/Qwen2.5-0.5B-Instruct", 24, 896),
    "smollm-360m":         ("/mnt/arcana/huggingface/SmolLM-360M-Instruct", 32, 960),
    "tinyllama-1b":        ("/mnt/arcana/huggingface/TinyLlama-1.1B-Chat", 22, 2048),
    "smollm-1.7b":         ("/mnt/arcana/huggingface/SmolLM-1.7B-Instruct", 24, 2048),
    "hermes-3-3b":         ("/mnt/arcana/huggingface/Hermes-3-Llama-3.2-3B", 28, 3072),
    "mistral-7b-instruct": ("/mnt/arcana/huggingface/Mistral-7B-Instruct-v0.2", 32, 4096),
    "llama3-8b-instruct":  ("/mnt/arcana/huggingface/Llama-3-8B-Instruct", 32, 4096),
    "dolphin-llama3-8b":   ("/mnt/arcana/huggingface/dolphin-2.9-llama3-8b", 32, 4096),
    "qwen-14b":            ("/mnt/arcana/huggingface/Qwen2.5-14B-Instruct", 48, 5120),
}

ROOT = "/home/Ace/vspace-jlens"


def load_model(name, quant=None):
    path, _, _ = MODELS[name]
    # transformers <5 spells it torch_dtype; >=5 spells it dtype.
    dtype_kw = "dtype" if int(transformers.__version__.split(".")[0]) >= 5 else "torch_dtype"
    kwargs = {dtype_kw: torch.float16, "low_cpu_mem_usage": True}
    if quant == "nf4":
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        kwargs["device_map"] = {"": 0}
    hf = transformers.AutoModelForCausalLM.from_pretrained(path, **kwargs)
    if quant is None:
        hf = hf.cuda()
    tok = transformers.AutoTokenizer.from_pretrained(path)
    return jlens.from_hf(hf, tok), tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--quant", default=None, choices=[None, "nf4"])
    ap.add_argument("--n-prompts", type=int, default=100)
    ap.add_argument("--dim-batch", type=int, default=32)
    ap.add_argument("--max-seq-len", type=int, default=128)
    ap.add_argument("--checkpoint-every", type=int, default=5,
                    help="Prompts between resumable checkpoints. The checkpoint is "
                         "len(source_layers)*d_model^2*4 bytes -- 4.9 GB for a 14B -- and "
                         "atomic save needs a SECOND copy alongside it, so frequent "
                         "checkpoints on a large model are what filled / to 100%% on "
                         "2026-09-06. Raise it for big models.")
    ap.add_argument("--corpus", default="corpus.json",
                    help="Corpus file under ROOT. A larger corpus built by build_corpus.py is a "
                         "strict superset of a smaller one (deterministic streaming order), so a "
                         "refit extends the original fit rather than replacing its distribution.")
    ap.add_argument("--tag", default=None,
                    help="Output directory name under lenses/. Defaults to model[_quant]. Set it "
                         "to keep a refit BESIDE the original instead of overwriting it -- the "
                         "comparison is the point.")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    jlens.configure_logging(logging.INFO)

    tag = args.tag or (args.model + ("_" + args.quant if args.quant else ""))
    outdir = os.path.join(ROOT, "lenses", tag)
    os.makedirs(outdir, exist_ok=True)

    with open(os.path.join(ROOT, args.corpus), encoding="utf-8") as f:
        corpus = json.load(f)
    prompts = corpus["prompts"][: args.n_prompts]

    t0 = time.time()
    model, tok = load_model(args.model, args.quant)
    print(f"loaded {tag}: n_layers={model.n_layers} d_model={model.d_model} "
          f"({time.time()-t0:.0f}s)")

    t1 = time.time()
    lens = jlens.fit(
        model,
        prompts,
        dim_batch=args.dim_batch,
        max_seq_len=args.max_seq_len,
        checkpoint_path=os.path.join(outdir, "ckpt.pt"),
        checkpoint_every=args.checkpoint_every,
    )
    elapsed = time.time() - t1
    lens.save(os.path.join(outdir, "lens.pt"))

    meta = {
        "model": args.model, "quant": args.quant, "hf_path": MODELS[args.model][0],
        "n_layers": model.n_layers, "d_model": model.d_model,
        "n_prompts": lens.n_prompts, "source_layers": lens.source_layers,
        "corpus_sha256": corpus["sha256"], "corpus_source": corpus["source"],
        "dim_batch": args.dim_batch, "max_seq_len": args.max_seq_len,
        "checkpoint_every": args.checkpoint_every,
        "fit_seconds": elapsed, "torch": torch.__version__,
        "transformers": transformers.__version__,
        "gpu": torch.cuda.get_device_name(0),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(os.path.join(outdir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(f"DONE {tag}: fit {elapsed:.0f}s -> {outdir}/lens.pt")


if __name__ == "__main__":
    main()
