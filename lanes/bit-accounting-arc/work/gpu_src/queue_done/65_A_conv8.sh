#!/bin/bash
# Amendment A16: is the late-layer high-precision count still falling? ARC net 4000 layer 31 local, depth 6 with 8x steps
# (96000; variant cap2steps8), after depth 6 + 4x steps lowered it by 14 / 22 / 24% at nMSE 0.01 / 0.003 / 0.001
# (4x steps alone: 10 / 17 / 18%; the output cell with 4x steps: 17 / 19 / 18%). VM A (bitarc-7).
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_65A.log 2>&1; }
sleep 30
run --family arc --seeds 4000 --steps 96000 --batch 1024 --layer 31 --cls local --restarts 1 --depth 6 --variant cap2steps8 --save_pt
