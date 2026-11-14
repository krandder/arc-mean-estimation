#!/bin/bash
cd /home/agent/workspaces/mats/work/moment-matching
(until grep -q "relu_L1_net0" runs/cg_n6_d6.log; do sleep 30; done; kill 3798367) &
(until grep -q "relu_L4_net0" runs/cg_n6_d6b.log; do sleep 30; done; kill 639284) &
wait
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python cg.py --n 4 --d 6 --only relu_L4_net1 --rounds 100 --rtol 0.05 --out runs/cg_n4.jsonl > runs/cg_n4_fix6c.log 2>&1
