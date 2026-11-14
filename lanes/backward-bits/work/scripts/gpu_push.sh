#!/bin/bash
# Push files (paths relative to gpu_src) to the running VM; print remote and local hashes.
# usage: gpu_push.sh <run-id> file1 file2 ...
RUN_ID=$1; shift
WORK=/home/agent/workspaces/mats/work/backward-bits
IP=$(gcloud --project=mnx-kas-dev --quiet compute instances list --filter="labels.soup-run=$RUN_ID" --format='value(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)
[ -n "$IP" ] || { echo "no VM for $RUN_ID"; exit 1; }
SSH="ssh -i $WORK/infra/state/soup_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 soup@$IP"
for f in "$@"; do
  timeout 30 $SSH "sudo mkdir -p /root/soup/$(dirname $f) && sudo tee /root/soup/$f >/dev/null" < "$WORK/gpu_src/$f"
done
timeout 30 $SSH "cd /tmp && for f in $*; do sudo sha256sum /root/soup/\$f; done"
(cd $WORK/gpu_src && sha256sum "$@")
