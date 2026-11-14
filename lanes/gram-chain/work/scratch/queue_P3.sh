#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
while pgrep -f "queue_P1b.sh" > /dev/null; do sleep 30; done
/home/agent/.venvs/arc-noisy/bin/python -W ignore scratch/partA.py share 1024
echo QUEUE_P3_DONE
