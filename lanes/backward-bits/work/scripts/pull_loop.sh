#!/bin/bash
# Pull /root/runs from the VM every 3 minutes until the VM is gone (spot preemption protection).
# usage: pull_loop.sh <run-id>
cd /home/agent/workspaces/mats/work/backward-bits
miss=0; ok=0
while true; do
  if bash scripts/gpu_pull.sh "$1" > logs/pull_loop_last.txt 2>&1; then
    miss=0; ok=1; echo "$(date -u +%H:%M:%SZ) pulled" >> logs/pull_loop.log
  else
    miss=$((miss + 1)); echo "$(date -u +%H:%M:%SZ) pull failed ($miss)" >> logs/pull_loop.log
    [ $ok -eq 1 ] && [ $miss -ge 6 ] && exit 0
  fi
  sleep 180
done
