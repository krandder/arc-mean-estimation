#!/bin/bash
# Part S7 (primary): entropy-coded and VIB bottlenecks with a lambda sweep. L = n nets first, all three seeds; then
# 16x4 and 32x8 seed 5000.
cd /root/soup
mkdir -p /root/runs/S_ent
A="--steps 2000 --batch 2048 --out /root/runs/S_ent"
python scripts/run_entropy.py --configs 16x16 --seeds 5000,5001,5002 $A > /root/runs/S_ent/log_16x16.txt 2>&1 &
python scripts/run_entropy.py --configs 32x32 --seeds 5000,5001 $A > /root/runs/S_ent/log_32x32a.txt 2>&1 &
( python scripts/run_entropy.py --configs 32x32 --seeds 5002 $A > /root/runs/S_ent/log_32x32b.txt 2>&1 ;
  python scripts/run_entropy.py --configs 16x4,32x8 --seeds 5000 $A > /root/runs/S_ent/log_small.txt 2>&1 ) &
wait
