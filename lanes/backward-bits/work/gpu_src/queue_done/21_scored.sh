#!/bin/bash
# Scored run, relaunch after a CUDA out-of-memory at 14:20Z (dev 3 + scored = 11 processes on 22 GB): dev 3 dropped,
# 6 workers, expandable allocator segments, pool.sh v2 (exit codes logged). Same registered job files; the chains resume
# from completed steps.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LOG=/root/runs/logs/scored
mkdir -p $LOG
echo "relaunch 21 $(date -u +%FT%TZ)" >> $LOG/pool.log
bash scripts/pool.sh queue/scored_chains.txt 6 $LOG
cat queue/scored_post.txt queue/scored_extra.txt queue/scored_conv.txt > queue/scored_postall.txt
bash scripts/pool.sh queue/scored_postall.txt 6 $LOG
echo "scored done $(date -u +%FT%TZ)" > $LOG/DONE
