#!/bin/bash
# S6 (VQ, cheap) at once; S5 certificates (toy, then 16x16 and 32x32 seed 5000) once the S1 curve processes end.
cd /root/soup
mkdir -p /root/runs/S_vq /root/runs/S_cert
python scripts/run_vq.py --configs 16x4,32x8,16x16,32x32 --seeds 5000,5001,5002 --out /root/runs/S_vq > /root/runs/S_vq/log.txt 2>&1 &
( while pgrep -f 'run_curves.py' > /dev/null; do sleep 30; done
  python scripts/run_cert.py --toy 2,4,8 --out /root/runs/S_cert > /root/runs/S_cert/log_toy.txt 2>&1
  python scripts/run_cert.py --configs 16x16 --seed 5000 --out /root/runs/S_cert > /root/runs/S_cert/log_16x16.txt 2>&1 ) &
( while pgrep -f 'run_curves.py' > /dev/null; do sleep 30; done
  python scripts/run_cert.py --configs 32x32 --seed 5000 --out /root/runs/S_cert > /root/runs/S_cert/log_32x32.txt 2>&1 ) &
wait
