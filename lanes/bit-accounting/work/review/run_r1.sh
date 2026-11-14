#!/bin/bash
# Round-1 gpt-6-astra review (fresh session, read-only, high effort) of FORMAL.md and the code.
cd /home/agent/workspaces/mats/work/bit-accounting
echo "r1 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting "$(cat review/prompt_r1_formal.md)" < /dev/null > review/review_r1.raw 2>&1
echo "r1 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
