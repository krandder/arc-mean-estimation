#!/bin/bash
# Amendment 4 queue: scratch/run_closure.py on the larger configurations, 2 concurrent processes (nice 19, idle IO,
# 1 BLAS thread).
cd /home/agent/workspaces/mats/work/bits-bounds
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
run_one() {
  set -- $1
  n=$1; L=$2; s=$3
  if [ -f runs/closure_n${n}_L${L}_s${s}.json ]; then return; fi
  echo "start closure4 n=$n L=$L s=$s $(date -u +%H:%M:%SZ)" >> logs/queue_closure4.log
  nice -n 19 ionice -c3 timeout 7200 $PY scratch/run_closure.py $n $L $s > logs/closure_n${n}_L${L}_s${s}.log 2>&1
  echo "end closure4 n=$n L=$L s=$s exit=$? $(date -u +%H:%M:%SZ)" >> logs/queue_closure4.log
}
export -f run_one
export PY
cat scratch/jobs_closure4.txt | xargs -P 2 -I{} bash -c 'run_one "{}"'
echo "closure4 queue done $(date -u +%H:%M:%SZ)" >> logs/queue_closure4.log
