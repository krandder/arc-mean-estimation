#!/bin/bash
# POST HOC: D1 half-width runs with the rank guard (lib/fa_kprop_guard.py). First reruns of registered SUCCESSES
# (must reproduce them), then the registered NaN runs (n = 128 seeds 304, 306; n = 256 seeds 200-203).
export OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 OMP_NUM_THREADS=2 FA_THREADS=2
cd /home/agent/workspaces/mats/work/future-aware
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
echo "queue G start $(date -u +%H:%M:%SZ)" >> logs/queue.log
$PY scratch/run_k3p_guard.py 64 8 300 --variants futv32,futmf2_32 >> logs/eval_guard.log 2>&1
$PY scratch/run_k3p_guard.py 128 16 300 --variants futv64,futmf2_64 >> logs/eval_guard.log 2>&1
$PY scratch/run_k3p_guard.py 256 32 204 --variants futv128,futmf2_128 >> logs/eval_guard.log 2>&1
for s in 304 306; do
  $PY scratch/run_k3p_guard.py 128 16 $s --variants futv64,futmf2_64 >> logs/eval_guard.log 2>&1
done
for s in 200 201 202 203; do
  $PY scratch/run_k3p_guard.py 256 32 $s --variants futv128,futmf2_128 >> logs/eval_guard.log 2>&1
done
echo "queue G done $(date -u +%H:%M:%SZ)" >> logs/queue.log
