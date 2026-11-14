#!/bin/bash
# Copy the canonical lib/ and scripts/*.py into gpu_src/ (rsync to the VM does not follow symlinks).
cd /home/agent/workspaces/mats/work/backward-bits
cp lib/bb.py gpu_src/lib/bb.py
cp scripts/*.py gpu_src/scripts/
sha256sum gpu_src/lib/bb.py gpu_src/scripts/*.py
