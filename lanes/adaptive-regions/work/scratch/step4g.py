"""Step 4, main's GMM formulation: per-layer joint-GMM mixtures of linear experts, population propagated in closed form.

For layers l0 .. L-1: low-rank coordinates u_l = P_l^T (h_l - c_l) (top-d principal axes of the sampled cloud; at the
input c_0 = 0 and P_0 = top-d axes of x, i.e. any d coordinates, and the population is exactly N(0, I_d)), a K-component
joint GMM on (u_l, u_{l+1}) from sampled pairs (lib/gmoe.py), and the closed-form population push (Gaussian gate x
Gaussian component, affine map, residual covariance, moment matching onto the K experts). Start: the exact input
(l0 = 0) or, "where the cloud is low-dimensional", the layer-l0 GMM marginal of u (an oracle start from samples).
Output mean = c_L + P_L sum_k w_k m_k; error against the truth (nMSE); held-out joint log-likelihood per layer (for K);
cost = sampled paths + EM flops (estimate: iterations x N x K x (2d)^2 x 6) in passes. MEASURED (exploratory).
Usage: step4g.py SEED n L [--l0 0] [--Ks 1,2,4,8] [--d 16] [--log2N 13]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import gmoe  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--l0', type=int, default=0)
ap.add_argument('--Ks', default='1,2,4,8')
ap.add_argument('--d', type=int, default=16)
ap.add_argument('--log2N', type=int, default=13)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
d = min(args.d, n)
KS = [int(k) for k in args.Ks.split(',')]
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4g_n{n}_L{L}_s{seed}_l0{args.l0}_d{d}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
PASS = 2.0 * n * n * L


@torch.no_grad()
def sample(gen_seed, M, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    H = np.zeros((L + 1, M, n), dtype=np.float32)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        H[0, done:done + k] = h.numpy()
        for l in range(L):
            h = torch.relu(h @ W[l].T)
            H[l + 1, done:done + k] = h.numpy()
        done += k
    return H


H_tr = sample(13_000_000 + seed, N)
H_te = sample(14_000_000 + seed, N)
try:
    tr = ar.au.load_arc_truth(seed, n, L)
    mu_true = tr['mean'][-1] if tr['mean'].ndim == 2 else tr['mean']
    V_true = float((tr['var'][-1] if tr['var'].ndim == 2 else tr['var']).sum())
except Exception:
    try:
        dd = np.load(f'/home/agent/workspaces/mats/work/arc-update/runs/truth_n{n}_L{L}_s{seed}.npz')
        NN = float(dd['N']); m_ = (dd['S1A'] + dd['S1B']) / NN; v_ = (dd['S2A'] + dd['S2B']) / NN - m_ ** 2
        mu_true, V_true = m_[L - 1], float(v_[L - 1].sum())
    except Exception:
        big = sample(15_000_000 + seed, 1 << 16)[L].astype(np.float64)
        mu_true, V_true = big.mean(0), float(big.var(0).sum())
# bases
bases = {}
for l in range(args.l0, L + 1):
    X = H_tr[l].astype(np.float64)
    c = np.zeros(n) if l == 0 else X.mean(0)
    _, sv, Vt = np.linalg.svd(X - c, full_matrices=False)
    bases[l] = (c, Vt[:d].T, float((sv[:d] ** 2).sum() / (sv ** 2).sum()))
coords = lambda H, l: (H[l].astype(np.float64) - bases[l][0]) @ bases[l][1]
mc_err = float(((H_tr[L].astype(np.float64).mean(0) - mu_true) ** 2).sum() / V_true)
print(f'sampled {2 * N} in {time.time() - t0:.0f}s; d={d}; captured variance by layer (l0..L): '
      f'{[round(bases[l][2], 3) for l in range(args.l0, L + 1)]}; plain MC on the {N} training paths: nMSE {mc_err:.2e}', flush=True)
res = dict(n=n, L=L, seed=seed, N=N, d=d, l0=args.l0, Ks=KS, mc_train_nmse=mc_err, runs=[])
for K in KS:
    t1 = time.time()
    models = []; lls = []; em_flops = 0.0
    for l in range(args.l0, L):
        U, Vv = coords(H_tr, l), coords(H_tr, l + 1)
        mdl = gmoe.LayerMoE(K, seed=seed).fit(U, Vv)
        models.append(mdl)
        lls.append(mdl.heldout_loglik(coords(H_te, l), coords(H_te, l + 1)))
        em_flops += mdl.gm.n_iter_ * N * K * (2 * d) ** 2 * 6
    # population start
    if args.l0 == 0:
        w = np.ones(1); M = (-(bases[0][0]) @ bases[0][1])[None]; S = np.eye(d)[None]       # exact N(0, I_d)
    else:
        g0 = models[0]
        w = g0.pi.copy(); M = g0.mu_u.copy(); S = g0.Suu.copy()                               # oracle start
    for mdl in models:
        w, M, S = mdl.push(w, M, S)
    est = bases[L][0] + bases[L][1] @ (w[:, None] * M).sum(0) / w.sum()
    err = float(((est - mu_true) ** 2).sum() / V_true)
    # pointwise check: chain of conditional means from held-out layer-l0 states (not the population push)
    U = coords(H_te, args.l0)
    for mdl in models:
        U = mdl.predict_mean(U)
    pt = bases[L][0] + U @ bases[L][1].T
    pt_nmse = float(((pt - H_te[L].astype(np.float64)) ** 2).sum(1).mean() / V_true)
    cost = N + em_flops / PASS
    res['runs'].append(dict(K=K, nmse=err, heldout_loglik=lls, mean_ll=float(np.mean(lls)), cost_passes=cost,
                            em_flops=em_flops, pointwise_chain_nmse=pt_nmse, secs=time.time() - t1))
    print(f'K={K}: output-mean nMSE {err:.2e} (MC on the training paths {mc_err:.2e}); pointwise chained prediction '
          f'nMSE {pt_nmse:.3f}; mean held-out joint loglik {np.mean(lls):.1f}; cost {cost:.0f} passes ({time.time() - t1:.0f}s)', flush=True)
    json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
