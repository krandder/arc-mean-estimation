#!/bin/bash
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_rec.py 128 16 9500 --variants gauss,radg,futnl8,futnl16,futnl32,futnl64,pca16,pca32,pca64,rand32 --log2N 18 --tag _dev >> logs/dev_rec_128_9500.log 2>&1
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_cut.py 128 16 9500 --cuts 1,2,4,8,12 --ks 16,32 --condks 4,8,16,32,64 --kinds futnl,pca,rand --log2N 18 --edge --edgeks 4,16 --edgekinds futnl,pca --tag _dev >> logs/dev_cut_128_9500.log 2>&1
