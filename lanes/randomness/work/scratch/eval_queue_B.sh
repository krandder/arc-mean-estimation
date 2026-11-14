#!/bin/bash
# Eval (registered, PREREG part 1): noise runs (E3), deterministic designs (E4), ladder structure runs (E1).
cd /home/agent/workspaces/mats/work/randomness
PY=/home/agent/.venvs/arc-noisy/bin/python
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 RND_THREADS=1
echo "queue B start $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do nice -n 19 ionice -c3 $PY scratch/noise.py $s 256 32 >> logs/eval_noise.log 2>&1; done
for nl in "32 4" "64 8" "128 16"; do set -- $nl
  for s in 300 301 302 303 304 305 306 307; do nice -n 19 ionice -c3 $PY scratch/noise.py $s $1 $2 >> logs/eval_noise.log 2>&1; done
done
echo "queue B E3 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for nl in "32 4 4" "64 8 4" "128 16 3"; do set -- $nl
  for s in 300 301 302 303 304 305 306 307; do nice -n 19 ionice -c3 $PY scratch/structure.py $s $1 $2 >> logs/eval_struct_lad.log 2>&1; done
done
echo "queue B E1-ladder done $(date -u +%H:%M:%SZ)" >> logs/queue.log
for s in 200 201 202 203 204; do nice -n 19 ionice -c3 $PY scratch/detqmc.py $s 256 32 --mmax 16 --kmax 2 >> logs/eval_det.log 2>&1; done
for nl in "32 4 4" "64 8 4" "128 16 3"; do set -- $nl
  for s in 300 301 302 303 304 305 306 307; do nice -n 19 ionice -c3 $PY scratch/detqmc.py $s $1 $2 --mmax 16 --kmax $3 --kpoints_max 3e7 >> logs/eval_det.log 2>&1; done
done
echo "queue B E4 done $(date -u +%H:%M:%SZ)" >> logs/queue.log
nice -n 19 ionice -c3 $PY scratch/detqmc.py 200 256 32 --mmax 6 --kmax 3 --kpoints_max 2e7 --out runs/det_k3_n256_L32_s200.json >> logs/eval_det_k3.log 2>&1
echo "queue B done $(date -u +%H:%M:%SZ)" >> logs/queue.log
