#!/bin/bash
# scheduler: at most 2 heavy processes. MEASURED (exploratory) runs.
cd /home/agent/workspaces/mats/work/moment-matching
PY=/home/agent/.venvs/arc-noisy/bin/python
run() { OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 19 ionice -c3 $PY cg.py "$@"; }
slotA() {  # n=6 after d=4 -> n=8 d=2,3,4 -> n=6 d=6
  until grep -q "n=6 d=5 M=462" runs/cg_n6.log; do sleep 30; done
  kill $(cat runs/cg_n6.pid)
  run --n 8 --d 2 3 4 --rounds 100 --rtol 0.05 --out runs/cg_n8.jsonl > runs/cg_n8.log 2>&1
  run --n 6 --d 6 --rounds 100 --rtol 0.05 --out runs/cg_n6.jsonl > runs/cg_n6_d6.log 2>&1
}
slotB() {  # n=4 after d=6 -> n=4 d=8 -> finite-sample check -> n=4 d=7
  until grep -q "n=4 d=7 M=330" runs/cg_n4.log; do sleep 30; done
  kill $(cat runs/cg_n4.pid)
  run --n 4 --d 8 --rounds 100 --rtol 0.05 --out runs/cg_n4.jsonl > runs/cg_n4_d8.log 2>&1
  OMP_NUM_THREADS=1 nice -n 19 ionice -c3 $PY fs.py > runs/fs.log 2>&1
  run --n 4 --d 7 --rounds 100 --rtol 0.05 --out runs/cg_n4.jsonl > runs/cg_n4_d7.log 2>&1
}
slotA & slotB & wait
