#!/bin/bash
# Eval (registered, PREREG Amendment 4): width scaling of the single-cut oracle defects. Starts when queue Y has
# ended (at most 2 heavy processes: this one and queue X2).
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R="nice -n 19 ionice -c3 $PY"
while ! grep -q "evalY end" logs/queue.log; do sleep 20; done
echo "evalW start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for cfg in "32 4" "64 8" "128 16"; do
  set -- $cfg
  for s in 300 301 302 303 304 305 306 307; do
    $R scratch/run_width.py $1 $2 $s >> logs/eval_width.log 2>&1
  done
  echo "evalW n=$1 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
for s in 200 201 202 203 204; do
  $R scratch/run_width.py 256 32 $s >> logs/eval_width.log 2>&1
done
echo "evalW end $(date -u +%H:%M:%SZ)" >> logs/queue.log
