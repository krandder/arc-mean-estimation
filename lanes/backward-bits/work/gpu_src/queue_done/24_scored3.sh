#!/bin/bash
# Scored run v3 (amendment A4: round-1 review fixes; notes/DEVIATIONS.md D5): fresh output dir /root/runs/scored3, the
# dependency scheduler with 8 workers: output codes first (no dependencies needed: every chain job builds its own if
# missing, but the outcode jobs run first in the list), then chains, then evaluations as their chains finish.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/logs/scored3
bash scripts/pool.sh queue/scored3_outcode.txt 6 /root/runs/logs/scored3
/root/venv/bin/python scripts/sched.py queue/scored3_dag.json 8 /root/runs/logs/scored3/dag
echo "scored3 done $(date -u +%FT%TZ)" > /root/runs/logs/scored3/DONE
