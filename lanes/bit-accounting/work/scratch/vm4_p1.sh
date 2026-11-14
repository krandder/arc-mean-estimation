#!/bin/bash
# Start phase 1 (P1) on VM 4 outside the held worker: the queue script picks jobs_vm4 by hostname. Run as root.
mkdir -p /root/runs/P1
cd /root/soup
setsid nohup bash staged/30_p1.sh >> /root/runs/P1/queue_vm4.log 2>&1 < /dev/null &
echo "P1 queue pid $!"
