#!/bin/bash
# Resume after the spot preemption of bitacct-2 (00:32Z): restore finished results, then run the rest of S1 and S2 and
# all of S3 and S4 in parallel (16 processes; the job is CPU-launch-bound, so the total time is about the same).
cd /root/soup
mkdir -p /root/runs/S_curves /root/runs/S_chain /root/runs/S_kelvin /root/runs/S_noisy
cp -n prior/S_curves/*.json /root/runs/S_curves/ 2>/dev/null
cp -n prior/S_chain/* /root/runs/S_chain/ 2>/dev/null
A1="--steps 1500 --batch 2048 --out /root/runs/S_curves"
python scripts/run_curves.py --configs 16x4 --seeds 5000,5001,5002 --classes local,unres $A1 > /root/runs/S_curves/log3_16x4.txt 2>&1 &
python scripts/run_curves.py --configs 32x8 --seeds 5000,5001,5002 --classes local,unres $A1 > /root/runs/S_curves/log3_32x8.txt 2>&1 &
python scripts/run_curves.py --configs 16x16 --seeds 5000,5001,5002 --classes local,unres $A1 > /root/runs/S_curves/log3_16x16.txt 2>&1 &
python scripts/run_curves.py --configs 32x32 --seeds 5000,5001 --classes local,unres $A1 > /root/runs/S_curves/log3_32x32a.txt 2>&1 &
( python scripts/run_curves.py --configs 32x32 --seeds 5002 --classes local,unres $A1 > /root/runs/S_curves/log3_32x32b.txt 2>&1 ;
  python scripts/run_curves.py --configs 16x4,32x8,16x16,32x32 --seeds 5000 --classes linear $A1 > /root/runs/S_curves/log3_linear.txt 2>&1 ) &
A2="--steps 2000 --batch 2048 --out /root/runs/S_chain"
for cfg in 16x4 16x16 32x8 32x32; do
  python scripts/run_chain.py --configs $cfg --seeds 5000,5001,5002 $A2 > /root/runs/S_chain/log3_$cfg.txt 2>&1 &
done
A3="--steps 2000 --batch 1024 --out /root/runs/S_kelvin"
for cfg in 16x16 32x32 16x4 32x8; do
  python scripts/run_kelvin.py --configs $cfg --seeds 5000,5001,5002 $A3 > /root/runs/S_kelvin/log3_$cfg.txt 2>&1 &
done
A4="--steps 1500 --batch 2048 --sigma 1 --out /root/runs/S_noisy"
python scripts/run_noisy.py --configs 16x16 --seeds 5000,5001,5002 $A4 > /root/runs/S_noisy/log3_16x16.txt 2>&1 &
python scripts/run_noisy.py --configs 32x32 --seeds 5000,5001 $A4 > /root/runs/S_noisy/log3_32x32a.txt 2>&1 &
python scripts/run_noisy.py --configs 32x32 --seeds 5002 $A4 > /root/runs/S_noisy/log3_32x32b.txt 2>&1 &
wait
touch /root/soup/queue/STOP
