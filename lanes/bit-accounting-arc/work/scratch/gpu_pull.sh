#!/bin/bash
# Pull /root/runs from a running bit-accounting-arc VM into runs/ (no delete; *.pt only with ALL=1); optional: push a
# queue file. usage: gpu_pull.sh <run-id> [queue-file-to-push]
RUN_ID=${1:-bitarc-1}
WORK=/home/agent/workspaces/mats/work/bit-accounting-arc
KEY=$WORK/infra/state/soup_ed25519
IP=$(gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$RUN_ID" --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)
[ -n "$IP" ] || { echo "no VM for $RUN_ID"; exit 1; }
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
if [ -n "$2" ]; then
  $SSH soup@$IP "sudo mkdir -p /root/soup/queue && sudo tee /root/soup/queue/$(basename $2) >/dev/null" < "$2" && echo "pushed $2"
fi
EXC="--exclude=*.pt"; [ "${ALL:-0}" = 1 ] && EXC=""
mkdir -p $WORK/runs/$RUN_ID
rsync -az $EXC --rsync-path="sudo rsync" -e "$SSH" soup@$IP:/root/runs/ $WORK/runs/$RUN_ID/ && echo "pulled from $IP"
