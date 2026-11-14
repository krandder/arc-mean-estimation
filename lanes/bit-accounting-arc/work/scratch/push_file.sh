#!/bin/bash
# Copy one local file to a path under /root/soup or /root/runs on a running bit-accounting-arc VM (as root).
# usage: push_file.sh <run-id> <local file> <remote path>
RUN_ID=$1; SRC=$2; DST=$3
case "$DST" in /root/soup/*|/root/runs/*) ;; *) echo "refusing destination $DST"; exit 2 ;; esac
WORK=/home/agent/workspaces/mats/work/bit-accounting-arc
KEY=$WORK/infra/state/soup_ed25519
IP=$(gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$RUN_ID" --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)
[ -n "$IP" ] || { echo "no VM for $RUN_ID"; exit 1; }
SSH="ssh -i $KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
$SSH soup@$IP "sudo mkdir -p $(dirname $DST) && sudo tee $DST >/dev/null" < "$SRC" && echo "pushed $SRC -> $RUN_ID:$DST"
