#!/bin/bash
# Re-run the first four degree measurements with degrees.py v2 (centred moments) after queue C2 (pid 3085107) ends.
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
while kill -0 3085107 2>/dev/null; do sleep 30; done
for cfg in "32 4 302" "64 8 302" "128 16 302" "256 32 201" "256 32 202"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/degrees.py $1 $2 $3 14 runs/deg_n$1_L$2_s$3.json
done
echo "queue D done $(date -u +%H:%M:%SZ)"
