#!/bin/bash
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_rec.py 256 32 100 --variants gauss,futnl16,futnl64,pca64,futnl128 --log2N 18 --tag _dev >> logs/dev_rec_256_100.log 2>&1
