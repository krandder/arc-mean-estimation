#!/bin/bash
# Pull /root/runs from the running bit-accounting VM into runs/ (no delete); optional: push a queue file.
# usage: gpu_pull.sh <run-id> [queue-file-to-push]
RUN_ID=${1:-bitacct-1}
WORK=/home/agent/workspaces/mats/work/bit-accounting
KEY=$WORK/infra/state/soup_ed25519
IP=$(gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$RUN_ID" --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)
[ -n "$IP" ] || { echo "no VM for $RUN_ID"; exit 1; }
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
if [ -n "$2" ]; then
  $SSH soup@$IP "sudo mkdir -p /root/soup/queue && sudo tee /root/soup/queue/$(basename $2) >/dev/null" < "$2" && echo "pushed $2"
fi
rsync -az --rsync-path="sudo rsync" -e "$SSH" soup@$IP:/root/runs/ $WORK/runs/ && echo "pulled from $IP"
