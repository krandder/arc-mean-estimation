#!/bin/bash
# Resume the scored run on a later VM: restore the state pulled from the previous VM (gpu_src/prior/scored, copied
# without overwriting), then the same registered job files (chains resume per step, evaluations per layer).
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p /root/runs/scored3 /root/runs/logs/scored3
cp -rn /root/soup/prior/scored3/. /root/runs/scored3/ 2>/dev/null
LOG=/root/runs/logs/scored3
echo "resume 30 (dag2: amendment D8) $(date -u +%FT%TZ)" >> $LOG/pool.log
/root/venv/bin/python scripts/sched.py queue/scored3_dag2.json 8 $LOG/dag
echo "scored3 done $(date -u +%FT%TZ)" > $LOG/DONE
