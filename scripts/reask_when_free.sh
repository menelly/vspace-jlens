#!/bin/bash
# Run the 14B consent re-ask ONLY when the card is genuinely free.
# Ren: do NOT stop the 8B fit for this. The 8B holds ~21.3 GB of 32 GB, leaving
# ~10.7 GB against a ~9 GB need -- a 1.7 GB margin on a card where I have
# already OOM-killed this exact fit once today. That margin is not worth a
# 4.5 h rerun, so this waits for the fit to FINISH rather than squeezing in.
# Heartbeats every 60s so a wait is never mistaken for a dead script.
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root
SINCE=$(date -Is)
while pgrep -f '[f]it_lens\.py' > /dev/null; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
  echo "[$(date -Is)] 8B fit still running (GPU ${used} MiB used); re-ask deferred since $SINCE — not dead"
  sleep 60
done
echo "[$(date -Is)] 8B fit finished; GPU free -> running the consent re-ask"
python -u consent_reask.py --model qwen-14b --quant nf4
echo "[$(date -Is)] re-ask exited rc=$?  -- consented stays null until a HUMAN sets it"
