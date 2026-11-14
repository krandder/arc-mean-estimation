#!/bin/bash
# Wait until the old VM is gone and its gpu-run launcher has exited (final sync done), copy finished results into
# gpu_src/prior/P1, then launch the replacement (spot first, on-demand if spot is unavailable).
# usage: relaunch_watch.sh <old-run-id> <new-run-id> <launcher-log-of-old>
cd /home/agent/workspaces/mats/work/bit-accounting-arc
OLD=$1; NEW=$2
while gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$OLD" --format='value(name)' 2>/dev/null | grep -q .; do sleep 60; done
while pgrep -f "gpu_launch.sh $OLD" > /dev/null; do sleep 30; done
bash scratch/prep_prior.sh >> logs/relaunch_$NEW.log 2>&1
Z="us-west1-c us-west1-a us-west1-b us-central1-a us-central1-b us-central1-c us-east1-b us-east1-c us-east1-d us-east4-a us-east4-c us-west4-a us-west4-c"
echo "$(date -u +%H:%M:%SZ) launching $NEW (on-demand first, after preemptions)" >> logs/relaunch_$NEW.log
GPU_ZONES="$Z" GPU_PROVISIONING=STANDARD bash scratch/gpu_launch.sh $NEW 5h >> logs/gpu_launch_$NEW.log 2>&1
rc=$?
if ! grep -q "READY vm=soup-gpu-$NEW" GPU-LOG.md; then
  echo "$(date -u +%H:%M:%SZ) on-demand failed rc=$rc, launching $NEW spot" >> logs/relaunch_$NEW.log
  GPU_ZONES="$Z" GPU_PROVISIONING=SPOT bash scratch/gpu_launch.sh $NEW 5h >> logs/gpu_launch_${NEW}_spot.log 2>&1
fi
echo "$(date -u +%H:%M:%SZ) launcher for $NEW exited" >> logs/relaunch_$NEW.log
