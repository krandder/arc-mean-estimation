#!/bin/bash
# Amendment 2: stop net 201 after PI_as_w 2^6 is written; then net 201's PI_rand_w (2^1..2^5) and MLMC_16; then net 204.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
until grep -q "s=201 PI_as_w    p= 6" logs/queue_B.log; do sleep 20; done
kill 3219652
echo "killed net-201 process 3219652 at $(date -u +%H:%M:%SZ) after PI_as_w 2^6"
nice -n 19 ionice -c3 $PY frozen/curves.py arc 256 32 201 runs/s3_arc_n256_L32_s201_b.json --methods PI_rand_w,MLMC_16 --reps 8 --pmin 6 --pmax 14 --pimin 1 --pimax 5
nice -n 19 ionice -c3 $PY frozen/curves.py arc 256 32 204 runs/s3_arc_n256_L32_s204.json --methods RQMC,RQMCRB,PI_as_w,PI_rand_w,MLMC_16 --reps 8 --pmin 6 --pmax 14 --pimin 1 --pimax 5
echo "queue F done $(date -u +%H:%M:%SZ)"
