#!/bin/bash
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python tc.py"
$PY --n 32 --L 4 --K 2 3 4 --M 1048576 --out runs/tc.jsonl
$PY --n 64 --L 8 --K 4 --M 262144 --seeds 0 --out runs/tc.jsonl
