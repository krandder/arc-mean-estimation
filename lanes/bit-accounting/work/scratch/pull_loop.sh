#!/bin/bash
# Pull /root/runs from the VM every 4 minutes until the VM is gone (protects against spot preemption losses).
# usage: pull_loop.sh <run-id>
cd /home/agent/workspaces/mats/work/bit-accounting
miss=0; ok=0
while true; do
  if bash scratch/gpu_pull.sh "$1" > logs/pull_loop_last.txt 2>&1; then
    miss=0; ok=1
    echo "$(date -u +%H:%M:%SZ) pulled" >> logs/pull_loop.log
  else
    miss=$((miss + 1))
    echo "$(date -u +%H:%M:%SZ) pull failed ($miss)" >> logs/pull_loop.log
    [ $ok -eq 1 ] && [ $miss -ge 6 ] && exit 0
  fi
  sleep 240
done
