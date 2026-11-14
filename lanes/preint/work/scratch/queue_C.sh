#!/bin/bash
# Post-hoc descriptive: angular degree energies on scored nets (F7 calibration). Starts after queue A ends.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
while pgrep -f "scratch/queue_A.sh" > /dev/null; do sleep 30; done
for cfg in "32 4 302" "64 8 302" "128 16 302" "256 32 201" "256 32 202" "32 4 303" "64 8 303" "128 16 303"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/degrees.py $1 $2 $3 14 runs/deg_n$1_L$2_s$3.json
done
echo "queue C done $(date -u +%H:%M:%SZ)"
# F9 non-Gaussianity (main's request 14:3xZ), after the degree runs
for cfg in "64 8 256" "128 16 256" "256 32 96" "32 4 512"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/nongauss.py $1 $2 $3 runs/nongauss_n$1_L$2.json
done
echo "queue C (F9) done $(date -u +%H:%M:%SZ)"
# post hoc (not in PREREG): u = top right singular vector of the cloud-averaged Jacobian, dev nets only
nice -n 19 ionice -c3 $PY scratch/curves.py small 6 3 1 runs/posthoc_jac_small_n6_L3_s1.json --methods PI_jac,PI_as --reps 16 --pimin 2 --pimax 13
nice -n 19 ionice -c3 $PY scratch/curves.py arc 32 4 9500 runs/posthoc_jac_arc_n32_L4_s9500.json --methods PI_jac_w,PI_as_w --reps 8 --pimin 2 --pimax 10
nice -n 19 ionice -c3 $PY scratch/curves.py nd 8 256 103 runs/posthoc_jac_nd_s103.json --methods PIJ_jac,PIJ_as --reps 8 --pimin 2 --pimax 10
echo "queue C (posthoc jac) done $(date -u +%H:%M:%SZ)"
