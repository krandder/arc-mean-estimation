#!/bin/bash
# VM 4 re-prioritisation for S11 (02:50Z). Run on the VM as root: bash -s < vm4_reprio.sh
# 1. Hold the worker (SIGSTOP; timeout's SIGTERM/SIGCONT/SIGKILL at the 4 h limit still ends it), so that jobs started
#    outside the worker (orphans of finished queue scripts and the jobs below) are not cut off by an early worker exit.
# 2. Stop the S5 certificate job (16x16; largest memory user), the all-arm S11 tanh4 S7 job and the controls script
#    (so it does not start the all-arm feistel S7 job).
# 3. Start S7 for the controls with the scored arm only (gfix), tanh4 and feistel.
set -u
kill -STOP 1981 && echo "worker 1981 stopped (hold)"
for p in 9599 14686 13528; do kill "$p" 2>/dev/null && echo "killed $p"; done
sleep 20
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for k in tanh4 feistel; do
  setsid nohup python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind $k --kinds gfix --steps 2000 \
    --batch 2048 --out /root/runs/S11_$k > /root/runs/S11_$k/log_ent_gfix.txt 2>&1 < /dev/null &
  echo "started S7 gfix $k pid $!"
  sleep 5
done
nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader
