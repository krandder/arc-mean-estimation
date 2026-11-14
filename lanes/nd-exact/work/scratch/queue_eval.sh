#!/bin/bash
# registered eval runs; usage: queue_eval.sh seed...   (CS2 config fixed in PREREG)
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in "$@"; do
  $PY frozen/run_cs2.py $s 32 26 surplus 0.01 32 runs/cs2_s${s}.json > logs/cs2_s${s}.log 2>&1
  $PY frozen/baselines.py $s 48 runs/baselines_s${s}.json > logs/baselines_s${s}.log 2>&1
  $PY frozen/region_code.py $s 22 runs/region_code_s${s}.json > logs/region_code_s${s}.log 2>&1
done
