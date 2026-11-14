#!/bin/bash
# EXPLORATORY (post hoc): (1) the n = 512 relevance spectrum on nets 501, 502; (2) how many Gaussian-mixture components
# the joint law in k = n/4 future directions needs as the width grows (single cut l = 1; nets 300 at n = 64, 128 and
# 200 at 256; M = 1, 4, 16, 64; 2^16 fit samples). Third heavy process next to nets 501 and 502.
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
echo "queue M start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 501 502; do
  $PY scratch/relevance_spectrum.py 512 64 $s --cuts 1,8,16,32 >> logs/relspec512.log 2>&1
done
$PY scratch/run_mix.py 64 8 300 --cuts 1 --k 16 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm >> logs/explore_mix.log 2>&1
$PY scratch/run_mix.py 128 16 300 --cuts 1 --k 32 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm >> logs/explore_mix.log 2>&1
$PY scratch/run_mix.py 256 32 200 --cuts 1 --k 64 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm >> logs/explore_mix.log 2>&1
echo "queue M done $(date -u +%H:%M:%SZ)" >> logs/queue.log
