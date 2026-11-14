#!/bin/bash
# Amendment 2: net 203 after net 202's process (3574959) exits.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 3574959 2>/dev/null; do sleep 20; done
nice -n 19 ionice -c3 $PY frozen/curves.py arc 256 32 203 runs/s3_arc_n256_L32_s203.json --methods RQMC,RQMCRB,PI_as_w,PI_rand_w,MLMC_16 --reps 8 --pmin 6 --pmax 14 --pimin 1 --pimax 5
echo "queue G done $(date -u +%H:%M:%SZ)"
