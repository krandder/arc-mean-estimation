#!/bin/bash
# Eval (registered, PREREG Amendment 5): ideal projection recursions. Starts when queue W has ended (at most 2 heavy
# processes: this one and queue X2).
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R="nice -n 19 ionice -c3 $PY"
while ! grep -q "evalW end" logs/queue.log; do sleep 20; done
echo "evalV start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for cfg in "64 8" "128 16"; do
  set -- $cfg
  for s in 300 301 302 303 304 305 306 307; do
    $R scratch/run_ipr.py $1 $2 $s >> logs/eval_ipr.log 2>&1
  done
  echo "evalV n=$1 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
for s in 200 201 202 203 204; do
  $R scratch/run_ipr.py 256 32 $s >> logs/eval_ipr.log 2>&1
done
echo "evalV end $(date -u +%H:%M:%SZ)" >> logs/queue.log
