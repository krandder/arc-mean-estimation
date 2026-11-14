#!/bin/bash
# Wait until backbits-1 is gone, then resume the scored run on backbits-2: restore the pulled scored3 state into
# gpu_src/prior/scored3, keep only queue/30_resume.sh, launch, and start a pull loop for backbits-2.
cd /home/agent/workspaces/mats/work/backward-bits
while gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=backbits-1" --format='value(name)' 2>/dev/null | grep -q .; do
  sleep 60
done
echo "$(date -u +%FT%TZ) backbits-1 gone" >> logs/launch_vm2.log
bash scripts/gpu_pull.sh backbits-1 > /dev/null 2>&1   # no-op if gone; the last pull_loop copy is in runs_gpu/
mkdir -p gpu_src/prior gpu_src/queue_done
cp -r runs_gpu/scored3 gpu_src/prior/
[ -f gpu_src/queue/23_dag.sh ] && mv gpu_src/queue/23_dag.sh gpu_src/queue_done/
[ -f gpu_src/queue/24_scored3.sh ] && mv gpu_src/queue/24_scored3.sh gpu_src/queue_done/
ls gpu_src/queue/*.sh >> logs/launch_vm2.log
GPU_PROVISIONING=${PROV:-SPOT} bash scripts/gpu_launch.sh backbits-2 4h > logs/gpu_launch_2.log 2>&1 &
sleep 300
nohup bash scripts/pull_loop.sh backbits-2 > /dev/null 2>&1 &
echo "$(date -u +%FT%TZ) launched backbits-2, pull loop started" >> logs/launch_vm2.log
