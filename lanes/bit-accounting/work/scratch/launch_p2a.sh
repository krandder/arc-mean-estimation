#!/bin/bash
# Launch two on-demand L4s for P2.0 parts 2-4 (queue 40_p2a.sh), un-stage the queue after both synced, pull loops.
cd /home/agent/workspaces/mats/work/bit-accounting
cp gpu_src/staged/40_p2a.sh gpu_src/queue/40_p2a.sh
GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh bitacct-10 2h > logs/gpu-run-bitacct-10.out 2>&1 &
sleep 20
GPU_PROVISIONING=STANDARD nohup bash scratch/gpu_launch.sh bitacct-11 2h > logs/gpu-run-bitacct-11.out 2>&1 &
until grep -q "RUN vm=soup-gpu-bitacct-10" GPU-LOG.md && grep -q "RUN vm=soup-gpu-bitacct-11" GPU-LOG.md; do sleep 15; done
mv gpu_src/queue/40_p2a.sh gpu_src/staged/40_p2a.sh
echo "$(date -u +%T) bitacct-10/11 running; queue un-staged" >> logs/launch_p2a.log
nohup bash scratch/pull_loop.sh bitacct-10 > /dev/null 2>&1 &
nohup bash scratch/pull_loop.sh bitacct-11 > /dev/null 2>&1 &
