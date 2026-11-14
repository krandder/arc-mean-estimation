#!/bin/bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
nice -n 19 ionice -c3 $PY scratch/curves.py arc 4 2 1 runs/dev_small_n4_L2_s1.json --methods RQMC,RQMCRB,PI_rand,PI_as --reps 16 --pmin 6 --pmax 18 --pimin 2 --pimax 14
nice -n 19 ionice -c3 $PY scratch/curves.py arc 6 3 1 runs/dev_small_n6_L3_s1.json --methods RQMC,RQMCRB,PI_rand,PI_as --reps 16 --pmin 6 --pmax 18 --pimin 2 --pimax 13
nice -n 19 ionice -c3 $PY scratch/curves.py arc 64 8 9500 runs/dev_arc_n64_L8_s9500.json --methods RQMC,RQMCRB,PI_rand_w,PI_as_w --reps 8 --pmin 6 --pmax 14 --pimin 2 --pimax 8
nice -n 19 ionice -c3 $PY scratch/curves.py arc 128 16 9500 runs/dev_arc_n128_L16_s9500.json --methods RQMC,RQMCRB,PI_rand_w,PI_as_w --reps 8 --pmin 6 --pmax 14 --pimin 2 --pimax 7
