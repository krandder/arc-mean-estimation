#!/usr/bin/env bash
# Launch the bit-accounting-arc GPU worker on one L4 (scripts/infra/gpu-run.sh from a detached worktree of the
# inconsistency-search repo; nothing is committed). Control root = this lane's work dir: GPU-LOG.md, infra/state (SSH
# key) and runs/ (synced back at the end) live here. Source synced to the VM: gpu_src/.
# usage: gpu_launch.sh <run-id> [timeout, default 5h]   (GPU_PROVISIONING=STANDARD for on-demand)
set -euo pipefail
RUN_ID=$1; TO=${2:-5h}
WORK=/home/agent/workspaces/mats/work/bit-accounting-arc
REPO=/home/agent/workspaces/inconsistency-search
WT=/tmp/l4runs-bitarc/$RUN_ID
mkdir -p /tmp/l4runs-bitarc
git -C "$REPO" worktree remove --force "$WT" 2>/dev/null || true
git -C "$REPO" worktree prune
git -C "$REPO" worktree add -q --detach "$WT" HEAD
SETUP='export DEBIAN_FRONTEND=noninteractive; apt-get update -q >/dev/null && apt-get install -y -q python3-venv python3-pip >/dev/null && python3 -m venv /root/venv && /root/venv/bin/pip install -q torch numpy && cd /root/soup && export PATH=/root/venv/bin:$PATH && python -c "import torch; print(torch.__version__, torch.cuda.is_available())" > /root/runs/torch_check.txt 2>&1; bash scripts/worker.sh'
GPU_STARTUP=minimal GPU_ZONES="${GPU_ZONES:-us-west1-c us-west1-b us-central1-b us-central1-c us-central1-a}" GPU_CONTROL_ROOT="$WORK" GPU_SOURCE_DIR="$WORK/gpu_src" GPU_RUN_TIMEOUT=$TO GPU_BUDGET_GROUP=bitarc \
  GPU_GROUP_BUDGET_USD=25 bash "$WT/scripts/infra/gpu-run.sh" --up --run-id "$RUN_ID" -- bash -c "$SETUP"
