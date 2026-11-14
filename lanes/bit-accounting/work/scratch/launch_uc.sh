#!/bin/bash
cd /home/agent/workspaces/mats/work/bit-accounting
ZONES="us-central1-b us-west1-a us-east4-c us-east1-c us-central1-a us-west1-c us-central1-c us-west1-b us-east4-a us-east1-d"
cp gpu_src/staged/55_unscr_c.sh gpu_src/queue/
for i in $(seq 1 15); do
  for v in $(grep "CREATE-FAILED" GPU-LOG.md | grep -o "vm=soup-gpu-bitacct[^ ]*" | sort -u | cut -d= -f2); do
    grep -q "COST-AUDIT vm=$v" GPU-LOG.md || echo "- $(date -u +%FT%H:%MZ) COST-AUDIT vm=$v cost_usd=0.00 (create failed with STOCKOUT, the VM never existed) by=opus-mats-bitacct" >> GPU-LOG.md
  done
  grep -q "RUN vm=soup-gpu-bitacct-15" GPU-LOG.md && break
  pgrep -f "gpu-run.sh --up --run-id bitacct-15" > /dev/null || {
    GPU_ZONES="$ZONES" GPU_PROVISIONING=SPOT nohup bash scratch/gpu_launch.sh bitacct-15 2.6h > logs/gpu-run-bitacct-15.out 2>&1 &
    echo "$(date -u +%T) try $i bitacct-15" >> logs/launch_uc.log; }
  sleep 240
done
mv gpu_src/queue/55_unscr_c.sh gpu_src/staged/ 2>/dev/null
grep -q "RUN vm=soup-gpu-bitacct-15" GPU-LOG.md && nohup bash scratch/pull_loop.sh bitacct-15 > /dev/null 2>&1 &
echo "$(date -u +%T) done" >> logs/launch_uc.log
