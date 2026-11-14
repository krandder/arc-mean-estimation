#!/bin/bash
# Round-1 gpt-6-astra review of the phase-1 method and code (fresh session, read-only, high effort), during the runs.
cd /home/agent/workspaces/mats/work/bit-accounting-arc
echo "r1 start $(date -u +%H:%M:%SZ)" >> review/status.txt
sha256sum PREREG.md gpu_src/lib/vrlib.py gpu_src/scripts/run_vr.py gpu_src/scripts/ref_curve.py scratch/score_P1.py lib/vra.py > review/reviewed_r1_hashes.txt
timeout 3600 nice -n 19 codex-any exec --skip-git-repo-check -s read-only -m gpt-6-astra -c model_reasoning_effort='"high"' -C /home/agent/workspaces/mats/work/bit-accounting-arc "$(cat review/prompt_r1_code.md)" < /dev/null > review/review_r1.raw 2>&1
echo "r1 exit $? $(date -u +%H:%M:%SZ)" >> review/status.txt
