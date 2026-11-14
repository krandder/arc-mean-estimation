#!/bin/bash
# Queue W (Amendment 1): n = 512, L = 64, nets 500-502: truth, RQMC, ARC k2/k3f and D1 variants.
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
for s in 500 501 502; do
  $PY scratch/run_w512.py 512 64 $s --log2T 22 --rqmc 8,10,12,14 --variants none,futmf2_128,futmf2_64,futmf2_16,pca128,pca64,pca16 >> logs/eval_w512.log 2>&1
done
echo "queue W done $(date -u +%H:%M:%SZ)" >> logs/queue.log
