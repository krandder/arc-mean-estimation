#!/bin/bash
# Kill the given PIDs on the VM (if any), push files from gpu_src (paths relative to gpu_src), print remote hashes.
# usage: gpu_push.sh <ip> "<pids or empty>" file1 file2 ...
WORK=/home/agent/workspaces/mats/work/bit-accounting
IP=$1; PIDS=$2; shift 2
SSH="ssh -i $WORK/infra/state/soup_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 soup@$IP"
if [ -n "$PIDS" ]; then timeout 30 $SSH "sudo kill $PIDS; sleep 3; ps -eo pid,args | grep -E 'run_curves|run_chain|run_kelvin|run_noisy' | grep -v grep | wc -l"; fi
for f in "$@"; do
  timeout 30 $SSH "sudo mkdir -p /root/soup/$(dirname $f) && sudo tee /root/soup/$f >/dev/null" < "$WORK/gpu_src/$f"
done
timeout 30 $SSH "cd /tmp && for f in $*; do sudo sha256sum /root/soup/\$f; done"
(cd $WORK/gpu_src && sha256sum "$@")
