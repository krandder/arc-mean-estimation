#!/bin/bash
# Amendment P2.0-b (noisy nets), after 60_p1b.sh. Jobs by hostname (bitacct-12 -> jobs_n_1, else jobs_n_2). Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
while [ ! -e /root/runs/worker/60_p1b.sh.done ]; do sleep 30; done
mkdir -p /root/runs/N/claims
case "$(hostname)" in *bitacct-12*) LIST=queue_lists/jobs_n_1.txt ;; *) LIST=queue_lists/jobs_n_2.txt ;; esac
slot() {
  while read -r name args; do
    [ -z "$name" ] && continue
    mkdir /root/runs/N/claims/$name 2>/dev/null || continue
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/N/slots.log
    python scripts/run_vr_noisy.py $args --out /root/runs/N >> /root/runs/N/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/N/slots.log
  done < $LIST
}
for i in 1 2 3 4 5 6; do slot $i & sleep 15; done
wait
touch /root/soup/queue/STOP
