#!/bin/bash
# Keep trying to start the phase-2 VMs (L4 stockouts): every 5 min for up to 2 h, alternate SPOT and STANDARD, wide
# zone list; zero-cost COST-AUDIT lines release the reservations of failed creates. Un-stage the queues once both run.
cd /home/agent/workspaces/mats/work/bit-accounting
ZONES="us-central1-b us-west1-a us-east4-c us-east1-c us-central1-a us-west1-c us-central1-c us-west1-b us-east4-a us-east1-d europe-west4-a"
audit() {
  for v in $(grep "CREATE-FAILED" GPU-LOG.md | grep -o "vm=soup-gpu-bitacct[^ ]*" | sort -u | cut -d= -f2); do
    grep -q "COST-AUDIT vm=$v" GPU-LOG.md || echo "- $(date -u +%FT%H:%MZ) COST-AUDIT vm=$v cost_usd=0.00 (create failed with STOCKOUT, the VM never existed) by=opus-mats-bitacct" >> GPU-LOG.md
  done
}
for i in $(seq 1 24); do
  audit
  for id in bitacct-12; do
    grep -q "RUN vm=soup-gpu-$id-11022[1-3]" GPU-LOG.md && continue
    pgrep -f "gpu-run.sh --up --run-id $id" > /dev/null && continue
    prov=$([ $((i % 2)) -eq 1 ] && echo STANDARD || echo SPOT)
    GPU_ZONES="$ZONES" GPU_PROVISIONING=$prov nohup bash scratch/gpu_launch.sh $id 2.6h > logs/gpu-run-$id.out 2>&1 &
    echo "$(date -u +%T) try $i $id $prov" >> logs/launch_retry.log
    sleep 60
  done
  [ $(grep -c "RUN vm=soup-gpu-bitacct-12-11022[1-3]" GPU-LOG.md) -ge 1 ] && break
  sleep 240
done
audit
mv gpu_src/queue/60_p1b.sh gpu_src/queue/70_noisy.sh gpu_src/staged/ 2>/dev/null
echo "$(date -u +%T) done: $(grep -c 'RUN vm=soup-gpu-bitacct-1[23]' GPU-LOG.md) running" >> logs/launch_retry.log
for id in bitacct-12 bitacct-13; do grep -q "RUN vm=soup-gpu-$id-11022[1-3]" GPU-LOG.md && nohup bash scratch/pull_loop.sh $id > /dev/null 2>&1 & done
