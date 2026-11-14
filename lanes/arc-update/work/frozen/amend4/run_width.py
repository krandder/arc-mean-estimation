"""PREREG Amendment 4: width scaling of the single-cut oracle defects (oracle Gaussian Gamma*_2 and oracle
radial-Gaussian Gamma_rad, as in run_attr.py) at fixed l/n and t/n along L = n/8.
Change from run_attr.py: each push half uses its OWN covariance, radius quantiles and pilot, estimated from an
independent true cloud, so the cross product <g_A - Y, g_B - Y>/V is unbiased to leading order in the cloud size.
Cuts: l = 1 and l = n/32, n/16, 3n/32. Truth: this lane's runs/truth_n{n}_L{L}_s{seed}.npz (n <= 128) or arc-noisy's
2^26-path noiseless truth (n = 256).
usage: run_width.py N L SEED [LOG2_PUSH] [LOG2_CLOUD]   -> runs/width_n{N}_L{L}_s{SEED}.json"""
import json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

n, L, seed = (int(a) for a in sys.argv[1:4])
lp = int(sys.argv[4]) if len(sys.argv) > 4 else (21 if n <= 128 else 20)
lc = int(sys.argv[5]) if len(sys.argv) > 5 else 18
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'width_n{n}_L{L}_s{seed}.json')
W = au.weights(seed, n, L)
if n == 256:
    d = np.load(os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_s0_seed{seed}.npz'))
    N_t = float(d['N']); S1 = d['S1']; S2 = d['S2']
else:
    d = np.load(os.path.join(RUNS, f'truth_n{n}_L{L}_s{seed}.npz'))
    N_t = float(d['N']); S1 = d['S1A'] + d['S1B']; S2 = d['S2A'] + d['S2B']
tmean = S1 / N_t
tvar = S2 / N_t - tmean ** 2
Y = tmean[-1]; V = float(tvar[-1].sum())
CUTS = sorted({c for c in (1, n // 32, n // 16, 3 * n // 32) if 1 <= c < L})
CH = 1 << 14
t0 = time.time()


@torch.no_grad()
def cloud_stats(l, N, sd):
    """covariance about the oracle mean and sorted radii of N true layer-l states (chunked)."""
    mu = tmean[l - 1]
    gen = torch.Generator().manual_seed(int(sd))
    acc = np.zeros((n, n)); radii = []; done = 0
    while done < N:
        k = min(CH, N - done)
        x = torch.randn(k, n, generator=gen, dtype=torch.float32)
        h = au.forward(W, x, l0=0, l1=l).double().numpy()
        D = h - mu[None, :]
        acc += D.T @ D
        radii.append(np.linalg.norm(h, axis=1))
        done += k
    r = np.sort(np.concatenate(radii))
    return acc / (N - 1), r


@torch.no_grad()
def push(l, S, rq, N, sd):
    """mean output over N pushes from N(mu_l, S) (rq None) or its radius-transported version (rq = true radii)."""
    mu = tmean[l - 1]
    A, clip = au.psd_sqrt(S)
    gen = torch.Generator().manual_seed(int(sd))
    At = torch.from_numpy(A.T.copy()).float(); mt = torch.from_numpy(mu).float()
    if rq is not None:
        zp = torch.randn(1 << 16, n, generator=gen)
        rp = np.sort(np.linalg.norm((zp @ At + mt).double().numpy(), axis=1))
    s = np.zeros(n); done = 0
    while done < N:
        k = min(CH, N - done)
        h = torch.randn(k, n, generator=gen) @ At + mt
        if rq is not None:
            r = np.linalg.norm(h.double().numpy(), axis=1)
            u = np.clip(np.searchsorted(rp, r) / len(rp), 0.5 / len(rq), 1 - 0.5 / len(rq))
            rt = np.quantile(rq, u)
            h = h * torch.from_numpy(rt / np.maximum(r, 1e-300)).float()[:, None]
        o = au.forward(W, h, l0=l, l1=L)
        s += o.double().sum(0).numpy(); done += k
    return s / N, clip


rows = []
for l in CUTS:
    half = []
    for hh in (0, 1):
        S, rq = cloud_stats(l, 1 << lc, 557_000 + seed * 100 + 2 * l + hh)
        half.append((S, rq))
    row = dict(l=l, rel_radius_sd=float(half[0][1].std() / half[0][1].mean()))
    for name, use_r, base in (('gauss', False, 911_000), ('radgauss', True, 913_000)):
        g = []; clips = []
        for hh in (0, 1):
            S, rq = half[hh]
            gm, clip = push(l, S, rq if use_r else None, 1 << (lp - 1), base + seed * 100 + 2 * l + hh)
            g.append(gm); clips.append(clip)
        row[name] = float(np.dot(g[0] - Y, g[1] - Y) / V)
        row[name + '_d2'] = float(np.dot(g[0] - g[1], g[0] - g[1]) / V)
        row[name + '_clip'] = max(clips)
    rows.append(row)
    print(f"n={n} L={L} s={seed} l={l}: Gamma2 {row['gauss']:.3e} Gamma_rad {row['radgauss']:.3e} "
          f"(half-diff {row['gauss_d2']:.1e}, {row['radgauss_d2']:.1e}) ({time.time() - t0:.0f}s)", flush=True)
res = dict(n=n, L=L, seed=seed, N_truth=N_t, V=V, cuts=CUTS, log2_push=lp, log2_cloud=lc, rows=rows,
           secs=time.time() - t0)
json.dump(res, open(out, 'w'))
print('done', out, f"{res['secs']:.0f}s", flush=True)
