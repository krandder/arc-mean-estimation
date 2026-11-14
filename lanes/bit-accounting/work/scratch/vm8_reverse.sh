#!/bin/bash
# VM 8 (run as root): the P1-A post-pass runs the same cell order as VM 7, so the two VMs would duplicate work.
# Hold the worker (SIGSTOP; the 5 h timeout still ends the run), stop this VM's post-pass slots (by PID), and restart
# the post-pass in REVERSED cell order; when it finishes, release the worker (SIGCONT) so the VM syncs and is deleted.
W=$(pgrep -o -f "bash scripts/worker.sh")
kill -STOP "$W" && echo "worker $W held"
for p in $(ps -eo pid,args | grep -E "queue/32_p1x.sh|run_vr_cert2.py" | grep -v grep | awk '{print $1}'); do
  kill "$p" 2>/dev/null && echo "killed $p"
done
sleep 5
mv /root/runs/P1X/claims "/root/runs/P1X/claims_old_$(date -u +%H%M%S)" && mkdir -p /root/runs/P1X/claims
cat > /root/soup/rev_p1x.sh <<EOF
#!/bin/bash
cd /root/soup
export PATH=/root/venv/bin:\$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
slot() {
  for j in \$( (ls /root/runs/P1/P_relu_*_local.json | tac; ls /root/runs/P1/P_relu_*_unres.json | tac; ls /root/runs/P1/P_*.json | grep -v P_relu_ | tac) 2>/dev/null | xargs -n1 basename | sed 's/\.json\$//'); do
    [ -e /root/runs/P1/\$j.pt ] || continue
    [ -e /root/runs/P1X/X_\${j#P_}.json ] && continue
    mkdir /root/runs/P1X/claims/\$j 2>/dev/null || continue
    echo "\$j" > /tmp/rcell_\$1.txt
    echo "\$(date -u +%T) rslot \$1 start \$j" >> /root/runs/P1X/slots.log
    python scripts/run_vr_cert2.py --runs /root/runs/P1 --cells /tmp/rcell_\$1.txt --out /root/runs/P1X >> /root/runs/P1X/log_rslot\$1.txt 2>&1
    echo "\$(date -u +%T) rslot \$1 end \$j rc=\$?" >> /root/runs/P1X/slots.log
  done
}
for i in 1 2 3 4 5 6; do slot \$i & sleep 10; done
wait
kill -CONT $W
EOF
setsid nohup bash /root/soup/rev_p1x.sh > /root/runs/P1X/rev.log 2>&1 < /dev/null &
echo "reverse post-pass started pid $!"
