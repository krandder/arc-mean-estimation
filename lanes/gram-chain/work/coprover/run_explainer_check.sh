#!/bin/bash
# gpt-6-astra math check of the explainer (read-only, high effort).
cd /home/agent/workspaces/mats/work/gram-chain
echo "explainer-check start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 3600 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/gram-chain --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/stationary-numerics --add-dir /home/agent/workspaces/mats/work/input-bits "$(cat coprover/prompt_explainer_check.md)" < /dev/null > coprover/explainer_check.raw 2>&1
echo "explainer-check exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
