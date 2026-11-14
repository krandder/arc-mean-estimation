#!/bin/bash
# Eval (registered, PREREG part 1): 256 x 32 structure runs (E1), then the head-to-head at ARC's budget (E2).
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
echo "queue A start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do
  nice -n 19 ionice -c3 $PY scratch/structure.py $s 256 32 >> logs/eval_struct_256.log 2>&1
done
echo "queue A E1 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do
  nice -n 19 ionice -c3 $PY scratch/combo.py $s >> logs/eval_combo.log 2>&1
done
echo "queue A done $(date -u +%H:%M:%SZ)" >> logs/queue.log
