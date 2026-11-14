#!/bin/bash
# Amendment A3: local encoders initialised at the exact one-layer look-ahead ('h1': hidden layer = h_{l+1}, code = the
# reference code of h_{l+1}), a nonlinear start for the local class (the 'ref' start stays affine in practice).
# VM A: ARC net 4000, every layer; VM B: narrow-deep, all six nets, every layer.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*) VM=A ;; *bitarc-2-*|*bitarc-4-*|*bitarc-6-*) VM=B ;; *) exit 0 ;; esac
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_h1_$VM.log 2>&1; }
if [ $VM = A ]; then
  for l in 31 0 16 8 24 4 28 12 20 2; do run --family arc --seeds 4000 --steps 12000 --batch 1024 --layer $l --cls local --init h1 --variant h1 --restarts 1 --save_pt; done
else
  for l in 255 0 64 16 128 32 192 8; do run --family nd --seeds 203,216,217,220,221,223 --steps 12000 --batch 2048 --graphs --layer $l --cls local --init h1 --variant h1 --restarts 1 --save_pt; done
fi
touch $O/h1_done_$VM
