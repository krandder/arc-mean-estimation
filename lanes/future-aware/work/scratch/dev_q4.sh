#!/bin/bash
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
while kill -0 3643422 2>/dev/null; do sleep 10; done
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_k3p.py 64 8 9500 --variants futmf2_8,futmf2_16,futmf2_32 --tag _dev2 >> logs/dev_k3p.log 2>&1
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_k3p.py 128 16 9500 --variants none,pca16,pca32,pca64,futmf2_32,futv16,futv32,futv64 --tag _dev >> logs/dev_k3p.log 2>&1
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_k3p.py 256 32 100 --variants none,futv64,pca64,futmf2_64,futv32 --tag _dev >> logs/dev_k3p.log 2>&1
