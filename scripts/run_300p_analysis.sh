#!/bin/bash
# Analysis of the 300-prompt hermes refit. Waits for topic-invariance to release
# the GPU first -- never contend, that is what caused the 18:55 OOM.
# Heartbeats so a wait is never mistaken for a dead script.
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root
SINCE=$(date -Is)
while pgrep -f "[t]opic_invariance_ext.py|[f]it_lens.py" > /dev/null; do
  echo "[$(date -Is)] GPU busy (topic-invariance); 300p analysis deferred since $SINCE - not dead"
  sleep 60
done
echo "[$(date -Is)] GPU free -> 300p analysis"
echo "[$(date -Is)] PHASE0-A on refit lens"
python -u eval_lens.py --model hermes-3-3b --lens-from hermes-3-3b_300p > logs_p0_hermes300p.log 2>&1
echo "[$(date -Is)] layerwise J-vs-logit discriminator on refit lens"
python -u layerwise_lens_check.py --model hermes-3-3b --lens-from hermes-3-3b_300p > logs_layerwise_hermes300p.log 2>&1
echo "[$(date -Is)] PHASE1 on refit lens"
python -u measure_vspace.py --model hermes-3-3b --lens-from hermes-3-3b_300p > logs_m1_hermes300p.log 2>&1
python -u summarize.py > SUMMARY.md 2>&1
echo "[$(date -Is)] 300p analysis DONE"
