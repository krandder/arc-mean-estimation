#!/bin/bash
# Restored registered design (main 21:52Z). Part a: after the running stationary job (pid 1312436).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 1312436 2>/dev/null; do sleep 20; done
echo "B3a start $(date -u +%H:%M:%SZ)"
for s in 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 64 $s 0,1,3,7,15,31,63,127 4096; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 128 $s 0,1,3,7,15,31,63,127 4096; done
nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 256 1000 0,1,3,7,15,31,63,127,255 2048
echo "B3a done $(date -u +%H:%M:%SZ)"
