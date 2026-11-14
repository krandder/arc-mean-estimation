#!/bin/bash
# Final adversarial GPT-6 review of the cut-rank report, code and numbers (read-only sandbox, fresh session).
cd /srv/agent-data/home/workspaces/mats/work/cut-rank
echo "final start $(date -u +%H:%M:%SZ)" >> review/review_status.txt
timeout 3600 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /srv/agent-data/home/workspaces/mats/work/cut-rank --add-dir /srv/agent-data/home/workspaces/mats/outbox "$(cat review/prompt_gpt6_final.md)" < /dev/null > review/review_gpt6_final.raw 2>&1
echo "final exit $? $(date -u +%H:%M:%SZ)" >> review/review_status.txt
