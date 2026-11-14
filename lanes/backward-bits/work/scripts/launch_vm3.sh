#!/bin/bash
# Wait until backbits-2 is gone, then resume the scored run on backbits-3: restore the pulled scored3 state into
# gpu_src/prior/scored3, keep only queue/30_resume.sh, launch, and start a pull loop for backbits-3.
cd /home/agent/workspaces/mats/work/backward-bits
gone=0
while [ $gone -lt 3 ]; do      # three consecutive successful listings without backbits-2 (a failed call never counts)
  out=$(timeout 60 gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=backbits-2" --format='value(name)' 2>/dev/null)
  rc=$?
  if [ $rc -eq 0 ] && [ -z "$out" ]; then gone=$((gone + 1)); else gone=0; fi
  sleep 60
done
echo "$(date -u +%FT%TZ) backbits-2 gone" >> logs/launch_vm3.log
bash scripts/gpu_pull.sh backbits-2 > /dev/null 2>&1   # no-op if gone; the last pull_loop copy is in runs_gpu/
mkdir -p gpu_src/prior gpu_src/queue_done
cp -r runs_gpu/scored3 gpu_src/prior/
[ -f gpu_src/queue/23_dag.sh ] && mv gpu_src/queue/23_dag.sh gpu_src/queue_done/
[ -f gpu_src/queue/24_scored3.sh ] && mv gpu_src/queue/24_scored3.sh gpu_src/queue_done/
ls gpu_src/queue/*.sh >> logs/launch_vm3.log
GPU_PROVISIONING=${PROV:-SPOT} bash scripts/gpu_launch.sh backbits-3 4h > logs/gpu_launch_3.log 2>&1 &
sleep 300
nohup bash scripts/pull_loop.sh backbits-3 > /dev/null 2>&1 &
echo "$(date -u +%FT%TZ) launched backbits-3, pull loop started" >> logs/launch_vm3.log
