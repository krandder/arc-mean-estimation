#!/bin/bash
# Part S1 rate curves, v2 settings (1500 steps x batch 2048): evaluation seeds 5000-5002, classes local and unres;
# the linear class on seed 5000 only (for S1.5). The 3000-step results already produced are kept as a training-length
# check (runs/S_curves_3000/).
cd /root/soup
mkdir -p /root/runs/S_curves /root/runs/S_curves_3000
find /root/runs/S_curves -name 'S_*.json' -exec mv {} /root/runs/S_curves_3000/ \;
A="--steps 1500 --batch 2048 --out /root/runs/S_curves"
python scripts/run_curves.py --configs 16x4 --seeds 5000,5001,5002 --classes local,unres $A > /root/runs/S_curves/log_16x4.txt 2>&1 &
python scripts/run_curves.py --configs 32x8 --seeds 5000,5001,5002 --classes local,unres $A > /root/runs/S_curves/log_32x8.txt 2>&1 &
python scripts/run_curves.py --configs 16x16 --seeds 5000,5001,5002 --classes local,unres $A > /root/runs/S_curves/log_16x16.txt 2>&1 &
python scripts/run_curves.py --configs 32x32 --seeds 5000,5001 --classes local,unres $A > /root/runs/S_curves/log_32x32a.txt 2>&1 &
( python scripts/run_curves.py --configs 32x32 --seeds 5002 --classes local,unres $A > /root/runs/S_curves/log_32x32b.txt 2>&1 ;
  python scripts/run_curves.py --configs 16x4,32x8,16x16,32x32 --seeds 5000 --classes linear $A > /root/runs/S_curves/log_linear.txt 2>&1 ) &
wait
