#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python tests/test_cubesphere.py > logs/test_cubesphere.log 2>&1
scratch/queue_truth.sh 64 22 16 21 103 111
