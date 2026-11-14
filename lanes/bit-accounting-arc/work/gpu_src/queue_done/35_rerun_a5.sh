#!/bin/bash
# A5: rerun the 8-model ARC processes that were stopped because their (pre-A5) evaluation would have taken ~2.7 h:
# VM A: l = 31 local and the output cell; VM B: l = 31 unrestricted (31_eval.sh's chain reruns it by itself).
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_a5.log 2>&1; }
ARC="--family arc --seeds 4000,4001,4002,4003 --restarts 2 --steps 12000 --batch 1024 --save_pt"
run $ARC --layer 31 --cls local &
run $ARC --layer 32 --cls out &
wait
