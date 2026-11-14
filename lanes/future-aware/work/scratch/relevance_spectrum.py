"""EXPLORATORY (post hoc): the whitened nonlinear relevance spectrum of the future map at a few cuts, for widths beyond
the registered ones (n = 512). Same construction as scratch/run_cut.py (the B1 runner): S = covariance of the true
layer-l cloud (2^16 samples here, 2^17 there), R_nl = E[(J - E J)^T (J - E J)] from 2^12 VJP rows minus the basis-VJP
mean Jacobian of 128 samples, M = S^{1/2} R_nl S^{1/2}; reports the participation ratio tr^2 / sum lambda^2 (full
spectrum), the stable rank tr / lambda_1 and the share of tr M in the top 4, 16, n/4 eigen-directions.
usage: relevance_spectrum.py N L SEED --cuts 1,8,16,32 -> runs/relspec_n{N}_L{L}_s{SEED}.json"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa, fa2  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--cuts', default='1'); ap.add_argument('--mrel', type=int, default=12)
ap.add_argument('--mjb', type=int, default=128); ap.add_argument('--log2S', type=int, default=16)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'relspec_n{n}_L{L}_s{seed}.json')
W = fa.au.weights(seed, n, L)
res = json.load(open(out)) if os.path.exists(out) else dict(n=n, L=L, seed=seed, args=vars(args), cuts={})
t0 = time.time()
for l in [int(x) for x in args.cuts.split(',')]:
    Xc = fa.true_samples(W, l, 1 << args.log2S, seed=7_100_000 + seed * 100 + l).double().numpy()
    mu = Xc.mean(0); D = Xc - mu[None, :]
    S = D.T @ D / (D.shape[0] - 1)
    del Xc, D
    Xr = fa.true_samples(W, l, 1 << args.mrel, seed=7_200_000 + seed * 100 + l)
    B, Vv = fa.vjp_rows(W, l, Xr, seed=7_300_000 + seed * 100 + l)
    Jb = fa.jbar(W, l, fa.true_samples(W, l, args.mjb, seed=7_400_000 + seed * 100 + l))
    Bnl = B - Vv @ Jb
    Rnl = Bnl.T @ Bnl / Bnl.shape[0]
    U, ev = fa.psd_sqrt(S)
    Sh = (U * np.sqrt(ev)) @ U.T
    Mnl = Sh @ Rnl @ Sh
    sp = np.sort(np.linalg.eigvalsh(0.5 * (Mnl + Mnl.T)))[::-1]
    tr = float(sp.sum())
    row = dict(l=l, participation_ratio=float(tr ** 2 / np.sum(sp ** 2)), stable_rank=float(tr / sp[0]),
               share={str(k): float(sp[:k].sum() / tr) for k in (4, 16, n // 4)}, spec_top=[float(x) for x in sp[:256]],
               trace=tr, secs=time.time() - t0)
    res['cuts'][str(l)] = row
    json.dump(res, open(out, 'w'))
    print(f'n={n} L={L} s={seed} l={l}: PR {row["participation_ratio"]:.1f}, stable rank {row["stable_rank"]:.1f}, '
          f'top-16 share {row["share"]["16"]:.3f}, top-n/4 share {row["share"][str(n // 4)]:.3f} ({row["secs"]:.0f}s)',
          flush=True)
print('done', out, flush=True)
