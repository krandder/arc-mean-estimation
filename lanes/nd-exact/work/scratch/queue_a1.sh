#!/bin/bash
# Amendment 1 eval runs (after the Part 1 eval queue finishes)
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while pgrep -f queue_slot2.sh >/dev/null; do sleep 10; done
for s in 203 216 217 220 221 223; do
  $PY frozen/run_cs2b.py $s 32 26 surplus_m 0.01 32 runs/cs2b_s${s}.json > logs/cs2b_s${s}.log 2>&1
  $PY frozen/run_unbiased.py $s 20 12,14,16 8 runs/unbiased_s${s}.json > logs/unbiased_s${s}.log 2>&1
done
$PY frozen/depth1_rate3.py runs/depth1_rate3.json > logs/depth1_rate3.log 2>&1
