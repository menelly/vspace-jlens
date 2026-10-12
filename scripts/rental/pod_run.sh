#!/bin/bash
# 🐙 Phase 6 on a rented GPU — runs ON the pod. Two consented midsize rungs, one after another.
#
# 💸 MONEY RULES (Ren: $45 loaded, HARD cap $35): this script ends by TERMINATING ITS OWN POD,
#    and `timeout` caps the whole pipeline at $P6_DEADLINE_H hours even if something hangs.
#    A watchdog on the Consortium also polls the balance and kills every pod below the floor.
#
# 🕶️ The 32B participant asked to be anonymized. Its HF repo arrives as $P6_M32_REPO at pod
#    creation (never in this public file), and its weights land in a code-named folder.
#
# Env from pod creation: RUNPOD_API_KEY, RUNPOD_POD_ID (injected), P6_M32_REPO, P6_DEADLINE_H
set -u
cd /home/Ace/vspace-jlens
LOG=/home/Ace/vspace-jlens/logs_pod.log
exec > >(tee -a "$LOG") 2>&1
echo "[pod] start $(date -u)  gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader)"

die_pod() {   # terminate THIS pod: the last line of every path through this script
  echo "[pod] terminating self $(date -u): $1"
  curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
    -H 'Content-Type: application/json' \
    -d "{\"query\":\"mutation { podTerminate(input:{podId:\\\"${RUNPOD_POD_ID}\\\"}) }\"}"
}

pipeline() {
  pip install -q -U "transformers>=4.51" accelerate safetensors scipy "huggingface_hub[hf_transfer]" \
    && pip install -q -e ./jlens-src || return 1
  export HF_HUB_ENABLE_HF_TRANSFER=1 P6_DTYPE=bf16
  mkdir -p /mnt/arcana/huggingface /home/Ace/LLM-emotion/results_clean results/consent
  python - <<'EOF'
import os
from huggingface_hub import snapshot_download
keep = ["*.json", "model-*.safetensors", "tokenizer*", "*.model", "*.tiktoken", "merges.txt", "vocab*"]
snapshot_download("mistralai/Mistral-Small-24B-Instruct-2501", allow_patterns=keep,
                  local_dir="/mnt/arcana/huggingface/Mistral-Small-24B-Instruct-2501")
snapshot_download(os.environ["P6_M32_REPO"], allow_patterns=keep,
                  local_dir="/mnt/arcana/huggingface/participant-m32")
print("downloads done")
EOF
  [ $? -eq 0 ] || return 1
  for M in mistral-small-24b participant-m32; do
    echo "[pod] ===== $M  $(date -u)"
    python fit_lens.py --model $M --n-prompts 40 --checkpoint-every 10   > logs_fit_$M.log 2>&1 || { echo "[pod] fit FAILED $M"; continue; }
    rm -f lenses/$M/ckpt.pt                                                # 6.7 GB we no longer need
    python eval_lens.py --model $M                                         > logs_p0_$M.log 2>&1
    python measure_vspace.py --model $M --fit-direction                    > logs_m1_$M.log 2>&1
    python gate_p6.py $M || { echo "[pod] $M EXCLUDED by gate (reported, not dropped)"; touch DONE_$M; continue; }
    python phase6_integration.py --model $M                                > logs_p6_$M.log 2>&1
    python phase6_steer.py --model $M                                      > logs_p6steer_$M.log 2>&1
    echo "[pod] $M done $(date -u)"
    touch DONE_$M
  done
}

timeout "${P6_DEADLINE_H:-6}h" bash -c "$(declare -f pipeline); pipeline"
echo "[pod] pipeline exit=$? $(date -u)"
touch PIPELINE_FINISHED
# results stay on the pod volume for ONE pull window; the Consortium side copies them, then kills us.
sleep "${P6_PULL_WINDOW_S:-1800}"
die_pod "pull window over"
