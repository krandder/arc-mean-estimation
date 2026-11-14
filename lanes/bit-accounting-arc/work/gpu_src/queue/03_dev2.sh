#!/bin/bash
# v2 (analytic reference anchor, standardised triangular prior, output head + preimage refinement): smoke runs, then
# dev runs on dev nets only (ARC 9100, narrow-deep 111, toy seed 9). Before PREREG.
case $(hostname) in *bitarc-1-*) ;; *) exit 0 ;; esac   # VM 1 only
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/DEV2; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt ${2:-6000} ] || [ "$(nrun)" -ge ${1:-3} ]; do sleep 15; done; sleep 20; }
S="--steps 300 --variant smoke --P_eval 4096 --t_step 1.5 --P_ref 2048"
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local $S --out $O > $O/smoke1.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres $S --out $O > $O/smoke2.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 32 --cls out $S --out $O > $O/smoke3.txt 2>&1
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --batch 4096 $S --out $O > $O/smoke4.txt 2>&1
python scripts/run_vr.py --family toy --toy_k 16 --seeds 9 --layer 0 --cls local $S --out $O > $O/smoke5.txt 2>&1
python scripts/ref_curve.py --family arc --seeds 9100 --layers 0 --P_jac 2048 --P_eval 4096 --t_step 1.5 --out $O/REFSMOKE > $O/smoke6.txt 2>&1
touch $O/SMOKE_DONE
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l0_unres.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l0_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 32 --cls out --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l32_out.txt 2>&1 &
gate 3; python scripts/ref_curve.py --family arc --seeds 9100 --layers 0,16,31,32 --out $O/REF > $O/ref_arc.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls local --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l16_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 31 --cls local --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l31_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls unres --restarts 2 --steps 20000 --out $O --save_pt > $O/arc_l16_unres.txt 2>&1 &
wait
