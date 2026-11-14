"""Known-answer tests for lib/bb.py (CPU). Run: python tests/test_bb.py
1. W_layer equals the stationary lane's st.W_layer.
2. 1-D exact case: h ~ N(0, 1), next code c = Q(h + sigma xi) with a uniform K-level quantiser on [-2, 2]. The posterior
   is exact (normal CDF differences), T = I(h; c) by quadrature. Monte Carlo + Miller-Madow must match.
3. Optimal K'-cell interval partition of h for c by dynamic programming (exact posteriors on a sample); the DIB /
   KL-k-means solution must match it (or beat it, which would mean a non-interval optimum).
4. End to end: predictor trained on Monte Carlo labels + DIB, relevance measured on held-out points with fresh draws,
   against the DP optimum at the same number of cells.
5. relevance() on a toy with a known answer; kmeans on separated clusters.
"""
import math
import os
import sys
import time

import numpy as np
import torch
from scipy.special import ndtr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
import bb  # noqa: E402

torch.set_num_threads(4)
RESULTS = []


def check(name, ok, msg):
    RESULTS.append((name, bool(ok), msg))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}", flush=True)


class Quant1D:
    def __init__(self, K, lo=-2.0, hi=2.0):
        self.K = K
        self.t = torch.linspace(lo, hi, K + 1)[1:-1]

    def assign(self, z):
        return torch.bucketize(z[:, 0].contiguous(), self.t)


class Net1D:
    def __init__(self, sigma):
        self.sigma = sigma
        self.L = 10

    def pre(self, h, l):
        return h

    def noisy(self, l):
        return True


def exact_post(h, K, sigma, lo=-2.0, hi=2.0):
    t = np.concatenate([[-np.inf], np.linspace(lo, hi, K + 1)[1:-1], [np.inf]])
    cdf = ndtr((t[None, :] - h[:, None]) / sigma)
    return np.clip(np.diff(cdf, axis=1), 0, 1)


def exact_T(K, sigma):
    x, w = np.polynomial.hermite_e.hermegauss(200)
    w = w / w.sum()
    P = exact_post(x, K, sigma)
    H = lambda p: -(p * np.log2(np.clip(p, 1e-300, 1))).sum(-1)
    return float(H((w[:, None] * P).sum(0)[None])[0] - (w * H(P)).sum())


def dp_intervals(P, Kc, w=None):
    """Optimal partition of sorted rows P (N, K) (weights w, default uniform) into at most Kc contiguous intervals
    minimising sum_i w_i KL(p_i || mu_I), mu_I the weighted interval mean. Returns the minimal weighted loss (bits)."""
    N = P.shape[0]
    w = np.full(N, 1.0 / N) if w is None else w / w.sum()
    cs = np.vstack([np.zeros((1, P.shape[1])), np.cumsum(w[:, None] * P, 0)])
    cw = np.concatenate([[0.0], np.cumsum(w)])
    plp = np.concatenate([[0.0], np.cumsum(w * (P * np.log2(np.clip(P, 1e-300, 1))).sum(1))])
    def cost(a, b):    # vectorised over a (array), interval [a, b)
        n = cw[b] - cw[a]
        mu = (cs[b][None, :] - cs[a]) / np.maximum(n, 1e-300)[:, None]
        return (plp[b] - plp[a]) - n * (mu * np.log2(np.clip(mu, 1e-300, 1))).sum(1)
    INF = 1e300
    D = np.full((Kc + 1, N + 1), INF)
    D[0, 0] = 0.0
    for k in range(1, Kc + 1):
        for b in range(1, N + 1):
            a = np.arange(0, b)
            D[k, b] = np.min(D[k - 1, a] + cost(a, b))
    return min(D[k, N] for k in range(1, Kc + 1))


def test_weights():
    sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
    import st
    ok = all(np.array_equal(bb.W_layer(s, n, l), st.W_layer(s, n, l)) for s in (9100, 5000) for n in (8, 16)
             for l in (1, 7, 16))
    check('weights', ok, 'bb.W_layer == st.W_layer on 12 (seed, n, l)')


def test_target_1d():
    for K, sigma in [(8, 0.3), (16, 0.1), (32, 0.25)]:
        Tx = exact_T(K, sigma)
        g = torch.Generator().manual_seed(1)
        h = torch.randn(32768, 1, generator=g)
        for M in (64, 256, 1024):
            cnt = bb.mc_counts_next(Net1D(sigma), 0, h, Quant1D(K), M, g)
            st = bb.target_stats(cnt)
            Tpl = st['H_next'] - st['erased_plugin']
            ok = abs(st["T"] - Tx) <= 3 * st["se"] + 0.004 or M < 256   # M = 64: bias shown, not required
            check(f'T 1-D K={K} sigma={sigma} M={M}', ok,
                  f"exact {Tx:.4f}, MM {st['T']:.4f} +- {st['se']:.4f}, plug-in {Tpl:.4f}")


def test_dib_vs_dp():
    K, sigma = 16, 0.3
    rng = np.random.default_rng(3)
    h = np.sort(rng.standard_normal(1500))
    P = exact_post(h, K, sigma)
    Tx = None
    Pt = torch.tensor(P, dtype=torch.float64)
    Hn = float(bb.ent_rows(Pt.mean(0)[None]))
    Ih = Hn - float(bb.ent_rows(Pt).mean())     # I(h; c) on this sample
    g = torch.Generator().manual_seed(5)
    for Kc in (2, 4, 8):
        loss_dp = dp_intervals(P, Kc)
        best = -1
        for r in range(8):
            logmu = bb.kl_kmeanspp(Pt, Kc, g)
            a, logmu, logpi, _ = bb.dib_lloyd(Pt, logmu, math.inf)
            Hc, I = bb.ib_stats(Pt, a, logmu.shape[0])
            best = max(best, I)
        loss_km = Ih - best
        ok = loss_km <= loss_dp + 1e-3
        check(f'KL-kmeans vs DP, Kc={Kc}', ok, f'I(h;c) {Ih:.4f}; loss DP {loss_dp:.5f}, KL-kmeans best of 8 {loss_km:.5f}')


def test_end_to_end_1d():
    K, sigma = 16, 0.3
    net, nxt = Net1D(sigma), Quant1D(K)
    g = torch.Generator().manual_seed(7)
    h_tr = torch.randn(32768, 1, generator=g)
    h_va = torch.randn(8192, 1, generator=g)
    h_te = torch.randn(32768, 1, generator=g)
    c_tr = bb.mc_counts_next(net, 0, h_tr, nxt, 64, g)
    c_va = bb.mc_counts_next(net, 0, h_va, nxt, 64, g)
    c_te = bb.mc_counts_next(net, 0, h_te, nxt, 1024, g)
    P_tr = c_tr.float() / 64
    P_va = c_va.float() / 64
    t0 = time.time()
    pred, info = bb.train_predictor(h_tr, P_tr, h_va, P_va, width=64, depth=2, steps=1500, batch=2048, lr=3e-3)
    # excess CE on held-out: CE against exact posteriors minus their exact entropy
    Pex = torch.tensor(exact_post(h_te[:, 0].numpy().astype(float), K, sigma), dtype=torch.float32)
    ce = bb.cross_entropy_bits(pred, h_te, Pex)
    Hex = float(bb.ent_rows(Pex).mean())
    check('1-D predictor excess CE', ce - Hex < 0.01, f'excess CE {ce - Hex:.4f} bits ({time.time() - t0:.0f}s)')
    Q = bb.predict(pred, h_tr)   # float32, as in the pipeline
    cands = bb.candidates(Q, g, [2, 4, 8], restarts=4, dib_K0=16)
    st = bb.target_stats(c_te)
    hs = np.linspace(-5, 5, 2001)
    ws = np.exp(-hs ** 2 / 2)
    Ps = exact_post(hs, K, sigma)
    Tgrid = float(bb.ent_rows(torch.tensor((ws[:, None] * Ps).sum(0) / ws.sum())[None])) - float(
        (torch.tensor(ws / ws.sum()) * bb.ent_rows(torch.tensor(Ps))).sum())
    q_te = bb.predict(pred, h_te)
    ev = []
    for c in cands:
        code = bb.LayerCode(pred, c['logmu'].float(), c['logpi'].float(), c['beta'])
        r = bb.relevance(code.assign_q(q_te), c_te, code.K)
        ev.append(dict(kind=c['kind'], K=c['K'], H=r['H'], I=r['I']))
    for Kc in (2, 4, 8):
        km = [e for e in ev if e['kind'] == 'kmeans' and e['K'] == Kc]
        loss_dp = dp_intervals(Ps, Kc, ws)
        ok = len(km) == 1 and km[0]['I'] >= Tgrid - loss_dp - 0.01
        env = max([e['I'] for e in ev if e['H'] <= math.log2(Kc) + 1e-9] + [0])
        check(f'end-to-end Kc={Kc}', ok, f"T {st['T']:.4f} (exact {Tgrid:.4f}); DP optimum {Tgrid - loss_dp:.4f}; pipeline k-means "
              f"{km[0]['I'] if km else float('nan'):.4f} (H {km[0]['H'] if km else float('nan'):.3f}); best code with "
              f"H <= log2 Kc: {env:.4f}")


def test_relevance_toy():
    # c uniform on 4 values, next = c with prob 0.9 else uniform over the 4: I = 2 - H(0.925, 0.025 x 3)
    N, M = 4000, 400
    g = torch.Generator().manual_seed(2)
    codes = torch.randint(4, (N,), generator=g)
    probs = torch.full((N, 4), 0.025)
    probs[torch.arange(N), codes] = 0.925
    counts = torch.stack([torch.bincount(torch.multinomial(probs[i], M, replacement=True, generator=g), minlength=4)
                          for i in range(N)]).int()
    p = torch.tensor([0.925, 0.025, 0.025, 0.025], dtype=torch.float64)
    Ix = 2 - float(bb.ent_rows(p[None]))
    r = bb.relevance(codes, counts, 4)
    check('relevance toy', abs(r['I'] - Ix) < 0.005 and abs(r['H'] - 2) < 0.005,
          f"exact I {Ix:.4f}, est {r['I']:.4f} (plug-in {r['I_plugin']:.4f}); H {r['H']:.4f}")


def test_kmeans():
    g = torch.Generator().manual_seed(0)
    C0 = torch.tensor([[0., 0.], [10., 0.], [0., 10.]])
    X = torch.cat([C0[i] + 0.1 * torch.randn(2000, 2, generator=g) for i in range(3)])
    C, d, _ = bb.kmeans(X, 3, g, restarts=3)
    err = min(float(((C[perm] - C0) ** 2).sum()) for perm in
              [torch.tensor(p) for p in [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]])
    check('kmeans', err < 0.01 and abs(d - 0.02) < 0.003, f'centre error {err:.5f}, distortion {d:.4f} (0.02)')


if __name__ == '__main__':
    only = sys.argv[1:]
    for f in [test_weights, test_relevance_toy, test_kmeans, test_target_1d, test_dib_vs_dp, test_end_to_end_1d]:
        if not only or f.__name__ in only:
            f()
    nf = sum(1 for r in RESULTS if not r[1])
    print(f'{len(RESULTS) - nf}/{len(RESULTS)} passed')
    sys.exit(1 if nf else 0)
