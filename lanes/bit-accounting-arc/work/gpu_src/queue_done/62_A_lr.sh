#!/bin/bash
# Amendment A13: does the local count depend on the optimiser's reach? The local encoder's weights train at lr 3e-5
# (set for precision); from a random start this does not find the planted toy's directions. Here the look-ahead start
# with a 10x encoder learning rate (3e-4; the linear paths stay at 3e-5), ARC net 4000, layers 0, 8, 16 (variant h1lr),
# and the reference start with it at layer 8 (variant reflr). VM A (bitarc-7 on).
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 5 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_62A.log 2>&1; }
C="--family arc --seeds 4000 --steps 12000 --batch 1024 --cls local --restarts 1 --lr_enc 3e-4"
sleep 45
for l in 8 0 16; do run $C --layer $l --init h1 --variant h1lr; done
run $C --layer 8 --variant reflr
