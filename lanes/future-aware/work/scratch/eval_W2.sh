#!/bin/bash
# Queue W2 (Amendment 1, net 502 in parallel with net 501; same command as eval_W.sh). Then, post hoc, the rank-guarded
# futmf2_128 (k = n/4) on nets 500-502 if their registered runs returned NaN (lib/fa_kprop_guard.py).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
echo "queue W2 start $(date -u +%H:%M:%SZ)" >> logs/queue.log
$PY scratch/run_w512.py 512 64 502 --log2T 22 --rqmc 8,10,12,14 --variants none,futmf2_128,futmf2_64,futmf2_16,pca128,pca64,pca16 >> logs/eval_w512_502.log 2>&1
echo "queue W2 net 502 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
$PY scratch/run_k3p_guard.py 512 64 500 --variants futmf2_128 >> logs/eval_guard512.log 2>&1
echo "queue W2 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
