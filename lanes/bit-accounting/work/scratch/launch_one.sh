#!/bin/bash
# One VM (bitacct-14, 2.5 h) for queue 80_rest.sh: try STANDARD then SPOT every 4 min for up to 1 h.
cd /home/agent/workspaces/mats/work/bit-accounting
ZONES="us-central1-b us-west1-a us-east4-c us-east1-c us-central1-a us-west1-c us-central1-c us-west1-b us-east4-a us-east1-d"
cp gpu_src/staged/80_rest.sh gpu_src/queue/
for i in $(seq 1 15); do
  for v in $(grep "CREATE-FAILED" GPU-LOG.md | grep -o "vm=soup-gpu-bitacct[^ ]*" | sort -u | cut -d= -f2); do
    grep -q "COST-AUDIT vm=$v" GPU-LOG.md || echo "- $(date -u +%FT%H:%MZ) COST-AUDIT vm=$v cost_usd=0.00 (create failed with STOCKOUT, the VM never existed) by=opus-mats-bitacct" >> GPU-LOG.md
  done
  grep -q "RUN vm=soup-gpu-bitacct-14" GPU-LOG.md && break
  pgrep -f "gpu-run.sh --up --run-id bitacct-14" > /dev/null || {
    prov=$([ $((i % 2)) -eq 1 ] && echo STANDARD || echo SPOT)
    GPU_ZONES="$ZONES" GPU_PROVISIONING=$prov nohup bash scratch/gpu_launch.sh bitacct-14 2.5h > logs/gpu-run-bitacct-14.out 2>&1 &
    echo "$(date -u +%T) try $i bitacct-14 $prov" >> logs/launch_one.log; }
  sleep 240
done
mv gpu_src/queue/80_rest.sh gpu_src/staged/ 2>/dev/null
echo "$(date -u +%T) done: $(grep -c 'RUN vm=soup-gpu-bitacct-14' GPU-LOG.md) running" >> logs/launch_one.log
grep -q "RUN vm=soup-gpu-bitacct-14" GPU-LOG.md && nohup bash scratch/pull_loop.sh bitacct-14 > /dev/null 2>&1 &
