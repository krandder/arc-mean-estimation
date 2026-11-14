#!/bin/bash
# Fresh-session adversarial review by gpt-6-astra (read-only sandbox, high effort) of the report and its support.
cd /home/agent/workspaces/mats/work/bits-bounds
echo "review start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bits-bounds --add-dir /home/agent/workspaces/mats/outbox "$(cat review/prompt_review.md)" < /dev/null > review/review_gpt6.raw 2>&1
echo "review exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
