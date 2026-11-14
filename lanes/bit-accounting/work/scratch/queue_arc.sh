#!/bin/bash
# ARC Part A1 M2 learned local codes for one seed (CPU, nice 19, 2 threads), cells in priority order.
# usage: queue_arc.sh <seed>
cd /home/agent/workspaces/mats/work/bit-accounting
S=$1
PY=/home/agent/.venvs/arc-noisy/bin/python
for cell in "32 gauss" "31 gauss" "16 gauss" "0 gauss" "32 fsq" "31 fsq" "16 fsq" "4 gauss" "0 fsq" "4 fsq"; do
  set -- $cell
  L=$1; K=$2
  OUT=runs/A1_arc${S}_l${L}_${K}.json
  [ -e "$OUT" ] && continue
  B=$($PY scratch/pick_basis.py arc $S $L)
  nice -n 19 ionice -c3 $PY scratch/train_bn2.py --net arc --seed $S --layer $L --kind $K --basis $B --out $OUT > logs/A1_arc${S}_l${L}_${K}.log 2>&1
done
