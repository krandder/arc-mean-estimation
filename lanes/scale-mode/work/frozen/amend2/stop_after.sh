#!/bin/bash
# Stop a queue script (PID $1) by PID right after LOG ($2) contains the line pattern $3; kill any child whose command line
# matches $4 (a job that belongs to the part moved to the GPU). Writes a note to the log.
cd /home/agent/workspaces/mats/work/scale-mode
until grep -q "$3" "$2"; do sleep 5; done
kids=$(pgrep -P $1)
kill $1
for c in $kids; do
  if tr '\0' ' ' < /proc/$c/cmdline 2>/dev/null | grep -q -E "$4"; then kill $c; echo "killed child $c ($4) $(date -u +%H:%M:%SZ)" >> "$2"; fi
done
echo "queue PID $1 stopped after '$3' $(date -u +%H:%M:%SZ); the rest runs on the GPU (Amendment 2)" >> "$2"
