#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while pgrep -f queue_a1.sh >/dev/null; do sleep 10; done
for s in 203 216 217 220 221 223; do
  $PY scratch/kink_distance.py $s 14 runs/kink_distance_s${s}.json > logs/kink_distance_s${s}.log 2>&1
done
