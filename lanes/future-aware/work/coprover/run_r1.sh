#!/bin/bash
# gpt-6-astra co-prover, round 1 (independent; read-only sandbox, xhigh effort).
cd /home/agent/workspaces/mats/work/future-aware
echo "r1 start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/future-aware --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/arc-update --add-dir /home/agent/workspaces/mats/work/relevance "$(cat coprover/prompt_r1.md)" < /dev/null >> coprover/astra_r1.raw 2>&1
echo "r1 exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
