"""Full recursions of future-aware closures, run as finite-sample stochastic recursions (the arc-update Amendment 6
design extended to feature-exact projections).

State after layer l: (mu_l, S_l, A_l, a_l, r_l): the mean and covariance of the model's own one-layer push
y = relu(W_l h), h ~ Q_{l-1}; k features A_l (n x k; future-aware kinds from VJPs of g_l on that push); the features
a = A_l^T y of every pushed sample (the kept k-dim marginal, as an empirical law of N particles); and the sorted push
radii r_l. The projection Q_l regenerates the complement given a by the linear-Gaussian conditional with (mu_l, S_l)
(so mean and covariance are matched and the k-dim marginal is the push's own), optionally followed by arc-update's
radial transport to r_l (rank within batches). k = 0: the Gaussian closure ('gauss') and the radius-corrected closure
('radg'), as arc-update's IPR2. The estimate is the mean of the exact last-layer push. Two replicates;
b2 = <est_0 - Y, est_1 - Y>/V is unbiased for the squared error of the noise-averaged recursion; noise = |est_0 - est_1|^2/(2V).
Variants: gauss, radg, <kind><k>, r<kind><k> (kind in futnl, fut, pca, rand).
Relevance at layer l: 2^MREL pushed samples, VJPs J^T v (v ~ N(0, I)) and E[J] from MJB samples (basis VJPs).
usage: run_rec.py N L SEED --variants gauss,radg,futnl16,pca16 [--log2N 19] [--tag T] -> runs/rec_n{N}_L{L}_s{SEED}{T}.json"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--variants', default='gauss,radg,futnl16,pca16'); ap.add_argument('--log2N', type=int, default=19)
ap.add_argument('--tag', default=''); ap.add_argument('--mrel', type=int, default=12)
ap.add_argument('--mjb', type=int, default=64); ap.add_argument('--reps', type=int, default=2)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
CH = 1 << 14 if n >= 128 else 1 << 15
CH = min(CH, N // 2)
nb = N // CH
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'rec_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
tvarsum = net['var'].sum(1)
t0 = time.time()
res = dict(n=n, L=L, seed=seed, log2N=args.log2N, V=V, Ntruth=net['Ntruth'], truth=net['truth_path'],
           args=vars(args), variants={})


def parse(v):
    if v in ('gauss', 'radg'):
        return dict(kind=None, k=0, rad=(v == 'radg'))
    rad = v.startswith('r') and not v.startswith('rand')
    body = v[1:] if rad else v
    for kind in ('futnl', 'futu', 'fut', 'pca', 'rand'):
        if body.startswith(kind):
            return dict(kind=kind, k=int(body[len(kind):]), rad=rad)
    raise ValueError(v)


def whiten(A, S):
    if A.shape[1] == 0:
        return A
    Ca = A.T @ S @ A
    ev, U = np.linalg.eigh(0.5 * (Ca + Ca.T))
    ev = np.clip(ev, 1e-300, None)
    return A @ (U / np.sqrt(ev)[None, :]) @ U.T


@torch.no_grad()
def model_batch(state, l, b, rep):
    """Batch b of samples of the model Q_{l} (l = 0: exact input)."""
    gz = torch.Generator().manual_seed(int(31_000_000 + seed * 100_000 + rep * 10_000 + l * 300 + b))
    if l == 0:
        return torch.randn(CH, n, generator=gz)
    Z = torch.randn(CH, n, generator=gz)
    a = state['a'][b * CH:(b + 1) * CH] if state['k'] > 0 else None
    base, xi = state['proj'].sample_feats(a, Z)
    h = base + xi
    if state['rad']:
        h = fa.radius_scale(h, state['r'])
    return h


def run(spec, rep):
    k, kind, rad = spec['k'], spec['kind'], spec['rad']
    state = None
    merr = []; relinfo = []
    for l in range(1, L + 1):
        Wl = W[l - 1].float()
        if l == L:
            s = np.zeros(n)
            for b in range(nb):
                h = model_batch(state, l - 1, b, rep)
                s += torch.relu(h @ Wl.T).double().sum(0).numpy()
            return s / N, merr, relinfo
        # pass 1: moments, radii, relevance subsample
        c = None; s1 = np.zeros(n); s2 = np.zeros((n, n)); radii = []; sub = None
        for b in range(nb):
            h = model_batch(state, l - 1, b, rep)
            y = torch.relu(h @ Wl.T)
            yd = y.double()
            if c is None:
                c = yd.mean(0)
                sub = y[:1 << args.mrel].clone()
            D = yd - c[None, :]
            s1 += D.sum(0).numpy(); s2 += (D.T @ D).numpy()
            if rad:
                radii.append(torch.linalg.norm(yd, dim=1).numpy())
        dm = s1 / N
        mu = c.numpy() + dm
        S = (s2 - N * np.outer(dm, dm)) / (N - 1)
        merr.append(float(((mu - net['mean'][l - 1]) ** 2).sum() / tvarsum[l - 1]))
        rs = np.sort(np.concatenate(radii)) if rad else None
        if k > 0:
            if kind in ('fut', 'futnl', 'futu'):
                B, Vv = fa.vjp_rows(W, l, sub, seed=41_000_000 + seed * 1000 + rep * 100 + l)
                R = B.T @ B / B.shape[0]
                if kind == 'futnl':
                    Jb = fa.jbar(W, l, sub[:args.mjb])
                    Bn = B - Vv @ Jb
                    R = Bn.T @ Bn / Bn.shape[0]
            else:
                R = None
            A = whiten(fa.features(kind, k, S, R, seed=42_000_000 + seed * 1000 + rep * 100 + l), S)
            # pass 2: features of every pushed sample
            a = torch.empty(N, k)
            for b in range(nb):
                h = model_batch(state, l - 1, b, rep)
                y = torch.relu(h @ Wl.T)
                a[b * CH:(b + 1) * CH] = y @ torch.from_numpy(A).float()
        else:
            A = np.zeros((n, 0)); a = None
        state = dict(k=k, rad=rad, a=a, r=rs, proj=fa.CondProjector(mu, S, A))
        if l in (1, 2, 4, 8, 16, 24) or l == L - 1:
            print(f'  rep {rep} l={l} mean err {merr[-1]:.2e} ({time.time() - t0:.0f}s)', flush=True)


for v in args.variants.split(','):
    spec = parse(v)
    ests, merrs = [], []
    tv = time.time()
    for rep in range(args.reps):
        e, me, _ = run(spec, rep)
        ests.append(e); merrs.append(me)
    row = dict(spec=spec, secs=time.time() - tv, layer_mean_err=[float(np.mean(x)) for x in zip(*merrs)])
    # honest cost of ONE replicate as an estimator (analytic flop count, pass units 2 n^2 L): per hidden layer l,
    # pass 1 (regenerate the model sample: Z @ Rt 2n^2, features-to-base 2nk; push 2n^2; covariance 2n^2), pass 2 when
    # k > 0 (regenerate 2n^2 + 2nk, push 2n^2, features 2nk), relevance VJPs 3 x 2n^2 (L - l) per sample (and n basis
    # VJPs per E[J] sample for futnl), ~20 n^3 dense linear algebra; last layer: regenerate + push.
    kk = spec['k']; fl = 0.0
    for l in range(1, L):
        fl += N * (2 * n * n + 2 * n * kk + 2 * n * n + 2 * n * n)
        if kk > 0:
            fl += N * (2 * n * n + 2 * n * kk + 2 * n * n + 2 * n * kk)
            if spec['kind'] in ('fut', 'futnl', 'futu'):
                fl += (1 << args.mrel) * 3 * 2 * n * n * (L - l)
            if spec['kind'] == 'futnl':
                fl += args.mjb * n * 3 * 2 * n * n * (L - l)
        fl += 20.0 * n ** 3
    fl += N * (2 * n * n + 2 * n * kk + 2 * n * n)
    row['passes_per_rep'] = fl / (2.0 * n * n * L)
    if len(ests) >= 2:
        row['b2'] = float(np.dot(ests[0] - Y, ests[1] - Y) / V)
        row['noise'] = float(np.dot(ests[0] - ests[1], ests[0] - ests[1]) / (2 * V))
    row['nmse_reps'] = [float(((e - Y) ** 2).sum() / V) for e in ests]
    res['variants'][v] = row
    print(f'n={n} L={L} s={seed} {v}: b2 {row.get("b2", float("nan")):.3e} noise {row.get("noise", float("nan")):.1e} '
          f'({row["secs"]:.0f}s)', flush=True)
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
