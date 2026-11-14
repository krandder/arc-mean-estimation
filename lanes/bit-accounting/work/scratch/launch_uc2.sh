#!/bin/bash
# Relaunch of the corrected Part U (U-c) after the spot preemption of bitacct-15 (00:01Z 3 Nov): two on-demand L4s,
# bitacct-16 (jobs_uc_1) and bitacct-17 (jobs_uc_2), 2.2 h each; pull loops; queue script un-staged once both run.
cd /home/agent/workspaces/mats/work/bit-accounting
ZONES="us-central1-b us-west1-a us-east4-c us-east1-c us-central1-a us-west1-c us-central1-c us-west1-b us-east4-a us-east1-d"
cp gpu_src/staged/55_unscr_c.sh gpu_src/queue/
for i in $(seq 1 15); do
  for v in $(grep "CREATE-FAILED" GPU-LOG.md | grep -o "vm=soup-gpu-bitacct[^ ]*" | sort -u | cut -d= -f2); do
    grep -q "COST-AUDIT vm=$v" GPU-LOG.md || echo "- $(date -u +%FT%H:%MZ) COST-AUDIT vm=$v cost_usd=0.00 (create failed with STOCKOUT, the VM never existed) by=opus-mats-bitacct" >> GPU-LOG.md
  done
  n=0
  for r in bitacct-16 bitacct-17; do
    if grep -q "RUN vm=soup-gpu-$r" GPU-LOG.md; then n=$((n + 1)); continue; fi
    pgrep -f "gpu-run.sh --up --run-id $r" > /dev/null || {
      GPU_ZONES="$ZONES" GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh $r 2.2h > logs/gpu-run-$r.out 2>&1 &
      echo "$(date -u +%T) try $i $r" >> logs/launch_uc2.log; sleep 60; }
  done
  [ $n -eq 2 ] && break
  sleep 180
done
mv gpu_src/queue/55_unscr_c.sh gpu_src/staged/ 2>/dev/null
for r in bitacct-16 bitacct-17; do
  grep -q "RUN vm=soup-gpu-$r" GPU-LOG.md && { nohup bash scratch/pull_loop.sh $r > /dev/null 2>&1 & }
done
echo "$(date -u +%T) done" >> logs/launch_uc2.log
