#!/bin/bash
# Run the registered evaluation configs with at most 2 concurrent processes (nice 19, idle IO, 1 BLAS thread).
cd /home/agent/workspaces/mats/work/bits-bounds
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
jobs_file=scratch/jobs_eval.txt
run_one() {
  set -- $1
  n=$1; L=$2; s=$3
  if [ -f runs/eval_n${n}_L${L}_s${s}.json ]; then return; fi
  echo "start n=$n L=$L s=$s $(date -u +%H:%M:%SZ)" >> logs/queue.log
  nice -n 19 ionice -c3 timeout 7200 $PY scratch/run_eval.py $n $L $s > logs/eval_n${n}_L${L}_s${s}.log 2>&1
  echo "end n=$n L=$L s=$s exit=$? $(date -u +%H:%M:%SZ)" >> logs/queue.log
}
export -f run_one
export PY
cat $jobs_file | xargs -P 2 -I{} bash -c 'run_one "{}"'
echo "queue done $(date -u +%H:%M:%SZ)" >> logs/queue.log
