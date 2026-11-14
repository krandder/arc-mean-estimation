#!/bin/bash
# Score the scored run, build the report tables and figures. usage: finalize.sh [root, default runs_gpu/scored3]
cd /home/agent/workspaces/mats/work/backward-bits
ROOT=${1:-runs_gpu/scored3}
PY=/home/agent/.venvs/arc-noisy/bin/python
$PY scripts/score.py $ROOT results > results/score_stdout.txt 2>&1 || { echo "score failed"; tail -n 20 results/score_stdout.txt; exit 1; }
$PY scripts/report_tables.py $ROOT results/scores.json results/tables.md
$PY scripts/figs.py $ROOT results/scores.json figs
$PY scripts/figs_exact.py results/exact_chain_1d_rho0.999_L16_K32.json results/exact_chain_1d_prsweep_rho0.999_L16_K32.json figs/exact_chain_1d.png
sha256sum scripts/score.py results/scores.json > results/scored_hashes.txt
echo "finalized $(date -u +%FT%TZ)"
