#!/bin/bash
# Amendment 1 (F1) queue: waits for the main evaluation queue to finish, then runs scratch/run_ml.py jobs with at most
# 2 concurrent processes (nice 19, idle IO, 1 BLAS thread).
cd /home/agent/workspaces/mats/work/bits-bounds
true
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
run_one() {
  set -- $1
  n=$1; L=$2; s=$3
  if [ -f runs/ml_n${n}_L${L}_s${s}.json ]; then return; fi
  echo "start ml n=$n L=$L s=$s $(date -u +%H:%M:%SZ)" >> logs/queue_ml.log
  nice -n 19 ionice -c3 timeout 7200 $PY scratch/run_ml.py $n $L $s > logs/ml_n${n}_L${L}_s${s}.log 2>&1
  echo "end ml n=$n L=$L s=$s exit=$? $(date -u +%H:%M:%SZ)" >> logs/queue_ml.log
}
export -f run_one
export PY
cat scratch/jobs_ml.txt | xargs -P 1 -I{} bash -c 'run_one "{}"'
echo "ml queue done $(date -u +%H:%M:%SZ)" >> logs/queue_ml.log
