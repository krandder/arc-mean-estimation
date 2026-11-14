#!/bin/bash
# Start GPU run 2 only after run 1's VM has been deleted (one L4 at a time).
cd /home/agent/workspaces/mats/work/scale-mode
until grep -q "DELETE vm=soup-gpu-scalemode-1" GPU-LOG.md; do sleep 20; done
sleep 10
exec scripts/gpu_launch2.sh scalemode-2 2h
