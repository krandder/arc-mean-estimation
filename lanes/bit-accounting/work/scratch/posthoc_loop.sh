#!/bin/bash
# Run the post-hoc chain analyses (incremental) whenever new saved chains appear; stops after 4 h.
cd /home/agent/workspaces/mats/work/bit-accounting
PY=/home/agent/.venvs/arc-noisy/bin/python
for i in $(seq 1 48); do
  n_pt=$(ls runs/S_chain/C_*.pt 2>/dev/null | wc -l)
  n_done=$($PY -c "import json,os; print(len(json.load(open('results/S2_onestep.json'))) if os.path.exists('results/S2_onestep.json') else 0)")
  if [ "$n_pt" -gt "$n_done" ]; then
    OMP_NUM_THREADS=1 nice -n 19 ionice -c3 $PY scratch/chain_posthoc.py >> logs/posthoc.log 2>&1
    OMP_NUM_THREADS=1 nice -n 19 ionice -c3 $PY scratch/chain_onestep.py >> logs/onestep.log 2>&1
    echo "$(date -u +%H:%M:%SZ) processed $n_pt chains" >> logs/posthoc_loop.log
  fi
  sleep 300
done
