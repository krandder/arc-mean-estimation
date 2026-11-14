#!/bin/bash
# Scored run v2 (amendment A2: the reuse code is a selectable candidate; notes/DEVIATIONS.md D2). Output dir
# /root/runs/scored2 (the superseded first launch stays in /root/runs/scored). Output codes (deterministic), the four
# chains per net, then the truth, Gaussian, forward and convergence passes. 6 workers.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LOG=/root/runs/logs/scored2
mkdir -p $LOG
bash scripts/pool.sh queue/scored2_outcode.txt 6 $LOG
bash scripts/pool.sh queue/scored2_chains.txt 6 $LOG
cat queue/scored2_post.txt queue/scored2_extra.txt queue/scored2_conv.txt > queue/scored2_postall.txt
bash scripts/pool.sh queue/scored2_postall.txt 6 $LOG
echo "scored2 done $(date -u +%FT%TZ)" > $LOG/DONE
