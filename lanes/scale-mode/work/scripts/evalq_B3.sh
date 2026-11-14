#!/bin/bash
# Queue B3 (execution reshuffle, no method change): the registered E4 jobs of queue A (arc k2,k2a; lv; cov; rqmc) for
# MLPs 11..0, run after queue B2 (PID $1) ends, so they overlap queue A's E3 256 x 64 cell; queue A is stopped by PID
# (scripts/stop_A_after_E3.sh) when it finishes E3, before its own E4 part.
cd /home/agent/workspaces/mats/work/scale-mode
while kill -0 $1 2>/dev/null; do sleep 15; done
R=scripts/run_cell.py; TP=thirdparty/scale-separation; O=runs; LOG=logs/evalq_B.log
run() { scripts/iso.sh 4 $R $TP $O "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
echo "evalB3 start $(date -u +%H:%M:%SZ)" >> $LOG
for i in 11 10 9 8 7 6 5 4 3 2 1 0; do
  run arc p2:$i k2,k2a; run lv p2:$i; run cov p2:$i
  if [ $i -le 5 ]; then run rqmc p2:$i 8,10,12,14,16 8; else run rqmc p2:$i 8,10,12,14 8; fi
done
echo "evalB3 end $(date -u +%H:%M:%SZ)" >> $LOG
