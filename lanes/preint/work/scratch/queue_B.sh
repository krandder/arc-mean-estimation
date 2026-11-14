#!/bin/bash
# Scored queue B: S3 ladder (32,4), (64,8), (128,16) seeds 302-304, then ARC 256 x 32 nets 201-204. Frozen code.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
for cfg in "32 4 11" "64 8 9" "128 16 8"; do
  set -- $cfg
  for s in 302 303 304; do
    nice -n 19 ionice -c3 $PY frozen/curves.py arc $1 $2 $s runs/s3_arc_n$1_L$2_s$s.json --methods RQMC,RQMCRB,PI_as_w,PI_rand_w,MLMC_$(( $2 / 2 )) --reps 8 --pmin 6 --pmax 14 --pimin 2 --pimax $3
  done
done
for s in 201 202 203 204; do
  nice -n 19 ionice -c3 $PY frozen/curves.py arc 256 32 $s runs/s3_arc_n256_L32_s$s.json --methods RQMC,RQMCRB,PI_as_w,PI_rand_w,MLMC_16 --reps 8 --pmin 6 --pmax 14 --pimin 1 --pimax 7
done
echo "queue B done $(date -u +%H:%M:%SZ)"
