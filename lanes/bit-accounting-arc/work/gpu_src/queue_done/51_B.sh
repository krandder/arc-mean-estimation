#!/bin/bash
# Amendment A8 (reduced plan), VM B. B1: ARC unrestricted, net 4000 restart 0 at layers 16, 8, 24 (layer 0 with all
# four nets and layer 31 with all four nets are run or running); B2: narrow-deep unrestricted at layers 16 and 8
# (0, 64, 255 run or running); B3: certificates (ARC net-4000 unrestricted and output, narrow-deep unrestricted and
# output, fixed-lambda); B4: the registered random-start toy. The post-hoc decoder diagnostic (37) keeps waiting.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_51B.log 2>&1; }
ND="--family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --save_pt"
N6="--family nd --seeds 203,216,217,220,221,223 --batch 2048 --graphs --restarts 1"
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
( for l in 16 8 24; do run $C4000 --layer $l --cls unres --restarts 1 --save_pt; done; touch $O/B1_done ) &
( for l in 16 8; do run $ND --layer $l --cls unres; done; touch $O/B2_done ) &
( sleep 120
  run $C4000 --layer 16 --cls unres --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 16 --cls unres --restarts 1 --variant cap2 --depth 6
  run $C4000 --layer 31 --cls unres --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 31 --cls unres --restarts 1 --variant cap2 --depth 6
  run $C4000 --layer 32 --cls out --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 32 --cls out --restarts 1 --variant cap2 --depth 6
  for l in 0 255; do run $N6 --layer $l --cls unres --variant cap2 --depth 6 --steps 12000; run $N6 --layer $l --cls unres --variant steps2 --steps 24000; done
  run $N6 --layer 256 --cls out --variant cap2 --depth 6 --steps 12000
  run $N6 --layer 256 --cls out --variant steps2 --steps 24000
  run $C4000 --layer 31 --cls unres --variant fixlam --fixlam=-2,-3.5,-5
  touch $O/B3_done ) &
( sleep 60
  for k in 4 16 64; do for c in local unres; do run --family toy --toy_k $k --seeds 1 --layer 0 --cls $c --restarts 3 --steps 12000 --batch 1024; done; done
  touch $O/B4_done ) &
wait
touch $O/DONE_51B
