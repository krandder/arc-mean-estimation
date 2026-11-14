#!/bin/bash
# Amendment A19: Kelvin's backward curriculum as another local start (ARC net 4000). Layer 31's best code (depth 6, 4x
# steps; A11) starts layer 28; each finished layer's code starts the next earlier measured layer (28 -> 24 -> ... -> 0),
# composed with the layer map inside the local class (scripts/run_vr.py, --init bwd: the hidden layer computes h_{l+1},
# the whole encoder is distilled onto the later code's signal, gains and prior copied; no lambda annealing, so the
# later code's per-price structure is kept). Then 2x steps from the same sources at layers 16 and 0 (the A18 rule).
# VM A (bitarc-7). The source file VR_arc_l31_local_cap2steps4_r0_s4000.pt is copied into /root/runs/P1 first.
case $(hostname) in *bitarc-1-*|*bitarc-3-*|*bitarc-5-*|*bitarc-7-*|*bitarc-9-*) ;; *) exit 0 ;; esac
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/P1; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py\|[r]efine_posthoc.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt 4000 ] || [ "$(nrun)" -ge 7 ]; do sleep 15; done; sleep 10; }
wait_same() { while pgrep -f -- "run_vr.py $*" > /dev/null; do sleep 20; done; }
run() { wait_same "$@"; gate; python scripts/run_vr.py "$@" --out $O >> $O/chain_71A.log 2>&1; }
C="--family arc --seeds 4000 --batch 1024 --restarts 1 --save_pt --cls local --init bwd --anneal 0"
SRC=$O/VR_arc_l31_local_cap2steps4_r0_s4000.pt
[ -e $SRC ] || cp -n prior/pt/VR_arc_l31_local_cap2steps4_r0_s4000.pt $O/ 2>/dev/null
while [ ! -e $SRC ]; do sleep 30; done
for l in 28 24 20 16 12 8 4 2 0; do
  run $C --layer $l --steps 12000 --bwd_pt $SRC --variant bwd
  [ $l = 16 ] && S16=$SRC
  [ $l = 0 ] && S0=$SRC
  SRC=$O/VR_arc_l${l}_local_bwd_r0_s4000.pt
  [ -e $SRC ] || break
done
( [ -n "$S16" ] && run $C --layer 16 --steps 24000 --bwd_pt $S16 --variant bwds2 ) &
( [ -n "$S0" ] && run $C --layer 0 --steps 24000 --bwd_pt $S0 --variant bwds2 ) &
wait
touch $O/DONE_71A
