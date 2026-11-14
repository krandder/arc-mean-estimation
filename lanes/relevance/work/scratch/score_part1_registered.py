"""Runs the registered Part 1 scorer (scratch/score_part1.py, unchanged, sha e8d686ca) on the registered Part 1 nets
only. Its glob runs/eval_*.json predates the Amendment 3A/3B nets (ARC seeds 4004-4009), which are not part of Part 1;
this wrapper hides them from the glob and changes nothing else (disclosed in logs/deviations.txt)."""
import glob
import re
import sys

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')

_orig = glob.glob
PART1_ARC = {4000, 4001, 4002, 4003}


def _filtered(pattern, *a, **k):
    out = []
    for f in _orig(pattern, *a, **k):
        m = re.search(r'eval_arc_n256_L32_seed(\d+)\.json$', f)
        if m and int(m.group(1)) not in PART1_ARC:
            continue
        out.append(f)
    return out


glob.glob = _filtered
import score_part1  # noqa: E402

if __name__ == '__main__':
    score_part1.main()
