#!/bin/bash
# Amendment A18 round 2 (registered rule: double again along the axis that moved the count most): layer 31
# unrestricted 8x steps (4x steps lowered it 5% at nMSE 0.01 against 2x). VM A (bitarc-7). 75_A_round2b.sh: more.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 7 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_74A.log 2>&1; }
run --family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt --layer 31 --cls unres --steps 96000 --variant steps8
