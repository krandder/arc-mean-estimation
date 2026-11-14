#!/bin/bash
# Scan a tree for secrets before every commit. Usage: secret_scan.sh DIR. Exit 1 if any strong hit.
D="${1:-.}"
STRONG='(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[0-9]{8,10}:AA[A-Za-z0-9_-]{30,}|rpa_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35}|eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}|https?://[^/ :@"]+:[^/ @"]+@|ya29\.[A-Za-z0-9_-]{20,}|tvly-[A-Za-z0-9]{20,}|wandb_v1_[A-Za-z0-9]+|glpat-[A-Za-z0-9_-]{20,})'
WEAK='((api[_-]?key|apikey|secret|passwd|password|token|bearer|authorization)["'"'"']?[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_/+.-]{16,}|(RUNPOD|WANDB|OPENAI|ANTHROPIC|EXA|HF|GEMINI|GOOGLE|AWS|TELEGRAM|METACULUS|VAST|LAMBDA)_[A-Z_]*(KEY|TOKEN|SECRET)[[:space:]]*=[[:space:]]*[^[:space:]$]{8,})'
echo "## strong"
nice -n 19 grep -rIEn --exclude-dir=.git -e "$STRONG" "$D" | cut -c1-240
echo "## weak"
nice -n 19 grep -rIEin --exclude-dir=.git -e "$WEAK" "$D" | cut -c1-240
echo "## secret-like file names"
find "$D" -path "$D/.git" -prune -o -type f \( -name '.env*' -o -name '*.pem' -o -name '*.key' -o -name 'id_rsa*' -o -name '*ed25519*' -o -name '*.pub' -o -name 'credentials*' -o -name '*.token' -o -name '.netrc' -o -name '*.p12' \) -print
