#!/bin/bash
# pieces along lines, ladder and ARC (one process; nice 19, ionice idle)
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/preint
PY=/home/agent/.venvs/arc-noisy/bin/python
for cfg in "arc 64 8 300 32" "arc 128 16 300 32" "arc 64 64 301 16" "arc 32 32 301 32" "nd 8 256 216 32" "nd 8 256 221 32" "arc 256 32 200 6"; do
  set -- $cfg
  nice -n 19 ionice -c3 $PY scratch/pieces.py $1 $2 $3 $4 $5 runs/pieces_$1_n$2_L$3_s$4.json
done
