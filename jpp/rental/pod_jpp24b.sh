#!/bin/bash
# 🐙 J++ 24B rung (CHA-743, amendment A1) — runs ON THE RENTED POD as root.
#
# 💸 D2's lesson, built in: this pod does NOT delete itself the moment it finishes. It writes
#    PIPELINE_FINISHED (or PIPELINE_FAILED), then WAITS for the Consortium supervisor to copy
#    /root/run and drop a PULLED marker. Only then does it terminate. Backstops: the pipeline has
#    a hard timeout ($JPP_DEADLINE_H, set by the launcher from the real $/hr), and if no PULL ever
#    comes the pod still dies after $JPP_PULL_WAIT_S, so it can never sit idle and bill forever.
#
# Env from pod creation: RUNPOD_API_KEY, RUNPOD_POD_ID (injected by RunPod), PUBLIC_KEY.
# Deadline comes in /root/bundle/deadline_h (written by the launcher). Readouts only.
set -u
mkdir -p /root/run
export LOG=/root/run/pod.log
exec > >(tee -a "$LOG") 2>&1
echo "[pod] start $(date -u)  $(nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader)"
DEADLINE_H=$(cat /root/bundle/deadline_h)
PULL_WAIT_S=${JPP_PULL_WAIT_S:-2400}
echo "[pod] pipeline deadline ${DEADLINE_H} h, pull wait ${PULL_WAIT_S} s"

die_pod() {   # the last line of every path through this script
  # 🔪 REST v2 (CHA-798, 2026-11-14): Runpod retires GraphQL "early 2027" with a 410. Same contract as
  # tfg-r22w/runpod_terminate.sh: DELETE /v2/pods/{id}, success is HTTP 204 with an EMPTY body, so judge by
  # the status code, never the body. A 429 on a kill gets exponential backoff, never a give-up.
  # We can't verify GET->404 from in here (a 204 kills us mid-check); the outside watchdog is the check.
  echo "[pod] terminating self $(date -u): $1"
  local code attempt
  for attempt in 1 2 3 4; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 60 -X DELETE \
      -H "Authorization: Bearer ${RUNPOD_API_KEY}" -H 'User-Agent: ace-jpp24b-pod/2.0' \
      "https://api.runpod.io/v2/pods/${RUNPOD_POD_ID}")
    [ "$code" = "429" ] || break
    echo "[pod] terminate rate-limited (429), attempt $attempt/4"; sleep $(( 20 * (1 << (attempt - 1)) ))
  done
  if [ "$code" = "204" ]; then echo "[pod] terminate accepted (HTTP 204)"
  else echo "[pod] FATAL: terminate HTTP $code. POD MAY STILL BE BILLING: kill it at https://console.runpod.io/pods"; fi
}

pipeline() {
  set -u
  cd /root
  echo "[pod] === setup $(date -u)"
  pip install -q uv || return 11
  # idempotent: a relaunch must not die on the venv the first launch built (12:06 UTC lesson)
  [ -x /root/venv/bin/python ] || uv venv -q --python 3.12 /root/venv || return 12
  source /root/venv/bin/activate
  # same pins as jpp/jpp_setup.sh on the Consortium (cu126 wheels cover sm_80/sm_90 too)
  CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | tr -d .)
  IDX=cu126; [ "${CC:-0}" -ge 100 ] && IDX=cu128   # Blackwell (sm_100/120) needs the cu128 wheels
  echo "[pod] compute_cap $CC -> torch index $IDX"
  uv pip install -q "torch==2.11.0" --index-url https://download.pytorch.org/whl/$IDX || return 13
  uv pip install -q "transformers==5.14.1" "huggingface_hub==1.26.0" "numpy==2.5.1" "pandas==3.0.5" \
    "datasets==5.0.1" "pyarrow==25.0.0" "accelerate==1.12.0" "pytest==9.1.1" || return 14
  uv pip install -q -e /root/jpp_lens --no-deps || return 15
  python -c "import torch; a=torch.randn(512,512,device='cuda',dtype=torch.bfloat16); print('[pod] torch', torch.__version__, torch.cuda.get_device_name(0), 'bf16 matmul ok', float((a@a).float().abs().mean()))" || return 16
  # our LRP patch, on THIS box, before any money goes to fitting (12 tests incl. a positive control)
  (cd /root/jpp_lens && CUDA_VISIBLE_DEVICES= python -m pytest -q src/workspace_lens/tests/test_lrp_llama_mistral.py 2>&1 | tail -3)
  (cd /root/jpp_lens && CUDA_VISIBLE_DEVICES= python -m pytest -q src/workspace_lens/tests/test_lrp_llama_mistral.py >/dev/null 2>&1) || return 17

  echo "[pod] === download $(date -u)"
  python - <<'EOF' || return 18
from huggingface_hub import snapshot_download
keep = ["*.json", "model-*.safetensors", "tokenizer*", "*.model", "*.tiktoken", "merges.txt", "vocab*"]
snapshot_download("mistralai/Mistral-Small-24B-Instruct-2501", allow_patterns=keep,
                  local_dir="/root/models/Mistral-Small-24B-Instruct-2501")
print("[pod] download done")
EOF
  du -sh /root/models/Mistral-Small-24B-Instruct-2501

  cp /root/bundle/wikitext_prompts_1000.json /root/run/
  export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
  # 🧵 nproc says 128 but the container's CFS quota is ~15 CPUs: torch spawned 210 threads and the CPU-side
  #    router (PCA + k-means) throttled for 25+ min (2026-10-13 ~12:05 UTC). Cap threads at the QUOTA.
  #    Thread count changes scheduling only, not the math.
  Q=$(awk '{ if ($1 != "max") printf "%d", $1/$2 }' /sys/fs/cgroup/cpu.max 2>/dev/null)
  export OMP_NUM_THREADS=${Q:-8} MKL_NUM_THREADS=${Q:-8}
  echo "[pod] cgroup CPU quota -> OMP_NUM_THREADS=$OMP_NUM_THREADS"
  cd /root/bundle
  echo "[pod] === stages prompts/smoke/grade/router $(date -u)"
  python run_cha743_24b.py prompts smoke grade router || return 21
  for MODE in rlens none; do
    echo "[pod] === shard_$MODE $(date -u)"
    if ! python run_cha743_24b.py shard_$MODE; then
      if grep -q -E "OutOfMemoryError|CUDA out of memory" "$LOG"; then
        echo "[pod] OOM in shard_$MODE -> retry with JPP_ROWS_PER_PASS=8 (amendment A1 item 6: batching only)"
        echo "rows_per_pass=8 used from shard_$MODE (OOM at 16)" >> /root/run/DEVIATION_rows_per_pass.txt
        rm -rf /root/run/artifacts/*/shards_$MODE
        JPP_ROWS_PER_PASS=8 python run_cha743_24b.py shard_$MODE || return 22
        export JPP_ROWS_PER_PASS=8   # keep the second mode on the same batching
      else
        return 23
      fi
    fi
  done
  echo "[pod] === fitw + evals $(date -u)"
  python run_cha743_24b.py fitw eval_filtered eval_unfiltered || return 24
  echo "[pod] === pipeline done $(date -u)"
}

timeout "${DEADLINE_H}h" bash -c "$(declare -f pipeline); pipeline"
RC=$?
pkill -f run_cha743_24b.py 2>/dev/null   # timeout only kills the direct child; on the pod itself -f is safe
echo "[pod] pipeline exit=$RC $(date -u)"
if [ $RC -eq 0 ]; then touch /root/run/PIPELINE_FINISHED; else echo "exit $RC" > /root/run/PIPELINE_FAILED; fi

# wait for the supervisor's copy to land; it terminates us itself after verifying. This is the backstop.
for i in $(seq 1 $((PULL_WAIT_S / 30))); do
  [ -f /root/run/PULLED ] && { sleep 60; die_pod "PULLED marker seen"; exit 0; }
  sleep 30
done
die_pod "no PULLED marker after ${PULL_WAIT_S}s"
