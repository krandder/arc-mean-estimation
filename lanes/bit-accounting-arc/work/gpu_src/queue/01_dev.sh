#!/bin/bash
# Dev runs on dev nets only (ARC 9100, narrow-deep 111, toy seed 9): timing, sanity, lambda range. Before PREREG.
case $(hostname) in *bitarc-1-*) ;; *) exit 0 ;; esac   # VM 1 only
cd /root/soup
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
O=/root/runs/DEV; mkdir -p $O
nrun() { ps -eo args | grep -c "[r]un_vr.py\|[r]ef_curve.py"; }
gate() { while [ "$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)" -lt ${2:-6000} ] || [ "$(nrun)" -ge ${1:-3} ]; do sleep 15; done; sleep 20; }
# timing benchmarks (1000 steps)
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --steps 1000 --variant bench --P_eval 4096 --t_step 1 --out $O > $O/bench_arc_l0_unres.txt 2>&1
python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --restarts 3 --steps 1000 --variant bench3 --P_eval 4096 --t_step 1 --out $O > $O/bench_arc_l0_local3.txt 2>&1
python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --restarts 3 --steps 1000 --variant bench3 --batch 4096 --P_eval 4096 --t_step 1 --out $O > $O/bench_nd_l0_local3.txt 2>&1
# full dev runs (20000 steps)
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 32 --cls out --steps 20000 --out $O --save_pt > $O/arc_l32_out.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 31 --cls local --steps 20000 --out $O --save_pt > $O/arc_l31_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls unres --steps 20000 --out $O --save_pt > $O/arc_l0_unres.txt 2>&1 &
gate 3; python scripts/ref_curve.py --family arc --seeds 9100 --layers 0,8,16,31,32 --out /root/runs/DEV_REF > $O/ref_arc.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 0 --cls local --steps 20000 --out $O --save_pt > $O/arc_l0_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls local --steps 20000 --out $O --save_pt > $O/arc_l16_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family arc --seeds 9100 --layer 16 --cls unres --steps 20000 --out $O --save_pt > $O/arc_l16_unres.txt 2>&1 &
gate 3; python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls local --steps 20000 --batch 4096 --out $O > $O/nd_l0_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family nd --seeds 111 --layer 256 --cls out --steps 20000 --batch 4096 --out $O > $O/nd_l256_out.txt 2>&1 &
gate 3; python scripts/run_vr.py --family nd --seeds 111 --layer 0 --cls unres --steps 20000 --batch 4096 --out $O > $O/nd_l0_unres.txt 2>&1 &
gate 3; python scripts/ref_curve.py --family nd --seeds 111 --layers 0,32,128,255,256 --out /root/runs/DEV_REF > $O/ref_nd.txt 2>&1 &
gate 3; python scripts/run_vr.py --family toy --toy_k 16 --seeds 9 --layer 0 --cls local --steps 20000 --out $O > $O/toy16_local.txt 2>&1 &
gate 3; python scripts/run_vr.py --family toy --toy_k 16 --seeds 9 --layer 0 --cls unres --steps 20000 --out $O > $O/toy16_unres.txt 2>&1 &
wait
