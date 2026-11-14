#!/bin/bash
# GPU worker: runs every queue/*.sh once (in name order, each in the background, so a queue file controls its own
# parallelism); new queue files can be copied in while it runs. Exits after queue/STOP appears and all jobs finished.
mkdir -p /root/soup/queue /root/runs/worker
nvidia-smi > /root/runs/worker/nvidia-smi.txt 2>&1 || true
while true; do
  for f in $(ls /root/soup/queue/*.sh 2>/dev/null | sort); do
    b=$(basename "$f")
    [ -e "/root/runs/worker/$b.started" ] && continue
    date -u +%FT%TZ > "/root/runs/worker/$b.started"
    ( bash "$f" > "/root/runs/worker/$b.log" 2>&1; echo "exit $? $(date -u +%FT%TZ)" > "/root/runs/worker/$b.done" ) &
  done
  if [ -e /root/soup/queue/STOP ]; then wait; echo "worker stop $(date -u +%FT%TZ)" > /root/runs/worker/STOPPED; exit 0; fi
  sleep 15
done
