#!/bin/bash
# Part 1 evaluation queue A: narrow-deep (6 nets) then ARC 256 x 32 (4 nets).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 203 216 217 220 221 223; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py nd $s; done
for s in 4000 4001 4002 4003; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py arc $s; done
echo "queue A done $(date -u +%H:%M:%SZ)"
