#!/bin/bash
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /home/agent/workspaces/mats/work/cumulant-ambiguity
nice -n 19 ionice -c3 python3 ps.py --n 4 --L 2 3 4 6 --d 2 3 --N0 3000 --N1 3000 --nets 3 --maxrank 1500 --out runs/ps_n4.jsonl
nice -n 19 ionice -c3 python3 ps.py --n 6 --L 2 3 4 --d 2 3 --N0 3000 --N1 3000 --nets 2 --maxrank 1500 --out runs/ps_n6.jsonl
