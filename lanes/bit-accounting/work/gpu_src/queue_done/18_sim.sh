#!/bin/bash
# S10 compressed simulator, 16x16 and 32x32 noiseless seed 5000, when >= 5 GB GPU memory are free.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/S_sim
waitmem() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 5000 ]; do sleep 20; done; sleep 45; }
waitmem; python scripts/run_sim.py --configs 16x16 --seed 5000 --out /root/runs/S_sim > /root/runs/S_sim/log_16x16.txt 2>&1 &
waitmem; python scripts/run_sim.py --configs 32x32 --seed 5000 --out /root/runs/S_sim > /root/runs/S_sim/log_32x32.txt 2>&1 &
wait
