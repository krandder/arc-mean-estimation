#!/usr/bin/env bash
# Launch the scale-mode GPU queue on one spot L4 through the fleet's gpu-run.sh (inconsistency-search scripts/infra, run
# from a detached worktree; nothing committed). Control root = this lane's work dir (GPU-LOG.md, infra/state, runs/ synced
# back). Source synced to the VM: gpu_src/ (copies of the needed code: anet, kprop_noisy, ARC's mlp_kprop, the two audited
# third-party files, sm_gpu.py, run.sh). Budget group scalemode capped at $3. The VM is deleted when the command ends.
# usage: gpu_launch.sh <run-id> [timeout, default 2h]
set -euo pipefail
RUN_ID=$1; TO=${2:-2h}
WORK=/home/agent/workspaces/mats/work/scale-mode
REPO=/home/agent/workspaces/inconsistency-search
WT=/tmp/l4runs/$RUN_ID
mkdir -p /tmp/l4runs
git -C "$REPO" worktree remove --force "$WT" 2>/dev/null || true
git -C "$REPO" worktree prune
git -C "$REPO" worktree add -q --detach "$WT" HEAD
SETUP='export DEBIAN_FRONTEND=noninteractive; apt-get update -q >/dev/null && apt-get install -y -q python3-venv python3-pip >/dev/null && python3 -m venv /root/venv && /root/venv/bin/pip install -q torch==2.14.1 numpy==2.5.4 scipy==1.18.1 jaxtyping==0.3.11 einops==0.8.2 tqdm==4.70.1 joblib==1.6.0 opt_einsum==3.4.0 > /root/runs/pip.log 2>&1; mkdir -p /root/runs/gpu; cd /root/soup && bash run.sh'
GPU_STARTUP=minimal GPU_ZONES="${GPU_ZONES:-us-west1-c us-central1-b us-central1-c us-west1-b}" GPU_CONTROL_ROOT="$WORK" GPU_SOURCE_DIR="$WORK/gpu_src" GPU_RUN_TIMEOUT=$TO GPU_BUDGET_GROUP=scalemode \
  GPU_GROUP_BUDGET_USD=3 bash "$WT/scripts/infra/gpu-run.sh" --up --run-id "$RUN_ID" -- bash -c "$SETUP"
