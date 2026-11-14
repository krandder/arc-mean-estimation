"""The backward recursion solved exactly on a 1-D Gaussian chain (no training, no Monte Carlo).
h_0 ~ N(0, 1); h_l = rho h_{l-1} + s xi_l (s^2 = 1 - rho^2, l = 1..L-1); output h_L = h_{L-1}; output code c_L = Lloyd-Max
quantiser of N(0, 1) with K_L cells (k-means on the quadrature grid, to convergence).
Codes are interval partitions of h_l on a quadrature grid. For an interval code with cuts t, the posterior one noisy layer
earlier is exact: P(c = k | h) = Phi((t_{k+1} - rho h)/s) - Phi((t_k - rho h)/s); over m noisy layers rho^m and
s_m^2 = 1 - rho^(2m). Candidate codes at each step: the optimal interval partition for every cell count (dynamic
programming on the relevance loss) and the entropy-penalised optimum for a grid of penalties (dynamic programming on
loss + lambda * rate, which is additive over cells). Chains K, R, P, PR as in FORMAL section 7 (tolH 0.02, rho_rel 0.05).
Truth I(h_l; c_L), each code's I(c_l; c_L) and the chain's own prediction of c_L (product of kernels) are exact.
usage: exact_chain_1d.py --rho 0.98 --L 16 --KL 32 [--fig]
"""
import argparse
import json
import math
import os

import numpy as np
from scipy.special import ndtr

ap = argparse.ArgumentParser()
ap.add_argument('--rho', type=float, default=0.98)
ap.add_argument('--L', type=int, default=16)
ap.add_argument('--KL', type=int, default=32)
ap.add_argument('--G', type=int, default=801)
ap.add_argument('--Kmax', type=int, default=96)
ap.add_argument('--fig', action='store_true')
ap.add_argument('--rels', default='0.95', help='relevance thresholds for chain PR (comma list); the first is the main one')
ap.add_argument('--only_pr', action='store_true')
args = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..')
rho, L = args.rho, args.L
s = math.sqrt(1 - rho * rho)
x = np.linspace(-6, 6, args.G)
w = np.exp(-x ** 2 / 2)
w /= w.sum()


def H(p):
    return -(p * np.log2(np.clip(p, 1e-300, 1))).sum(-1)


# output code: Lloyd-Max on the grid
c = np.quantile(np.random.default_rng(0).standard_normal(200000), (np.arange(args.KL) + 0.5) / args.KL)
for it in range(2000):
    cuts = (c[1:] + c[:-1]) / 2
    a = np.searchsorted(cuts, x)
    cn = np.array([(w[a == k] * x[a == k]).sum() / max(w[a == k].sum(), 1e-300) for k in range(args.KL)])
    if np.abs(cn - c).max() < 1e-12:
        break
    c = cn
out_cuts = (c[1:] + c[:-1]) / 2
dist = float((w * (x - c[np.searchsorted(out_cuts, x)]) ** 2).sum())


def post_cuts(cuts, m):
    """P(code | h_l = x) for an interval code with cuts, m noisy layers later (m = 0: deterministic)."""
    t = np.concatenate([[-np.inf], cuts, [np.inf]])
    if m == 0:
        P = np.zeros((len(x), len(t) - 1))
        P[np.arange(len(x)), np.searchsorted(cuts, x)] = 1.0
        return P
    rm, sm = rho ** m, math.sqrt(1 - rho ** (2 * m))
    return np.clip(np.diff(ndtr((t[None, :] - rm * x[:, None]) / sm), axis=1), 0, 1)


def info(P):
    return float(H((w[:, None] * P).sum(0)[None])[0] - (w * H(P)).sum())


def code_stats(bounds, P):
    """bounds: list of (a, b) grid index ranges (cells). Returns rate, relevance, cell table, assignment."""
    asg = np.zeros(len(x), int)
    tab, pk = [], []
    for k, (a, b) in enumerate(bounds):
        asg[a:b] = k
        n = w[a:b].sum()
        pk.append(n)
        tab.append((w[a:b, None] * P[a:b]).sum(0) / max(n, 1e-300))
    pk = np.array(pk)
    tab = np.array(tab)
    Hc = float(H(pk[pk > 0][None])[0])
    I = float(H((w[:, None] * P).sum(0)[None])[0] - (pk * H(tab)).sum())
    return Hc, I, tab, asg


def candidates(P):
    """Optimal interval partitions: every cell count (fixed-K DP) and entropy-penalised optima (Lagrangian DP)."""
    G = len(x)
    cs = np.vstack([np.zeros((1, P.shape[1])), np.cumsum(w[:, None] * P, 0)])
    cw = np.concatenate([[0.0], np.cumsum(w)])
    plp = np.concatenate([[0.0], np.cumsum(w * (P * np.log2(np.clip(P, 1e-300, 1))).sum(1))])

    def cost_row(b):
        a = np.arange(b)
        n = cw[b] - cw[a]
        mu = (cs[b][None, :] - cs[a]) / np.maximum(n, 1e-300)[:, None]
        return (plp[b] - plp[a]) - n * (mu * np.log2(np.clip(mu, 1e-300, 1))).sum(1), n

    rows = [None] + [cost_row(b) for b in range(1, G + 1)]
    out = []
    Kmax = args.Kmax
    D = np.full((Kmax + 1, G + 1), np.inf)
    A = np.zeros((Kmax + 1, G + 1), int)
    D[0, 0] = 0.0
    for k in range(1, Kmax + 1):
        for b in range(1, G + 1):
            v = D[k - 1, :b] + rows[b][0]
            j = int(np.argmin(v))
            D[k, b], A[k, b] = v[j], j
        bounds, b = [], G
        for kk in range(k, 0, -1):
            a = A[kk, b]
            bounds.append((a, b))
            b = a
        out.append(sorted(bounds))
    for lam in np.concatenate([np.geomspace(1e-3, 3, 40)]):
        E = np.full(G + 1, np.inf)
        Ab = np.zeros(G + 1, int)
        E[0] = 0.0
        for b in range(1, G + 1):
            cst, n = rows[b]
            v = E[:b] + cst - lam * n * np.log2(np.maximum(n, 1e-300))
            j = int(np.argmin(v))
            E[b], Ab[b] = v[j], j
        bounds, b = [], G
        while b > 0:
            a = Ab[b]
            bounds.append((a, b))
            b = a
        out.append(sorted(bounds))
    # every 2-cell code (one cut anywhere): the low-rate end, which the penalised DP skips
    for a_ in range(1, G):
        out.append([(0, a_), (a_, G)])
    # cell-count-limited penalised DP (3-6 cells): unbalanced few-cell codes
    for lam in np.geomspace(1e-3, 3, 25):
        Dk = np.full((7, G + 1), np.inf)
        Ak = np.zeros((7, G + 1), int)
        Dk[0, 0] = 0.0
        for k in range(1, 7):
            for b in range(1, G + 1):
                cst, n = rows[b]
                v = Dk[k - 1, :b] + cst - lam * n * np.log2(np.maximum(n, 1e-300))
                j = int(np.argmin(v))
                Dk[k, b], Ak[k, b] = v[j], j
            if k >= 3:
                bounds, b = [], G
                for kk in range(k, 0, -1):
                    a_ = Ak[kk, b]
                    bounds.append((a_, b))
                    b = a_
                out.append(sorted(bounds))
    return out


def cuts_of(bounds):
    return np.array([(x[a - 1] + x[a]) / 2 for a, b in bounds[1:]])


def run_chain(kind, rel=0.95):
    target_out = kind in ('P', 'PR')
    rel_rule = kind in ('R', 'PR')
    steps = {}
    cuts_next = out_cuts                       # code at L-1 = output code
    Q_next = np.eye(args.KL)                   # P(c_L | c_{L-1})
    kernels = {}
    for l in range(L - 2, -1, -1):
        P = post_cuts(cuts_next, 1)
        if target_out:
            P = P @ Q_next
        T = info(P)
        best = None
        cands = []
        for bounds in candidates(P):
            Hc, I, tab, asg = code_stats(bounds, P)
            cands.append((Hc, I, bounds, tab))
        # reuse: the next code composed with the noise-free layer (cuts / rho)
        reuse_cuts = cuts_next / rho
        Pr = post_cuts(reuse_cuts, 0)
        bounds_r = []
        a = 0
        asg = np.searchsorted(reuse_cuts, x)
        for k in range(len(reuse_cuts) + 1):
            idx = np.where(asg == k)[0]
            if len(idx):
                bounds_r.append((idx[0], idx[-1] + 1))
        Hr, Ir, tabr, _ = code_stats(bounds_r, P)
        cands.append((Hr, Ir, bounds_r, tabr))
        if not rel_rule:
            ok = [c_ for c_ in cands if c_[0] <= T + 0.02]
            best = max(ok, key=lambda c_: c_[1])
        else:
            ok = [c_ for c_ in cands if c_[1] >= rel * T]
            best = min(ok, key=lambda c_: c_[0]) if ok else max(cands, key=lambda c_: c_[1])
        Hc, I, bounds, tab = best
        steps[l] = dict(T=T, H=Hc, I=I, K=len(bounds), reuse_H=Hr, reuse_I=Ir, reached=bool(ok),
                        curve=sorted([(round(c_[0], 4), round(c_[1], 4)) for c_ in cands]))
        kernels[l] = tab
        cuts_next = cuts_of(bounds)
        Q_next = tab if target_out else None
        steps[l]['cuts'] = cuts_next.tolist()
    return steps, kernels


res = dict(rho=rho, L=L, KL=args.KL, output_nmse=dist, H_cL=info(post_cuts(out_cuts, 0)), chains={})
truth = {}
for l in range(L):
    truth[l] = info(post_cuts(out_cuts, L - 1 - l))
res['truth'] = truth
rels = [float(r) for r in args.rels.split(',')]
kinds = [('PR', r) for r in rels] if args.only_pr else [('K', 0.95), ('R', rels[0]), ('P', 0.95)] + [('PR', r) for r in rels]
for kind0, rel in kinds:
    kind = kind0 if (kind0 != 'PR' or rel == rels[0]) else f'PR{rel:g}'
    steps, kernels = run_chain(kind0, rel)
    for l, st in steps.items():
        # the code's information about c_L (best decoder) and the chain's own prediction
        Pt = post_cuts(out_cuts, L - 1 - l)
        cuts = np.array(st['cuts'])
        asg = np.searchsorted(cuts, x)
        K = len(cuts) + 1
        pk = np.array([w[asg == k].sum() for k in range(K)])
        tabo = np.array([(w[asg == k, None] * Pt[asg == k]).sum(0) / max(pk[k], 1e-300) for k in range(K)])
        st['I_out'] = float(H((w[:, None] * Pt).sum(0)[None])[0] - (pk * H(tabo)).sum())
        if kind0 in ('K', 'R'):
            M = kernels[l]
            for k in range(l + 1, L - 1):
                M = M @ kernels[k]
        else:
            M = kernels[l]
        q = M[asg]
        st['I_chain'] = float(H((w[:, None] * Pt).sum(0)[None])[0] + (w[:, None] * Pt * np.log2(np.clip(q, 1e-300, 1))).sum())
        st['I_star'] = truth[l]
    res['chains'][kind] = {str(l): {k: v for k, v in st.items() if k not in ('cuts', 'curve')} for l, st in steps.items()}
    res['chains'][kind + '_curves'] = {str(l): st['curve'] for l, st in steps.items() if l in (L - 2, 0)}
if args.only_pr:
    os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)
    json.dump(res, open(os.path.join(OUT, 'results', f'exact_chain_1d_prsweep_rho{rho:g}_L{L}_K{args.KL}.json'), 'w'), indent=1)
    names = list(res['chains'].keys())
    names = [n for n in names if not n.endswith('_curves')]
    print(f"rho {rho}: chain PR at relevance thresholds {args.rels}; per layer: truth | (target, rate, knows) per threshold")
    for l in range(L - 2, -1, -1):
        print(f"{l:2d} | {truth[l]:.3f} | " + ' | '.join(f"{n}: {res['chains'][n][str(l)]['T']:.3f} {res['chains'][n][str(l)]['H']:.3f} "
                                                      f"{res['chains'][n][str(l)]['I_out']:.3f}" for n in names))
    raise SystemExit(0)
# direct codes: the best interval partitions on the exact posterior of the output code at each layer
res['direct'] = {}
for l in range(L - 2, -1, -1):
    Pt = post_cuts(out_cuts, L - 1 - l)
    cands = [code_stats(bounds, Pt)[:2] for bounds in candidates(Pt)]
    d = {}
    for kind in ('K', 'PR'):
        R = res['chains'][kind][str(l)]['H']
        ok = [c_ for c_ in cands if c_[0] <= R + 0.02]
        d[f'at_rate_{kind}'] = dict(H=max(ok, key=lambda c_: c_[1])[0], I=max(c_[1] for c_ in ok)) if ok else None
    ok = [c_ for c_ in cands if c_[0] <= truth[l] + 0.02]
    d['at_rate_truth'] = dict(H=max(ok, key=lambda c_: c_[1])[0], I=max(c_[1] for c_ in ok)) if ok else None
    ok = [c_ for c_ in cands if c_[1] >= 0.95 * truth[l]]
    d['rate_for_95'] = min(c_[0] for c_ in ok) if ok else None
    res['direct'][str(l)] = d
os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)
tag = f'rho{rho:g}_L{L}_K{args.KL}_G{args.G}'
json.dump(res, open(os.path.join(OUT, 'results', f'exact_chain_1d_{tag}.json'), 'w'), indent=1)
print(f"rho {rho} (s {s:.3f}), L {L}, output code K {args.KL}: nMSE {dist:.4f}, H(c_L) {res['H_cL']:.3f}")
print(' l | truth | K: T H I I_out I_chain | R: T H I_out | P: T H I_out | PR: T H I_out I_chain')
for l in range(L - 2, -1, -1):
    k, r, p, pr = (res['chains'][c_][str(l)] for c_ in ('K', 'R', 'P', 'PR'))
    print(f"{l:2d} | {truth[l]:.3f} | {k['T']:.3f} {k['H']:.3f} {k['I']:.3f} {k['I_out']:.3f} {k['I_chain']:.3f} | "
          f"{r['T']:.3f} {r['H']:.3f} {r['I_out']:.3f} | {p['T']:.3f} {p['H']:.3f} {p['I_out']:.3f} | "
          f"{pr['T']:.3f} {pr['H']:.3f} {pr['I_out']:.3f} {pr['I_chain']:.3f}")
print(' l | direct: I at rate I* | I at PR rate | rate for 95% of I*')
for l in range(L - 2, -1, -1):
    d = res['direct'][str(l)]
    print(f"{l:2d} | {d['at_rate_truth']['I']:.3f} (H {d['at_rate_truth']['H']:.3f}) | "
          f"{d['at_rate_PR']['I'] if d['at_rate_PR'] else float('nan'):.3f} | {d['rate_for_95']:.3f}")
