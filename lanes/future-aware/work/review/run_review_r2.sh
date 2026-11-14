#!/bin/bash
# GPT-6 (gpt-6-astra) fresh-session adversarial review of the report (read-only sandbox, high effort).
cd /home/agent/workspaces/mats/work/future-aware
echo "review_r2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/future-aware --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/arc-update "$(cat review/prompt_review_r2.md)" < /dev/null >> review/review_gpt6_r2.raw 2>&1
echo "review_r2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
