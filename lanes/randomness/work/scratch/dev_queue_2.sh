#!/bin/bash
# Dev (not scored): structure runs v2 (multilevel depth fix; antipodal RQMC; polar-aligned Kerdock) on dev nets.
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export RND_NOISY_TRUTH=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
for nl in "32 4" "64 8" "128 16"; do
  set -- $nl
  nice -n 19 ionice -c3 $PY scratch/structure.py 9500 $1 $2 --out runs/dev_struct_n$1_L$2_s9500.json >> logs/dev_struct2.log 2>&1
done
for s in 100 101 102; do
  nice -n 19 ionice -c3 $PY scratch/structure.py $s 256 32 --out runs/dev_struct_n256_L32_s$s.json >> logs/dev_struct2.log 2>&1
done
echo "dev_queue_2 done $(date -u +%H:%M:%SZ)" >> logs/dev_struct2.log
