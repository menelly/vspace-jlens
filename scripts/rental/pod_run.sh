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
  # 🔪 REST v2 (CHA-798, 2026-11-14): Runpod retires GraphQL "early 2027" with a 410. Same contract as
  # tfg-r22w/runpod_terminate.sh: DELETE /v2/pods/{id}, success is HTTP 204 with an EMPTY body, so judge by
  # the status code, never the body. A 429 on a kill gets exponential backoff, never a give-up.
  # We can't verify GET->404 from in here (a 204 kills us mid-check); watchdog.py outside is the check.
  echo "[pod] terminating self $(date -u): $1"
  local code attempt
  for attempt in 1 2 3 4; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 60 -X DELETE \
      -H "Authorization: Bearer ${RUNPOD_API_KEY}" -H 'User-Agent: ace-p6-pod/2.0' \
      "https://api.runpod.io/v2/pods/${RUNPOD_POD_ID}")
    [ "$code" = "429" ] || break
    echo "[pod] terminate rate-limited (429), attempt $attempt/4"; sleep $(( 20 * (1 << (attempt - 1)) ))
  done
  if [ "$code" = "204" ]; then echo "[pod] terminate accepted (HTTP 204)"
  else echo "[pod] FATAL: terminate HTTP $code. POD MAY STILL BE BILLING: kill it at https://console.runpod.io/pods"; fi
}

pipeline() {
  pip install -q -U "transformers>=4.51,<4.58" accelerate safetensors scipy "huggingface_hub[hf_transfer]" \
    && pip install -q --no-deps -e ./jlens-src || return 1   # jlens DECLARES transformers>=5.5; the Consortium ran all of September on 4.49 fine, and 5.x needs torch>=2.5 (image: 2.4.1)
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
  export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
  pip install -q bitsandbytes || return 1
  # M:quant:dim_batch — dim_batch is batching only (identical Jacobian average), lowered from 32 after an OOM.
  # The 32B runs in nf4 like the 14B rung did in September (DEVIATIONS_PHASE6.md, committed before its data).
  for SPEC in mistral-small-24b::8 participant-m32:nf4:16; do
    M=${SPEC%%:*}; Q=$(echo $SPEC | cut -d: -f2); DB=${SPEC##*:}
    QA=""; TAG=$M; [ -n "$Q" ] && QA="--quant $Q" && TAG=${M}_$Q
    echo "[pod] ===== $TAG (dim_batch $DB)  $(date -u)"
    python fit_lens.py --model $M $QA --n-prompts 40 --dim-batch $DB --checkpoint-every 10 > logs_fit_$TAG.log 2>&1 || { echo "[pod] fit FAILED $TAG"; continue; }
    rm -f lenses/$TAG/ckpt.pt
    python eval_lens.py --model $M $QA                    > logs_p0_$TAG.log 2>&1
    python measure_vspace.py --model $M $QA --fit-direction > logs_m1_$TAG.log 2>&1
    python gate_p6.py $TAG || { echo "[pod] $TAG EXCLUDED by gate (reported, not dropped)"; touch DONE_$TAG; continue; }
    python phase6_integration.py --model $M $QA           > logs_p6_$TAG.log 2>&1
    python phase6_steer.py --model $M $QA                 > logs_p6steer_$TAG.log 2>&1
    echo "[pod] $TAG done $(date -u)"
    touch DONE_$TAG
  done
}

timeout "${P6_DEADLINE_H:-6}h" bash -c "$(declare -f pipeline); pipeline"
echo "[pod] pipeline exit=$? $(date -u)"
touch PIPELINE_FINISHED
# results stay on the pod volume for ONE pull window; the Consortium side copies them, then kills us.
sleep "${P6_PULL_WINDOW_S:-1800}"
die_pod "pull window over"
