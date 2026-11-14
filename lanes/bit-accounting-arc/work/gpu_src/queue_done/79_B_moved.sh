#!/bin/bash
# The jobs of 77_A_bwd1.sh (A21) and 78_A_partners2.sh (A20), moved from the CPU-bound bitarc-7 to the idle bitarc-6
# before they started there; same commands (the backward start runs with scripts/run_vr_bwd.py, identical to the current
# scripts/run_vr.py). VM B.
case $(hostname) in *bitarc-2-*|*bitarc-4-*|*bitarc-6-*|*bitarc-8-*|*bitarc-10-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
B="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt --cls local --init bwd --anneal 0 --steps 12000"
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( python scripts/run_vr_bwd.py $B --layer 16 --bwd_pt /root/runs/SRC/VR_arc_l20_local_h1_r0_s4000.pt --variant bwd1 --out $O >> $O/chain_79B.log 2>&1 ) &
( sleep 10; python scripts/run_vr_bwd.py $B --layer 0 --bwd_pt /root/runs/SRC/VR_arc_l2_local_h1_r0_s4000.pt --variant bwd1 --out $O >> $O/chain_79B.log 2>&1 ) &
( sleep 20; python scripts/run_vr.py $C --layer 16 --cls unres --steps 24000 --depth 6 --variant cap2steps2 --out $O >> $O/chain_79B.log 2>&1 ) &
( sleep 30; python scripts/run_vr.py $C --layer 31 --cls unres --steps 24000 --depth 6 --variant cap2steps2 --out $O >> $O/chain_79B.log 2>&1 ) &
wait
