#!/bin/bash
# Part S2 chains, v2 (XOR baseline fixed for CUDA; 2000 steps x batch 2048), evaluation seeds only.
cd /root/soup
mkdir -p /root/runs/S_chain
A="--steps 2000 --batch 2048 --out /root/runs/S_chain"
python scripts/run_chain.py --configs 16x4,16x16 --seeds 5000,5001,5002 $A > /root/runs/S_chain/log_a.txt 2>&1 &
python scripts/run_chain.py --configs 32x8,32x32 --seeds 5000,5001,5002 $A > /root/runs/S_chain/log_b.txt 2>&1 &
wait
