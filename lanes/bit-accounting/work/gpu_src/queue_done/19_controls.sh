#!/bin/bash
# S11 controls (priority over the remaining S2/S3 reruns). 16x16 seed 5000 for tanh4, feistel, linear.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
waitmem() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ]; do sleep 20; done; sleep 30; }
for k in feistel tanh4 linear; do mkdir -p /root/runs/S11_$k; done
waitmem; python scripts/run_chain.py --configs 16x16 --seeds 5000 --classes local --netkind feistel --steps 2000 --batch 2048 --out /root/runs/S11_feistel > /root/runs/S11_feistel/log_chain.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind feistel --out /root/runs/S11_feistel > /root/runs/S11_feistel/log_real.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind tanh4 --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log_real.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind linear --out /root/runs/S11_linear > /root/runs/S11_linear/log_real.txt 2>&1 &
waitmem; python scripts/run_chain.py --configs 16x16 --seeds 5000 --classes local --netkind tanh4 --steps 2000 --batch 2048 --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log_chain.txt 2>&1 &
waitmem; python scripts/run_sim.py --configs 16x16 --seed 5000 --classes mlp,linear,sparse2 --netkind tanh4 --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log_sim.txt 2>&1 &
waitmem; python scripts/run_sim.py --configs 16x16 --seed 5000 --classes mlp,linear,sparse2 --netkind feistel --out /root/runs/S11_feistel > /root/runs/S11_feistel/log_sim.txt 2>&1 &
waitmem; python scripts/run_sim.py --configs 16x16 --seed 5000 --classes mlp,linear,sparse2 --netkind linear --out /root/runs/S11_linear > /root/runs/S11_linear/log_sim.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind tanh4 --steps 2000 --batch 2048 --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log_ent.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind feistel --steps 2000 --batch 2048 --out /root/runs/S11_feistel > /root/runs/S11_feistel/log_ent.txt 2>&1 &
wait
