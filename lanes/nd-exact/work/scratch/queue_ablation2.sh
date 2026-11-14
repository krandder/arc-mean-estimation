#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in "$@"; do
  $PY scratch/posthoc_unb_ablation.py $s 32 > logs/posthoc_unb_ablation2_s${s}.log 2>&1
done
