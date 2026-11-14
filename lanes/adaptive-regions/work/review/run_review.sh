#!/bin/bash
# gpt-6-astra review of the draft report, theory and code (read-only sandbox, xhigh).
cd /home/agent/workspaces/mats/work/adaptive-regions
echo "review start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/adaptive-regions --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work "$(cat review/prompt_review.md)" < /dev/null >> review/astra_review.raw 2>&1
echo "review exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
