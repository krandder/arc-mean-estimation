#!/bin/bash
# GPT-6 review round 3 (fresh session, high effort, read-only) of the relevance-accounting document.
cd /home/agent/workspaces/mats/work/relevance
echo "review r3 start $(date -u +%H:%M:%SZ)" >> review/review_status.txt
timeout 3600 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/relevance --add-dir /home/agent/workspaces/mats/outbox "$(cat review/prompt_gpt6_r3.md)" < /dev/null > review/review_gpt6_r3.raw 2>&1
echo "review r3 exit $? $(date -u +%H:%M:%SZ)" >> review/review_status.txt
