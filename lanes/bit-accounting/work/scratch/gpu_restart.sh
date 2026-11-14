#!/bin/bash
# Stop the given PIDs on the VM, move old outputs aside (/root/old, not synced back), push the patched code and the
# new queue files. usage: gpu_restart.sh <ip> <pid>...
WORK=/home/agent/workspaces/mats/work/bit-accounting
IP=$1; shift
SSH="ssh -i $WORK/infra/state/soup_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15 soup@$IP"
timeout 30 $SSH "sudo kill $*; sleep 3; sudo mkdir -p /root/old/S_curves /root/old/S_chain; sudo find /root/runs/S_curves -name 'S_*.json' -exec mv {} /root/old/S_curves/ \; ; sudo find /root/runs/S_chain -name 'C_*' -exec mv {} /root/old/S_chain/ \; ; ps -eo pid,args | grep -E 'run_curves|run_chain' | grep -v grep | wc -l"
for f in lib/smallnets.py scripts/run_chain.py scripts/run_curves.py queue/04_curves.sh queue/05_chain.sh; do
  timeout 30 $SSH "sudo tee /root/soup/$f >/dev/null" < "$WORK/gpu_src/$f"
done
timeout 30 $SSH "cd /root/soup && sudo sha256sum lib/smallnets.py scripts/run_chain.py scripts/run_curves.py queue/04_curves.sh queue/05_chain.sh"
(cd $WORK/gpu_src && sha256sum lib/smallnets.py scripts/run_chain.py scripts/run_curves.py queue/04_curves.sh queue/05_chain.sh)
