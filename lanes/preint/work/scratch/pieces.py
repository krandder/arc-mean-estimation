"""Pieces along lines (Q1): vertices of the exact line + radius integral after each layer, full half circle and the
eps-window, for random u and yhat. Usage: pieces.py FAMILY N L SEED NLINES OUT.json [EPS]
FAMILY arc (anet stream) or nd (narrow-deep stream). Records per-layer mean/median/quantiles of vertex counts, the
cost per line in passes (counted FLOPs / 2 n^2 L) and the wall time per line."""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import line as LN  # noqa: E402
import nets  # noqa: E402


def stats(c):
    c = np.asarray(c, dtype=float)
    return dict(mean=float(c.mean()), median=float(np.median(c)), q10=float(np.quantile(c, 0.1)),
                q90=float(np.quantile(c, 0.9)))


def main():
    fam, n, L, seed, m, outp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), \
        sys.argv[6]
    eps = float(sys.argv[7]) if len(sys.argv) > 7 else 1e-8
    Ws = nets.arc_weights(seed, n, L) if fam == 'arc' else nets.nd_weights(seed, n, L)
    d = n
    rng = np.random.default_rng([4242, seed, n, L])
    wt = LN.Weight('student', d - 1)
    res = dict(family=fam, n=n, L=L, seed=seed, lines=m, eps=eps, s0=wt.window(eps),
               psi0=math.atan(wt.window(eps)), modes={})
    for mode in ('full', 'window'):
        if mode == 'window' and d < 16:
            continue
        cnts, costs, times = [], [], []
        for i in range(m):
            u = rng.standard_normal(d)
            u /= np.linalg.norm(u)
            B = LN.orth_basis(u)
            Y = LN.bases_from_uniform(rng.random((1, d - 1)), B)
            t0 = time.time()
            if mode == 'full':
                I, fl, cnt = LN.line_integrals(Ws, Y, u, wt)
            else:
                I, fl, cnt = LN.line_integrals(Ws, Y, u, wt, eps=eps, rng=rng)
            times.append(time.time() - t0)
            cnts.append(cnt[0])
            costs.append(fl[0] / nets.pass_flops(n, L))
        cnts = np.array(cnts)
        res['modes'][mode] = dict(
            per_layer=[stats(cnts[:, l]) for l in range(L + 1)],
            cost_passes=stats(costs), sec_per_line=stats(times),
            mean_vertices_over_layers=stats(cnts[:, :-1].mean(1)))
        print(fam, n, L, seed, mode, 'final vertices median %.0f mean %.1f; cost/line %.1f passes; %.3f s/line' % (
            np.median(cnts[:, -1]), cnts[:, -1].mean(), np.mean(costs), np.mean(times)), flush=True)
    json.dump(res, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
