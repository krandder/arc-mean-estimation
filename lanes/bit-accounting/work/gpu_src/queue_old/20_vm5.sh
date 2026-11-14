#!/bin/bash
# VM 5: restore finished results (JSON only; every script skips cells whose JSON exists), then run what is left, in
# priority order, each job starting only when >= 4 GB of GPU memory are free. Ends with STOP.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for d in prior/*/; do b=$(basename $d); mkdir -p /root/runs/$b; cp -n prior/$b/*.json /root/runs/$b/ 2>/dev/null; done
waitmem() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ]; do sleep 20; done; sleep 30; }
E="--steps 2000 --batch 2048"
for k in feistel tanh4 linear; do mkdir -p /root/runs/S11_$k; done
waitmem; python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind feistel --out /root/runs/S11_feistel > /root/runs/S11_feistel/log5_real.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind tanh4 --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log5_real.txt 2>&1 &
waitmem; python scripts/run_chain.py --configs 16x16 --seeds 5000 --classes local --netkind feistel $E --out /root/runs/S11_feistel > /root/runs/S11_feistel/log5_chain.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 16x16 --seeds 5000,5001,5002 $E --out /root/runs/S_ent > /root/runs/S_ent/log5_16x16.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 32x32 --seeds 5000,5001,5002 $E --out /root/runs/S_ent > /root/runs/S_ent/log5_32x32.txt 2>&1 &
waitmem; python scripts/run_chain_real.py --configs 16x16,32x32 --seeds 5000,5001 --out /root/runs/S_real > /root/runs/S_real/log5.txt 2>&1 &
waitmem; ( python scripts/run_sim.py --configs 16x16,32x32 --seed 5000 --out /root/runs/S_sim > /root/runs/S_sim/log5.txt 2>&1;
           for k in tanh4 feistel linear; do python scripts/run_sim.py --configs 16x16 --seed 5000 --classes mlp,linear,sparse2 --netkind $k --out /root/runs/S11_$k >> /root/runs/S11_$k/log5_sim.txt 2>&1; done ) &
waitmem; ( python scripts/run_chain_real.py --configs 16x16 --seeds 5000 --netkind linear --out /root/runs/S11_linear > /root/runs/S11_linear/log5_real.txt 2>&1;
           python scripts/run_chain.py --configs 16x16 --seeds 5000 --classes local --netkind tanh4 $E --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log5_chain.txt 2>&1 ) &
waitmem; ( python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind tanh4 $E --out /root/runs/S11_tanh4 > /root/runs/S11_tanh4/log5_ent.txt 2>&1;
           python scripts/run_entropy.py --configs 16x16 --seeds 5000 --netkind feistel $E --out /root/runs/S11_feistel > /root/runs/S11_feistel/log5_ent.txt 2>&1 ) &
waitmem; python scripts/run_chain.py --configs 16x16,32x8,32x32 --seeds 5000,5001,5002 $E --out /root/runs/S_chain > /root/runs/S_chain/log7.txt 2>&1 &
waitmem; python scripts/run_entropy.py --configs 16x4,32x8 --seeds 5000 $E --out /root/runs/S_ent > /root/runs/S_ent/log5_small.txt 2>&1 &
waitmem; ( python scripts/run_cert.py --configs 16x16 --seed 5000 --out /root/runs/S_cert > /root/runs/S_cert/log5_16x16.txt 2>&1;
           python scripts/run_cert.py --configs 32x32 --seed 5000 --out /root/runs/S_cert > /root/runs/S_cert/log5_32x32.txt 2>&1 ) &
waitmem; python scripts/run_kelvin.py --configs 16x4,32x8 --seeds 5000,5001,5002 --steps 2000 --batch 1024 --out /root/runs/S_kelvin > /root/runs/S_kelvin/log7_small.txt 2>&1 &
wait
touch /root/soup/queue/STOP
