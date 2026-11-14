#!/bin/bash
# Run the commands in a jobs file (one per line) with P parallel workers; log per job; skip lines starting with #.
# usage: pool.sh <jobs-file> <P> <logdir>      (v2 14:22Z: the exit code is captured before the log line is written)
JOBS=$1; P=$2; LOGD=$3
mkdir -p $LOGD
grep -v '^#' "$JOBS" | grep -v '^$' | awk '{print NR "\t" $0}' | xargs -P "$P" -d '\n' -I{} bash -c 'n=$(echo "{}" | cut -f1); cmd=$(echo "{}" | cut -f2-); echo "$(date -u +%FT%TZ) start $n: $cmd" >> '"$LOGD"'/pool.log; eval "$cmd" > '"$LOGD"'/job_$(basename '"$JOBS"' .txt)_$n.log 2>&1; rc=$?; echo "$(date -u +%FT%TZ) end $n rc=$rc" >> '"$LOGD"'/pool.log'
