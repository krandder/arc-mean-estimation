#!/bin/bash
# Phase-1 dev check of the revised run_vr.py (identity anchor, upward lambda anneal, per-lambda loss normalisation,
# correlated prior, linear reference) on dev seed 9100 only. Run on the VM as root.
mkdir -p /root/runs/P1_dev2
cd /root/soup
export PATH=/root/venv/bin:$PATH PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for spec in "16x16 0 local" "16x16 0 unres" "16x16 4 local" "32x32 8 local"; do
  set -- $spec
  setsid nohup python scripts/run_vr.py --configs $1 --seeds 9100 --layers $2 --classes $3 \
    --out /root/runs/P1_dev2 >> /root/runs/P1_dev2/log_$1_$2_$3.txt 2>&1 < /dev/null &
  echo "dev $spec pid $!"
  sleep 3
done
