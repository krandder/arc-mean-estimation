#!/bin/bash
# S3 32x32 rerun (the 11_all.sh copy died of CUDA OOM with 16 processes on the L4); then 16x4 and 32x8 if time allows,
# and S4 32x32 seed 5002, once the S1 curve processes have finished.
cd /root/soup
mkdir -p /root/runs/S_kelvin /root/runs/S_noisy
A3="--steps 2000 --batch 1024 --out /root/runs/S_kelvin"
python scripts/run_kelvin.py --configs 32x32 --seeds 5000,5001,5002 $A3 > /root/runs/S_kelvin/log4_32x32.txt 2>&1 &
( while pgrep -f 'run_curves.py' > /dev/null; do sleep 30; done
  python scripts/run_kelvin.py --configs 16x4,32x8 --seeds 5000,5001,5002 $A3 > /root/runs/S_kelvin/log4_small.txt 2>&1 ) &
( while pgrep -f 'run_curves.py' > /dev/null; do sleep 30; done
  python scripts/run_noisy.py --configs 32x32 --seeds 5002 --steps 1500 --batch 2048 --sigma 1 --out /root/runs/S_noisy > /root/runs/S_noisy/log4_32x32b.txt 2>&1 ) &
wait
