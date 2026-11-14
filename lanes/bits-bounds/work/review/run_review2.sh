#!/bin/bash
# Focused fresh-session re-review by gpt-6-astra (read-only sandbox, high effort) of the closure test and round 3.
cd /home/agent/workspaces/mats/work/bits-bounds
echo "review2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bits-bounds --add-dir /home/agent/workspaces/mats/outbox "$(cat review/prompt_review2.md)" < /dev/null > review/review2_gpt6.raw 2>&1
echo "review2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
