#!/bin/bash
# Round-1 gpt-6-astra review (read-only, high effort) of FORMAL, PREREG and the code, while the scored runs proceed.
cd /home/agent/workspaces/mats/work/backward-bits
echo "r1 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum FORMAL.md PREREG.md notes/DEVIATIONS.md lib/bb.py scripts/*.py > review/reviewed_r1_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/backward-bits "$(cat review/prompt_r1.md)" < /dev/null > review/review_r1.raw 2>&1
echo "r1 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
