#!/bin/bash
# Amendment A14 on the running VM A (bitarc-5), where a slot is free: 4x steps for the output cell and layer 24 local
# (net 4000). 61_A.sh repeats them on bitarc-7 and skips them if they finished here.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 5 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_63A.log 2>&1; }
C4000="--family arc --seeds 4000 --steps 12000 --batch 1024"
run $C4000 --layer 32 --cls out --restarts 1 --variant steps4 --steps 48000 --save_pt
run $C4000 --layer 24 --cls local --restarts 1 --variant steps4 --steps 48000 --save_pt
