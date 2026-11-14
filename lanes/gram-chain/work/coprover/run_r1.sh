#!/bin/bash
# gpt-6-astra co-prover, round 1: independent attempt from the questions alone (read-only, xhigh). Must not read work/gram-chain/.
cd /home/agent/workspaces/mats
echo "r1 start $(date -u +%H:%M:%SZ)" >> /home/agent/workspaces/mats/work/gram-chain/coprover/status.txt
timeout 5400 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats --add-dir /home/agent/workspaces/mats/outbox "$(cat /home/agent/workspaces/mats/work/gram-chain/coprover/prompt_r1.md)" < /dev/null > /home/agent/workspaces/mats/work/gram-chain/coprover/astra_r1.raw 2>&1
echo "r1 exit $? $(date -u +%H:%M:%SZ)" >> /home/agent/workspaces/mats/work/gram-chain/coprover/status.txt
