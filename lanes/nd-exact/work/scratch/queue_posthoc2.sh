#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while pgrep -f "queue_dsob.sh $1" >/dev/null; do sleep 10; done
shift
for s in "$@"; do
  $PY scratch/posthoc_unb_ablation.py $s 32 > logs/posthoc_unb_ablation_s${s}.log 2>&1
  if [ "$s" != "203" ] && [ "$s" != "217" ]; then
    $PY scratch/run_cs2c.py $s 32 26 surplus_m 0.01 32 runs/posthoc_cs2c_s${s}.json > logs/posthoc_cs2c_s${s}.log 2>&1
  fi
done
