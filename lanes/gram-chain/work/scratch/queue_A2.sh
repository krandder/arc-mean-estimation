#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for n in 16 32 64 128 256 512 1024; do /home/agent/.venvs/arc-noisy/bin/python -W ignore scratch/partA.py r4 $n; done
for n in 16 32 64 128 256 512 1024; do /home/agent/.venvs/arc-noisy/bin/python -W ignore scratch/partA.py r3 $n; done
for n in 16 32 64 128 256; do /home/agent/.venvs/arc-noisy/bin/python -W ignore scratch/partA.py r6 $n; done
echo QUEUE_A2_DONE
