#!/usr/bin/env bash
# 🔬 J++ lens env on the Consortium (CHA-743). Its OWN venv: never pip into /home/codex/venv.
# Our GPUs are old (PG500 = sm_70 Volta, P40 = sm_61 Pascal); the cu128 torch wheels dropped those,
# so try the cu126 build of the pinned torch first and REPORT what actually runs, not what installed.
set -u
UV=/home/chaos/.local/bin/uv
V=/home/Ace/jpp-venv
cd /home/Ace/jpp_lens
echo "== $(date) creating venv (python 3.12)"
$UV venv --python 3.12 $V || exit 1
source $V/bin/activate
echo "== torch 2.11.0 from cu126"
$UV pip install "torch==2.11.0" --index-url https://download.pytorch.org/whl/cu126 \
  || { echo "== cu126 2.11 FAILED, trying latest cu126"; $UV pip install torch --index-url https://download.pytorch.org/whl/cu126; }
echo "== deps"
$UV pip install "transformers==5.14.1" "huggingface_hub==1.26.0" "numpy==2.5.1" "pandas==3.0.5" \
  "datasets==5.0.1" "pyarrow==25.0.0" "accelerate==1.12.0" "pytest==9.1.1"
$UV pip install -e . --no-deps
echo "== GPU check (a tiny matmul on EACH card; 'installed' is not 'runs')"
python - <<'PY'
import torch
print("torch", torch.__version__, "cuda", torch.version.cuda, "arch list", torch.cuda.get_arch_list())
for i in range(torch.cuda.device_count()):
    name = torch.cuda.get_device_name(i)
    try:
        a = torch.randn(256, 256, device=f"cuda:{i}", dtype=torch.float16)
        print(f"GPU{i} {name} cap={torch.cuda.get_device_capability(i)} matmul OK:", float((a @ a).float().abs().mean()))
    except Exception as e:
        print(f"GPU{i} {name} FAILED: {e}")
PY
echo "== their tiny CPU test suite"
python -m pytest -q src/workspace_lens/tests 2>&1 | tail -15
echo "== DONE $(date)"
