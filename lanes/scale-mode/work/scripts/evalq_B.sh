#!/bin/bash
# Evaluation queue B (registered in PREREG.md): E3 512x128 (4 nets), E4 K3 rows (MLPs 0-5), E3 1024x256 (640-642, then 643).
cd /home/agent/workspaces/mats/work/scale-mode
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs; LOG=logs/evalq_B.log
run() { scripts/iso.sh 4 $R $TP $O "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
echo "evalB start $(date -u +%H:%M:%SZ)" >> $LOG
for s in 630 631 632 633; do net=au:$s:512:128; run truth $net 18; run lv $net; run arc $net k2,k2a; run rqmc $net 8,10,12,13 8; done
for i in 0 1 2 3 4 5; do run arc p2:$i k3f; run sl3 p2:$i; done
for s in 640 641 642 643; do net=au:$s:1024:256; run truth $net 17; run lv $net; run arc $net k2,k2a; run rqmc $net 8,10,12 8; done
echo "evalB end $(date -u +%H:%M:%SZ)" >> $LOG
