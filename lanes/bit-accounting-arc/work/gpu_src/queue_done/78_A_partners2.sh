#!/bin/bash
# Amendment A20 (A18 matched partners, second set, VM A): steps partners of the new best unrestricted runs (depth 6 with
# 4x steps) at layers 16 and 31: depth 6 with 2x steps.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 9 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_78A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 16 --cls unres --steps 24000 --depth 6 --variant cap2steps2 ) &
( sleep 20; run $C --layer 31 --cls unres --steps 24000 --depth 6 --variant cap2steps2 ) &
wait
