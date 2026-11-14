#!/bin/bash
# Eval (Amendment 2, E6): 512 x 64 test of astra's round-2 prediction on fresh nets 500-502.
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
echo "queue D start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 500 501 502; do
  nice -n 19 ionice -c3 $PY scratch/structure.py $s 512 64 --quick >> logs/eval_512.log 2>&1
  nice -n 19 ionice -c3 $PY scratch/noise.py $s 512 64 --P 2048 >> logs/eval_512.log 2>&1
done
echo "queue D done $(date -u +%H:%M:%SZ)" >> logs/queue.log
