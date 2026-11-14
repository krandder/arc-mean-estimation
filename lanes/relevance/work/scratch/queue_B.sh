#!/bin/bash
# Part 1 evaluation queue B: stationary n = 32, 64, 128 (4 nets), then n = 256 (2 nets).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 1000 1001 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 32 $s 0,1,3,7,15,31,63 4096; done
for s in 1000 1001 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 64 $s 0,1,3,7,15,31,63,127 4096; done
for s in 1000 1001 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 128 $s 0,1,3,7,15,31,63,127 4096; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 256 $s 0,1,3,7,15,31,63,127,255 2048; done
echo "queue B done $(date -u +%H:%M:%SZ)"
