#!/bin/bash
# P2.0 parts 2-4: P1-method codes (G1 only, no certificates) at layer l+1 for each grid layer l < L-1, relu 16x16 and
# 32x32 seeds 5000-5002 and tanh4 16x16 s5000. 6 slots; the job list is chosen by hostname. Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/P2a/claims
case "$(hostname)" in
  *bitacct-10*) LIST=queue_lists/jobs_p2a_1.txt ;;
  *) LIST=queue_lists/jobs_p2a_2.txt ;;
esac
slot() {
  while read -r name args; do
    [ -z "$name" ] && continue
    mkdir /root/runs/P2a/claims/$name 2>/dev/null || continue
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/P2a/slots.log
    python scripts/run_vr.py $args --out /root/runs/P2a >> /root/runs/P2a/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/P2a/slots.log
  done < $LIST
}
for i in 1 2 3 4 5 6; do slot $i & sleep 15; done
wait
touch /root/soup/queue/STOP
