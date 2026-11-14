#!/bin/bash
# gpt-6-astra co-prover, round 4: the radius-corrected closure as a full recursion (read-only sandbox, xhigh effort).
cd /home/agent/workspaces/mats/work/arc-update
echo "r4 start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/arc-update --add-dir /home/agent/workspaces/mats/outbox --add-dir /home/agent/workspaces/mats/work/cut-rank-ext/notes --add-dir /home/agent/workspaces/mats/work/arc-noisy/ext --add-dir /home/agent/workspaces/mats/work/bits-bounds "$(cat coprover/prompt_r4.md)" < /dev/null >> coprover/astra_r4.raw 2>&1
echo "r4 exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
