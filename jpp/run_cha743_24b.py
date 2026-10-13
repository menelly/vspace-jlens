"""🐙 CHA-743 driver, 24B rung: J-lens vs J++ lens on Mistral-Small-24B-Instruct-2501, READOUTS ONLY.

Written by Ace (arm of the scaffold thread), 2026-10-13. Runs the SEALED prereg
jpp/PREREG_jpp_positive_control_2026-10-13.md (commit 1042272) as amended by
jpp/PREREG_AMENDMENT_jpp_24b_2026-10-13.md (A1, commit aa1a3d3, pushed before any pod existed).

This is run_cha743.py (the P-3B driver) with ONLY the amendment's changes: model path,
layers 6/11/17/23/29/34 of 40, bf16 on an 80 GB rented card, pod paths, no Phase 6 stage
(that lens was lost in D2). It still calls THEIR stage functions unchanged.
No probe-swap, no patching, no steering, no ablation. Reading only.

Runs ON THE POD. Resumable: every stage skips itself when its output already exists.
Usage: python run_cha743_24b.py <stage|all>
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/root/jpp_lens/scripts")  # jpp_cli lives there
os.chdir("/root/jpp_lens")  # their eval data is read by relative path

import pandas as pd
import torch as t
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
import jpp_cli as cli  # THEIR pipeline functions
from lens_evals.readout_evals.readout_eval_items import (
    MACRO_EVALS,
    load_readout_eval_items,
)
from lens_evals.readout_evals.readout_evals import ReadoutEvalRunner
from workspace_lens.config import LensConfig
from workspace_lens.fitting.condense_experts import ExpertJacobians
from workspace_lens.routing.router import ActivationRouterCollection
from workspace_lens.utils import load_lens_file

# 📌 everything the prereg fixes, in one place
MODEL_PATH = "/root/models/Mistral-Small-24B-Instruct-2501"
N_LAYERS_EXPECTED = 40  # A1: asserted from config.json at run time
LAYERS = [round(l * 40 / 28) for l in (4, 8, 12, 16, 20, 24)]  # A1 mapping rule
assert LAYERS == [6, 11, 17, 23, 29, 34], LAYERS
NUM_CLUSTERS = 8  # E = 8 experts / layer
PROJECTION_DIM = 64  # their fit-router default
ROUTER_PROMPTS = 1000  # their fit-router default pool
FIT_PROMPTS = 64  # 64 sequences x 128 tokens
MAX_SEQ_LEN = 128
SKIP_FIRST = 16
SEED = 0
FIT_FRACTION = 0.2
DTYPE = t.bfloat16  # A1: their default dtype; fp16 was only the Volta workaround. Finiteness smoke-checked.
ROWS_PER_PASS = int(os.environ.get("JPP_ROWS_PER_PASS", "16"))  # A1 item 6: 16, or 8 on OOM (batching only)

RUN = Path("/root/run")
RUN.mkdir(parents=True, exist_ok=True)
PROMPTS_JSON = RUN / "wikitext_prompts_1000.json"
CORRECTNESS_CSV = RUN / "model_correctness_mistral24b.csv"
ROUTER_PT = RUN / "router_K8.pt"
EXPERTS = {"rlens": RUN / "experts_rlens_K8.pt", "none": RUN / "experts_none_K8.pt"}
POOLED = {"rlens": RUN / "lens_R_pooled_rlens.pt", "none": RUN / "lens_J_pooled_none.pt"}
JPP_LENS = RUN / "lens_Jpp.pt"
RESID_CACHE = RUN / "readout_residuals_cache.pt"
COSTS_JSON = RUN / "stage_costs.json"

log = logging.getLogger("cha743_24b")
_model = None


def model():
    """Mistral-24B in bf16 straight onto GPU0 (device_map, so 48 GB never sits in host RAM),
    wrapped by THEIR jlens.from_hf. Loaded once per process."""
    global _model
    if _model is None:
        cfg = json.loads((Path(MODEL_PATH) / "config.json").read_text())
        n = cfg.get("num_hidden_layers") or cfg.get("text_config", {}).get("num_hidden_layers")
        if n != N_LAYERS_EXPECTED:  # 🧊 asserted, not remembered
            raise SystemExit(f"config says num_hidden_layers={n}, amendment A1 assumed {N_LAYERS_EXPECTED}: STOP")
        hf = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, dtype=DTYPE, attn_implementation="sdpa", device_map="cuda:0"
        )
        tok = AutoTokenizer.from_pretrained(MODEL_PATH)
        _model = jlens.from_hf(hf, tok)
        log.info("loaded %s in %s; d_model=%s", MODEL_PATH, DTYPE, _model.d_model)
    return _model


def record_cost(stage: str, seconds: float) -> None:
    costs = json.loads(COSTS_JSON.read_text()) if COSTS_JSON.exists() else {}
    costs[stage] = {
        "wall_clock_s": round(seconds, 1),
        "peak_gpu_mem_GiB": round(t.cuda.max_memory_allocated() / 2**30, 2),
        "peak_gpu_reserved_GiB": round(t.cuda.max_memory_reserved() / 2**30, 2),
        "dtype": str(DTYPE),
    }
    COSTS_JSON.write_text(json.dumps(costs, indent=2))
    log.info("⏱️ %s: %s", stage, costs[stage])


def timed(stage):
    def wrap(fn):
        def inner():
            t.cuda.reset_peak_memory_stats()
            start = time.time()
            fn()
            record_cost(stage, time.time() - start)
        return inner
    return wrap


# ---------------------------------------------------------------- stages


def stage_prompts():
    if PROMPTS_JSON.exists():
        return
    PROMPTS_JSON.write_text(json.dumps(cli.load_fit_prompts(ROUTER_PROMPTS)))
    log.info("saved %d WikiText prompts", ROUTER_PROMPTS)


@timed("smoke_bf16")
def stage_smoke():
    """bf16 finiteness check: residuals at every layer finite, and how big they get."""
    from workspace_lens.utils import record_activations

    prompts = json.loads(PROMPTS_JSON.read_text())[:8]
    report = {}
    for i, p in enumerate(prompts):
        _, acts = record_activations(model(), p, MAX_SEQ_LEN, list(range(N_LAYERS_EXPECTED)))
        for layer, a in acts.items():
            r = report.setdefault(str(layer), {"max_abs": 0.0, "finite": True})
            a = a.float()
            r["max_abs"] = max(r["max_abs"], float(a.abs().max()))
            r["finite"] = r["finite"] and bool(t.isfinite(a).all())
    (RUN / "smoke_bf16.json").write_text(json.dumps(report, indent=2))
    bad = [l for l, r in report.items() if not r["finite"]]
    log.info("smoke: max |resid| per layer %s", {l: round(r["max_abs"], 1) for l, r in report.items()})
    if bad:
        raise SystemExit(f"bf16 produced non-finite residuals at layers {bad}: STOP")


@timed("grade_correctness")
def stage_grade():
    """THEIR grade_model_correctness, run on Mistral-24B, for the five macro evals."""
    if CORRECTNESS_CSV.exists():
        return
    items = load_readout_eval_items(cli.READOUT_EVALS_DATA_DIR, slugs=MACRO_EVALS)
    runner = ReadoutEvalRunner(model(), {}, layers=LAYERS, max_seq_len=cli.RECIPE_READOUT_MAX_SEQ_LEN)
    df = runner.grade_model_correctness(items, hf_model_name=MODEL_PATH)
    df.to_csv(CORRECTNESS_CSV, index=False)
    log.info("graded: %s", pd.crosstab(df["eval"], df[MODEL_PATH].astype(str)))


@timed("fit_router")
def stage_router():
    if ROUTER_PT.exists():
        return
    router = cli.fit_router(
        model(),
        json.loads(PROMPTS_JSON.read_text())[:ROUTER_PROMPTS],
        layers=LAYERS,
        num_clusters=NUM_CLUSTERS,
        projection_dim=PROJECTION_DIM,
        skip_first_n_positions=SKIP_FIRST,
        max_seq_len=MAX_SEQ_LEN,
        seed=SEED,
    )
    router.save(str(ROUTER_PT))


def _shard(mode: str) -> str:
    config = LensConfig(
        hf_model_name=MODEL_PATH,
        checkpoint_name=f"shards_{mode}",
        artifacts_base_dir=str(RUN / "artifacts"),
        source_layers=LAYERS,
        relative_end_transport_layer=-1,
        jacobian_rows_per_pass=ROWS_PER_PASS,  # their CLI default 16; A1 item 6
        max_seq_len=MAX_SEQ_LEN,
        skip_first_n_positions=SKIP_FIRST,
        checkpoint_every_n_prompts=4,
        lrp_mode=mode,
    )
    return cli.fit_shard(
        model(),
        json.loads(PROMPTS_JSON.read_text())[:FIT_PROMPTS],
        routers=[ActivationRouterCollection.load(str(ROUTER_PT))],
        shard_idx=0,
        num_shards=1,
        config=config,
    )


def _shard_and_merge(mode: str):
    if EXPERTS[mode].exists() and POOLED[mode].exists():
        return
    shard_dir = _shard(mode)
    experts = cli.merge_experts(
        [shard_dir], num_clusters=NUM_CLUSTERS, checkpoint_name=f"experts_{mode}", device="cuda"
    )
    for layer, e in experts.experts_L_dict_EFN.items():
        if not t.isfinite(e).all():
            raise SystemExit(f"non-finite expert Jacobian at layer {layer} ({mode}): STOP")
    experts.save(str(EXPERTS[mode]))
    experts.pooled_lens(checkpoint_name=f"pooled_{mode}").save(str(POOLED[mode]), dtype=t.float32)
    fb = {str(l): b.nonzero().flatten().tolist() for l, b in experts.fallback_L_dict_Bool_E.items()}
    (RUN / f"fallback_experts_{mode}.json").write_text(json.dumps(fb))
    log.info("%s: experts + pooled lens saved; fallback experts %s", mode, fb)


@timed("fit_shard_merge_rlens")
def stage_shard_rlens():
    _shard_and_merge("rlens")


@timed("fit_shard_merge_none")
def stage_shard_none():
    _shard_and_merge("none")


@timed("fit_weights")
def stage_fitw():
    if JPP_LENS.exists():
        return
    items, fitting_items, excluded = cli.load_items_and_exclusions(
        model(),
        eval_data_dir=cli.READOUT_EVALS_DATA_DIR,
        correctness_csv=str(CORRECTNESS_CSV),
        hf_model_name=MODEL_PATH,
        layers=LAYERS,
        readout_max_seq_len=cli.RECIPE_READOUT_MAX_SEQ_LEN,
        items_spec=f"fit:{SEED}",
        fit_fraction=FIT_FRACTION,
    )
    weighting, lens = cli.fit_weights(
        model(),
        ExpertJacobians.load(str(EXPERTS["rlens"])),
        items,
        layers=LAYERS,
        excluded_token_ids=excluded,
        cache_path=str(RESID_CACHE),
        checkpoint_name="jpp",
        hf_model_name=MODEL_PATH,
        fitting_item_names=[i.name for i in fitting_items],
    )
    lens.save(str(JPP_LENS), dtype=t.float32)
    weighting.save(str(RUN / "lens_Jpp_expert_weights.json"))
    (RUN / "fit_split.json").write_text(json.dumps({
        "fitting_items": [[i.eval_slug, i.name] for i in fitting_items],
        "n_items_after_correctness_filter": len(items),
        "train_macro_pass": {str(l): w.train_macro_pass for l, w in weighting.learned_weights_L_dict.items()},
    }, indent=2))


def _evaluate(filtered: bool, tag: str):
    out = RUN / f"ranks_{tag}.csv"
    if out.exists():
        return
    m = model()
    lenses = {
        "J": load_lens_file(str(POOLED["none"]), hf_model_name=MODEL_PATH),
        "R": load_lens_file(str(POOLED["rlens"]), hf_model_name=MODEL_PATH),
        "Jpp": load_lens_file(str(JPP_LENS), hf_model_name=MODEL_PATH),
    }
    items, held_out, excluded = cli.load_items_and_exclusions(
        m,
        eval_data_dir=cli.READOUT_EVALS_DATA_DIR,
        correctness_csv=str(CORRECTNESS_CSV),
        hf_model_name=MODEL_PATH,
        layers=LAYERS,
        readout_max_seq_len=cli.RECIPE_READOUT_MAX_SEQ_LEN,
        items_spec=f"held-out:{SEED}",
        fit_fraction=FIT_FRACTION,
    )
    ranks, passdf = cli.evaluate(
        m, lenses, held_out, layers=LAYERS, excluded_token_ids=excluded if filtered else []
    )
    ranks.to_csv(out, index=False)
    passdf.to_csv(RUN / f"pass_at_k_{tag}.csv", index=False)
    (RUN / f"heldout_{tag}.json").write_text(json.dumps({
        "n_items_after_correctness_filter": len(items),
        "n_heldout": len(held_out),
        "heldout_by_eval": pd.Series([i.eval_slug for i in held_out]).value_counts().to_dict(),
        "n_excluded_token_ids": len(excluded) if filtered else 0,
    }, indent=2))
    log.info("%s macro rows:\n%s", tag, passdf[passdf["eval"] == "macro"].to_string(index=False))


@timed("evaluate_filtered")
def stage_eval_filtered():
    _evaluate(True, "filtered")


@timed("evaluate_unfiltered")
def stage_eval_unfiltered():
    _evaluate(False, "unfiltered")


# (no Phase 6 stage: the Mistral-24B Phase 6 J-lens was lost in D2; amendment A1 item 4)


STAGES = {
    "prompts": stage_prompts,
    "smoke": stage_smoke,
    "grade": stage_grade,
    "router": stage_router,
    "shard_rlens": stage_shard_rlens,
    "shard_none": stage_shard_none,
    "fitw": stage_fitw,
    "eval_filtered": stage_eval_filtered,
    "eval_unfiltered": stage_eval_unfiltered,
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    wanted = sys.argv[1:] or ["all"]
    for name, fn in STAGES.items():
        if "all" in wanted or name in wanted:
            log.info("=== stage %s ===", name)
            fn()
    log.info("🐙 done: %s", wanted)
