#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while kill -0 4137747 2>/dev/null; do sleep 5; done
$PY tests/test_cubesphere.py > logs/test_cubesphere.log 2>&1
$PY scratch/run_cs2.py 103 32 22 surplus 0.01 64 runs/dev_cs2_s103_c32.json > logs/dev_cs2_s103_c32.log 2>&1
$PY scratch/depth1_rate.py runs/depth1_rate.json > logs/depth1_rate.log 2>&1
$PY scratch/region_code.py 103 22 runs/dev_region_code_s103.json > logs/dev_region_code_s103.log 2>&1
