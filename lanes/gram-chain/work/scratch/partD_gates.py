"""Part D (descriptive): expected number of gates that differ between two independent inputs at layer l + 1,
E[n arccos(rho_l)/pi] (exact given the Gram, then averaged over the exact chain), sigma = 0, n = 256 and 64, against the
kernel and the input-bits lane's measured medians (128, 100, 74, 51, 33, 18, 11, 5 at l = 1, 2, 4, 8, 16, 32, 64, 128
for n = 256)."""
import sys, json, math
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import numpy as np
import gc2

rng = np.random.default_rng(77)
out = {}
for n, L in ((256, 129), (64, 65)):
    P = 4000
    G = gc2.wishart_inputs(n, P, 2, rng)
    c = 0.0
    rows = []
    for l in range(0, L):
        if l > 0:
            G = gc2.step(G, n, rng, sigma=0.0)
            c = float(gc2.kappa(c))
        d = gc2.diffs(G, n, out_closed=False)
        g = n * np.arccos(np.clip(d['rho'], -1, 1)) / math.pi
        rows.append(dict(l=l, chain=float(g.mean()), chain_median=float(np.median(g)), kernel=n * math.acos(c) / math.pi))
    out[n] = rows
    print('n=%d' % n, [(r['l'], round(r['chain'], 1), round(r['kernel'], 1)) for r in rows if r['l'] in (0, 1, 2, 4, 8, 16, 32, 64, 128)])
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/partD_gates.json', 'w'), indent=1)
