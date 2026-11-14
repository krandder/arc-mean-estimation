#!/bin/bash
# GPU queue 2 for the scale-mode lane (PREREG Amendment 2). Runs in /root/soup on the VM; outputs to /root/runs/gpu2
# (synced back to work/scale-mode/runs/gpu2 by gpu-run.sh).
cd /root/soup
export PATH=/root/venv/bin:$PATH
OUT=/root/runs/gpu2; LOG=/root/runs/gpu2/queue.log
mkdir -p $OUT
nvidia-smi > $OUT/nvidia-smi.txt 2>&1
python -c "import torch, numpy, scipy; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), numpy.__version__, scipy.__version__)" > $OUT/versions.txt 2>&1
run() { echo "start $* $(date -u +%H:%M:%SZ)" >> $LOG; env -i HOME=/root PATH=/root/venv/bin:/usr/bin:/bin SM_PREFIX="${SM_PREFIX:-}" python -I sm_gpu2.py $OUT "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
# parity on Phase 2 dev MLP 12 (CPU results exist locally in runs_dev/)
for job in "arc p2:12 k2,k2a,k3f" "lv p2:12" "cov p2:12" "sl3 p2:12" "rqmc p2:12 8,10 8"; do SM_PREFIX=parity_ run $job; done
# E3 256 x 64, nets 620-627
for s in 620 621 622 623 624 625 626 627; do net=au:$s:256:64
  run truth $net 20; run lv $net; run arc $net k2,k2a,k3f; run sl3 $net; run rqmc $net 8,10,12,14 8
done
# E4, Phase 2 public MLPs 0-11
for i in 0 1 2 3 4 5 6 7 8 9 10 11; do
  run arc p2:$i k2,k2a; run lv p2:$i; run cov p2:$i
  if [ $i -le 5 ]; then run rqmc p2:$i 8,10,12,14,16 8; else run rqmc p2:$i 8,10,12,14 8; fi
done
for i in 0 1 2 3 4 5; do run arc p2:$i k3f; run sl3 p2:$i; done
echo "queue end $(date -u +%H:%M:%SZ)" >> $LOG
