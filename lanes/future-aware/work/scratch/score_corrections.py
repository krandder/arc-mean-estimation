"""Scoring correction fixed in logs/deviations.txt (item 3) before any score was computed: a D1 run that returned NaN
(futv128, futmf2_128 at 256 x 32: rank-deficient whitening at k = n/2) is a failed run, reported, and excluded from
P7's "every D1 variant". The hashed scorer's output (results/score_part1.json) is kept unchanged; this writes
results/score_corrections.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_part1 as S  # noqa: E402

n, L = 256, 32
G, failed = [], []
for s in range(200, 205):
    d = S.load('k3p', n, L, s)
    if d is None:
        continue
    cur = S.rqmc_curve(n, L, s)
    for v, r in d['variants'].items():
        if not np.isfinite(r['nmse']):
            failed.append((s, v)); continue
        G.append(S.rqmc_err(cur, r['passes'])[0] / r['nmse'])
out = dict(P7_corrected=dict(n_runs=len(G), max_G=float(max(G)) if G else None, failed_runs=failed,
                             holds=(len(G) > 0 and all(g < 0.2 for g in G))))
json.dump(out, open(os.path.join(S.RES, 'score_corrections.json'), 'w'), indent=1)
print(out)
