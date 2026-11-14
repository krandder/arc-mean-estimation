#!/bin/bash
# Run a python script of this lane in isolation: no secrets in the environment (env -i), python -I, nice 19, ionice -c3.
# usage: iso.sh THREADS script.py args...
T=$1; shift
exec env -i HOME=/tmp/sm_home PATH=/usr/bin:/bin OMP_NUM_THREADS=$T MKL_NUM_THREADS=$T OPENBLAS_NUM_THREADS=$T AU_THREADS=$T \
  nice -n 19 ionice -c3 /home/agent/.venvs/arc-noisy/bin/python -I "$@"
