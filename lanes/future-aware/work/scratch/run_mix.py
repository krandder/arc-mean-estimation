"""EXPLORATORY (not registered): can the JOINT law of the cloud in the k future directions be replaced by a small
Gaussian mixture? At each cut: features = whitened top-k nonlinear active subspace of g_l (as run_cut.py 'futnl');
fit an M-component full-covariance Gaussian mixture (EM, sklearn) to the k-dim features of 2^15 true samples; sample the
features from the mixture and regenerate the complement by the same linear-Gaussian conditional. Single-cut b2 against
the truth, common random numbers. Variants: gauss, cond (true features), gmm<M>. Output runs/mix_n{N}_L{L}_s{SEED}{TAG}.json.
usage: run_mix.py N L SEED --cuts 1,2,4 --k 16 --Ms 1,2,4,8,16,32 --log2N 18 [--tag T]"""
import argparse, json, os, sys, time
import numpy as np
import torch
from sklearn.mixture import GaussianMixture
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--cuts', default='1,2,4'); ap.add_argument('--k', type=int, default=16)
ap.add_argument('--Ms', default='1,2,4,8,16,32'); ap.add_argument('--log2N', type=int, default=18)
ap.add_argument('--tag', default='')
ap.add_argument('--log2fit', type=int, default=15); ap.add_argument('--maxiter', type=int, default=200)
args = ap.parse_args()
n, L, seed, k = args.n, args.L, args.seed, args.k
cuts = [int(c) for c in args.cuts.split(',') if int(c) < L]
Ms = [int(m) for m in args.Ms.split(',')]
N = 1 << args.log2N
CH = 1 << 14 if n >= 128 else 1 << 15
nb = max(2, N // CH)
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'mix_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
res = dict(n=n, L=L, seed=seed, k=k, log2N=args.log2N, cuts={}, exploratory=True)
t0 = time.time()


def whiten(A, S):
    Ca = A.T @ S @ A
    ev, U = np.linalg.eigh(0.5 * (Ca + Ca.T))
    return A @ (U / np.sqrt(np.clip(ev, 1e-300, None))[None, :]) @ U.T


for l in cuts:
    mu = net['mean'][l - 1].copy()
    Xc = fa.true_samples(W, l, 1 << 17, seed=7_100_000 + seed * 100 + l).double().numpy()
    D = Xc - mu[None, :]
    S = D.T @ D / (D.shape[0] - 1)
    Xr = fa.true_samples(W, l, 1 << 12, seed=7_200_000 + seed * 100 + l)
    B, Vv = fa.vjp_rows(W, l, Xr, seed=7_300_000 + seed * 100 + l)
    Jb = fa.jbar(W, l, fa.true_samples(W, l, 128, seed=7_400_000 + seed * 100 + l))
    Bnl = B - Vv @ Jb
    Rnl = Bnl.T @ Bnl / Bnl.shape[0]
    Aw = whiten(fa.features('futnl', k, S, Rnl), S)
    proj = fa.CondProjector(mu, S, Aw)
    gproj = fa.CondProjector(mu, S, np.zeros((n, 0)))
    feats = D[:1 << args.log2fit] @ Aw + (Aw.T @ mu)[None, :]   # features a = A^T h of 2^log2fit true samples
    gmms = {}
    for M in Ms:
        gm = GaussianMixture(n_components=M, covariance_type='full', random_state=seed * 100 + l + M, max_iter=args.maxiter,
                             reg_covar=1e-6).fit(feats)
        gmms[M] = gm
    var = ['true', 'gauss', 'cond'] + [f'gmm{M}' for M in Ms]
    sums = {v: [np.zeros(n), np.zeros(n)] for v in var}
    for b in range(nb):
        half = 0 if b < nb // 2 else 1
        Xb = fa.true_samples(W, l, CH, seed=8_000_000 + seed * 10_000 + l * 500 + b)
        Zb = torch.randn(CH, n, generator=torch.Generator().manual_seed(9_000_000 + seed * 10_000 + l * 500 + b))
        batch = {'true': Xb}
        base, xi = gproj.sample(Xb, Zb); batch['gauss'] = base + xi
        base, xi = proj.sample(Xb, Zb); batch['cond'] = base + xi
        for M, gm in gmms.items():
            # sklearn's sample() re-seeds from gm.random_state at every call, so without this every batch (and both
            # halves) reused the same feature draw and b2 carried that draw's noise (bug found 18:41Z, deviations 16)
            gm.random_state = (int(seed * 100_000 + l * 1_000 + M * 10 + b) * 7 + 3) % (2 ** 31 - 1)
            a, _ = gm.sample(CH)
            a = torch.from_numpy(a[np.random.RandomState(seed * 7 + b).permutation(CH)]).float()
            base, xi = proj.sample_feats(a, Zb); batch[f'gmm{M}'] = base + xi
        for v in var:
            sA, sB, _, _ = fa.push_halves(W, l, batch[v], half=half)
            sums[v][half] += sA + sB
    row = {}
    for v in var:
        eA = sums[v][0] / (N / 2); eB = sums[v][1] / (N / 2)
        row[v] = dict(b2=float(np.dot(eA - Y, eB - Y) / V))
    row['loglik'] = {str(M): float(gmms[M].score(feats)) for M in Ms}
    res['cuts'][str(l)] = row
    print(f'n={n} s={seed} l={l} k={k}: ' + ' '.join(f'{v}={row[v]["b2"]:.2e}' for v in var) + f' ({time.time() - t0:.0f}s)',
          flush=True)
    json.dump(res, open(out, 'w'))
print('done', out, flush=True)
