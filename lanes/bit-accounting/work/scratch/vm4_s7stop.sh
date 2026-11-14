#!/bin/bash
# Stop the S7 all-arm jobs once seed 5000 is complete (phase 1 supersedes S7; seed-5000 cells serve as fixed-lambda
# references). Kill by PID only. Run on the VM as root.
setsid nohup bash -c '
  until [ -e /root/runs/S_ent/E_n16_L16_s5000_l16_unres.json ]; do sleep 20; done; kill 11063
  echo "$(date -u +%T) killed 11063" >> /root/runs/S_ent/stop.log' > /dev/null 2>&1 < /dev/null &
setsid nohup bash -c '
  until [ -e /root/runs/S_ent/E_n32_L32_s5000_l32_unres.json ]; do sleep 20; done; kill 11254
  echo "$(date -u +%T) killed 11254" >> /root/runs/S_ent/stop.log' > /dev/null 2>&1 < /dev/null &
echo started
