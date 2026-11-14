"""T-RANK at 256 x 32: third-cumulant structure of the true layer-l cloud (FORMAL A4, B2-B3).
For each layer l in LAYERS: ||kappa_3(h_l)||_F^2 (U-statistic), the participation ratio of the mode-1 flattening Gram
K3 = kappa_(1) kappa_(1)^T, its held-out top-k energy fraction, and the held-out multilinear top-k capture
E[((P d).(P d'))^3] / E[(d . d')^3] (the Frobenius energy kept by the best rank-k compression in that basis; by the
random-probe lemma this is what a forward-only compressed representation can serve to the next layer's neurons).
Also the per-layer participation ratio of the covariance (for comparison: the cloud's PR ~ n/l).
usage: run_rank.py SEED TRUTH(s0|s0.001) [LOG2_N]   -> runs/rank_s{SEED}.json
       run_rank.py control 0 [LOG2_N]                -> runs/rank_control.json (n = 256 planted and Gaussian clouds)"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
lp = int(sys.argv[3]) if len(sys.argv) > 3 else 15
KS = (1, 2, 4, 8, 16, 32, 64, 128)
n, L = 256, 32
t0 = time.time()
if sys.argv[1] == 'control':
    rng = np.random.default_rng(31)
    N = 1 << lp
    res = {}
    X = rng.standard_normal((N, n))
    res['gauss'] = au.k3_flat_stats(X, np.zeros(n), ks=KS)
    for r_pl in (8, 32):
        U = np.linalg.qr(rng.standard_normal((n, r_pl)))[0]
        E = (rng.chisquare(1, size=(N, r_pl)) - 1) / math.sqrt(2)
        Xp = rng.standard_normal((N, n)) + 1.0 * E @ U.T
        res[f'planted{r_pl}'] = au.k3_flat_stats(Xp, np.zeros(n), ks=KS)
        print(f'planted {r_pl}: pr {res[f"planted{r_pl}"]["pr"]:.1f} cap {res[f"planted{r_pl}"]["capk"]}', flush=True)
    print(f'gauss: fro2 {res["gauss"]["fro2"]:.3e} pr {res["gauss"]["pr"]:.1f}', flush=True)
    json.dump(res, open(os.path.join(RUNS, 'rank_control.json'), 'w'))
    sys.exit(0)

seed, tkind = int(sys.argv[1]), sys.argv[2]
LAYERS = [1, 2, 4, 8, 12, 16, 20, 24, 28, 31]
W = au.weights(seed, n, L)
d = np.load(os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_{tkind}_seed{seed}.npz'))
N_t = float(d['N']); tmean = d['S1'] / N_t
res = dict(seed=seed, truth=tkind, log2_N=lp, layers={})
import torch
gen_seed = 444_000 + seed
x = torch.randn(1 << lp, n, generator=torch.Generator().manual_seed(gen_seed))
_, keep = au.forward(W, x, keep=set(LAYERS))
for l in LAYERS:
    X = keep[l].numpy()
    mu = tmean[l - 1]
    s = au.k3_flat_stats(X, mu, ks=KS)
    D = X - mu[None, :]
    C = D.T @ D / (D.shape[0] - 1)
    ev = np.linalg.eigvalsh(C)
    s['cov_pr'] = float(ev.sum() ** 2 / (ev ** 2).sum())
    s['cov_tr'] = float(ev.sum())
    # standardised size: ||kappa_3||_F^2 / (tr C)^3 (the probe-variance scale of gamma_3, FORMAL A4)
    s['fro2_std'] = s['fro2'] / s['cov_tr'] ** 3
    res['layers'][l] = s
    print(f'l={l}: fro2 {s["fro2"]:.3e} std {s["fro2_std"]:.2e} pr3 {s["pr"]:.1f} covPR {s["cov_pr"]:.1f} '
          f'cap8 {s["capk"][8]:.3f} cap32 {s["capk"][32]:.3f} ({time.time() - t0:.0f}s)', flush=True)
json.dump(res, open(os.path.join(RUNS, f'rank_s{seed}.json'), 'w'))
print('done', f'{time.time() - t0:.0f}s', flush=True)
