#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY="/home/agent/.venvs/arc-noisy/bin/python -W ignore"
while kill -0 894819 2>/dev/null; do sleep 20; done
for s in 0.001 0.01 0.1; do $PY scratch/partB.py inputVP 256 --L 32 --sigma $s; $PY scratch/partB.py inputVP 8 --L 256 --sigma $s; $PY scratch/partB.py inputVP 64 --L 64 --sigma $s; done
for n in 8 16 32 64; do $PY scratch/partC.py $n 5000 32; done
$PY scratch/partC.py 128 5000 24
$PY scratch/partC.py 256 5000 16
echo QUEUE_P1B_DONE
