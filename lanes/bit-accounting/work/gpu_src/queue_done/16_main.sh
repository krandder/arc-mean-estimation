#!/bin/bash
# Priority queue after the OOM crashes and Kelvin's 02:10Z changes: S7 (revised, primary) and S9 first, then the S2
# chains and S3 runs that died of OOM. Each job starts only when >= 5 GB of GPU memory are free.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/S_ent /root/runs/S_real /root/runs/S_chain /root/runs/S_kelvin
waitmem() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 5000 ]; do sleep 20; done; sleep 45; }
E="--steps 2000 --batch 2048 --out /root/runs/S_ent"
waitmem; python scripts/run_entropy.py --configs 16x16 --seeds 5000,5001,5002 $E > /root/runs/S_ent/log3_16x16.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 32x32 --seeds 5000,5001,5002 $E > /root/runs/S_ent/log3_32x32.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16,32x32 --seeds 5000,5001 --out /root/runs/S_real > /root/runs/S_real/log.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 16x4,32x8 --seeds 5000 $E > /root/runs/S_ent/log3_small.txt 2>&1 &
waitmem; python scripts/run_chain.py --configs 16x16 --seeds 5000,5001,5002 --steps 2000 --batch 2048 --out /root/runs/S_chain > /root/runs/S_chain/log6_16x16.txt 2>&1 &
waitmem; python scripts/run_chain.py --configs 32x8 --seeds 5000,5001,5002 --steps 2000 --batch 2048 --out /root/runs/S_chain > /root/runs/S_chain/log6_32x8.txt 2>&1 &
waitmem; python scripts/run_kelvin.py --configs 16x4,32x8 --seeds 5000,5001,5002 --steps 2000 --batch 1024 --out /root/runs/S_kelvin > /root/runs/S_kelvin/log6_small.txt 2>&1 &
wait
