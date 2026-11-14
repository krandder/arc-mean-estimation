"""Print the full-recursion summary numbers for the report (descriptive): per width, medians and ranges of the Gaussian
and radial closures' errors (Amendment 5 files at n = 64, 128; Amendment 6 files at 256 and, when present, at 64, 128),
ratios, RQMC cost to reach the radial error, RQMC nMSE at the k2 cost over it, MC gain at own cost, noise."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
SEEDS = {64: range(300, 308), 128: range(300, 308), 256: range(200, 205)}
rows = SL.score({n: list(s) for n, s in SEEDS.items()})


def rqmc_cost(cur, e):
    Ns, es = cur
    if e >= es[0]:
        return Ns[0] * es[0] / e
    if e <= es[-1]:
        return Ns[-1] * es[-1] / e
    return float(np.exp(np.interp(-np.log(e), -np.log(es), np.log(Ns))))


for tag in ('ipr', 'ipr2'):
    for n, seeds in SEEDS.items():
        L = SL.CFG[n]
        c2 = np.median([r['passes'] for (nn, s, v), r in rows.items() if nn == n and v == 'k2'])
        G, R, rat, cost, X, nz, k2a = [], [], [], [], [], [], []
        for s in seeds:
            p = os.path.join(RUNS, f'{tag}_n{n}_L{L}_s{s}.json')
            if not os.path.exists(p):
                continue
            M = json.load(open(p))['models']
            g, r = M['gauss']['b2'], M['radgauss']['b2']
            G.append(g); R.append(r); rat.append(r / g); nz.append(M['radgauss']['noise_var'])
            k2a.append(rows[(n, s, 'k2a')]['nmse'])
            cur = SL.rqmc_curve(n, L, s)
            if cur is not None and r > 0:
                cost.append(rqmc_cost(cur, r)); X.append(SL.rqmc_at(cur, c2) / r)
        if not G:
            continue
        f = lambda v: f'{np.median(v):.3g} [{min(v):.2g}, {max(v):.2g}]'  # noqa: E731
        print(f'{tag} n={n} nets={len(G)} gauss {f(G)} radial {f(R)} ratio {f(rat)} k2a(same nets) {f(k2a)}'
              f' rqmc_cost {f(cost) if cost else "-"} X {f(X) if X else "-"} MCgain(J=1) '
              f'{1 / (np.median(R) * c2):.2f} noise {f(nz)}')
