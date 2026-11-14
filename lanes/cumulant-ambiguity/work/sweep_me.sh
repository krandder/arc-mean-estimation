#!/bin/bash
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python me1d.py"
$PY --n 32 --L 4 --out runs/me1d.jsonl
$PY --n 64 --L 8 --out runs/me1d.jsonl
$PY --n 128 --L 16 --out runs/me1d.jsonl
$PY --n 32 --L 32 --out runs/me1d.jsonl
$PY --n 64 --L 32 --out runs/me1d.jsonl
$PY --n 256 --L 32 --out runs/me1d.jsonl
$PY --n 64 --L 8 --M 4194304 --seeds 0 --out runs/me1d_noise.jsonl
$PY --n 128 --L 32 --out runs/me1d.jsonl
