"""How many activation regions (layers 1..c) does a random line through the input cross? This sets the cost of exact
pre-integration along lines. Lines x(t) = z + t e, e a random unit vector, z ~ N(0, I) projected orthogonal to e,
t on a grid of G points in [-4, 4]; counts pattern changes between consecutive grid points (a lower bound on the
number of crossings within |t| <= 4). Usage: line_crossings.py SEED C NLINES G"""
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

seed, c, nl, G = (int(v) for v in sys.argv[1:5])
Ws = ndx.make_weights(seed)
rng = np.random.default_rng([31, seed])
t = np.linspace(-4, 4, G)
w = np.exp(-0.5 * t * t)
counts, wcounts = [], []
for _ in range(nl):
    e = rng.standard_normal(8)
    e /= np.linalg.norm(e)
    z = rng.standard_normal(8)
    z -= (z @ e) * e
    X = z[None, :] + t[:, None] * e[None, :]
    _, pat = ndx.fwd_patterns(Ws, X, 0, c)
    ch = np.any(pat[1:] != pat[:-1], axis=1)
    counts.append(int(ch.sum()))
    wcounts.append(float((ch * w[1:]).sum() / w.sum() * G))
counts = np.array(counts)
print(seed, 'c', c, 'lines', nl, 'grid', G, 'crossings in |t|<=4: median %d mean %.1f q10 %d q90 %d' % (
    np.median(counts), counts.mean(), np.quantile(counts, 0.1), np.quantile(counts, 0.9)), flush=True)
