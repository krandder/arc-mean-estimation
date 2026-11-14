#!/bin/bash
# Remaining ARC A1 M2 cells: seed 4000 (fsq at 32 and 0, both kinds at 4) and the registered sign-code runs ('bin',
# K = 256 nested bits) at l in {32, 31, 16} on seeds 4000 and 4001. Starts each run only while fewer than 3
# train_bn2 processes are running (the lane's CPU limit).
cd /home/agent/workspaces/mats/work/bit-accounting
PY=/home/agent/.venvs/arc-noisy/bin/python
for cell in "4000 32 fsq" "4000 4 gauss" "4000 0 fsq" "4000 4 fsq" "4000 32 bin" "4000 31 bin" "4000 16 bin" "4001 32 bin" "4001 31 bin" "4001 16 bin"; do
  set -- $cell
  S=$1; L=$2; K=$3
  OUT=runs/A1_arc${S}_l${L}_${K}.json
  [ -e "$OUT" ] && continue
  while kill -0 3612744 2>/dev/null; do sleep 30; done
  B=$($PY scratch/pick_basis.py arc $S $L)
  nice -n 19 ionice -c3 $PY scratch/train_bn2.py --net arc --seed $S --layer $L --kind $K --basis $B --out $OUT > logs/A1_arc${S}_l${L}_${K}.log 2>&1

done
wait
