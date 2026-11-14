#!/bin/bash
# Part 2 queue: starts when queue A (pid 1001859) has finished.
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 1001859 2>/dev/null; do sleep 30; done
echo "queue C start $(date -u +%H:%M:%SZ)"
for s in 4000 4001 4002 4003; do nice -n 19 ionice -c3 $PY scratch/eval_part2.py arc $s; done
for s in 300 301; do nice -n 19 ionice -c3 $PY scratch/eval_part2.py sync 16 256 $s; done
for s in 300 301; do nice -n 19 ionice -c3 $PY scratch/eval_part2.py sync 32 512 $s; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part2.py stat 64 $s 3,15; done
for s in 1000 1001; do nice -n 19 ionice -c3 $PY scratch/eval_part2.py stat 128 $s 3,15; done
echo "queue C done $(date -u +%H:%M:%SZ)"
