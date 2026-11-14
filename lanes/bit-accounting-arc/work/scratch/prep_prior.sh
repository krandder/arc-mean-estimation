#!/bin/bash
# Copy every finished evaluation JSON (P1 runs and references) pulled so far into gpu_src/prior/P1 so a new VM skips
# those cells (21_eval.sh restores prior/P1 into /root/runs/P1). usage: prep_prior.sh
cd /home/agent/workspaces/mats/work/bit-accounting-arc
mkdir -p gpu_src/prior/P1/REF
for d in runs/bitarc-*/P1 runs/P1; do   # runs/P1: a final sync of gpu-run.sh lands there
  cp -n $d/VR_*.json gpu_src/prior/P1/ 2>/dev/null
  cp -n $d/REF/REF_*.json gpu_src/prior/P1/REF/ 2>/dev/null
done
echo "prior: $(ls gpu_src/prior/P1/VR_*.json 2>/dev/null | wc -l) runs, $(ls gpu_src/prior/P1/REF/*.json 2>/dev/null | wc -l) refs"
