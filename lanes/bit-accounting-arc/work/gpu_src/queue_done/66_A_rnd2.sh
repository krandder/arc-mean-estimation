#!/bin/bash
# Amendment A17: the random start with a high encoder learning rate (A15) finds much cheaper codes at >= 20% error
# (narrow-deep layer 0: 2-3x fewer bits at 30% error; ARC layer 8: 6 / 22 bits against 9 / 30 at 30% / 20%) but does
# not reach 10% error. Here the random start with a moderate rate (3e-4, variant rndmid) at ARC net 4000 layers 0 and
# 8 and narrow-deep layer 0 (six nets, restarts 0-2), and the high rate (1e-3, rndhi) at ARC layer 0, to see whether
# the search limit reaches 10% error and the input layer. VM A.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_66A.log 2>&1; }
C="--family arc --seeds 4000 --steps 12000 --batch 1024 --cls local --restarts 1 --init random"
( run $C --layer 8 --lr_enc 3e-4 --variant rndmid ) &
( sleep 15; run $C --layer 0 --lr_enc 3e-4 --variant rndmid ) &
( sleep 30; run $C --layer 0 --lr_enc 1e-3 --variant rndhi ) &
( sleep 45; run --family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --layer 0 --cls local --init random --lr_enc 3e-4 --variant rndmid ) &
wait
