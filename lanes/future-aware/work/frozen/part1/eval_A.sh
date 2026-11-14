#!/bin/bash
# Queue A: B1 single-cut benchmark on all evaluation nets (PREREG Part 1).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_cut.py 64 8 $s --cuts 1,2,4,6 --ks 16 --condks 4,16,32 --kinds fut,futnl,pca,rand --log2N 18 --edge --edgeks 4,16 --edgekinds futnl,pca >> logs/eval_cut.log 2>&1
done
for s in 200 201 202 203 204; do
  $PY scratch/run_cut.py 256 32 $s --cuts 1,4,8,16,24 --ks 16,64 --condks 4,16,64,128 --kinds futnl,pca,rand --log2N 18 --edge --edgeks 4,16 --edgekinds futnl,pca >> logs/eval_cut.log 2>&1
done
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_cut.py 128 16 $s --cuts 1,2,4,8,12 --ks 16,32 --condks 4,16,32,64 --kinds fut,futnl,pca,rand --log2N 18 --edge --edgeks 4,16 --edgekinds futnl,pca >> logs/eval_cut.log 2>&1
done
echo "queue A done $(date -u +%H:%M:%SZ)" >> logs/queue.log
