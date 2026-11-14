#!/bin/bash
# Amendment P1-B (more explorer restarts), after 50_unscr.sh. Cells by hostname (bitacct-12 -> jobs_y_1, else jobs_y_2).
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
while [ -e /root/runs/worker/50_unscr.sh.started ] && [ ! -e /root/runs/worker/50_unscr.sh.done ]; do sleep 30; done
mkdir -p /root/runs/P1Y/claims /root/runs/P1
cp -n prior/P1/*.json /root/runs/P1/ 2>/dev/null
case "$(hostname)" in *bitacct-12*) LIST=queue_lists/jobs_y_1.txt ;; *) LIST=queue_lists/jobs_y_2.txt ;; esac
slot() {
  while read -r name; do
    [ -z "$name" ] && continue
    mkdir /root/runs/P1Y/claims/$name 2>/dev/null || continue
    echo "$name" > /tmp/ycell_$1.txt
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/P1Y/slots.log
    python scripts/run_vr_cert3.py --runs /root/runs/P1 --cells /tmp/ycell_$1.txt --out /root/runs/P1Y >> /root/runs/P1Y/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/P1Y/slots.log
  done < $LIST
}
for i in 1 2 3 4 5 6; do slot $i & sleep 15; done
wait
