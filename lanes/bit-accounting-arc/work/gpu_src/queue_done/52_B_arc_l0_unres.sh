#!/bin/bash
# A8: the ARC layer-0 unrestricted base cell (all four nets, restarts 0-1) running on bitarc-4 when A8 was written;
# on a replacement VM B this reruns it if it did not finish (its JSON is then missing).
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_52B.log 2>&1; }
sleep 90
run --family arc --seeds 4000,4001,4002,4003 --restarts 2 --steps 12000 --batch 1024 --save_pt --layer 0 --cls unres
