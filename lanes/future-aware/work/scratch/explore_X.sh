#!/bin/bash
# Exploratory queue X (not registered): order-4 truncation at n = 64 (dense ARC k4 'simple'), after queue C.
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 300 301 302; do
  $PY scratch/run_k4p.py 64 8 $s --variants none,futv16,futv32,pca16,pca32 --tag _x >> logs/explore_k4p.log 2>&1
  $PY scratch/run_k4p.py 64 8 $s --variants futv16,futv32 --orders 4 --tag _x4only >> logs/explore_k4p.log 2>&1
  $PY scratch/run_k4p.py 64 8 $s --variants futv16,futv32 --orders 3 --tag _x3only >> logs/explore_k4p.log 2>&1
done
echo "queue X done $(date -u +%H:%M:%SZ)" >> logs/queue.log
