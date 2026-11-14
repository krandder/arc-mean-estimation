#!/bin/bash
# VM 1 only: run two cells of the registered queue earlier (process change, same commands): the ARC output cell
# (needed by certificates C1/C2) and the references of net 4000. The chains of 10_eval.sh skip them later.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 3 ]; do sleep 15; done; sleep 10; }
gate; python scripts/run_vr.py --family arc --seeds 4000,4001,4002,4003 --restarts 2 --steps 12000 --batch 1024 --save_pt --layer 32 --cls out --out $O >> $O/chain_early.log 2>&1
gate; python scripts/ref_curve.py --family arc --seeds 4000 --layers 31,0,16,8,24,4,28,12,20,2,32 --out $O/REF >> $O/ref_early.log 2>&1
