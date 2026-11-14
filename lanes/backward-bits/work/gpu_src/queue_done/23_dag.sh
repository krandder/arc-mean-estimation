#!/bin/bash
# Scored run v2 under the dependency scheduler (amendment A3, infrastructure): the registered scored2 commands, 8
# workers; a net's truth pass starts when its four chains are done, gauss/conv after its chain K, fwd right away.
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/logs/scored2
/root/venv/bin/python scripts/sched.py queue/scored2_dag.json 8 /root/runs/logs/scored2/dag
echo "scored2 dag done $(date -u +%FT%TZ)" > /root/runs/logs/scored2/DAG_DONE
