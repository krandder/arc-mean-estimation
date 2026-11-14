#!/bin/bash
# Eval (registered, PREREG Part 1): the ladder along L = n/8 at n = 32, 64, 128, seeds 300-307 (2^24-path truths).
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1
R="nice -n 19 ionice -c3 $PY"
echo "evalY start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for cfg in "32 4 k1,k2,k2a,k3,k3f,k3fa,k4,k4f" "64 8 k1,k2,k2a,k3,k3f,k3fa,k4,k4f" "128 16 k1,k2,k2a,k3,k3f,k3fa,k4f"; do
  set -- $cfg
  for s in 300 301 302 303 304 305 306 307; do
    $R scratch/truth.py $1 $2 $s 24 >> logs/eval_truth.log 2>&1
    $R scratch/run_lad.py $1 $2 $s $3 >> logs/eval_lad_small.log 2>&1
    $R scratch/run_rqmc.py $1 $2 $s runs/truth_n$1_L$2_s$s.npz 8,10,12,14 8 >> logs/eval_rqmc_small.log 2>&1
  done
  echo "evalY n=$1 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
echo "evalY end $(date -u +%H:%M:%SZ)" >> logs/queue.log
