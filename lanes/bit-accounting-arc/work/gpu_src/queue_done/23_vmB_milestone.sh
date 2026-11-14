#!/bin/bash
# VM B only: seed-4000 certificate runs of the registered queue for l = 31, 0, 16 run earlier (milestone 1); the
# certificate chains of 10_eval.sh skip them later. Same commands.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_milestone.log 2>&1; }
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
for l in 31 0 16; do
  for c in local unres; do run $C4000 --layer $l --cls $c --restarts 1 --restart0 2; done
done
run $C4000 --layer 32 --cls out --restarts 1 --restart0 2
for l in 0 16 31; do for c in local unres; do run $C4000 --layer $l --cls $c --restarts 1 --variant steps2 --steps 24000; run $C4000 --layer $l --cls $c --restarts 1 --variant cap2 --depth 6; done; done
run $C4000 --layer 32 --cls out --restarts 1 --variant steps2 --steps 24000; run $C4000 --layer 32 --cls out --restarts 1 --variant cap2 --depth 6
