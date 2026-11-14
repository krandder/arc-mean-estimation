#!/bin/bash
# Queue B2 = the CPU remainder of the registered queue B after the 1024 x 256 cell moved to the GPU (PREREG Amendment 1):
# the 512 x 128 nets 631-633 exactly as registered, then the E4 K3 rows (MLPs 0-5). Starts when PID $1 (the queue B job
# that was running, rqmc au:630:512:128) has exited.
cd /home/agent/workspaces/mats/work/scale-mode
while kill -0 $1 2>/dev/null; do sleep 10; done
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs; LOG=logs/evalq_B.log
run() { scripts/iso.sh 4 $R $TP $O "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
echo "evalB2 start $(date -u +%H:%M:%SZ)" >> $LOG
for s in 631 632 633; do net=au:$s:512:128; run truth $net 18; run lv $net; run arc $net k2,k2a; run rqmc $net 8,10,12,13 8; done
for i in 0 1 2 3 4 5; do run arc p2:$i k3f; run sl3 p2:$i; done
echo "evalB2 end $(date -u +%H:%M:%SZ)" >> $LOG
