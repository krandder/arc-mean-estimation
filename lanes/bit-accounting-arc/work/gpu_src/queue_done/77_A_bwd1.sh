#!/bin/bash
# Amendment A21: the backward start from the next measured layer's look-ahead code (one step, no chain): layer 16 from
# layer 20, layer 0 from layer 2 (variant bwd1), because the A19 chain loses precision as it compounds (layer 20: 42
# against 19.7 bits at 10% error, 1% not reached). VM A (bitarc-7); sources pushed to /root/runs/SRC.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 9 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_77A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt --cls local --init bwd --anneal 0 --steps 12000"
( run $C --layer 16 --bwd_pt /root/runs/SRC/VR_arc_l20_local_h1_r0_s4000.pt --variant bwd1 ) &
( sleep 20; run $C --layer 0 --bwd_pt /root/runs/SRC/VR_arc_l2_local_h1_r0_s4000.pt --variant bwd1 ) &
wait
