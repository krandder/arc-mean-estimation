#!/bin/bash
# Smoke test of the backward-curriculum start (A18 addition, not a registered result): 300 steps at ARC net 4000
# layer 28 local from the layer-31 depth-6 4x-steps code; output in /root/runs/BWDTEST. VM B.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/BWDTEST
python scripts/run_vr_bwd.py --family arc --seeds 4000 --layer 28 --cls local --init bwd \
  --bwd_pt /root/runs/P1/VR_arc_l31_local_cap2steps4_r0_s4000.pt --anneal 0 --steps 300 --batch 1024 --P_eval 4096 \
  --t_step 1.0 --refine_every 100 --variant bwdtest --out /root/runs/BWDTEST >> /root/runs/BWDTEST/out.txt 2>&1
echo "exit $?" >> /root/runs/BWDTEST/out.txt
