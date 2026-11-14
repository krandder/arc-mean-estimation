#!/bin/bash
cd /home/agent/workspaces/mats/work/scale-mode
echo "check2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 1800 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/scale-mode --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/arc-update "$(cat review/prompt_check2.md)" < /dev/null >> review/check2_gpt6.raw 2>&1
echo "check2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
