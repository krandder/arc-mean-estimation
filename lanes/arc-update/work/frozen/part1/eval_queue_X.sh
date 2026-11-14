#!/bin/bash
# Eval (registered, PREREG Part 1): 256 x 32 on seeds 200-204 (arc-noisy noiseless truths).
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1
R="nice -n 19 ionice -c3 $PY"
echo "evalX start $(date -u +%H:%M:%SZ)" >> logs/queue.log
$R scratch/run_rank.py control 0 16 >> logs/eval_rank_control.log 2>&1
for s in 200 201 202 203 204; do
  $R scratch/run_lad.py 256 32 $s k1,k2,k2a,k3f >> logs/eval_lad_256.log 2>&1
  $R scratch/run_rqmc.py 256 32 $s s0 8,10,12,14,16 8 >> logs/eval_rqmc_256.log 2>&1
  $R scratch/run_attr.py $s s0 19 >> logs/eval_attr_$s.log 2>&1
  $R scratch/run_rank.py $s s0 16 >> logs/eval_rank_$s.log 2>&1
  echo "evalX seed $s done $(date -u +%H:%M:%SZ)" >> logs/queue.log
done
for s in 200 201 202 203 204; do
  $R scratch/run_lad.py 256 32 $s k3 >> logs/eval_lad_256.log 2>&1
done
echo "evalX core end $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201; do
  $R scratch/run_lad.py 256 32 $s k3fa >> logs/eval_lad_256.log 2>&1
done
echo "evalX end $(date -u +%H:%M:%SZ)" >> logs/queue.log
