#!/bin/bash
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd /home/agent/workspaces/mats/work/nd-exact
PY="nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python"
while pgrep -f queue_dev3.sh >/dev/null; do sleep 5; done
$PY tests/test_cubesphere.py > logs/test_cubesphere_frozen.log 2>&1
$PY frozen/depth1_rate2.py runs/depth1_rate2.json > logs/depth1_rate2.log 2>&1
for s in 103 111; do
  for d in 18 20 22; do
    $PY scratch/run_unbiased.py $s $d 14 8 runs/dev_unbiased_s${s}_D${d}.json >> logs/dev_unbiased.log 2>&1
  done
done
for s in 203 216 217 220 221 223; do
  $PY scratch/preimage.py $s 20 runs/preimage_s${s}.json > logs/preimage_s${s}.log 2>&1
done
