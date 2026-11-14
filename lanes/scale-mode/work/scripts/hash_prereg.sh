#!/bin/bash
# Freeze and hash the registration: PREREG.md, the lane's code and the two third-party files that run.
cd /home/agent/workspaces/mats/work/scale-mode
TAG=${1:-part1}
mkdir -p frozen/$TAG
FILES="PREREG.md scripts/smlib.py scripts/run_cell.py scripts/score.py scripts/score_predictions.py scripts/iso.sh scripts/evalq_A.sh scripts/evalq_B.sh thirdparty/scale-separation/estimator/lvlib.py thirdparty/scale-separation/arc_ladder/descale_fac_src.py"
for f in $FILES; do cp $f frozen/$TAG/; done
{ echo "# $TAG hashed $(date -u +%Y-%m-%dT%H:%M:%SZ) (thirdparty HEAD $(git -C thirdparty/scale-separation rev-parse HEAD))"; sha256sum $FILES; } >> prereg_hashes.txt
tail -12 prereg_hashes.txt
