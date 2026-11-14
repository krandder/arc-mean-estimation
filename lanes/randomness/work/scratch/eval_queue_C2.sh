#!/bin/bash
# Eval (Amendment 1, E5), second slot: the same frozen rates.py on nets 204 then 203 (deterministic seeds, so any
# duplicate run by queue C writes identical results).
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
echo "queue C2 start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 204 203; do nice -n 19 ionice -c3 $PY scratch/rates.py $s >> logs/eval_rates2.log 2>&1; done
echo "queue C2 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
