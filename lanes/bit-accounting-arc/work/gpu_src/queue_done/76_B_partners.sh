#!/bin/bash
# Amendment A20 (A18 matched partners, VM B): doubling partners of the convergence subset's best runs that match them
# in every other setting. Short runs, to finish before bitarc-6 ends at 14:44Z.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 7 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_76B.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( run $C --layer 0 --cls local --init h1 --steps 24000 --depth 6 --variant h1c2s2 ) &
( sleep 20; run $C --layer 31 --cls local --steps 24000 --depth 6 --variant cap2steps2 ) &
( sleep 40; run $C --layer 0 --cls unres --steps 24000 --depth 6 --variant cap2steps2 ) &
wait
