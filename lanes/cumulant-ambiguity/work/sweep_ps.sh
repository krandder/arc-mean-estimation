#!/bin/bash
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
for n in "$@"; do
  nice -n 19 ionice -c3 python3 ps.py --n $n --L 1 2 3 4 6 --d ${DS:-2 3 4} --N0 3000 --N1 3000 --nets 3 --maxrank 1500 --out runs/ps_n$n.jsonl
done
