#!/bin/bash
# gpt-6-astra co-prover, round 2: audit and lemma exchange (read-only sandbox, xhigh).
cd /home/agent/workspaces/mats/work/preint
echo "r2 start $(date -u +%H:%M:%SZ)" >> coprover/status.txt
timeout 5400 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"xhigh"' -C /home/agent/workspaces/mats/work/preint --add-dir /home/agent/workspaces/mats/outbox "You are gpt-6-astra, co-prover on the preint lane, round 2. Read coprover/STATEMENT_r2.md in this directory and answer it. Read-only sandbox; do not modify files. Write everything to stdout." < /dev/null >> coprover/astra_r2.raw 2>&1
echo "r2 exit $? $(date -u +%H:%M:%SZ)" >> coprover/status.txt
