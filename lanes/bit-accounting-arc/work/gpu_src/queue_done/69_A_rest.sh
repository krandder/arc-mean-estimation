#!/bin/bash
# Amendment A18: what stays of VM A's registered remainder (61_A.sh is retired): the ARC local base at layer 4 (all four
# nets) and the narrow-deep layer-0 fixed-lambda check. Up to 6 processes.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_69A.log 2>&1; }
( run --family arc --seeds 4000,4001,4002,4003 --restarts 1 --steps 12000 --batch 1024 --save_pt --layer 4 --cls local ) &
( sleep 30; run --family nd --seeds 203 --batch 2048 --graphs --steps 12000 --layer 0 --cls local --variant fixlam --fixlam=-1,-2.5,-4 ) &
wait
touch $O/DONE_69A
