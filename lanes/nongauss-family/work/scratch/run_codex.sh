#!/bin/bash
# usage: scratch/run_codex.sh PROMPT_FILE OUT_RAW
cd /srv/agent-data/home/workspaces/mats/work/nongauss-family
codex-any exec --skip-git-repo-check -s read-only -c model_reasoning_effort='"high"' -C /srv/agent-data/home/workspaces/mats/work/nongauss-family "$(cat "$1")" < /dev/null > "$2" 2>&1
