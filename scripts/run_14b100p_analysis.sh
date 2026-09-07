#!/bin/bash
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh
echo "[$(date -Is)] PHASE0-A on the 100-prompt 14B lens"
python -u eval_lens.py --model qwen-14b --quant nf4 --lens-from qwen-14b_nf4_100p > logs_p0_qwen14b_100p.log 2>&1
echo "[$(date -Is)] PHASE1 on the 100-prompt 14B lens"
python -u measure_vspace.py --model qwen-14b --quant nf4 --lens-from qwen-14b_nf4_100p > logs_m1_qwen14b_100p.log 2>&1
python -u summarize.py > SUMMARY.md 2>&1
echo "[$(date -Is)] 14B 100p ANALYSIS DONE"
