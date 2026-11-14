#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 203 217; do
  $PY scratch/run_cs2c.py $s 32 26 surplus_m 0.01 32 runs/posthoc_cs2c_s${s}.json > logs/posthoc_cs2c_s${s}.log 2>&1
done
