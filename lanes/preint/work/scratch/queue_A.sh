#!/bin/bash
# Scored queue A: S2 (narrow-deep 8 x 256) then S1 (small nets). PREREG Part 1 (hashed 14:03:47Z). Frozen code.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
for s in 203 216 217 220 221 223; do
  nice -n 19 ionice -c3 $PY frozen/curves.py nd 8 256 $s runs/s2_nd_s$s.json --methods RQMC,RQMCRB,RQMCJ,PIJ_as,PIJ_rand --reps 8 --pmin 6 --pmax 16 --pimin 2 --pimax 11 --cut 48
  nice -n 19 ionice -c3 $PY frozen/curves.py nd 8 256 $s runs/s2_nd_mlmc_s$s.json --methods MLMC_32 --reps 8 --pmin 8 --pmax 16
done
for nl in "4 2 14" "6 3 14" "8 4 13"; do
  set -- $nl
  for s in 11 12 13; do
    nice -n 19 ionice -c3 $PY frozen/curves.py small $1 $2 $s runs/s1_small_n$1_L$2_s$s.json --methods RQMC,RQMCRB,PI_rand,PI_as --reps 16 --pmin 6 --pmax 18 --pimin 2 --pimax $3
  done
done
echo "queue A done $(date -u +%H:%M:%SZ)"
