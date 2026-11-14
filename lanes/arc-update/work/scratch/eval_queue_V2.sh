#!/bin/bash
# Eval (registered, PREREG Amendment 6): ideal projection recursions with the rank transport; 256 x 32 first.
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R="nice -n 19 ionice -c3 $PY"
echo "evalV2 start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do
  $R scratch/run_ipr2.py 256 32 $s >> logs/eval_ipr2.log 2>&1
done
echo "evalV2 n=256 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for cfg in "128 16" "64 8"; do
  set -- $cfg
  for s in 300 301 302 303 304 305 306 307; do
    $R scratch/run_ipr2.py $1 $2 $s >> logs/eval_ipr2.log 2>&1
  done
  echo "evalV2 n=$1 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
echo "evalV2 end $(date -u +%H:%M:%SZ)" >> logs/queue.log
