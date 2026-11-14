#!/bin/bash
# Amendment P1-A post-pass: extra certificates (run_vr_cert2.py) on every finished P1 cell present on this VM (main
# cells computed here and those restored from prior/P1 with their .pt models). Waits for the main P1 slots of this VM
# (30_p1.sh) to finish if they run here. NSLOT parallel slots; a cell is claimed with mkdir. Ends with STOP.
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/P1 /root/runs/P1X/claims
[ -d prior/P1 ] && cp -n prior/P1/*.json prior/P1/*.pt /root/runs/P1/ 2>/dev/null
[ -d prior/P1X ] && cp -n prior/P1X/*.json /root/runs/P1X/ 2>/dev/null
while [ -e /root/runs/worker/30_p1.sh.started ] && [ ! -e /root/runs/worker/30_p1.sh.done ]; do sleep 30; done
NSLOT=${NSLOT:-6}
slot() {
  # order: relu local cells, relu unres cells, then the controls (budget may end the run before the controls)
  for j in $( (ls /root/runs/P1/P_relu_*_local.json; ls /root/runs/P1/P_relu_*_unres.json; ls /root/runs/P1/P_*.json | grep -v P_relu_) 2>/dev/null | xargs -n1 basename | sed 's/\.json$//'); do
    [ -e /root/runs/P1/$j.pt ] || continue
    [ -e /root/runs/P1X/X_${j#P_}.json ] && continue
    mkdir /root/runs/P1X/claims/$j 2>/dev/null || continue
    echo "$j" > /tmp/cell_$1.txt
    echo "$(date -u +%T) slot $1 start $j" >> /root/runs/P1X/slots.log
    python scripts/run_vr_cert2.py --runs /root/runs/P1 --cells /tmp/cell_$1.txt --out /root/runs/P1X >> /root/runs/P1X/log_slot$1.txt 2>&1
    echo "$(date -u +%T) slot $1 end $j rc=$?" >> /root/runs/P1X/slots.log
  done
}
for i in $(seq 1 $NSLOT); do slot $i & sleep 10; done
wait
touch /root/soup/queue/STOP
