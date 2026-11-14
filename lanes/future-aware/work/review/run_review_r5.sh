#!/bin/bash
# GPT-6 (gpt-6-astra) fresh-session review, round 5 (verification of additions; read-only sandbox, high effort).
cd /home/agent/workspaces/mats/work/future-aware
sha256sum future-aware.md > review/report_sha_at_review_r5.txt
echo "review_r5 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/future-aware --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/arc-update "$(cat review/prompt_review_r5.md)" < /dev/null >> review/review_gpt6_r5.raw 2>&1
echo "review_r5 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
