#!/bin/bash
# Round-2 gpt-6-astra review (fresh session, read-only, high effort) of the report and its support.
cd /home/agent/workspaces/mats/work/bit-accounting
echo "r2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum bit-accounting.md FORMAL.md > review/reviewed_r2_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting "$(cat review/prompt_r2_report.md)" < /dev/null > review/review_r2.raw 2>&1
echo "r2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
