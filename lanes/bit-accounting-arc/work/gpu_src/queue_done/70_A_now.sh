#!/bin/bash
# Amendment A18 round 1, the two short layer-0 local runs of 68_A_conv.sh, started on bitarc-5 before it ends at 12:16Z
# (bitarc-7 skips them if they finished). VM A.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_70A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 0 --cls local --init h1 --steps 12000 --depth 6 --variant h1c2 ) &
( sleep 15; run $C --layer 0 --cls local --init h1 --steps 24000 --variant h1s2 ) &
wait
