#!/bin/bash
# Queue C: D1 (k3 with future-projected third cumulant), H1 (hybrid), and B2 at n = 128 (PREREG Part 1).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 200 201 202 203 204; do
  $PY scratch/run_k3p.py 256 32 $s --variants none,futv64,futv32,futv128,pca64,pca32,pca128,futmf2_64,futmf2_32,futmf2_128,futv16,pca16,futmf2_16 >> logs/eval_k3p.log 2>&1
done
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_k3p.py 64 8 $s --variants none,futv16,futv8,futv32,pca16,pca8,pca32,futmf2_16,futmf2_8,futmf2_32 >> logs/eval_k3p.log 2>&1
  $PY scratch/run_k3p.py 128 16 $s --variants none,futv32,futv16,futv64,pca32,pca16,pca64,futmf2_32,futmf2_16,futmf2_64 >> logs/eval_k3p.log 2>&1
done
for s in 200 201 202 203 204; do
  $PY scratch/run_hyb.py 256 32 $s --layers 1,2,4,8,16,24 --qk 16 >> logs/eval_hyb.log 2>&1
done
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_hyb.py 64 8 $s --layers 1,2,4,6 --qk 16 >> logs/eval_hyb.log 2>&1
  $PY scratch/run_hyb.py 128 16 $s --layers 1,2,4,8,12 --qk 16 >> logs/eval_hyb.log 2>&1
done
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_rec.py 128 16 $s --variants gauss,radg,futnl16,futnl32,futnl64,pca32,pca64,rand32 --log2N 18 >> logs/eval_rec.log 2>&1
done
echo "queue C done $(date -u +%H:%M:%SZ)" >> logs/queue.log
