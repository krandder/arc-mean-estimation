#!/bin/bash
# Post hoc (PREREG's stated follow-up if P3b failed): larger-N PI_as_w at 128 x 16, nets 302 and 304, lines 2^9..2^10.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 302 304; do
  nice -n 19 ionice -c3 $PY frozen/curves.py arc 128 16 $s runs/posthoc_largeN_n128_L16_s$s.json --methods PI_as_w --reps 8 --pimin 9 --pimax 10
done
echo "queue H done $(date -u +%H:%M:%SZ)"
