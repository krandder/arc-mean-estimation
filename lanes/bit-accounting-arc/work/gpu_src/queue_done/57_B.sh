#!/bin/bash
# Amendment A10, VM B from bitarc-6 on (replaces 51_B.sh and 52_B, which ran on bitarc-4). The remaining A8 jobs of VM B
# plus the layers of A8 chains A1 (ARC local base) and A2 (narrow-deep local base) that VM A reaches last, in six
# parallel chains with at most 5 processes on the GPU; then A10's 'h1' start on ARC nets 4001-4003 at layers 12-28.
# Finished cells are skipped (their JSON exists, copied from every VM at launch); a job waits while the same command
# still runs.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF $O/REFINE
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 5 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_57B.log 2>&1; }
ARC1="--family arc --seeds 4000,4001,4002,4003 --restarts 1 --steps 12000 --batch 1024 --save_pt"
ND="--family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --save_pt"
N6="--family nd --seeds 203,216,217,220,221,223 --batch 2048 --graphs --restarts 1"
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
H1="--family arc --seeds 4001,4002,4003 --steps 12000 --batch 1024 --cls local --init h1 --variant h1 --restarts 1 --save_pt"
# a: ARC local base (A8 chain A1) at the layers VM A reaches last, in reverse order
( for l in 2 20 12 28; do run $ARC1 --layer $l --cls local; done; touch $O/B57a_done ) &
# b: narrow-deep local base (A8 chain A2) at the layers VM A reaches last, in reverse order
( sleep 30; for l in 8 192 32; do run $ND --layer $l --cls local; done; touch $O/B57b_done ) &
# c: ARC net-4000 unrestricted (B1), then narrow-deep unrestricted (B2)
( sleep 60
  for l in 16 8 24; do run $C4000 --layer $l --cls unres --restarts 1 --save_pt; done
  for l in 16 8; do run $ND --layer $l --cls unres; done
  touch $O/B57c_done ) &
# d: ARC certificates (B3, ARC part)
( sleep 90
  run $C4000 --layer 16 --cls unres --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 16 --cls unres --restarts 1 --variant cap2 --depth 6
  run $C4000 --layer 31 --cls unres --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 31 --cls unres --restarts 1 --variant cap2 --depth 6
  run $C4000 --layer 32 --cls out --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 32 --cls out --restarts 1 --variant cap2 --depth 6
  run $C4000 --layer 31 --cls unres --variant fixlam --fixlam=-2,-3.5,-5
  touch $O/B57d_done ) &
# e: narrow-deep certificates (B3, narrow-deep part)
( sleep 120
  for l in 0 255; do
    run $N6 --layer $l --cls unres --variant cap2 --depth 6 --steps 12000
    run $N6 --layer $l --cls unres --variant steps2 --steps 24000
  done
  run $N6 --layer 256 --cls out --variant cap2 --depth 6 --steps 12000
  run $N6 --layer 256 --cls out --variant steps2 --steps 24000
  touch $O/B57e_done ) &
# f: the registered random-start toy (B4), the post-hoc decoder diagnostic (not registered), then A10
( sleep 150
  for k in 16 64; do for c in local unres; do run --family toy --toy_k $k --seeds 1 --layer 0 --cls $c --restarts 3 --steps 12000 --batch 1024; done; done
  for l in 16 8 24; do
    f=$O/VR_arc_l${l}_unres_base_r0_s4000.pt
    if [ -e $f ]; then gate; python scripts/refine_posthoc.py --family arc --seeds 4000 --restarts 1 --layer $l --pt $f --out $O/REFINE >> $O/REFINE/refine.log 2>&1; fi
  done
  for l in 16 24 12 20 28; do run $H1 --layer $l; done
  touch $O/B57f_done ) &
wait
touch $O/DONE_57B
