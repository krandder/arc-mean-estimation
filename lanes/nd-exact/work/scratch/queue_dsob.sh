#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in "$@"; do
  $PY scratch/posthoc_dsob.py $s 16 64 > logs/posthoc_dsob_s${s}.log 2>&1
done
