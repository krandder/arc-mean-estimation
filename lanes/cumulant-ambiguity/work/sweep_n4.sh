#!/bin/bash
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
for tg in unit readout; do
  nice -n 19 ionice -c3 python3 lw.py --n 4 --L 1 2 3 4 6 8 --d 1 2 3 4 5 6 --N0 4000 --N1 4000 --nets 5 --target $tg --maxrank 700 --out runs/n4.jsonl
done
