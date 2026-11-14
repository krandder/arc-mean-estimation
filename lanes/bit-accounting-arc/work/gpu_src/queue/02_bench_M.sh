#!/bin/bash
# Throughput with many models per process (dev nets only): ARC M = 12 local and unres at l = 0, narrow-deep M = 18.
case $(hostname) in *bitarc-2-*) ;; *) exit 0 ;; esac   # VM 2 only
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/BENCH; mkdir -p $O
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 12 --steps 300 --variant benchM12 --P_eval 2048 --t_step 2 --out $O > $O/b1.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --restarts 12 --steps 300 --variant benchM12 --P_eval 2048 --t_step 2 --out $O > $O/b2.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --restarts 12 --steps 300 --batch 1024 --variant benchM12b1024 --P_eval 2048 --t_step 2 --out $O > $O/b3.txt 2>&1
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --restarts 18 --steps 300 --batch 4096 --variant benchM18 --P_eval 2048 --t_step 2 --out $O > $O/b4.txt 2>&1
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --restarts 18 --steps 300 --batch 2048 --variant benchM18b2048 --P_eval 2048 --t_step 2 --out $O > $O/b5.txt 2>&1
