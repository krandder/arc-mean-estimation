#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while pgrep -f queue_slot3.sh >/dev/null || pgrep -f queue_a1.sh >/dev/null; do sleep 10; done
$PY scratch/check_faces.py > logs/check_faces.log 2>&1
$PY scratch/depth1_rate4.py runs/depth1_rate4.json > logs/depth1_rate4.log 2>&1
