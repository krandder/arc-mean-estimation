#!/bin/bash
# Dev 3 (seed 9100, 8x8 only, not scored): the four chains, then the truth, Gaussian, forward and convergence passes:
# a full-size test of the evaluation scripts while the scored runs proceed.
cd /root/soup
LOG=/root/runs/logs/dev3
mkdir -p $LOG
bash scripts/pool.sh queue/dev3_chains.txt 4 $LOG
bash scripts/pool.sh queue/dev3_post.txt 5 $LOG
echo "dev3 done $(date -u +%FT%TZ)" > $LOG/DONE
