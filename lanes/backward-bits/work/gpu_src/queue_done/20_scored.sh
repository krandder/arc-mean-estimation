#!/bin/bash
# Scored run (seeds 5000-5002, registered in PREREG.md before this file was pushed): job pool of 7: output codes, the
# four chains per net, then the truth passes, the Gaussian-channel and forward-trained comparisons, the estimator checks.
cd /root/soup
LOG=/root/runs/logs/scored
mkdir -p $LOG
bash scripts/pool.sh queue/scored_outcode.txt 6 $LOG
bash scripts/pool.sh queue/scored_chains.txt 7 $LOG
cat queue/scored_post.txt queue/scored_extra.txt queue/scored_conv.txt > queue/scored_postall.txt
bash scripts/pool.sh queue/scored_postall.txt 7 $LOG
echo "scored done $(date -u +%FT%TZ)" > $LOG/DONE
