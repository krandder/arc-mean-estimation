#!/bin/bash
# POST HOC (review round 2, finding 1): direct scoring of the H1 hybrid estimates, same nets and layers as eval_C.sh.
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
echo "queue H start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do
  $PY scratch/run_hyb_direct.py 256 32 $s --layers 1,2,4,8,16,24 --qk 16 >> logs/eval_hybd.log 2>&1
done
for s in 300 301 302 303 304 305 306 307; do
  $PY scratch/run_hyb_direct.py 64 8 $s --layers 1,2,4,6 --qk 16 >> logs/eval_hybd.log 2>&1
  $PY scratch/run_hyb_direct.py 128 16 $s --layers 1,2,4,8,12 --qk 16 >> logs/eval_hybd.log 2>&1
done
echo "queue H done $(date -u +%H:%M:%SZ)" >> logs/queue.log
