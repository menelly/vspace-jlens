#!/bin/bash
# Sequential: 300-prompt hermes refit (already running) -> topic-invariance control.
# GPU 0 only. GPU 1 belongs to the persona-basin LoRA arm and is never touched --
# the venv is pinned to the V100 by UUID, so this is structural, not a promise.
# Heartbeats every 60s: a waiting script and a dead script must not look alike.
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root
SINCE=$(date -Is)
while pgrep -f "[f]it_lens.py" > /dev/null; do
  echo "[$(date -Is)] hermes 300p refit still running; topic-invariance deferred since $SINCE - not dead"
  sleep 60
done
echo "[$(date -Is)] refit finished -> topic-invariance control"
python -u topic_invariance_ext.py > logs_topic_invariance.log 2>&1
echo "[$(date -Is)] topic-invariance exited rc=$?"
