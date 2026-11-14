#!/bin/bash
# gpt-6-astra short check of the revised report (read-only sandbox, high effort).
cd /home/agent/workspaces/mats/work/arc-update
echo "check2 start $(date -u +%H:%M:%SZ)" >> review/status.txt
timeout 2400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/arc-update "$(cat review/prompt_check2.md)" < /dev/null >> review/check2_gpt6.raw 2>&1
echo "check2 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
