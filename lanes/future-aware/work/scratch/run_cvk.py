"""EXPLORATORY (not registered): residual variance of an EXACT-MEAN control variate as its complexity grows.
Control at l = 1 (whose law is explicit, so the mean of any polynomial in h_1 is computable exactly): c(h_1) = linear
in h_1 (all n coordinates) + all quadratic monomials of the top-k whitened future (futnl) directions of g_1, fitted by
least squares on 2^log2fit pilot samples, evaluated on independent samples: eta(k) = tr Var(h_L - c) / V. The exact
mean of each quadratic feature uses the true second moments of h_1 (here estimated from 2^17 true samples, an O(1e-3)
relative approximation... replaced: the exact arc-cosine first-layer moments are used, so the control's mean is exact). RQMC (8 scrambles,
2^10..2^14, the same points) on the residual vs on h_L. Construction cost (passes): pilot samples + VJPs for the
directions + the least-squares solve (N_fit p^2 + p^3 flops, p = n + k(k+1)/2), reported per k.
usage: run_cvk.py N L SEED --ks 4,8,16,32 [--log2fit 15] [--tag T] -> runs/cvk_n{N}_L{L}_s{SEED}{T}.json"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--ks', default='4,8,16,32'); ap.add_argument('--log2fit', type=int, default=15)
ap.add_argument('--log2ev', type=int, default=15); ap.add_argument('--rqmc', default='10,12,14'); ap.add_argument('--tag', default='')
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
ks = [int(k) for k in args.ks.split(',')]
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'cvk_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
t0 = time.time()


@torch.no_grad()
def samples(Nn, sd):
    x = torch.randn(Nn, n, generator=torch.Generator().manual_seed(int(sd)))
    _, keep = fa.au.forward(W, x, l0=0, l1=L, keep={1, L})
    return keep[1].numpy(), keep[L].numpy()


h1f, fLf = samples(1 << args.log2fit, 71_000_000 + seed)
h1e, fLe = samples(1 << args.log2ev, 72_000_000 + seed)
# exact first-layer moments (h_1 = relu(W_1 x), x ~ N(0, I)): E h_i = |w_i| / sqrt(2 pi);
# E h_i h_j = |w_i| |w_j| (sin t + (pi - t) cos t) / (2 pi), cos t = w_i . w_j / (|w_i| |w_j|)  (arc-cosine kernel)
W1 = W[0].double().numpy()
nr = np.linalg.norm(W1, axis=1)
mu1 = nr / np.sqrt(2 * np.pi)
ct = np.clip((W1 @ W1.T) / np.outer(nr, nr), -1.0, 1.0); th = np.arccos(ct)
E2 = np.outer(nr, nr) * (np.sin(th) + (np.pi - th) * ct) / (2 * np.pi)
S1 = E2 - np.outer(mu1, mu1)
X1 = fa.true_samples(W, 1, 1 << 13, seed=73_000_000 + seed).double().numpy()
Xr = torch.from_numpy(X1[:1 << 12]).float()
B, Vv = fa.vjp_rows(W, 1, Xr, seed=74_000_000 + seed)
Jb = fa.jbar(W, 1, torch.from_numpy(X1[:128]).float())
Bn = B - Vv @ Jb
Rnl = Bn.T @ Bn / len(Bn)
res = dict(n=n, L=L, seed=seed, V=V, rows={}, exploratory=True)
from scipy.stats import qmc
from scipy.special import ndtri
ms = [int(m) for m in args.rqmc.split(',')]
pts = {}
for m in ms:
    for r in range(8):
        eng = qmc.Sobol(d=n, scramble=True, seed=int(seed) * 1000 + 17 * m + r)
        x = torch.from_numpy(ndtri(np.clip(eng.random(1 << m), 1e-12, 1 - 1e-12))).float()
        _, keep = fa.au.forward(W, x, l0=0, l1=L, keep={1, L})
        pts[(m, r)] = (keep[1].numpy(), keep[L].numpy())
plain = {m: float(np.mean([((pts[(m, r)][1].mean(0) - Y) ** 2).sum() / V for r in range(8)])) for m in ms}
for k in [0] + ks:
    if k > 0:
        A = fa.features('futnl', k, S1, Rnl)
        Ca = A.T @ S1 @ A; ev_, U_ = np.linalg.eigh(0.5 * (Ca + Ca.T))
        A = A @ (U_ / np.sqrt(np.clip(ev_, 1e-300, None))) @ U_.T
        iu = np.triu_indices(k)
    else:
        A = None

    def feats(h):
        Dh = h - mu1[None, :]
        if A is None:
            return Dh
        a = Dh @ A
        return np.concatenate([Dh, (a[:, :, None] * a[:, None, :])[:, iu[0], iu[1]]], 1)
    Ff = feats(h1f)
    # exact means: linear part E[h - mu1] = 0; quadratic part E[a a^T] = A^T S1 A (exact first-layer covariance)
    if A is None:
        Fm_true = np.zeros(n)
    else:
        Eaa = A.T @ S1 @ A
        Fm_true = np.concatenate([np.zeros(n), Eaa[iu[0], iu[1]]])
    Fc = Ff - Fm_true[None, :]
    coef = np.linalg.lstsq(Fc, fLf - fLf.mean(0), rcond=None)[0]
    cfun = lambda h: (feats(h) - Fm_true[None, :]) @ coef
    eta = float((fLe - cfun(h1e)).var(0).sum() / V)
    rq = {}
    for m in ms:
        e = [(((pts[(m, r)][1] - cfun(pts[(m, r)][0])).mean(0) - Y) ** 2).sum() / V for r in range(8)]
        rq[str(m)] = float(np.mean(e))
    p = Ff.shape[1]
    cost = (1 << args.log2fit) + (((1 << 12) + 128 * n) * 3.0 * (L - 1) / L if k > 0 else 0.0) + \
        ((1 << args.log2fit) * p * p + p ** 3) / PASS
    res['rows'][str(k)] = dict(k=k, p=p, eta=eta, rqmc_resid=rq, construction_passes=cost)
    print(f'n={n} s={seed} k={k} p={p}: eta {eta:.3f} cost {cost:.0f} passes; RQMC resid ' +
          ' '.join(f'2^{m} {rq[str(m)]:.2e} (plain {plain[m]:.2e})' for m in ms) + f' ({time.time() - t0:.0f}s)', flush=True)
res['rqmc_plain'] = {str(m): v for m, v in plain.items()}
json.dump(res, open(out, 'w'))
print('done', out, flush=True)
