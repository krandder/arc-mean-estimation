#!/bin/bash
# Relaunch the S11 gfix-only S7 jobs with the fixed log line (02:56Z). tanh4 crashed after its first cell; feistel will
# crash after its first cell, so wait for that PID to exit before relaunching it. Run on the VM as root.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
setsid nohup python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind tanh4 --kinds gfix --steps 2000 \
  --batch 2048 --out /root/runs/S11_tanh4 >> /root/runs/S11_tanh4/log_ent_gfix.txt 2>&1 < /dev/null &
echo "tanh4 pid $!"
setsid nohup bash -c 'while kill -0 15392 2>/dev/null; do sleep 15; done; python scripts/run_entropy.py --configs 16x16 \
  --seeds 5000 --netkind feistel --kinds gfix --steps 2000 --batch 2048 --out /root/runs/S11_feistel \
  >> /root/runs/S11_feistel/log_ent_gfix.txt 2>&1' > /dev/null 2>&1 < /dev/null &
echo "feistel waiter pid $!"
