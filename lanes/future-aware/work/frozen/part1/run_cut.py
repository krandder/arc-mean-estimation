"""Single-cut oracle projections (future-aware family (a) and future-weighted truncation (b)) on one net.

At each cut l the TRUE layer-l law P_l is replaced by a projection Q_l and pushed through the exact layers l+1..L;
b2 = <est_A - Y, est_B - Y> / V (two independent halves) is unbiased for the squared single-cut defect
|int g_l d(Q_l - P_l)|^2 / V. Common random numbers: every variant at a cut uses the same true samples X_b (which
supply the kept features) and the same normals Z_b, batch by batch.
Variants (k = number of kept features; kinds: fut, futnl = whitened active subspace of g_l or of its nonlinear part,
from VJPs on 2^12 true samples; pca = top cloud axes; rand = Haar frame):
  true          push the true samples themselves (noise check: E b2 = 0)
  gauss         oracle Gaussian N(mu, S)                     radg   gauss with arc-update's radial transport
  cond_<kind><k>  k features exact, linear-Gaussian conditional complement (mean and covariance exact)
  radg_<kind><k>  cond followed by arc-update's radial transport (whole samples rescaled to the true radius law by
                  rank within the batch; the features are then exact up to that rescaling)
  edge_<kind><k>  oracle Gaussian reweighted by the order-3 Gram-Charlier weight of the k features' TRUE third
                  cumulant (signed measure; (b) restricted to the k-dim span)
mu = truth mean; S, radius law and third cumulants from 2^17 true samples (seeds fixed below).
usage: run_cut.py N L SEED --cuts 1,2,4 --ks 4,16,64 --kinds fut,futnl,pca,rand --log2N 19 [--edge]
       [--tag TAG]  -> runs/cut_n{N}_L{L}_s{SEED}{TAG}.json"""
import argparse, json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--cuts', default='1,2,4,8,16,24'); ap.add_argument('--ks', default='4,16,64')
ap.add_argument('--kinds', default='fut,futnl,pca,rand'); ap.add_argument('--log2N', type=int, default=19)
ap.add_argument('--condks', default='16'); ap.add_argument('--edge', action='store_true')
ap.add_argument('--edgeks', default='4,16'); ap.add_argument('--edgekinds', default='futnl,pca')
ap.add_argument('--tag', default='')
ap.add_argument('--mrel', type=int, default=12); ap.add_argument('--mjb', type=int, default=128)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
cuts = [int(c) for c in args.cuts.split(',') if int(c) < L]
ks = [int(k) for k in args.ks.split(',')]
condks = [int(k) for k in args.condks.split(',') if k]
kinds = args.kinds.split(',')
N = 1 << args.log2N
CH = 1 << 14 if n >= 128 else 1 << 15
nb = max(2, N // CH)
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'cut_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
t0 = time.time()
res = dict(n=n, L=L, seed=seed, log2N=args.log2N, V=V, Ntruth=net['Ntruth'], truth=net['truth_path'], cuts={},
           args=vars(args))


def whiten(A, S):
    if A.shape[1] == 0:
        return A
    Ca = A.T @ S @ A
    ev, U = np.linalg.eigh(0.5 * (Ca + Ca.T))
    ev = np.clip(ev, 1e-300, None)
    return A @ (U / np.sqrt(ev)[None, :]) @ U.T


def share(Aw, S, M):
    """Fraction of tr M (M a whitened relevance matrix S^{1/2} R S^{1/2}) captured by the span of S^{1/2} Aw."""
    if Aw.shape[1] == 0:
        return 0.0
    U, ev = fa.psd_sqrt(S)
    Sh = (U * np.sqrt(ev)) @ U.T
    Q, _ = np.linalg.qr(Sh @ Aw)
    return float(np.trace(Q.T @ M @ Q) / np.trace(M))


for l in cuts:
    tc = time.time()
    mu = net['mean'][l - 1].copy()
    Xc = fa.true_samples(W, l, 1 << 17, seed=7_100_000 + seed * 100 + l).double().numpy()
    D = Xc - mu[None, :]
    S = D.T @ D / (D.shape[0] - 1)
    r_true = np.sort(np.linalg.norm(Xc, axis=1))
    # relevance of the future map on the true cloud
    Xr = fa.true_samples(W, l, 1 << args.mrel, seed=7_200_000 + seed * 100 + l)
    B, Vv = fa.vjp_rows(W, l, Xr, seed=7_300_000 + seed * 100 + l)
    R = B.T @ B / B.shape[0]
    Jb = fa.jbar(W, l, fa.true_samples(W, l, args.mjb, seed=7_400_000 + seed * 100 + l))
    Bnl = B - Vv @ Jb
    Rnl = Bnl.T @ Bnl / Bnl.shape[0]
    U, ev = fa.psd_sqrt(S)
    Sh = (U * np.sqrt(ev)) @ U.T
    Mw = Sh @ R @ Sh; Mnl = Sh @ Rnl @ Sh
    spec = np.sort(np.linalg.eigvalsh(0.5 * (Mw + Mw.T)))[::-1]
    spec_nl = np.sort(np.linalg.eigvalsh(0.5 * (Mnl + Mnl.T)))[::-1]
    crow = dict(l=l, t=L - l, trS=float(np.trace(S)), pr_cov=float(np.trace(S) ** 2 / np.sum(S * S)),
                rel_trace=float(np.trace(Mw)), rel_nl_trace=float(np.trace(Mnl)),
                rel_spec_top=[float(x) for x in spec[:128]], rel_nl_spec_top=[float(x) for x in spec_nl[:128]],
                variants={}, shares={}, setup_secs=None)
    feats = {}
    for kind in kinds:
        for k in sorted(set(ks + condks + ([int(x) for x in args.edgeks.split(',')] if args.edge else []))):
            if kind not in ('fut', 'futnl', 'pca', 'rand'):
                continue
            Rk = Rnl if kind == 'futnl' else R
            A = fa.features(kind, k, S, Rk, seed=7_500_000 + seed * 100 + l)
            Aw = whiten(A, S)
            feats[(kind, k)] = Aw
            crow['shares'][f'{kind}{k}'] = dict(rel=share(Aw, S, Mw), rel_nl=share(Aw, S, Mnl))
    # variants
    var = ['true', 'gauss', 'radg']
    for kind in kinds:
        for k in ks:
            var.append(f'radg_{kind}{k}')
        for k in condks:
            var.append(f'cond_{kind}{k}')
    proj = {'gauss': fa.CondProjector(mu, S, np.zeros((n, 0)))}
    for (kind, k), Aw in feats.items():
        proj[(kind, k)] = fa.CondProjector(mu, S, Aw)
    edge = {}
    if args.edge:
        for kind in args.edgekinds.split(','):
            for k in [int(x) for x in args.edgeks.split(',')]:
                Aw = feats.get((kind, k))
                if Aw is None:
                    Aw = whiten(fa.features(kind, k, S, Rnl if kind == 'futnl' else R, seed=7_500_000 + seed * 100 + l), S)
                zf = torch.from_numpy(D @ Aw)
                edge[f'edge_{kind}{k}'] = (Aw, fa.third_cumulant(zf))
                var.append(f'edge_{kind}{k}')
    sums = {v: [np.zeros(n), np.zeros(n)] for v in var}
    wsum = {v: [0.0, 0.0] for v in var}
    crow['setup_secs'] = time.time() - tc
    for b in range(nb):
        half = 0 if b < nb // 2 else 1
        gx = torch.Generator().manual_seed(7_600_000 + seed * 1000 + l * 37 + b)
        Xb = fa.true_samples(W, l, CH, seed=8_000_000 + seed * 10_000 + l * 500 + b)
        Zb = torch.randn(CH, n, generator=torch.Generator().manual_seed(9_000_000 + seed * 10_000 + l * 500 + b))
        batch = {}
        batch['true'] = (Xb, None)
        base, xi = proj['gauss'].sample(Xb, Zb)
        hg = base + xi
        batch['gauss'] = (hg, None)
        batch['radg'] = (fa.radius_scale(hg, r_true), None)
        for kind in kinds:
            for k in sorted(set(ks + condks)):
                if (kind, k) not in proj:
                    continue
                base, xi = proj[(kind, k)].sample(Xb, Zb)
                if k in condks:
                    batch[f'cond_{kind}{k}'] = (base + xi, None)
                if k in ks:
                    batch[f'radg_{kind}{k}'] = (fa.radius_scale(base + xi, r_true), None)
        for name, (Aw, kap) in edge.items():
            zg = (hg.double() - torch.from_numpy(mu)) @ torch.from_numpy(Aw)
            batch[name] = (hg, fa.edgeworth_weights(zg.float(), kap))
        for name in var:
            H, w = batch[name]
            sA, sB, wA, wB = fa.push_halves(W, l, H, wts=w, half=half)
            sums[name][half] += sA + sB
            wsum[name][half] += CH
    for name in var:
        eA = sums[name][0] / wsum[name][0]; eB = sums[name][1] / wsum[name][1]
        b2 = float(np.dot(eA - Y, eB - Y) / V)
        noise = float(np.dot(eA - eB, eA - eB) / (2 * V))
        crow['variants'][name] = dict(b2=b2, noise=noise)
    crow['secs'] = time.time() - tc
    res['cuts'][str(l)] = crow
    print(f'n={n} L={L} s={seed} l={l}: ' + ' '.join(f'{k}={v["b2"]:.2e}' for k, v in crow['variants'].items())
          + f' ({crow["secs"]:.0f}s)', flush=True)
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
