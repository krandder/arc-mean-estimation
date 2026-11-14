#!/bin/bash
# Gaussian-channel comparison, amended (notes/DEVIATIONS.md D8): power-constrained codes (per-dimension SNR grid), seed
# 5000 per config, layers L-2, floor((L-1)/2), 0. Output chainK/gauss_p.json.
cd /root/soup
LOG=/root/runs/logs/gauss2
mkdir -p $LOG
bash scripts/pool.sh queue/gauss2_jobs.txt 4 $LOG
echo "gauss2 done $(date -u +%FT%TZ)" > $LOG/DONE
