#!/bin/bash
cd /home/agent/workspaces/mats/work/preint
echo "review r3 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/preint "$(cat review/REVIEW_PROMPT_r3.md)" < /dev/null >> review/review_r3.raw 2>&1
echo "review r3 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
