#!/bin/bash
# Stop queue A (PID $1) by PID right after it logs the end of its E3 256 x 64 cell, so its E4 part (moved to queue B3)
# does not run twice; a p2 job it may already have started is killed by PID too.
cd /home/agent/workspaces/mats/work/scale-mode
until grep -q "done rqmc au:627:256:64" logs/evalq_A.log; do sleep 5; done
kids=$(pgrep -P $1)
kill $1
for c in $kids; do
  if tr '\0' ' ' < /proc/$c/cmdline 2>/dev/null | grep -q "p2:"; then kill $c; echo "killed queue A child $c (p2 job) $(date -u +%H:%M:%SZ)" >> logs/evalq_A.log; fi
done
echo "queue A stopped after E3 (PID $1) $(date -u +%H:%M:%SZ); its E4 part runs in queue B3" >> logs/evalq_A.log
