#!/bin/bash
# Round-2a gpt-6-astra review of the phase-1 method and code (fresh session, read-only, high effort).
cd /home/agent/workspaces/mats/work/bit-accounting
echo "r2a start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum PREREG.md gpu_src/scripts/run_vr.py gpu_src/scripts/score_P1.py > review/reviewed_r2a_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting "$(cat review/prompt_r2a_p1code.md)" < /dev/null > review/review_r2a.raw 2>&1
echo "r2a exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
