#!/usr/bin/env bash
# A5 (plain PoE, learned diagonal variances from the fused NLL, calibration weight 1.0 with sampling covariance) on
# 32x4 seed 9611. Same settings at every K: 2,000 training populations x 512 paths (1.02M advice paths), torch EM warm
# start, 300 steps, 2 populations per step, training deduce on 16 mass-sampled parts x 32 draws (evaluation uses all
# parts and 256 draws). Order K = 256, 1024, 64, 16, each with its own time cap. Outputs and logs in /root/runs.
cd /root/soup
nvidia-smi > /root/runs/nvidia_smi.txt 2>&1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
for KC in $(cat scripts/klist.txt 2>/dev/null || echo "16:1200 64:1800 256:3600 1024:6600"); do
  K=${KC%%:*}; CAP=${KC##*:}
  echo "K=$K start $(date -u +%H:%M:%SZ) cap ${CAP}s" >> /root/runs/worker_status.txt
  timeout $CAP python step5_gpu.py 9611 32 4 --K $K --pops 2000 --M 512 --em torch --steps 300 --batch_pops 2 \
    --train_parts 16 --train_draws 32 --fusion poe --lam_cal 1.0 \
    --out /root/runs/step5_n32_L4_s9611_K${K}_poe_cal1_1M_gpu.json > /root/runs/step5_K${K}_1M_gpu.log 2>&1
  echo "K=$K exit $? $(date -u +%H:%M:%SZ)" >> /root/runs/worker_status.txt
done
