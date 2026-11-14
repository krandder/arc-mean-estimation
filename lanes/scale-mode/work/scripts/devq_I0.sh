#!/bin/bash
# dev (not scored): the claim's own cell I net 0 (1024x256, seed 8026560): LVTV2 V_L must equal the claim's log (0.0284);
# also gives the CPU timing of the estimator at 1024x256. Starts when PID $1 has exited.
cd /home/agent/workspaces/mats/work/scale-mode
while kill -0 $1 2>/dev/null; do sleep 20; done
scripts/iso.sh 4 scripts/dev_check.py thirdparty/scale-separation runs_dev claimI0 >> logs/dev_claimI0.log 2>&1
echo "done claimI0 $(date -u +%H:%M:%SZ)" >> logs/dev_claimI0.log
