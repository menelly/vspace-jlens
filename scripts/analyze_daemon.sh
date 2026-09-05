#!/bin/bash
# Watches for newly fitted lenses and runs the full analysis on each, so the
# remaining compute is self-driving after the arm that started it goes away.
# Idempotent: every stage skips if its output already exists. Safe to re-run.
set -u
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate

MODELS="qwen-0.5b hermes-3-3b tinyllama-1b smollm-1.7b llama3-8b-instruct"
DEADLINE=$(( $(date +%s) + 14*3600 ))   # hard stop after 14h, never runs forever

analyze () {
  local m=$1 tag=$1
  [ -f "lenses/${tag}/lens.pt" ] || return 0

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
}

quant_analysis () {
  # PHASE 0-B: geometry comparison + cross-reading (fp16 lens on NF4 weights)
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

while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  for m in $MODELS; do analyze "$m"; done
  quant_analysis
  python -u summarize.py > SUMMARY.md 2>&1
  # done when every model that has a lens also has a phase-2 result
  pending=0
  for m in $MODELS; do
    if [ -f "lenses/${m}/lens.pt" ] && [ ! -f "results/phase2_dynamic_${m}_lens-${m}.json" ]; then
      pending=1
    fi
  done
  if pgrep -f "[f]it_lens.py" > /dev/null; then pending=1; fi
  [ "$pending" -eq 0 ] && { echo "[$(date -Is)] ALL DONE"; break; }
  sleep 120
done
python -u summarize.py > SUMMARY.md 2>&1
echo "[$(date -Is)] analyze_daemon exiting"
