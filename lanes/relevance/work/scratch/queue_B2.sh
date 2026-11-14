#!/bin/bash
# Replacement for queue B (deviation, compute: load ~32 at 21:38Z): n = 64 seeds 1001-1003, n = 128 seeds 1000-1001,
# n = 256 seeds 1000-1001 with t <= 128. Starts when the running n = 64 seed 1000 job (pid 1106015) has finished.
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 1106015 2>/dev/null; do sleep 20; done
echo "queue B2 start $(date -u +%H:%M:%SZ)"
for s in 1001 1002 1003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 64 $s 0,1,3,7,15,31,63,127 4096; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 128 $s 0,1,3,7,15,31,63,127 4096; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py stat 256 $s 0,1,3,7,15,31,63,127 2048; done
echo "queue B2 done $(date -u +%H:%M:%SZ)"
