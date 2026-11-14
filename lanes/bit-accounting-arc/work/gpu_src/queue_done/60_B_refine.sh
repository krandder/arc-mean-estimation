#!/bin/bash
# Post-hoc decoder diagnostic (not registered; see 37_refine_posthoc.sh, retired): preimage refinement of the saved ARC
# net-4000 unrestricted models at layers 16, 8, 24, waiting for each model file (57_B.sh chain c saves them); the copy
# in 57_B.sh chain f skipped them because they did not exist yet. VM B.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O/REFINE
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 6 ]; do sleep 15; done; sleep 10; }
for l in 16 8 24; do
  f=$O/VR_arc_l${l}_unres_base_r0_s4000.pt
  while [ ! -e $f ] || pgrep -f -- "run_vr.py --family arc --seeds 4000 --steps 12000 --batch 1024 --layer $l --cls unres --restarts 1 --save_pt" > /dev/null; do sleep 60; done
  [ -e $O/REFINE/REFINE_arc_l${l}_unres_$(basename $f).json ] && continue
  gate; python scripts/refine_posthoc.py --family arc --seeds 4000 --restarts 1 --layer $l --pt $f --out $O/REFINE >> $O/REFINE/refine.log 2>&1
done
