#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 103 111; do
  for rule in surplus distortion hybrid; do
    $PY scratch/run_cs2.py $s 32 22 $rule 0.01 32 runs/dev_cs2_s${s}_${rule}.json > logs/dev_cs2_s${s}_${rule}.log 2>&1
  done
done
for s in 103 111; do
  $PY scratch/baselines.py $s 48 runs/dev_baselines_s${s}.json > logs/dev_baselines_s${s}.log 2>&1
done
$PY scratch/region_code.py 103 22 runs/dev_region_code2_s103.json > logs/dev_region_code2_s103.log 2>&1
