#!/bin/bash
# Part U (unscrambling at fixed rate): restore the P1 (layer l) and P2a (layer l+1) local models, then 6 slots run
# run_unscr.py jobs; the job list is chosen by hostname (bitacct-12 -> jobs_u_1, else jobs_u_2). Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/P1 /root/runs/P2a /root/runs/U/claims
cp -n prior/P1/* /root/runs/P1/ 2>/dev/null; cp -n prior/P2a/* /root/runs/P2a/ 2>/dev/null
case "$(hostname)" in
  *bitacct-12*) LIST=queue_lists/jobs_u_1.txt ;;
  *) LIST=queue_lists/jobs_u_2.txt ;;
esac
slot() {
  while read -r name args; do
    [ -z "$name" ] && continue
    mkdir /root/runs/U/claims/$name 2>/dev/null || continue
    echo "$(date -u +%T) slot $1 start $name" >> /root/runs/U/slots.log
    python scripts/run_unscr.py $args --p1 /root/runs/P1 --p2a /root/runs/P2a --out /root/runs/U >> /root/runs/U/log_$name.txt 2>&1
    echo "$(date -u +%T) slot $1 end $name rc=$?" >> /root/runs/U/slots.log
  done < $LIST
}
for i in 1 2 3 4 5 6; do slot $i & sleep 15; done
wait
# (no STOP: 60_p1b.sh and 70_noisy.sh follow)
