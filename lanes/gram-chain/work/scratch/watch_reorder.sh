#!/bin/bash
# Reorder: when queue_A1 starts share n=1024, stop that run and its shell so Part C (queue_P1b) starts; queue_P3 reruns share 1024 after P1b.
while kill -0 894819 2>/dev/null; do
  P=$(pgrep -f "partA.py share 1024")
  if [ -n "$P" ]; then kill 894819; kill $P; echo "stopped share 1024 pid $P at $(date -u +%H:%M:%SZ)"; break; fi
  sleep 15
done
