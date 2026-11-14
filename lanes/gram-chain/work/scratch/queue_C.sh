#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY="/home/agent/.venvs/arc-noisy/bin/python -W ignore"
while pgrep -f "queue_A1.sh" > /dev/null; do sleep 30; done
for n in 8 16 32 64; do $PY scratch/partC.py $n 5000 32; done
$PY scratch/partC.py 128 5000 24
$PY scratch/partC.py 256 5000 16
echo QUEUE_C_DONE
