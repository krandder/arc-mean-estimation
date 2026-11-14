#!/bin/bash
# Amendment A18 (convergence subset), VM A part (bitarc-7): ARC net 4000 layers 0 and 31, round 1. Up to 6 processes.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_68A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 0 --cls unres --steps 48000 --variant steps4
  run $C --layer 0 --cls unres --steps 24000 --width 2048 --variant wide2steps2 ) &
( sleep 20
  run $C --layer 0 --cls unres --steps 48000 --depth 6 --variant cap2steps4 ) &
( sleep 40
  run $C --layer 0 --cls local --init h1 --steps 24000 --variant h1s2
  run $C --layer 0 --cls local --init h1 --steps 48000 --variant h1s4 ) &
( sleep 60
  run $C --layer 0 --cls local --init h1 --steps 12000 --depth 6 --variant h1c2
  run $C --layer 31 --cls local --steps 48000 --depth 12 --variant cap4steps4 ) &
wait
touch $O/DONE_68A
