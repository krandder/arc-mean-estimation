"""Post hoc (descriptive): the direction cloud's participation ratio by radius bin, from the A-r4 chains, against the
per-net four-point law PR_C = n theta*/pi (theta* from the exact mean-field fixed point at the bin's radius;
leading order 0.6724 n Q^{-1/3}). Binning by the replicas' geometric-mean radius is approximate conditioning."""
import json, math, sys, os
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import gc2

R = '/home/agent/workspaces/mats/work/gram-chain/runs/'
out = {}
for n in (16, 32, 64, 128, 256, 512, 1024):
    f = R + 'A_r4_n%d.npz' % n
    if not os.path.exists(f):
        continue
    z = np.load(f)
    q = z['qbar']
    num, den = 0.25 * z['x11'] * z['x22'], 0.25 * z['x12'] ** 2
    rows = []
    for lo, hi in ((0, 0.3), (0.3, 0.6), (0.6, 1.2), (1.2, 2.5), (2.5, 5), (5, 1e9)):
        m = (q >= lo) & (q < hi)
        if m.sum() < 400:
            continue
        qm = float(np.median(q[m]))
        ds = float(gc2.mf_fixed_point(qm * n)[0])
        th = math.acos(1 - ds)
        pred = n * th / math.pi
        prb = float(num[m].mean() / den[m].mean())
        rows.append(dict(lo=lo, hi=hi, count=int(m.sum()), q_median=qm, PR=prb, pred=pred, ratio=prb / pred))
    out[n] = rows
    print('n=%d ' % n + '  '.join('q~%.2f PR=%.1f pred=%.1f r=%.2f' % (r['q_median'], r['PR'], r['pred'], r['ratio']) for r in rows))
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/pr_by_radius.json', 'w'), indent=1)
