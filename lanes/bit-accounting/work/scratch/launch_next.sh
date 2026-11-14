#!/bin/bash
# Launch a follow-up on-demand L4 once the given VM is gone (at most 2 VMs at once).
# usage: launch_next.sh <old run-id> <new run-id> <list a|b> <timeout>
cd /home/agent/workspaces/mats/work/bit-accounting
OLD=$1; NEW=$2; LST=$3; TO=$4
while gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$OLD" --format='value(name)' 2>/dev/null | grep -q .; do sleep 30; done
echo "$(date -u +%T) $OLD gone" >> logs/launch_$NEW.log
sleep 60
while [ -e /tmp/bitacct_launch.lock ]; do sleep 20; done
touch /tmp/bitacct_launch.lock
python3 scratch/prep_next.py $LST >> logs/launch_$NEW.log 2>&1
GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh $NEW $TO > logs/gpu-run-$NEW.out 2>&1 &
until grep -q "RUN vm=soup-gpu-$NEW" GPU-LOG.md; do sleep 15; done
mv gpu_src/queue/30_p1.sh gpu_src/queue/32_p1x.sh gpu_src/staged/ 2>/dev/null
rm -f /tmp/bitacct_launch.lock
echo "$(date -u +%T) $NEW running; queue un-staged" >> logs/launch_$NEW.log
nohup bash scratch/pull_loop.sh $NEW > /dev/null 2>&1 &
