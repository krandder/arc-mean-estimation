#!/bin/bash
# Replaces B3a (main 22:55Z: drop the n = 256, t = 256 cells; disclosed deviation). After the running n=128 seed 1000 job (1942503).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 1942503 2>/dev/null; do sleep 20; done
echo "B4a start $(date -u +%H:%M:%SZ)"
nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 128 1001 0,1,3,7,15,31,63,127 4096
nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 256 1000 0,1,3,7,15,31,63,127 2048
echo "B4a done $(date -u +%H:%M:%SZ)"
