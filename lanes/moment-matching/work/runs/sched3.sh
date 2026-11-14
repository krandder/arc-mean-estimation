#!/bin/bash
cd /home/agent/workspaces/mats/work/moment-matching
PY=/home/agent/.venvs/arc-noisy/bin/python
run() { OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 ionice -c3 $PY cg.py "$@"; }
run --n 4 --d 5 --only relu_L8_net0 --rounds 100 --rtol 0.05 --verbose --out runs/cg_n4.jsonl > runs/cg_n4_fix5b.log 2>&1
run --n 4 --d 8 --only relu_L8_net0 relu_L1_net1 relu_L2_net1 relu_L4_net1 relu_L8_net1 relu_L1_net2 relu_L2_net2 relu_L4_net2 relu_L8_net2 --rounds 40 --rtol 0.05 --out runs/cg_n4.jsonl > runs/cg_n4_d8b.log 2>&1
run --n 4 --d 6 --only relu_L8_net0 relu_L1_net1 relu_L8_net1 relu_L1_net2 --rounds 100 --rtol 0.05 --out runs/cg_n4.jsonl > runs/cg_n4_fix6b.log 2>&1
OMP_NUM_THREADS=1 nice -n 19 ionice -c3 $PY fs.py > runs/fs.log 2>&1
