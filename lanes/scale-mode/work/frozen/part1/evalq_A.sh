#!/bin/bash
# Evaluation queue A (registered in PREREG.md): E1 (256x32, seeds 200-204), E2 (L = n/8, seeds 300-307),
# E3 cells 64x16, 128x32, 256x64 (L = n/4, fresh nets), E4 (Phase 2 public MLPs 0-11) without K3.
cd /home/agent/workspaces/mats/work/scale-mode
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs; LOG=logs/evalq_A.log
run() { scripts/iso.sh 4 $R $TP $O "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
cell() {  # n L seed0 count log2truth rqmc_m_list
  for t in $(seq 0 $(($4 - 1))); do s=$(($3 + t)); net=au:$s:$1:$2
    run truth $net $5; run lv $net; run arc $net k2,k2a,k3f; run sl3 $net; run rqmc $net $6 8
  done; }
echo "evalA start $(date -u +%H:%M:%SZ)" >> $LOG
for s in 200 201 202 203 204; do run lv au:$s:256:32; run sl3 au:$s:256:32; run cov au:$s:256:32; done
for nl in "32 4" "64 8" "128 16"; do set -- $nl
  for s in 300 301 302 303 304 305 306 307; do run lv au:$s:$1:$2; run sl3 au:$s:$1:$2; done; done
cell 64 16 600 8 22 8,10,12,14
cell 128 32 610 8 22 8,10,12,14
cell 256 64 620 8 20 8,10,12,14
for i in 0 1 2 3 4 5 6 7 8 9 10 11; do
  run arc p2:$i k2,k2a; run lv p2:$i; run cov p2:$i
  if [ $i -le 5 ]; then run rqmc p2:$i 8,10,12,14,16 8; else run rqmc p2:$i 8,10,12,14 8; fi
done
echo "evalA end $(date -u +%H:%M:%SZ)" >> $LOG
