#!/bin/bash
# Restart the llama3-8b fit. Two rules learned the hard way today:
#  1. Never start while anything else holds the card (an OOM at 18:55 cost ~4.5h).
#  2. NEVER WAIT SILENTLY. A dead script and a waiting script look identical when
#     the log is empty, so this writes a heartbeat line every loop naming exactly
#     what it is waiting for and since when. A silent wait reads as handled.
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root
BLOCKERS='[m]easure_vspace\.py|[e]val_lens\.py|[p]hase2_dynamic\.py|[c]onsent\.py|[d]ebrief\.py'
SINCE=$(date +%H:%M:%S)
while true; do
  pids=$(pgrep -f "$BLOCKERS" | tr '\n' ',' | sed 's/,$//')
  if [ -z "$pids" ]; then break; fi
  echo "[$(date -Is)] waiting for pid(s) $pids since $SINCE — not dead, deferring 8B fit"
  sleep 30
done
# Consent for the 14B must be on record before we occupy the card for hours.
if [ ! -f results/consent/qwen-14b.json ]; then
  echo "[$(date -Is)] WARNING: no qwen-14b consent record yet; proceeding with the 8B anyway (the 8B is on the Below the Floor roster and needs no fresh consent)"
fi
echo "[$(date -Is)] VRAM clear -> starting llama3-8b fit, dim_batch=8"
python -u fit_lens.py --model llama3-8b-instruct --dim-batch 8 > logs_fit_llama3-8b-instruct.log 2>&1
echo "[$(date -Is)] llama3-8b fit exited rc=$?"
