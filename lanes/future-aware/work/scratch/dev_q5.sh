#!/bin/bash
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
while kill -0 3672826 2>/dev/null; do sleep 10; done
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/run_hyb.py 256 32 100 --layers 1,2,4,8,16,24 --qk 16 --tag _dev >> logs/dev_hyb_256.log 2>&1
