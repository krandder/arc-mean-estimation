#!/bin/bash
cd /home/agent/workspaces/mats/work/moment-matching
while kill -0 $(cat runs/sched3.pid) 2>/dev/null; do sleep 30; done
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python cg.py --n 6 --d 6 --only relu_L1_net0 relu_L2_net0 relu_L4_net0 relu_L8_net0 --rounds 30 --rtol 0.05 --out runs/cg_n6.jsonl > runs/cg_n6_d6.log 2>&1
