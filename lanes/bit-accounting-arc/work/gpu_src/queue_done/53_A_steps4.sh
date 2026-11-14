#!/bin/bash
# Amendment A9: convergence check after C3 (2x steps) failed at ARC net 4000 layer 31 local (24k steps: 84 / 161 / 265
# bits against 90 / 181 / 299 at nMSE 0.01 / 0.003 / 0.001). 4x steps (48k) at layer 31 local. VM A.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_53A.log 2>&1; }
run --family arc --seeds 4000 --steps 48000 --batch 1024 --layer 31 --cls local --restarts 1 --variant steps4
