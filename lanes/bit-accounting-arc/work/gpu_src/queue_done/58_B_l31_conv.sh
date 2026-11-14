#!/bin/bash
# Amendment A11: convergence corner at ARC net 4000 layer 31 local, where both C3 variants beat the base at nMSE <= 0.03
# (2x steps: 84 / 161 / 265 bits, 2x depth: 85 / 167 / 281, base 90 / 181 / 299 at 0.01 / 0.003 / 0.001). Depth 6 and
# 48000 steps together (variant cap2steps4), one restart. VM B, its own slot (up to 6 processes).
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_58B.log 2>&1; }
sleep 200
run --family arc --seeds 4000 --steps 48000 --batch 1024 --layer 31 --cls local --restarts 1 --depth 6 --variant cap2steps4 --save_pt
