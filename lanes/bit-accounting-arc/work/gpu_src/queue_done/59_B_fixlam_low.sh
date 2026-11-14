#!/bin/bash
# Amendment A12: C7 at the low-rate end of ARC net 4000 layer 0 local, where the registered check failed at t = -2 (a
# dedicated model reaches nMSE 0.73 with 4.0 bits; the variable-rate curve has a gap there: 3.3 bits at 0.785, then
# 116 bits at 0.734). Dedicated models at t = -2.25, -2.5, -2.75 (the variable-rate curve's nMSE 0.3-0.7), from the
# reference start (as registered) and from the look-ahead start. VM B, its own slot (up to 6 processes).
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_59B.log 2>&1; }
sleep 30
run --family arc --seeds 4000 --steps 12000 --batch 1024 --layer 0 --cls local --variant fixlamlo --fixlam=-2.25,-2.5,-2.75
run --family arc --seeds 4000 --steps 12000 --batch 1024 --layer 0 --cls local --init h1 --variant fixlamh1 --fixlam=-2.25,-2.5,-2.75
