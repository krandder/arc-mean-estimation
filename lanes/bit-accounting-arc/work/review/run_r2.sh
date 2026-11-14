#!/bin/bash
# Round-2 gpt-6-astra review of the report and the analysis code (fresh session, read-only, high effort).
cd /home/agent/workspaces/mats/work/bit-accounting-arc
echo "r2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum bit-accounting-arc.md PREREG.md lib/vra.py lib/vrb.py scratch/score_P1_v2.py scratch/report_tables.py \
  scratch/export_curves.py scratch/conv_table.py scratch/c7_table.py scratch/conv_subset.py scratch/consistency.py \
  scratch/spectrum_table.py scratch/perturb_exponent.py gpu_src/scripts/run_vr.py > review/reviewed_r2_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting-arc "$(cat review/prompt_r2_report.md)" < /dev/null > review/review_r2.raw 2>&1
echo "r2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
