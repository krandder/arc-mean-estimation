#!/bin/bash
# Pull /root/runs (no *.pt) from the VM every 4 minutes until it is gone. usage: pull_loop.sh <run-id>
cd /home/agent/workspaces/mats/work/bit-accounting-arc
miss=0; ok=0
while true; do
  if bash scratch/gpu_pull.sh "$1" > logs/pull_loop_$1_last.txt 2>&1; then
    miss=0; ok=1
    echo "$(date -u +%H:%M:%SZ) pulled" >> logs/pull_loop_$1.log
  else
    miss=$((miss + 1))
    echo "$(date -u +%H:%M:%SZ) pull failed ($miss)" >> logs/pull_loop_$1.log
    [ $ok -eq 1 ] && [ $miss -ge 6 ] && exit 0
  fi
  sleep 240
done
