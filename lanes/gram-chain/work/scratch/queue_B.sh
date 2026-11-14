#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY="/home/agent/.venvs/arc-noisy/bin/python -W ignore"
while pgrep -f "queue_A2.sh" > /dev/null; do sleep 30; done
$PY scratch/partB.py input 64 --L 64
$PY scratch/partB.py input 8 --L 256
for s in 0.001 0.01 0.1; do $PY scratch/partB.py input 256 --L 32 --sigma $s; $PY scratch/partB.py input 8 --L 256 --sigma $s; done
for n in 16 64 256 1024; do $PY scratch/partB.py curves $n; done
for n in 16 64 256; do $PY scratch/partB.py pr $n; done
for n in 16 64 256 1024; do $PY scratch/partB.py pert $n; done
echo QUEUE_B_DONE
