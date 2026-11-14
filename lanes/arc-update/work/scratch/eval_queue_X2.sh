#!/bin/bash
# Eval (registered, PREREG Part 1), replanned 06:12Z (logs/deviations.txt): 256 x 32 on seeds 201-204 without the slow
# rank statistics first; then rank 201; then k3 basic on 200-204; then ranks 202-204 and k3fa 200 if time allows.
# Starts after run_rank 200 (queue X's job) has finished.
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
R="nice -n 19 ionice -c3 $PY"
while [ ! -s runs/rank_s200.json ]; do sleep 20; done
echo "evalX2 start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 201 202 203 204; do
  $R scratch/run_lad.py 256 32 $s k1,k2,k2a,k3f >> logs/eval_lad_256.log 2>&1
  $R scratch/run_rqmc.py 256 32 $s s0 8,10,12,14,16 8 >> logs/eval_rqmc_256.log 2>&1
  $R scratch/run_attr.py $s s0 19 >> logs/eval_attr_$s.log 2>&1
  echo "evalX2 seed $s core done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
$R scratch/run_rank.py 201 s0 16 >> logs/eval_rank_201.log 2>&1
echo "evalX2 rank 201 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do
  $R scratch/run_lad.py 256 32 $s k3 >> logs/eval_lad_256.log 2>&1
done
echo "evalX2 k3 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 202 203 204; do
  $R scratch/run_rank.py $s s0 16 >> logs/eval_rank_$s.log 2>&1
done
$R scratch/run_lad.py 256 32 200 k3fa >> logs/eval_lad_256.log 2>&1
echo "evalX2 end $(date -u +%H:%M:%SZ)" >> logs/queue.log
