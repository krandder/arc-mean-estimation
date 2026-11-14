#!/bin/bash
cd /home/agent/workspaces/mats/work/nd-exact
while kill -0 4137748 2>/dev/null; do sleep 5; done
echo "eval start $(date -u +%H:%M:%SZ)"
scratch/queue_eval.sh 203 216 217 220 221 223
echo "eval end $(date -u +%H:%M:%SZ)"
