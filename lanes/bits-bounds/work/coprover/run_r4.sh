#!/bin/bash
# gpt-6-astra co-prover, round 4: the bits at layer l (variance profile, cell lower bound, effective dimension) (read-only sandbox, xhigh effort).
cd /home/agent/workspaces/mats/work/bits-bounds
echo "r4 start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/bits-bounds --add-dir /home/agent/workspaces/mats/outbox "$(cat coprover/prompt_r4.md)" < /dev/null > coprover/astra_r4.raw 2>&1
echo "r4 exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
