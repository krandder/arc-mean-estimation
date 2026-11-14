#!/bin/bash
# Post-hoc held-out Walsh statistics and one-step decoding for the S11 sign-bit chains (feistel, tanh4), as soon as
# each saved chain has been pulled from the VM. Stops when both are done or after 3 h.
cd /home/agent/workspaces/mats/work/bit-accounting
PY=/home/agent/.venvs/arc-noisy/bin/python
for i in $(seq 1 36); do
  left=0
  for k in feistel tanh4; do
    pt=runs/S11_$k/C_n16_L16_s5000_local.pt
    out=results/S11_${k}_posthoc.json
    if [ -e "$pt" ] && [ ! -e "$out" ]; then
      sleep 60   # let the rsync of the .pt finish
      CHAIN_DIR=runs/S11_$k NETKIND=$k POSTHOC_OUT=$out OMP_NUM_THREADS=2 nice -n 19 ionice -c3 $PY scratch/chain_posthoc.py >> logs/posthoc_s11_$k.log 2>&1
      CHAIN_DIR=runs/S11_$k NETKIND=$k ONESTEP_OUT=results/S11_${k}_onestep.json OMP_NUM_THREADS=2 nice -n 19 ionice -c3 $PY scratch/chain_onestep.py >> logs/onestep_s11_$k.log 2>&1
      echo "$(date -u +%H:%M:%SZ) $k done" >> logs/posthoc_s11.log
    fi
    [ -e "$out" ] || left=1
  done
  [ $left -eq 0 ] && exit 0
  sleep 300
done
