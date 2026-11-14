#!/bin/bash
# Amendment A15: a search from outside both informed starts, where they differ most. Random local start ('random':
# random hidden layer) with the encoder learning rate at the MLP's (1e-3, 33x the default): narrow-deep layer 0, all six
# nets, restarts 0-2 (variant rndhi; the reference and look-ahead starts differ by 13-56% there at nMSE 0.1), and ARC
# net 4000 layer 8 (one restart). VM A.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_64A.log 2>&1; }
sleep 20
run --family nd --seeds 203,216,217,220,221,223 --restarts 3 --steps 12000 --batch 2048 --graphs --layer 0 --cls local --init random --lr_enc 1e-3 --variant rndhi
run --family arc --seeds 4000 --steps 12000 --batch 1024 --layer 8 --cls local --restarts 1 --init random --lr_enc 1e-3 --variant rndhi
