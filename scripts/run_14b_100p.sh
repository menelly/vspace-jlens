#!/bin/bash
# 100-prompt 14B refit. GPU 0 only (venv is UUID-pinned to the V100, so the
# persona-basin LoRA arm on GPU 1 is unreachable from here by construction).
#
# HF cache redirected to /mnt/arcana so downloads can never grow / again. Root is
# a SHARED disk: the 872 MB pythia-410m we pulled tonight was moved to arcana,
# but the other ~36 GB in /home/chaos/.cache/huggingface predates us (dolphin-8b
# 15G, Mistral-7B-v0.3 14G, speech models, April-August dates) and is NOT ours
# to relocate while another arm is mid-training. Left alone deliberately.
export HF_HOME=/mnt/nursery/hf-cache
export HF_HUB_CACHE=/mnt/nursery/hf-cache/hub
export TRANSFORMERS_CACHE=/mnt/nursery/hf-cache/hub
export HF_DATASETS_CACHE=/mnt/nursery/hf-cache/datasets
cd /home/Ace/vspace-jlens
source /home/codex/venv/bin/activate
source /home/Ace/vspace-jlens/hf_env.sh   # HOT=arcana COLD=nursery NOTHING=root
echo "[$(date -Is)] HF_HOME=$HF_HOME  root free: $(df -h / | tail -1 | awk "{print \$4}")"
python -u fit_lens.py --model qwen-14b --quant nf4 --corpus corpus.json \
  --tag qwen-14b_nf4_100p --dim-batch 16 --n-prompts 100 --checkpoint-every 20 \
  > logs_fit_qwen-14b_nf4_100p.log 2>&1
echo "[$(date -Is)] 14B 100p fit exited rc=$?  root free: $(df -h / | tail -1 | awk "{print \$4}")"
