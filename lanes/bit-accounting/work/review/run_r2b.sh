#!/bin/bash
# Round-2b gpt-6-astra review of the phase-1 report (fresh session, read-only, high effort).
cd /home/agent/workspaces/mats/work/bit-accounting
echo "r2b start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum bit-accounting.md PREREG.md results/P1_scores.json > review/reviewed_r2b_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting "$(cat review/prompt_r2b_report.md)" < /dev/null > review/review_r2b.raw 2>&1
echo "r2b exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
