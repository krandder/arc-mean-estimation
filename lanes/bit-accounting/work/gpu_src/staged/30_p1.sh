#!/bin/bash
# Phase 1 (PREREG Part P1): NSLOT parallel slots; each claims the next unclaimed job of this VM's list (mkdir lock)
# and runs run_vr.py on it. The list is chosen by the VM's hostname (bitacct-5 -> jobs_a, bitacct-6 -> jobs_b).
# Earlier results in prior/P1 are restored first (run_vr.py skips finished cells). Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/P1/claims
[ -d prior/P1 ] && cp -n prior/P1/*.json /root/runs/P1/ 2>/dev/null
case "$(hostname)" in
  *bitacct-4*) LIST=queue_lists/jobs_vm4.txt ;;
  *bitacct-5*) LIST=queue_lists/jobs_a.txt ;;
  *bitacct-6*) LIST=queue_lists/jobs_b.txt ;;
  *bitacct-7*) LIST=queue_lists/jobs_a.txt ;;
  *bitacct-8*) LIST=queue_lists/jobs_b.txt ;;
  *) LIST=queue_lists/jobs_a.txt ;;
esac
NSLOT=${NSLOT:-6}
slot() {
  while read -r name args; do
    [ -z "$name" ] && continue
    mkdir /root/runs/P1/claims/$name 2>/dev/null || continue
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/P1/slots.log
    python scripts/run_vr.py $args --out /root/runs/P1 >> /root/runs/P1/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/P1/slots.log
  done < $LIST
}
for i in $(seq 1 $NSLOT); do slot $i & sleep 15; done
wait
touch /root/soup/queue/STOP
