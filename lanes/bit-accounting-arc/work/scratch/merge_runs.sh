#!/bin/bash
# Merged, deduplicated copy of every finished result (newest file of each name wins) for the registered scorer, which
# loads recursively: results/merged/P1 (VR_*.json) and results/merged/P1/REF (REF_*.json). usage: merge_runs.sh
cd /home/agent/workspaces/mats/work/bit-accounting-arc
M=results/merged/P1
mkdir -p $M/REF
for f in $(ls -t runs/bitarc-*/P1/VR_*.json runs/P1/VR_*.json 2>/dev/null); do
  [ -e $M/$(basename $f) ] && [ ! $f -nt $M/$(basename $f) ] && continue
  cp -p $f $M/
done
for f in $(ls -t runs/bitarc-*/P1/REF/REF_*.json runs/P1/REF/REF_*.json 2>/dev/null); do
  [ -e $M/REF/$(basename $f) ] && [ ! $f -nt $M/REF/$(basename $f) ] && continue
  cp -p $f $M/REF/
done
echo "merged: $(ls $M/VR_*.json | wc -l) runs, $(ls $M/REF/REF_*.json | wc -l) refs"
