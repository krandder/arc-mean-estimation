#!/bin/bash
# Keep the scored run going across spot preemptions / timeouts: wait until backbits-$N is gone (three consecutive
# successful listings without it), stop if the run's DONE marker was pulled, else copy the pulled scored3 state into
# gpu_src/prior/, launch backbits-$((N+1)) with queue/30_resume.sh only, start its pull loop, and repeat (up to 5).
# The infra's group budget check (GPU_GROUP_BUDGET_USD=10) refuses a launch beyond the cap.
cd /home/agent/workspaces/mats/work/backward-bits
N=${1:-2}
while [ $N -lt 5 ]; do
  gone=0
  while [ $gone -lt 3 ]; do
    out=$(timeout 60 gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=backbits-$N" --format='value(name)' 2>/dev/null)
    rc=$?
    if [ $rc -eq 0 ] && [ -z "$out" ]; then gone=$((gone + 1)); else gone=0; fi
    sleep 60
  done
  echo "$(date -u +%FT%TZ) backbits-$N gone" >> logs/launch_chain.log
  if [ -f runs_gpu/logs/scored3/DONE ]; then echo "$(date -u +%FT%TZ) DONE marker present, stop" >> logs/launch_chain.log; exit 0; fi
  mkdir -p gpu_src/prior gpu_src/queue_done
  cp -r runs_gpu/scored3 gpu_src/prior/
  [ -f gpu_src/queue/23_dag.sh ] && mv gpu_src/queue/23_dag.sh gpu_src/queue_done/
  [ -f gpu_src/queue/24_scored3.sh ] && mv gpu_src/queue/24_scored3.sh gpu_src/queue_done/
  N=$((N + 1))
  GPU_PROVISIONING=${PROV:-SPOT} bash scripts/gpu_launch.sh backbits-$N 4h > logs/gpu_launch_$N.log 2>&1 &
  sleep 300
  nohup bash scripts/pull_loop.sh backbits-$N > /dev/null 2>&1 &
  echo "$(date -u +%FT%TZ) launched backbits-$N, pull loop started" >> logs/launch_chain.log
done
