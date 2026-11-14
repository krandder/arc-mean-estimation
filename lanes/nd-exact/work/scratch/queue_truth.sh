#!/bin/bash
# usage: queue_truth.sh C LOG2M R LOG2M2 seed...
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
C=$1; M=$2; R=$3; M2=$4; shift 4
for s in "$@"; do
  nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python scratch/truth.py $s $C $M $R $M2 runs/truth_s${s}.json > logs/truth_s${s}.log 2>&1
done
