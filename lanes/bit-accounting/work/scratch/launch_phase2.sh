#!/bin/bash
# Launch bitacct-12 and bitacct-13 (on-demand, 4.2 h) with the chained queues 50 (unscrambling), 60 (explorers),
# 70 (noisy). Retry a failed create once in other zones. Un-stage the queues after both runs started (or after 20 min).
cd /home/agent/workspaces/mats/work/bit-accounting
cp gpu_src/staged/50_unscr.sh gpu_src/staged/60_p1b.sh gpu_src/staged/70_noisy.sh gpu_src/queue/
for id in bitacct-12 bitacct-13; do
  GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh $id 4.2h > logs/gpu-run-$id.out 2>&1 &
  sleep 30
done
for i in $(seq 1 40); do
  ok=0
  for id in bitacct-12 bitacct-13; do grep -q "RUN vm=soup-gpu-$id" GPU-LOG.md && ok=$((ok+1)); done
  [ $ok -eq 2 ] && break
  for id in bitacct-12 bitacct-13; do
    if grep -q "CREATE-FAILED vm=soup-gpu-$id" GPU-LOG.md && ! grep -q "RUN vm=soup-gpu-$id" GPU-LOG.md && [ ! -e logs/retry_$id ]; then
      touch logs/retry_$id
      GPU_ZONES="us-central1-b us-central1-c us-west1-b us-west1-a us-east4-c" GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh $id 4.2h > logs/gpu-run-$id.retry.out 2>&1 &
    fi
  done
  sleep 30
done
mv gpu_src/queue/50_unscr.sh gpu_src/queue/60_p1b.sh gpu_src/queue/70_noisy.sh gpu_src/staged/ 2>/dev/null
echo "$(date -u +%T) phase-2 VMs: $(grep -c 'RUN vm=soup-gpu-bitacct-1[23]' GPU-LOG.md) running; queues un-staged" >> logs/launch_phase2.log
for id in bitacct-12 bitacct-13; do nohup bash scratch/pull_loop.sh $id > /dev/null 2>&1 & done
