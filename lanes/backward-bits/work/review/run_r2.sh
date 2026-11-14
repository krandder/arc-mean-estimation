#!/bin/bash
# Round-2 gpt-6-astra review (read-only, high effort) of the report and its support.
cd /home/agent/workspaces/mats/work/backward-bits
echo "r2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum backward-bits.md FORMAL.md results/scores.json results/tables.md > review/reviewed_r2_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/backward-bits "$(cat review/prompt_r2.md)" < /dev/null > review/review_r2.raw 2>&1
echo "r2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
