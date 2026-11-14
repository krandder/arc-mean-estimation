#!/bin/bash
# PREREG Amendment 1: ARC 256 x 32 nets 202-204 with PI lines 2^1..2^5 (second process, parallel to net 201).
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 202 203 204; do
  nice -n 19 ionice -c3 $PY frozen/curves.py arc 256 32 $s runs/s3_arc_n256_L32_s$s.json --methods RQMC,RQMCRB,PI_as_w,PI_rand_w,MLMC_16 --reps 8 --pmin 6 --pmax 14 --pimin 1 --pimax 5
done
echo "queue E done $(date -u +%H:%M:%SZ)"
