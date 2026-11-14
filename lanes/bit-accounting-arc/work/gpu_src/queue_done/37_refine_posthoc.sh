#!/bin/bash
# Post-hoc decoder certificate (not registered; reported as a diagnostic): stronger preimage refinement of the saved
# unrestricted base models at early ARC layers, as their .pt files appear on this VM. VM B only.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1/REFINE; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 4 ]; do sleep 15; done; sleep 10; }
for l in 0 16 8 4 2; do
  f=/root/runs/P1/VR_arc_l${l}_unres_base_r0_s4000.pt
  [ -e /root/runs/P1/pt/$(basename $f) ] && f=/root/runs/P1/pt/$(basename $f)
  while [ ! -e $f ]; do sleep 60; [ -e /root/runs/P1/pt/$(basename $f) ] && f=/root/runs/P1/pt/$(basename $f); done
  gate; python scripts/refine_posthoc.py --family arc --seeds 4000,4001,4002,4003 --restarts 2 --layer $l --pt $f --out $O >> $O/refine.log 2>&1
done
