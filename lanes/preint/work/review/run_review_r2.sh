#!/bin/bash
# gpt-6-astra review round 2 (read-only, xhigh).
cd /home/agent/workspaces/mats/work/preint
echo "review r2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/preint "$(cat review/REVIEW_PROMPT_r2.md)" < /dev/null >> review/review_r2.raw 2>&1
echo "review r2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
