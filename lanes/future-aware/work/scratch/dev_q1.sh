#!/bin/bash
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_cut.py 256 32 100 --cuts 1,4,8,16,24 --ks 16,64 --condks 4,16,64,128 --kinds futnl,pca,rand --log2N 18 --edge --edgeks 4,16 --edgekinds futnl,pca --tag _dev >> logs/dev_cut_256_100.log 2>&1
