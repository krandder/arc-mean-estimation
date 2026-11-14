#!/bin/bash
# Part S4 (noisy Model S nets, common random numbers): starts when the S1 curves (06_curves) have finished.
cd /root/soup
while [ ! -e /root/runs/worker/06_curves.sh.done ]; do sleep 30; done
mkdir -p /root/runs/S_noisy
A="--steps 1500 --batch 2048 --sigma 1 --out /root/runs/S_noisy"
python scripts/run_noisy.py --configs 16x16 --seeds 5000,5001,5002 $A > /root/runs/S_noisy/log_16x16.txt 2>&1 &
python scripts/run_noisy.py --configs 32x32 --seeds 5000,5001 $A > /root/runs/S_noisy/log_32x32a.txt 2>&1 &
python scripts/run_noisy.py --configs 32x32 --seeds 5002 $A > /root/runs/S_noisy/log_32x32b.txt 2>&1 &
wait
