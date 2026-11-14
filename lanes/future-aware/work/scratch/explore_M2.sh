#!/bin/bash
# EXPLORATORY (post hoc), after fixing run_mix.py's repeated mixture draws (deviations item 16): (1) the development
# single cut of section 5 again (n = 64, net 9500, k = 16, M = 1..32, same settings as before); (2) how many mixture
# components the joint law in k = n/4 future directions needs as the width grows (single cut l = 1; nets 300 at
# n = 64, 128 and 200 at 256; M = 1, 4, 16, 64; 2^16 fit samples).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
echo "queue M2 start $(date -u +%H:%M:%SZ)" >> logs/queue.log
$PY scratch/run_mix.py 64 8 9500 --cuts 1,2,4 --k 16 --Ms 1,2,4,8,16,32 --tag _dev2 >> logs/explore_mix2.log 2>&1
$PY scratch/run_mix.py 64 8 300 --cuts 1 --k 16 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm2 >> logs/explore_mix2.log 2>&1
$PY scratch/run_mix.py 128 16 300 --cuts 1 --k 32 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm2 >> logs/explore_mix2.log 2>&1
$PY scratch/run_mix.py 256 32 200 --cuts 1 --k 64 --Ms 1,4,16,64 --log2fit 16 --maxiter 100 --tag _xm2 >> logs/explore_mix2.log 2>&1
echo "queue M2 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
