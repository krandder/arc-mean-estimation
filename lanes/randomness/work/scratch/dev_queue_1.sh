#!/bin/bash
# Dev (not scored): structure runs on dev nets (256 x 32 seeds 100, 101 with sigma=1e-3 truths as approximations;
# ladder seed 9500 at n = 32, 64, 128 with arc-update's 2^22-path dev truths are not in runs/, so V from samples).
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export RND_NOISY_TRUTH=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
for s in 100 101; do
  nice -n 19 ionice -c3 $PY scratch/structure.py $s 256 32 --out runs/dev_struct_n256_L32_s$s.json >> logs/dev_struct.log 2>&1
done
for nl in "32 4" "64 8" "128 16"; do
  set -- $nl
  nice -n 19 ionice -c3 $PY scratch/structure.py 9500 $1 $2 --out runs/dev_struct_n$1_L$2_s9500.json >> logs/dev_struct.log 2>&1
done
echo "dev_queue_1 done $(date -u +%H:%M:%SZ)" >> logs/dev_struct.log
