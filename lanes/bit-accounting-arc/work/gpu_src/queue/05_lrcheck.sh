#!/bin/bash
# VM 2: dev 9100 only: learning-rate check for the precision regime (local l = 0 and 16, out), 4000 steps.
case $(hostname) in *bitarc-2-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/LRCHK; mkdir -p $O
S="--steps 4000 --batch 1024 --P_eval 8192 --t_step 1 --refine_every 3 --P_ref 2048"
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 1 --variant lrA --lr_lin 1e-4 --lr_enc 3e-4 $S --out $O > $O/a.txt 2>&1 &
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 1 --variant lrB --lr_lin 3e-5 --lr_enc 3e-5 $S --out $O > $O/b.txt 2>&1 &
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 1 --variant lrC --lr 3e-4 --lr_lin 3e-5 --lr_enc 3e-5 $S --out $O > $O/c.txt 2>&1 &
wait
python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls local --restarts 1 --variant lrA --lr_lin 1e-4 --lr_enc 3e-4 $S --out $O > $O/d.txt 2>&1 &
python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls local --restarts 1 --variant lrB --lr_lin 3e-5 --lr_enc 3e-5 $S --out $O > $O/e.txt 2>&1 &
python scripts/ref_curve.py --family arc --seeds 9100 --layers 0,16 --P_eval 8192 --t_step 1 --out $O/REF > $O/f.txt 2>&1 &
wait
touch $O/DONE
