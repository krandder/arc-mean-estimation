#!/bin/bash
# Amendment 3A: two more prospective ARC nets for theory v2.
cd /home/agent/workspaces/mats/work/relevance
export OPENBLAS_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 4004 4005; do nice -n 19 ionice -c3 $PY scratch/eval_part1.py arc $s; done
echo "queue D done $(date -u +%H:%M:%SZ)"
