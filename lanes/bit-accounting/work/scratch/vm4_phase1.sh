#!/bin/bash
# Kelvin 02:55Z (via main): phase 1 (best per-layer bits-vs-accuracy curves) is the only priority; S9/S10 and the S11
# spectra/price parts are deferred. Stop those jobs by PID; keep S7 (per-lambda references), VQ, and the S11 S7 rates
# (gfix-only, relaunched with the fixed log line). Run on the VM as root.
for p in 12083 12619 12688 14381 14452 14469 14540 14557 14575 14650 14667; do
  ps -p "$p" -o args= | cut -c1-90 | sed "s/^/kill $p: /"; kill "$p" 2>/dev/null
done
sleep 10
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
setsid nohup python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind tanh4 --kinds gfix --steps 2000 \
  --batch 2048 --out /root/runs/S11_tanh4 >> /root/runs/S11_tanh4/log_ent_gfix.txt 2>&1 < /dev/null &
echo "tanh4 gfix pid $!"
setsid nohup bash -c 'while kill -0 15392 2>/dev/null; do sleep 15; done; python scripts/run_entropy.py --configs 16x16 \
  --seeds 5000 --netkind feistel --kinds gfix --steps 2000 --batch 2048 --out /root/runs/S11_feistel \
  >> /root/runs/S11_feistel/log_ent_gfix.txt 2>&1' > /dev/null 2>&1 < /dev/null &
echo "feistel gfix waiter pid $!"
setsid nohup python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind linear --kinds gfix --steps 2000 \
  --batch 2048 --out /root/runs/S11_linear >> /root/runs/S11_linear/log_ent_gfix.txt 2>&1 < /dev/null &
echo "linear gfix pid $!"
sleep 5
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
ps -eo pid,etime,args | grep "scripts/run_" | grep -v grep | cut -c1-140
