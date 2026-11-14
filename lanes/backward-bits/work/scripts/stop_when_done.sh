#!/bin/bash
# When both the scored run's DONE marker and the amended Gaussian run's DONE marker have been pulled, push queue/STOP to
# the VM so its worker exits and gpu-run's cleanup syncs and deletes the VM. usage: stop_when_done.sh <run-id>
cd /home/agent/workspaces/mats/work/backward-bits
until [ -f runs_gpu/logs/scored3/DONE ] && [ -f runs_gpu/logs/gauss2/DONE ] && [ -f runs_gpu/logs/gauss3/DONE ]; do sleep 60; done
echo "stop" > /tmp/STOP
bash scripts/gpu_pull.sh "$1" /tmp/STOP >> logs/stop_when_done.log 2>&1
echo "$(date -u +%FT%TZ) pushed STOP to $1" >> logs/stop_when_done.log
