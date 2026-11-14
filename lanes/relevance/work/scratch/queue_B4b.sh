#!/bin/bash
# Replaces B3b (n = 256 without t = 256). After queue C (1206654).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 1206654 2>/dev/null; do sleep 30; done
echo "B4b start $(date -u +%H:%M:%SZ)"
for s in 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 128 $s 0,1,3,7,15,31,63,127 4096; done
nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 256 1001 0,1,3,7,15,31,63,127 2048
echo "B4b done $(date -u +%H:%M:%SZ)"
