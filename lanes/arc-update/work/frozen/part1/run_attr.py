"""T-ATTR at 256 x 32: per-net error attribution est - Y = a_l + b_l (FORMAL A6) for
  (i) ARC's K = 2 'simple' (state = Gaussian N(m_l, S_l) after layer l),
  (ii) the exact single-Gaussian recursion (bits-bounds lib/closure.py relu_moments; state = Gaussian),
  (iii) the oracle moment-matched Gaussian of the TRUE layer-l law (Gamma*_2(l), single-cut Gaussian defect),
at cuts l in CUTS. b_l = E_{G_l} g_l - Y (past model's defect tested by the actual future), a_l = est - E_{G_l} g_l
(suffix error). Squared norms debiased with two independent push halves (cross products).
usage: run_attr.py SEED TRUTH(s0|s0.001) [LOG2_PUSH]  -> runs/attr_s{SEED}.json"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
sys.path.insert(0, '/home/agent/workspaces/mats/work/bits-bounds/lib')
import au  # noqa: E402
import closure as CL  # noqa: E402

seed, tkind = int(sys.argv[1]), sys.argv[2]
lp = int(sys.argv[3]) if len(sys.argv) > 3 else 18
n, L = 256, 32
CUTS = [1, 2, 4, 8, 16, 24, 28, 31]
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'attr_s{seed}.json')
W = au.weights(seed, n, L)
d = np.load(os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_{tkind}_seed{seed}.npz'))
N_t = float(d['N']); tmean = d['S1'] / N_t; tvar = d['S2'] / N_t - tmean ** 2
Y = tmean[-1]; V = float(tvar[-1].sum())
t0 = time.time()
res = dict(seed=seed, truth=tkind, N_truth=N_t, V=V, cuts=CUTS, log2_push=lp, models={})

# (i) ARC K = 2 simple
r = au.arc_kprop(W, 2, kind='simple', keep_states=tuple(CUTS))
models = {'arc_k2': (r['mean'], r['states'], r['flops'])}

# (ii) exact single-Gaussian recursion with states
m = np.zeros(n); S = np.eye(n); st = {}
Wn = [w.numpy() for w in W]
for l, Wl in enumerate(Wn, start=1):
    m, S = CL.relu_moments(Wl @ m, Wl @ S @ Wl.T, 48)
    if l in CUTS:
        st[l] = (m.copy(), S.copy())
cost_mm = 4.0 * n ** 3 * L                       # W S W^T: two n^3 products (2 n^3 flops each) per layer
cost_phi2 = float(n * n * 48 * (16 + 12) * L)    # pairwise moments: q = 48 nodes, exp (16) + ~12 flops per node
models['exact_gauss'] = (m, st, cost_mm + cost_phi2)
res['exact_gauss_cost'] = dict(matmul=cost_mm, phi2=cost_phi2)

# (iii) oracle: true mean (truth file) and sample covariance of the true law (2^17 fresh inputs)
st_or = {}
for l in CUTS:
    X = au.true_cloud(W, l, 1 << 17, seed=555_000 + seed * 100 + l)
    mu_l = tmean[l - 1]
    D = X - mu_l[None, :]
    st_or[l] = (mu_l.copy(), D.T @ D / (D.shape[0] - 1))
models['oracle_gauss'] = (None, st_or, None)
# (iv) oracle radial-Gaussian: Gaussian directions with the TRUE radius marginal (monotone radius transport);
#      measures how much of the single-cut Gaussian defect is the radial (amplitude) marginal
rad_q = {}
for l in CUTS:
    X = au.true_cloud(W, l, 1 << 17, seed=556_000 + seed * 100 + l)
    rad_q[l] = np.sort(np.linalg.norm(X, axis=1))
models['oracle_radgauss'] = (None, st_or, None)


def radgauss_push(l, N, sd):
    """push Gaussian samples whose radii are mapped to the true radius marginal (empirical quantiles)."""
    import torch
    ml, Sl = st_or[l]
    A, clip = au.psd_sqrt(Sl)
    gen = torch.Generator().manual_seed(int(sd))
    At = torch.from_numpy(A.T.copy()).float(); mt = torch.from_numpy(ml).float()
    # reference radius cdf of the Gaussian model from a pilot
    zp = torch.randn(1 << 16, n, generator=gen)
    rp = np.sort(np.linalg.norm((zp @ At + mt).double().numpy(), axis=1))
    qt = rad_q[l]
    sums = np.zeros((2, n)); done = 0; chunk = 1 << 14
    while done < N:
        k = min(chunk, N - done); half = 0 if done < N // 2 else 1
        h = torch.randn(k, n, generator=gen) @ At + mt
        r = np.linalg.norm(h.double().numpy(), axis=1)
        u = np.clip(np.searchsorted(rp, r) / len(rp), 0.5 / len(qt), 1 - 0.5 / len(qt))
        rt = np.quantile(qt, u)
        h = h * torch.from_numpy(rt / np.maximum(r, 1e-300)).float()[:, None]
        out = au.forward(W, h, l0=l, l1=L)
        sums[half] += out.double().sum(0).numpy(); done += k
    return sums.sum(0) / N, clip, sums[0] / (N / 2), sums[1] / (N / 2)


for name, (est, states, cost) in models.items():
    rows = []
    for l in CUTS:
        ml, Sl = states[l]
        if name == 'oracle_radgauss':
            g, clip, gA, gB = radgauss_push(l, 1 << lp, 910_000 + seed * 100 + l)
        else:
            g, clip, gA, gB = au.gauss_push(W, ml, Sl, l, 1 << lp, seed=900_000 + seed * 100 + l)
        b2 = float(np.dot(gA - Y, gB - Y) / V)
        row = dict(l=l, b2=b2, clip=clip)
        if est is not None:
            row['a2'] = float(np.dot(est - gA, est - gB) / V)
            row['ab'] = float(np.dot(est - gA, gB - Y) / V)    # cross term (one half each side)
        rows.append(row)
        print(f'{name} l={l}: b2 {b2:.3e}' + (f' a2 {row["a2"]:.3e} ab {row["ab"]:.3e}' if est is not None else '')
              + f' clip {clip:.1e} ({time.time() - t0:.0f}s)', flush=True)
    res['models'][name] = dict(rows=rows, total=(float(((est - Y) ** 2).sum() / V) if est is not None else None),
                               cost=cost)
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
