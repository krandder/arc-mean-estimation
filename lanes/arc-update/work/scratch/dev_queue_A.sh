#!/bin/bash
# Dev (calibration, not scored): attribution and rank statistics on dev net 100 (256 x 32, truth s0.001), controls.
cd /home/agent/workspaces/mats/work/arc-update
PY=/home/agent/.venvs/arc-noisy/bin/python
export AU_THREADS=1
echo "devA start $(date -u +%H:%M:%SZ)" >> logs/queue.log
nice -n 19 ionice -c3 $PY scratch/run_rank.py control 0 14 >> logs/dev_rank_control.log 2>&1
nice -n 19 ionice -c3 $PY scratch/run_rank.py 100 s0.001 14 >> logs/dev_rank_100.log 2>&1
nice -n 19 ionice -c3 $PY scratch/run_attr.py 100 s0.001 16 >> logs/dev_attr_100.log 2>&1
echo "devA end $(date -u +%H:%M:%SZ)" >> logs/queue.log
