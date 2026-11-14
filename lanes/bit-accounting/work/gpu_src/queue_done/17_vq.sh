#!/bin/bash
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 3000 ]; do sleep 20; done
python scripts/run_vq.py --configs 32x8,16x16,32x32 --seeds 5000,5001,5002 --tag _b --out /root/runs/S_vq > /root/runs/S_vq/log_b.txt 2>&1
