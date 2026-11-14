#!/bin/bash
# Queue B: B2 full-recursion benchmark at n = 64 and 256 (PREREG Part 1).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_rec.py 64 8 $s --variants gauss,radg,futnl16,futnl32,pca16,pca32,rand16 --log2N 18 >> logs/eval_rec.log 2>&1
done
for s in 200 201 202 203 204; do
  $PY scratch/run_rec.py 256 32 $s --variants gauss,futnl16,futnl64,pca64,futnl128,radg --log2N 18 >> logs/eval_rec.log 2>&1
done
echo "queue B done $(date -u +%H:%M:%SZ)" >> logs/queue.log
