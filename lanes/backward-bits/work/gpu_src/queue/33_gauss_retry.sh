#!/bin/bash
# Retry of the two amended Gaussian jobs that hit CUDA out-of-memory (16x16 and 16x8, seed 5000): wait until at most 6
# job processes are running, then run both (2 at a time).
cd /root/soup
LOG=/root/runs/logs/gauss3
mkdir -p $LOG
while [ "$(pgrep -fc 'python scripts/')" -gt 6 ]; do sleep 30; done
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
bash scripts/pool.sh queue/gauss3_jobs.txt 2 $LOG
echo "gauss3 done $(date -u +%FT%TZ)" > $LOG/DONE
