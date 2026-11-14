#!/bin/bash
# VM A from bitarc-7 on (replaces 51_A.sh, 53_A_steps4.sh, 38_h1_more.sh, 34_h1.sh): what VM A had not finished when
# bitarc-5 ended, plus A10's look-ahead runs from the other end of their list and A14. Finished cells are skipped (their
# JSON exists, copied from every VM at launch); a job waits while the same command still runs. At most 5 processes.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 5 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_61A.log 2>&1; }
ARC1="--family arc --seeds 4000,4001,4002,4003 --restarts 1 --steps 12000 --batch 1024 --save_pt"
ND="--family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --save_pt"
N6="--family nd --seeds 203,216,217,220,221,223 --batch 2048 --graphs --restarts 1"
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
H1="--family arc --seeds 4001,4002,4003 --steps 12000 --batch 1024 --cls local --init h1 --variant h1 --restarts 1 --save_pt"
# A8 chain A1 (ARC local base) leftovers
( for l in 24 4 8; do run $ARC1 --layer $l --cls local; done; touch $O/A61a_done ) &
# A8 chain A2 (narrow-deep local base) leftovers
( sleep 30; for l in 64 16 128; do run $ND --layer $l --cls local; done; touch $O/A61b_done ) &
# A8 chain A2 certificates (narrow-deep local) and its fixed-lambda check
( sleep 60
  for l in 0 255; do
    run $N6 --layer $l --cls local --variant cap2 --depth 6 --steps 12000
    run $N6 --layer $l --cls local --variant steps2 --steps 24000
  done
  run --family nd --seeds 203 --batch 2048 --graphs --steps 12000 --layer 0 --cls local --variant fixlam --fixlam=-1,-2.5,-4
  touch $O/A61c_done ) &
# A10 look-ahead start on nets 4001-4003, from the other end of VM B's list (16 24 12 20 28)
( sleep 90; for l in 28 20 12; do run $H1 --layer $l; done; touch $O/A61d_done ) &
# A14 convergence of the output cell and layer 24 (4x steps, net 4000)
( sleep 120
  run $C4000 --layer 32 --cls out --restarts 1 --variant steps4 --steps 48000 --save_pt
  run $C4000 --layer 24 --cls local --restarts 1 --variant steps4 --steps 48000 --save_pt
  touch $O/A61e_done ) &
wait
touch $O/DONE_61A
