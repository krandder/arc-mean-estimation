#!/bin/bash
# Amendment 3B: four fresh ARC nets for theory v3.3 and v2 (two chains in parallel; at most 2 heavy processes).
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
( for s in 4006 4008; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py arc $s; echo "net $s done $(date -u +%H:%M:%SZ)"; done ) &
( for s in 4007 4009; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py arc $s; echo "net $s done $(date -u +%H:%M:%SZ)"; done ) &
wait
echo "queue E done $(date -u +%H:%M:%SZ)"
