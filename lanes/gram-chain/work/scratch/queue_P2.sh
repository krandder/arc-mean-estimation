#!/bin/bash
cd /home/agent/workspaces/mats/work/gram-chain
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY="/home/agent/.venvs/arc-noisy/bin/python -W ignore"
while kill -0 1060489 2>/dev/null; do sleep 20; done
$PY scratch/partB.py input 8 --L 256
for s in 0.001 0.01 0.1; do $PY scratch/partB.py input 256 --L 32 --sigma $s; $PY scratch/partB.py input 8 --L 256 --sigma $s; done
for n in 16 64 256 1024; do $PY scratch/partB.py curves $n; done
for n in 16 64 256; do $PY scratch/partB.py pr $n; done
for n in 16 64 256 1024; do $PY scratch/partB.py pert $n; done
for n in 1024 512; do $PY scratch/partA.py r4 $n; done
for n in 16 32 64 128; do $PY scratch/partA.py r6 $n; done
for n in 16 32 64 128 256; do $PY scratch/partA.py r3 $n; done
echo QUEUE_P2_DONE
