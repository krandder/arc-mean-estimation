#!/bin/bash
# After the spot preemptions: one VM runs the noisy cells first (P2.0 part 5, 32x32 first), then the remaining P1-B
# cells (finished ones restored from prior/P1Y are skipped). 6 slots each phase. Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/P1 /root/runs/P1Y/claims /root/runs/N/claims
cp -n prior/P1/*.json /root/runs/P1/ 2>/dev/null; cp -n prior/P1Y/*.json /root/runs/P1Y/ 2>/dev/null
nslot() {
  while read -r name args; do
    [ -z "$name" ] && continue
    mkdir /root/runs/N/claims/$name 2>/dev/null || continue
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/N/slots.log
    python scripts/run_vr_noisy.py $args --out /root/runs/N >> /root/runs/N/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/N/slots.log
  done < queue_lists/jobs_n_all.txt
}
yslot() {
  while read -r name; do
    [ -z "$name" ] && continue
    [ -e /root/runs/P1Y/Y_${name#P_}.json ] && continue
    mkdir /root/runs/P1Y/claims/$name 2>/dev/null || continue
    echo "$name" > /tmp/ycell_$1.txt
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/P1Y/slots.log
    python scripts/run_vr_cert3.py --runs /root/runs/P1 --cells /tmp/ycell_$1.txt --out /root/runs/P1Y >> /root/runs/P1Y/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/P1Y/slots.log
  done < queue_lists/jobs_y_all.txt
}
for i in 1 2 3 4 5 6; do nslot $i & sleep 10; done
wait
for i in 1 2 3 4 5 6; do yslot $i & sleep 10; done
wait
touch /root/soup/queue/STOP
