#!/bin/bash
# Dev run (restart 11, float32 clustering) (seed 9100, not scored): full-size chains for the four configs (sigma from the CPU calibration), truth passes,
# estimator convergence on 16x16 and 8x8. One process per net, in parallel.
cd /root/soup
export PATH=/root/venv/bin:$PATH
OUT=/root/runs/dev
mkdir -p $OUT /root/runs/logs
run_net() {  # n L sigma
  n=$1; L=$2; s=$3; tag=dev_${n}x${L}
  for CH in K PR; do python scripts/run_chain.py --n $n --L $L --seed 9100 --sigma $s --KL 64 --chain $CH --cert 1 --device cuda --out $OUT > /root/runs/logs/${tag}_$CH.log 2>&1; done
  for CH in R P; do python scripts/run_chain.py --n $n --L $L --seed 9100 --sigma $s --KL 64 --chain $CH --device cuda --out $OUT > /root/runs/logs/${tag}_$CH.log 2>&1; done
  python scripts/run_truth.py --n $n --L $L --seed 9100 --sigma $s --KL 64 --chains K,R,P,PR --device cuda --out $OUT > /root/runs/logs/${tag}_truth.log 2>&1
  python scripts/conv_check.py --n $n --L $L --seed 9100 --sigma $s --KL 64 --chain K --layers $((L-2)),$((L/2)),0 --device cuda --out $OUT > /root/runs/logs/${tag}_conv.log 2>&1
}
run_net 16 16 0.1 &
run_net 8 8 0.01 &
run_net 16 8 0.2 &
run_net 8 16 0.0003 &
wait
echo "dev done $(date -u +%FT%TZ)" > /root/runs/logs/dev_DONE
