#!/bin/bash
# Amendment A20 (A18 matched partners, VM A): doubling partners of the convergence subset's best runs that match them
# in every other setting. Longer runs.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 8 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_76A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 16 --cls local --init h1 --steps 48000 --depth 6 --variant h1c2s4 ) &
( sleep 20; run $C --layer 31 --cls unres --steps 48000 --width 2048 --variant wide2steps4 ) &
( sleep 40; run $C --layer 16 --cls unres --steps 48000 --width 2048 --variant wide2steps4 ) &
wait
