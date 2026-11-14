#!/bin/bash
# gpt-6-astra fresh-session adversarial review of the report and code (read-only sandbox, high effort).
cd /home/agent/workspaces/mats/work/randomness
echo "review start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/randomness --add-dir /home/agent/workspaces/mats/outbox "$(cat review/prompt_review.md)" < /dev/null >> review/review_gpt6.raw 2>&1
echo "review exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
