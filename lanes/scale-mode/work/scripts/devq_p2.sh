#!/bin/bash
# dev queue: Phase 2 public dev MLP 12 (not scored): timing and calibration of every method.
cd /home/agent/workspaces/mats/work/scale-mode
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs_dev
for job in "arc p2:12 k2,k2a" "lv p2:12" "cov p2:12" "rqmc p2:12 8,10,12,14,16 8" "arc p2:12 k3f" "sl3 p2:12"; do
  set -- $job
  scripts/iso.sh 4 $R $TP $O $job >> logs/devq_p2.log 2>&1
  echo "done $job $(date -u +%H:%M:%SZ)" >> logs/devq_p2.log
done
