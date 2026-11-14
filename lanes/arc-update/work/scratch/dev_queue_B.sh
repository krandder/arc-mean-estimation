#!/bin/bash
# Dev (calibration, not scored): T-LAD on dev seed 9500 at n = 32, 64, 128 (L = n/8) with 2^22-path truths,
# ARC variants at 256 x 32 on dev net 100, RQMC on dev nets.
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1
echo "devB start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for cfg in "32 4" "64 8" "128 16"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/truth.py $1 $2 9500 22 >> logs/dev_truth.log 2>&1
done
nice -n 19 ionice -c3 $PY scratch/run_lad.py 32 4 9500 k1,k2,k2a,k3,k3f,k3fa,k4,k4f >> logs/dev_lad.log 2>&1
nice -n 19 ionice -c3 $PY scratch/run_lad.py 64 8 9500 k1,k2,k2a,k3,k3f,k3fa,k4f >> logs/dev_lad.log 2>&1
nice -n 19 ionice -c3 $PY scratch/run_lad.py 128 16 9500 k1,k2,k2a,k3,k3f,k3fa,k4f >> logs/dev_lad.log 2>&1
nice -n 19 ionice -c3 $PY scratch/run_lad.py 256 32 100 k1,k2,k2a,k3f >> logs/dev_lad.log 2>&1
for cfg in "32 4" "64 8" "128 16"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/run_rqmc.py $1 $2 9500 runs/truth_n$1_L$2_s9500.npz 8,10,12,14 8 >> logs/dev_rqmc.log 2>&1
done
nice -n 19 ionice -c3 $PY scratch/run_rqmc.py 256 32 100 s0.001 8,10,12,14 4 >> logs/dev_rqmc.log 2>&1
echo "devB end $(date -u +%H:%M:%SZ)" >> logs/queue.log
