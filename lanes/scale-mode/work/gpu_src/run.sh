#!/bin/bash
# GPU queue for the scale-mode lane (PREREG Amendment 1). Runs in /root/soup on the VM; outputs to /root/runs/gpu
# (synced back to work/scale-mode/runs/gpu by gpu-run.sh). Setup is done by the launch command before this script.
cd /root/soup
export PATH=/root/venv/bin:$PATH
OUT=/root/runs/gpu; LOG=/root/runs/gpu/queue.log
mkdir -p $OUT
nvidia-smi > $OUT/nvidia-smi.txt 2>&1
python -c "import torch, numpy, scipy; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), numpy.__version__, scipy.__version__)" > $OUT/versions.txt 2>&1
run() { echo "start $* $(date -u +%H:%M:%SZ)" >> $LOG; env -i HOME=/root PATH=/root/venv/bin:/usr/bin:/bin SM_PREFIX="${SM_PREFIX:-}" python -I sm_gpu.py $OUT "$@" >> $LOG 2>&1 || echo "FAILED $*" >> $LOG; echo "done $* $(date -u +%H:%M:%SZ)" >> $LOG; }
# parity on dev net 699 at 128 x 32 (CPU results exist locally in runs_dev/)
SM_PREFIX=parity_ run lv au:699:128:32
SM_PREFIX=parity_ run arc au:699:128:32 k2,k2a
SM_PREFIX=parity_ run truth au:699:128:32 22
# the 1024 x 256 cell, nets 640-647
for s in 640 641 642 643 644 645 646 647; do net=au:$s:1024:256
  run truth $net 20; run lv $net; run arc $net k2,k2a; run rqmc $net 8,10,12,14 8
done
# extra 512 x 128 nets 634-637 (the CPU queue runs 630-633)
for s in 634 635 636 637; do net=au:$s:512:128
  run truth $net 20; run lv $net; run arc $net k2,k2a; run rqmc $net 8,10,12,13 8
done
echo "queue end $(date -u +%H:%M:%SZ)" >> $LOG
