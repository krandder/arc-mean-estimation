#!/bin/bash
# Part S3 (Kelvin's curriculum autoencoder), v2: starts at once, 2000 steps, the L = n nets first (16x16, 32x32), then
# 16x4 and 32x8 if time allows. Replaces 08_kelvin.sh (which waited for the S2 chains).
cd /root/soup
mkdir -p /root/runs/S_kelvin
A="--steps 2000 --batch 1024 --out /root/runs/S_kelvin"
( python scripts/run_kelvin.py --configs 16x16 --seeds 5000,5001,5002 $A > /root/runs/S_kelvin/log_a.txt 2>&1 ;
  python scripts/run_kelvin.py --configs 16x4 --seeds 5000,5001,5002 $A > /root/runs/S_kelvin/log_c.txt 2>&1 ) &
( python scripts/run_kelvin.py --configs 32x32 --seeds 5000,5001,5002 $A > /root/runs/S_kelvin/log_b.txt 2>&1 ;
  python scripts/run_kelvin.py --configs 32x8 --seeds 5000,5001,5002 $A > /root/runs/S_kelvin/log_d.txt 2>&1 ) &
wait
