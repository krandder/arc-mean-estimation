#!/bin/bash
# VM 2: v2 code throughput with and without CUDA graphs (dev nets only).
case $(hostname) in *bitarc-2-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/BENCH2; mkdir -p $O
S="--steps 300 --P_eval 2048 --t_step 3 --refine_every 0"
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --restarts 18 --batch 2048 --variant g0 $S --out $O > $O/nd_g0.txt 2>&1
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --restarts 18 --batch 2048 --variant g1 --graphs $S --out $O > $O/nd_g1.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 8 --batch 1024 --variant g0 $S --out $O > $O/arc_g0.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 8 --batch 1024 --variant g1 --graphs $S --out $O > $O/arc_g1.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --restarts 8 --batch 1024 --variant g1 --graphs $S --out $O > $O/arcu_g1.txt 2>&1
touch $O/DONE
