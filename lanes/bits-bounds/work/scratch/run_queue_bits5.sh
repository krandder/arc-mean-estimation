#!/bin/bash
# Amendment 5 queue: scratch/run_bits5.py, 2 concurrent processes (nice 19, idle IO, 1 BLAS thread).
cd /home/agent/workspaces/mats/work/bits-bounds
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
PY=/home/agent/.venvs/arc-noisy/bin/python
run_one() {
  set -- $1
  n=$1; L=$2; s=$3
  if [ -f runs5/bits5_n${n}_L${L}_s${s}.json ]; then return; fi
  echo "start bits5 n=$n L=$L s=$s $(date -u +%H:%M:%SZ)" >> logs/queue_bits5.log
  nice -n 19 ionice -c3 timeout 7200 $PY scratch/run_bits5.py $n $L $s > logs/bits5_n${n}_L${L}_s${s}.log 2>&1
  echo "end bits5 n=$n L=$L s=$s exit=$? $(date -u +%H:%M:%SZ)" >> logs/queue_bits5.log
}
export -f run_one
export PY
cat scratch/jobs_bits5.txt | xargs -P 2 -I{} bash -c 'run_one "{}"'
echo "bits5 queue done $(date -u +%H:%M:%SZ)" >> logs/queue_bits5.log
