#!/bin/bash
# Amendment A22: round 2 of the convergence subset after bitarc-7 (spot) was preempted at ~14:32Z with its 8x-steps runs
# unfinished: depth 6 with 8x steps at layer 31 local (A16) and at layers 16 and 31 unrestricted (their best runs are
# depth 6 with 4x steps), the look-ahead start with 8x steps at layer 16 local, and layer-0 unrestricted depth 6 with 4x
# steps (the depth partner of its best run). At most 5 processes. VM A (bitarc-9).
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O $O/REF
for d in prior/P1 prior/P1/REF; do [ -d $d ] && cp -n $d/*.json $O/${d#prior/P1}/ 2>/dev/null; done
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt"
( python scripts/run_vr.py $C --layer 31 --cls local --steps 96000 --depth 6 --variant cap2steps8 --out $O >> $O/chain_80A.log 2>&1 ) &
( sleep 10; python scripts/run_vr.py $C --layer 31 --cls unres --steps 96000 --depth 6 --variant cap2steps8 --out $O >> $O/chain_80A.log 2>&1 ) &
( sleep 20; python scripts/run_vr.py $C --layer 16 --cls local --init h1 --steps 96000 --variant h1s8 --out $O >> $O/chain_80A.log 2>&1 ) &
( sleep 30; python scripts/run_vr.py $C --layer 16 --cls unres --steps 96000 --depth 6 --variant cap2steps8 --out $O >> $O/chain_80A.log 2>&1 ) &
( sleep 40; python scripts/run_vr.py $C --layer 0 --cls unres --steps 48000 --depth 6 --variant cap2steps4 --out $O >> $O/chain_80A.log 2>&1 ) &
wait
touch $O/DONE_80A
