#!/bin/bash
# Dev run 2 (seed 9100, not scored): reduced sizes, job pool of 7: output codes, the four chains per net, then the truth
# passes, the Gaussian-channel and forward-trained comparisons, and the estimator convergence checks.
cd /root/soup
LOG=/root/runs/logs/dev2
mkdir -p $LOG
bash scripts/pool.sh queue/dev2_outcode.txt 4 $LOG
bash scripts/pool.sh queue/dev2_chains.txt 7 $LOG
cat queue/dev2_post.txt queue/dev2_extra.txt queue/dev2_conv.txt > queue/dev2_postall.txt
bash scripts/pool.sh queue/dev2_postall.txt 7 $LOG
echo "dev2 done $(date -u +%FT%TZ)" > $LOG/DONE
