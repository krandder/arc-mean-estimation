#!/bin/bash
# Amendment A7: the 'h1' local start on the other ARC nets (4001-4003) at the early layers, where on net 4000 it beat
# the reference start (l = 0: 575 against 642 bits at nMSE 0.1). VM A.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_h1more.log 2>&1; }
for l in 0 4 8 2; do run --family arc --seeds 4001,4002,4003 --steps 12000 --batch 1024 --layer $l --cls local --init h1 --variant h1 --restarts 1 --save_pt; done
