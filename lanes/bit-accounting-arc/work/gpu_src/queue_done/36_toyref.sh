#!/bin/bash
# Amendment A6: the planted toy with the nets' local start ('ref': the analytic reference code), beside the registered
# random start; restarts 0-2, k = 4, 16, 64. VM B only.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_toyref.log 2>&1; }
for k in 16 4 64; do run --family toy --toy_k $k --seeds 1 --layer 0 --cls local --init ref --variant toyref --restarts 3 --steps 12000 --batch 1024; done
