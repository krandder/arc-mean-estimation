#!/bin/bash
# Launch VM 6 (on-demand L4, 5 h) for phase-1 list b once VM 4 is gone (at most 2 VMs at once). VM 4's gpu-run.sh syncs
# runs/ before deleting it. Then: copy finished P1 cells to gpu_src/prior/P1, put VM 4's unfinished jobs first in
# list b, stage the queue, launch, un-stage the queue after the source sync, start the pull loop.
cd /home/agent/workspaces/mats/work/bit-accounting
while gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=bitacct-4" --format='value(name)' 2>/dev/null | grep -q .; do sleep 30; done
echo "$(date -u +%T) VM 4 gone" >> logs/launch_vm6.log
python3 scratch/prep_vm6.py >> logs/launch_vm6.log 2>&1
GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh bitacct-6 5h > logs/gpu-run-bitacct-6.out 2>&1 &
until grep -q "RUN vm=soup-gpu-bitacct-6" GPU-LOG.md; do sleep 15; done
mv gpu_src/queue/30_p1.sh gpu_src/staged/30_p1.sh
echo "$(date -u +%T) VM 6 running; queue un-staged" >> logs/launch_vm6.log
nohup bash scratch/pull_loop.sh bitacct-6 > /dev/null 2>&1 &
