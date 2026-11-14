#!/bin/bash
# Amendment A18 (convergence subset), VM B part: ARC net 4000 layers 16 and 31, round 1. Also the two kept jobs of the
# cut chain d of 57_B.sh (layer 31 unrestricted 2x depth; its fixed-lambda check). Up to 6 processes.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_67B.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 31 --cls unres --steps 48000 --variant steps4
  run $C --layer 31 --cls unres --steps 48000 --depth 6 --variant cap2steps4
  run $C --layer 31 --cls unres --steps 12000 --depth 6 --variant cap2 ) &
( sleep 20
  run $C --layer 16 --cls unres --steps 48000 --variant steps4
  run $C --layer 16 --cls unres --steps 48000 --depth 6 --variant cap2steps4 ) &
( sleep 40
  run $C --layer 16 --cls local --init h1 --steps 24000 --variant h1s2
  run $C --layer 16 --cls local --init h1 --steps 48000 --variant h1s4 ) &
( sleep 60
  run $C --layer 16 --cls local --init random --lr_enc 1e-3 --steps 12000 --variant rndhi
  run $C --layer 16 --cls local --init random --lr_enc 3e-4 --steps 12000 --variant rndmid
  run $C --layer 16 --cls local --init h1 --steps 12000 --depth 6 --variant h1c2
  run --family arc --seeds 4000 --steps 12000 --batch 1024 --layer 31 --cls unres --variant fixlam --fixlam=-2,-3.5,-5 ) &
wait
touch $O/DONE_67B
