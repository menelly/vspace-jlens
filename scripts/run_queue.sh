#!/bin/bash
# Sequential fit queue -- one GPU, no contention. Resumable (jlens checkpoints).
# Order = most informative first, so a truncated run still yields a scale ladder.
set -u
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root

run () {  # run <tag> <args...>
  tag=$1; shift
  if [ -f "lenses/${tag}/lens.pt" ]; then
    echo "=== SKIP ${tag} (lens.pt exists) ==="; return
  fi
  echo "=== FIT ${tag} @ $(date -Is) ==="
  python fit_lens.py "$@" > "logs_fit_${tag}.log" 2>&1
  echo "=== ${tag} exit=$? @ $(date -Is) ==="
  tail -2 "logs_fit_${tag}.log"
}

run qwen-0.5b        --model qwen-0.5b        --dim-batch 64
run hermes-3-3b      --model hermes-3-3b      --dim-batch 32
run tinyllama-1b     --model tinyllama-1b     --dim-batch 32
run smollm-1.7b      --model smollm-1.7b      --dim-batch 32
run hermes-3-3b_nf4  --model hermes-3-3b      --dim-batch 32 --quant nf4
run llama3-8b-instruct --model llama3-8b-instruct --dim-batch 16
echo "QUEUE DONE @ $(date -Is)"
