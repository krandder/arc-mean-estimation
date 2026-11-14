#!/bin/bash
# PREREG Part P1 evaluation runs (amendments A1, A2: restarted with AMAX 256 and fp32 linear paths; same commands as 10_eval.sh). Every VM runs this file; the chains a VM takes depend on its name (VMA = bitarc-1 or
# bitarc-3, VMB = bitarc-2 or bitarc-4). Finished results restored from prior/ (every script skips cells whose JSON
# exists). Jobs start only with >= 4 GB GPU memory free and at most 3 training processes on the GPU.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*) VM=A ;; *bitarc-2-*|*bitarc-4-*|*bitarc-6-*) VM=B ;; *) exit 0 ;; esac
O=/root/runs/P1; mkdir -p $O $O/REF $O/pt
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 3 ]; do sleep 15; done; sleep 10; }
ARC="--family arc --seeds 4000,4001,4002,4003 --restarts 2 --steps 12000 --batch 1024 --save_pt"
ND="--family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --save_pt"
run() { gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_$VM.log 2>&1; }
chainA_arc() { for l in 31 0 16 8 24 4 28 12 20 2; do run $ARC --layer $l --cls local; done; run $ARC --layer 32 --cls out; }
chainB_arc() { for l in 31 0 16 8 24 4 28 12 20 2; do run $ARC --layer $l --cls unres; done; }
chainA_nd() { for l in 255 0 64 16 128 32 192 8; do run $ND --layer $l --cls local; done; run $ND --layer 256 --cls out; }
chainB_nd() { for l in 255 0 64 16 128 32 192 8; do run $ND --layer $l --cls unres; done; }
chainB_x() {
  gate; python scripts/ref_curve.py --family arc --seeds 4000,4001,4002,4003 --layers 31,0,16,8,24,4,28,12,20,2,32 --out $O/REF >> $O/ref.log 2>&1
  gate; python scripts/ref_curve.py --family nd --seeds 203,216,217,220,221,223 --layers 255,0,64,16,128,32,192,8,256 --out $O/REF >> $O/ref.log 2>&1
  for k in 4 16 64; do for c in local unres; do run --family toy --toy_k $k --seeds 1 --layer 0 --cls $c --restarts 3 --steps 12000 --batch 1024; done; done
}
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
chainA_cert() {
  for l in 31 0 16 8 24 4 28 12 20 2; do run $C4000 --layer $l --cls local --restarts 1 --restart0 2; done
  run $C4000 --layer 32 --cls out --restarts 1 --restart0 2
  for l in 0 16 31 8 24; do run $C4000 --layer $l --cls local --restarts 1 --variant steps2 --steps 24000; run $C4000 --layer $l --cls local --restarts 1 --variant cap2 --depth 6; done
  run $C4000 --layer 32 --cls out --restarts 1 --variant steps2 --steps 24000; run $C4000 --layer 32 --cls out --restarts 1 --variant cap2 --depth 6
  for l in 0 16 31; do run $C4000 --layer $l --cls local --variant fixlam --fixlam -2,-3.5,-5; done
}
chainB_cert() {
  for l in 31 0 16 8 24 4 28 12 20 2; do run $C4000 --layer $l --cls unres --restarts 1 --restart0 2; done
  for l in 0 16 31 8 24; do run $C4000 --layer $l --cls unres --restarts 1 --variant steps2 --steps 24000; run $C4000 --layer $l --cls unres --restarts 1 --variant cap2 --depth 6; done
  for l in 0 16 31 8 24 4 28 12 20 2; do run $C4000 --layer $l --cls unres --restarts 1 --variant refu --init refu; done
  for l in 0 16 31; do run $C4000 --layer $l --cls unres --variant fixlam --fixlam -2,-3.5,-5; done
}
N6="--family nd --seeds 203,216,217,220,221,223 --batch 2048 --graphs --restarts 1"
chainA_ndcert() {
  for l in 0 64 255; do run $N6 --layer $l --cls local --variant cap2 --depth 6 --steps 12000; run $N6 --layer $l --cls local --variant steps2 --steps 24000; done
  run $N6 --layer 256 --cls out --variant cap2 --depth 6 --steps 12000; run $N6 --layer 256 --cls out --variant steps2 --steps 24000
  for l in 0 64; do run --family nd --seeds 203 --batch 2048 --graphs --steps 12000 --layer $l --cls local --variant fixlam --fixlam -1,-2.5,-4; done
}
chainB_ndcert() {
  for l in 0 64 255; do run $N6 --layer $l --cls unres --variant cap2 --depth 6 --steps 12000; run $N6 --layer $l --cls unres --variant steps2 --steps 24000; done
  for l in 0 64; do run --family nd --seeds 203 --batch 2048 --graphs --steps 12000 --layer $l --cls unres --variant fixlam --fixlam -1,-2.5,-4; done
}
if [ $VM = A ]; then
  ( chainA_arc; chainA_cert; touch $O/A_arc_done ) &
  ( chainA_nd; chainA_ndcert; touch $O/A_nd_done ) &
else
  ( chainB_x; touch $O/B_x_done ) &
  ( chainB_arc; chainB_cert; touch $O/B_arc_done ) &
  ( chainB_nd; chainB_ndcert; touch $O/B_nd_done ) &
fi
wait
mv /root/runs/P1/*.pt /root/runs/P1/pt/ 2>/dev/null
touch $O/DONE_$VM
