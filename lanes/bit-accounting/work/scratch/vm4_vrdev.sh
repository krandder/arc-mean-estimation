#!/bin/bash
# Phase-1 dev timing runs of run_vr.py on dev seed 9100 (registered later; dev seeds only). Run on the VM as root.
mkdir -p /root/runs/P1_dev
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
setsid nohup python scripts/run_vr.py --configs 16x16 --seeds 9100 --layers 0 --classes local,unres \
  --out /root/runs/P1_dev >> /root/runs/P1_dev/log_16x16.txt 2>&1 < /dev/null &
echo "16x16 dev pid $!"
setsid nohup python scripts/run_vr.py --configs 32x32 --seeds 9100 --layers 0 --classes local \
  --out /root/runs/P1_dev >> /root/runs/P1_dev/log_32x32.txt 2>&1 < /dev/null &
echo "32x32 dev pid $!"
