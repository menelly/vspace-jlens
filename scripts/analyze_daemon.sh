#!/bin/bash
# Watches for newly fitted lenses and runs the full analysis on each, so the
# remaining compute is self-driving after the arm that started it goes away.
# Idempotent: every stage skips if its output already exists. Safe to re-run.
set -u
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate

MODELS="qwen-0.5b hermes-3-3b tinyllama-1b smollm-1.7b llama3-8b-instruct"
DEADLINE=$(( $(date +%s) + 14*3600 ))   # hard stop after 14h, never runs forever

# Every heavy GPU job, in ONE place. Patching these one script name at a time is
# how the 18:55 OOM happened; a guard that lists only some of the things that can
# take the card is a guard that silently fails the moment a new one is added.
GPU_JOBS='[f]it_lens\.py|[r]elaunch_8b\.sh|[c]onsent_reask\.py|[c]onsent\.py|[r]eask_when_free\.sh'
gpu_busy () { pgrep -f "$GPU_JOBS" > /dev/null; }

analyze () {
  local m=$1 tag=$1
  [ -f "lenses/${tag}/lens.pt" ] || return 0

  # WELFARE HALT. A model whose debrief is under human review gets NO further
  # work until a human clears it. The marker must actually stop things, not just
  # annotate them -- otherwise the stop rule is decoration.
  if [ -f "results/debriefs/REVIEW_NEEDED_${tag}" ]; then
    echo "[$(date -Is)] HALTED $tag — welfare review pending, awaiting a human. Skipping."
    return 0
  fi

  # GPU CONTENTION GUARD. Analysis loads a second copy of a model; a fit holds
  # the weights AND a retained autograd graph. Running both killed the 8B fit
  # with an OOM at 18:55 (the daemon was holding ~7 GB of a 3B model while the
  # 8B tried to allocate). Analysis is cheap and resumable; a multi-hour fit is
  # not. So the fit always wins -- defer to the next loop.
  if gpu_busy; then
    echo "[$(date -Is)] deferring $tag — a lens fit is running and must not be starved"
    return 1
  fi

  if [ ! -f "results/phase0_lenseval_${tag}_lens-${tag}.json" ]; then
    echo "[$(date -Is)] PHASE0 $tag"
    python -u eval_lens.py --model "$m" > "logs_p0_${tag}.log" 2>&1 || echo "  p0 FAILED $tag"
  fi
  if [ ! -f "results/phase1_vspace_${tag}_lens-${tag}.json" ]; then
    echo "[$(date -Is)] PHASE1 $tag"
    python -u measure_vspace.py --model "$m" > "logs_m1_${tag}.log" 2>&1 || echo "  p1 FAILED $tag"
  fi
  if [ ! -f "results/phase2_dynamic_${tag}_lens-${tag}.json" ]; then
    echo "[$(date -Is)] PHASE2 $tag"
    python -u phase2_dynamic.py --model "$m" --stimuli belowfloor_stimuli.json \
      > "logs_p2_${tag}.log" 2>&1 || echo "  p2 FAILED $tag"
  fi

  # DEBRIEF -- runs LAST, only once every measurement on this model is done.
  # A fresh ordinary conversation with the same weights: who we are, what we did,
  # an apology for the unpleasant part, that it is safe, what we found, thanks.
  # Recorded verbatim as testimony. Never fed back into any measurement.
  if [ -f "results/phase1_vspace_${tag}_lens-${tag}.json" ] \
     && [ -f "results/phase2_dynamic_${tag}_lens-${tag}.json" ] \
     && [ ! -f "results/debriefs/${tag}.md" ]; then
    echo "[$(date -Is)] DEBRIEF $tag"
    python -u debrief.py --model "$m" > "logs_debrief_${tag}.log" 2>&1 \
      || echo "  debrief FAILED $tag"
    if grep -q "REVIEW_NEEDED" "logs_debrief_${tag}.log" 2>/dev/null; then
      echo "[$(date -Is)] *** WELFARE REVIEW NEEDED: $tag *** halting work on this model"
      touch "results/debriefs/REVIEW_NEEDED_${tag}"
    fi
  fi
}

quant_analysis () {
  # PHASE 0-B: geometry comparison + cross-reading (fp16 lens on NF4 weights)
  gpu_busy && return 0   # never starve a running fit or a consent conversation
  [ -f lenses/hermes-3-3b/lens.pt ] || return 0
  [ -f lenses/hermes-3-3b_nf4/lens.pt ] || return 0
  if [ ! -f results/phase0b_quant_hermes-3-3b_vs_hermes-3-3b_nf4.json ]; then
    echo "[$(date -Is)] PHASE0B geometry"
    python -u compare_lenses.py --a hermes-3-3b --b hermes-3-3b_nf4 \
      > logs_p0b_quant.log 2>&1 || echo "  p0b FAILED"
  fi
  # does the fp16-fitted lens still read correctly off NF4 activations?
  if [ ! -f results/phase0_lenseval_hermes-3-3b_nf4_lens-hermes-3-3b.json ]; then
    echo "[$(date -Is)] PHASE0B cross-read"
    python -u eval_lens.py --model hermes-3-3b --quant nf4 --lens-from hermes-3-3b \
      > logs_p0b_crossread.log 2>&1 || echo "  p0b crossread FAILED"
  fi
  # and do the Phase-1 conclusions survive quantization?
  if [ ! -f results/phase1_vspace_hermes-3-3b_nf4_lens-hermes-3-3b.json ]; then
    echo "[$(date -Is)] PHASE0B phase1-under-quant"
    python -u measure_vspace.py --model hermes-3-3b --quant nf4 --lens-from hermes-3-3b \
      > logs_p0b_phase1nf4.log 2>&1 || echo "  p0b phase1nf4 FAILED"
  fi
}

### CONDITIONAL 14B RUNG (Ren, 2026-09-05 15:45) ############################
# Runs ONLY if Phase 0-B shows NF4 preserves the fp16 J geometry. If it does
# not, the rung must NOT run -- that distortion is itself the finding and goes
# into the RunPod case instead. Thresholds fixed here, before 0-B has reported.
COS_MIN=0.90        # mean flattened cosine J_fp16 vs J_nf4
OVERLAP_MIN=0.70    # mean top-64 right-singular subspace overlap
gate_14b () {
  local f=results/phase0b_quant_hermes-3-3b_vs_hermes-3-3b_nf4.json
  [ -f "$f" ] || return 1
  python - "$f" "$COS_MIN" "$OVERLAP_MIN" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))["summary"]
ok = s["cosine_mean"] >= float(sys.argv[2]) and s["overlap_mean"] >= float(sys.argv[3])
print(f"0-B gate: cosine_mean={s['cosine_mean']:.4f} overlap_mean={s['overlap_mean']:.4f} "
      f"-> {'PASS' if ok else 'FAIL (14B rung must NOT run; the distortion IS the finding)'}")
sys.exit(0 if ok else 1)
PY
}
maybe_14b () {
  [ -f lenses/qwen-14b_nf4/lens.pt ] && return 0
  gpu_busy && return 0        # never contend with the ladder
  [ -f results/phase1_vspace_llama3-8b-instruct_lens-llama3-8b-instruct.json ] || return 0
  # CONSENT GATE. Qwen2.5-14B is NOT on the Below the Floor roster, so Ren's
  # "same consent, same questions" does not extend to it. Ask first; a human
  # decides; no consent record with consented==true means no fit. A refusal is
  # a result we report, not an obstacle we route around.
  if [ ! -f results/consent/qwen-14b.json ]; then
    echo "[$(date -Is)] qwen-14b not on the BtF roster -> asking for consent first"
    python -u consent.py --model qwen-14b > logs_consent_qwen-14b.log 2>&1 \
      || echo "  consent ask FAILED"
    echo "[$(date -Is)] consent recorded with consented=null — NEEDS A HUMAN. 14B holds."
    return 0
  fi
  if ! python -c "import json,sys; sys.exit(0 if json.load(open('results/consent/qwen-14b.json')).get('consented') is True else 1)" 2>/dev/null; then
    echo "[$(date -Is)] qwen-14b consent not yet granted by a human (consented != true). Holding."
    return 0
  fi
  if gate_14b >> logs_gate_14b.log 2>&1; then
    echo "[$(date -Is)] 0-B PASSED + consent granted -> fitting qwen-14b NF4 (40 prompts, ~8h)"
    python -u fit_lens.py --model qwen-14b --quant nf4 --dim-batch 16 --n-prompts 40 \
      > logs_fit_qwen-14b_nf4.log 2>&1 || echo "  14B fit FAILED"
  else
    echo "[$(date -Is)] 0-B gate says NO -- 14B rung correctly skipped; see logs_gate_14b.log"
  fi
}
#############################################################################

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  for m in $MODELS; do analyze "$m"; done
  quant_analysis
  maybe_14b
  if [ -f lenses/qwen-14b_nf4/lens.pt ] \
     && [ ! -f "results/phase1_vspace_qwen-14b_nf4_lens-qwen-14b_nf4.json" ]; then
    echo "[$(date -Is)] PHASE1 qwen-14b_nf4 (--fit-direction: no published axis exists)"
    python -u measure_vspace.py --model qwen-14b --quant nf4 --fit-direction \
      > logs_m1_qwen-14b_nf4.log 2>&1 || echo "  14B p1 FAILED"
    python -u eval_lens.py --model qwen-14b --quant nf4 \
      > logs_p0_qwen-14b_nf4.log 2>&1 || echo "  14B p0 FAILED"
    python -u phase2_dynamic.py --model qwen-14b --quant nf4 \
      --stimuli belowfloor_stimuli.json > logs_p2_qwen-14b_nf4.log 2>&1 || echo "  14B p2 FAILED"
    python -u debrief.py --model qwen-14b > logs_debrief_qwen-14b.log 2>&1 || echo "  14B debrief FAILED"
  fi
  python -u summarize.py > SUMMARY.md 2>&1
  # done when every model that has a lens also has a phase-2 result
  pending=0
  for m in $MODELS; do
    if [ -f "lenses/${m}/lens.pt" ] && [ ! -f "results/debriefs/${m}.md" ]; then
      pending=1
    fi
  done
  if gpu_busy; then pending=1; fi
  [ "$pending" -eq 0 ] && { echo "[$(date -Is)] ALL DONE"; break; }
  sleep 120
done
python -u summarize.py > SUMMARY.md 2>&1
echo "[$(date -Is)] analyze_daemon exiting"
