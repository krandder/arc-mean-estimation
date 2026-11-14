#!/bin/bash
# Amendment A8 (reduced plan), VM A. Three chains, at most 4 training processes on the GPU.
# A1: ARC local base, restart 0 only (4 nets per process); A2: the narrow-deep output cell and local base (6 nets x 3
# restarts), then the
# narrow-deep local certificates; A3: ARC net-4000 local certificates. The 'h1' chains (34_h1.sh, 38_h1_more.sh) keep
# running beside them. Finished cells are skipped (their JSON exists); a job waits while the same command still runs.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_51A.log 2>&1; }
ARC1="--family arc --seeds 4000,4001,4002,4003 --restarts 1 --steps 12000 --batch 1024 --save_pt"
ND="--family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --save_pt"
N6="--family nd --seeds 203,216,217,220,221,223 --batch 2048 --graphs --restarts 1"
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
( for l in 0 16 8 24 4 28 12 20 2; do run $ARC1 --layer $l --cls local; done; touch $O/A1_done ) &
( run $ND --layer 256 --cls out
  for l in 0 64 16 128 32 192 8; do run $ND --layer $l --cls local; done
  for l in 0 255; do run $N6 --layer $l --cls local --variant cap2 --depth 6 --steps 12000; run $N6 --layer $l --cls local --variant steps2 --steps 24000; done
  run --family nd --seeds 203 --batch 2048 --graphs --steps 12000 --layer 0 --cls local --variant fixlam --fixlam=-1,-2.5,-4
  touch $O/A2_done ) &
( sleep 120
  run $C4000 --layer 31 --cls local --restarts 1 --variant steps2 --steps 24000
  run $C4000 --layer 31 --cls local --restarts 1 --variant cap2 --depth 6
  for l in 0 31; do run $C4000 --layer $l --cls local --variant fixlam --fixlam=-2,-3.5,-5; done
  touch $O/A3_done ) &
wait
touch $O/DONE_51A
