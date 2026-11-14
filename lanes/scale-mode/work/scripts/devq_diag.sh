#!/bin/bash
# dev queue (not scored): RQMC and the claim's estimator on diagonal dev nets (L = n/4): claim cell B nets 0-1 (64x16) and
# our-stream dev nets 699 at 128x32 and 256x64. Starts when the claimB reproduction (PID $1) has exited.
cd /home/agent/workspaces/mats/work/scale-mode
while kill -0 $1 2>/dev/null; do sleep 20; done
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs_dev
for job in "truth claim:B:64:16:0 24" "rqmc claim:B:64:16:0 8,10,12,14 8" "lv claim:B:64:16:0" \
           "truth claim:B:64:16:1 24" "rqmc claim:B:64:16:1 8,10,12,14 8" "lv claim:B:64:16:1" \
           "truth au:699:128:32 23" "lv au:699:128:32" "rqmc au:699:128:32 8,10,12,14 8" "arc au:699:128:32 k2,k2a" "sl3 au:699:128:32" \
           "truth au:699:256:64 22" "lv au:699:256:64" "rqmc au:699:256:64 8,10,12,14 8" "arc au:699:256:64 k2,k2a"; do
  set -- $job
  scripts/iso.sh 4 $R $TP $O $job >> logs/devq_diag.log 2>&1
  echo "done $job $(date -u +%H:%M:%SZ)" >> logs/devq_diag.log
done
