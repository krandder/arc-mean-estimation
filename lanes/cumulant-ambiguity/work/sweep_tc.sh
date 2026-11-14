#!/bin/bash
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python tc.py"
$PY --n 32 --L 8 --K 2 3 4 --M 1048576 --out runs/tc.jsonl
$PY --n 32 --L 8 --K 2 3 4 --M 262144 --seeds 0 --out runs/tc_noise.jsonl
$PY --n 64 --L 8 --K 2 3 --M 1048576 --out runs/tc.jsonl
$PY --n 128 --L 16 --K 2 --M 1048576 --out runs/tc.jsonl
$PY --n 16 --L 8 --K 2 3 4 --M 1048576 --out runs/tc.jsonl
$PY --n 128 --L 16 --K 2 3 --M 262144 --seeds 0 1 --out runs/tc.jsonl
