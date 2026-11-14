#!/bin/bash
# Round-3 gpt-6-astra review of the final report (fresh session, read-only, high effort).
cd /home/agent/workspaces/mats/work/bit-accounting-arc
echo "r3 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum bit-accounting-arc.md PREREG.md lib/vra.py lib/vrb.py scratch/score_P1_v3.py scratch/conv_subset.py \
  scratch/export_curves.py scratch/consistency.py > review/reviewed_r3_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting-arc "$(cat review/prompt_r3_final.md)" < /dev/null > review/review_r3.raw 2>&1
echo "r3 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
