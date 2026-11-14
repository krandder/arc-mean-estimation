#!/bin/bash
# usage: queue_census.sh LOG2N seed...
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
N=$1; shift
for s in "$@"; do
  nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/census.py $s $N runs/census_s${s}_n${N}.json > logs/census_s${s}_n${N}.log 2>&1
done
