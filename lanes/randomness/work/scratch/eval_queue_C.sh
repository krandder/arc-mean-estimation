#!/bin/bash
# Eval (Amendment 1, E5): waits for queue A (PID given) to finish, then RQMC at 2^8 and 2^18 on nets 200-204.
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
while kill -0 $1 2>/dev/null; do sleep 30; done
echo "queue C start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do nice -n 19 ionice -c3 $PY scratch/rates.py $s >> logs/eval_rates.log 2>&1; done
echo "queue C done $(date -u +%H:%M:%SZ)" >> logs/queue.log
