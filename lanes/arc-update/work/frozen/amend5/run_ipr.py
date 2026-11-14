"""Ideal projection recursions (IPR): the full recursion of a projection closure whose per-layer moments are computed
exactly up to Monte Carlo noise (2^LOG2N samples of the MODEL state per layer), so that what is measured is the
closure's own bias at full depth, not a single cut. Two closures:
  gauss    : Q_l = N(m_l, C_l), the moment-matched Gaussian of the exact one-layer push-forward of Q_{l-1}
             (the same closure as the exact Gaussian recursion of run_attr.py; used as a method check);
  radgauss : Q_l = Gaussian directions N(m_l, C_l) with the radius marginal of that push-forward (monotone transport,
             as the oracle radial-Gaussian of run_attr.py), i.e. the ideal version of astra's radial closure.
Q_0 = N(0, I) (exact). The estimate is the mean of the last pushed cloud (exact last step for Q_{L-1}, up to noise).
Two independent replicates; b2 = <est_A - Y, est_B - Y>/V is unbiased for the squared error of the noise-averaged
closure. Also records, per layer, the mean error |m_l - mu_l|^2 / tr Var_l against the truth's layer means.
usage: run_ipr.py N L SEED [LOG2N]   -> runs/ipr_n{N}_L{L}_s{SEED}.json"""
import json, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import au  # noqa: E402

n, L, seed = (int(a) for a in sys.argv[1:4])
lN = int(sys.argv[4]) if len(sys.argv) > 4 else 19
N = 1 << lN
CH = 1 << 14
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'ipr_n{n}_L{L}_s{seed}.json')
W = au.weights(seed, n, L)
if n == 256:
    d = np.load(os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_s0_seed{seed}.npz'))
    N_t = float(d['N']); S1 = d['S1']; S2 = d['S2']
else:
    d = np.load(os.path.join(RUNS, f'truth_n{n}_L{L}_s{seed}.npz'))
    N_t = float(d['N']); S1 = d['S1A'] + d['S1B']; S2 = d['S2A'] + d['S2B']
tmean = S1 / N_t
tvarsum = (S2 / N_t - tmean ** 2).sum(1)
Y = tmean[-1]; V = float(tvarsum[-1])
t0 = time.time()


@torch.no_grad()
def run(model, sd):
    gen = torch.Generator().manual_seed(int(sd))
    m = np.zeros(n); C = np.eye(n); rq = None
    merr = []
    for l in range(1, L + 1):
        A, _ = au.psd_sqrt(C)
        At = torch.from_numpy(A.T.copy()).float(); mt = torch.from_numpy(m).float()
        if model == 'radgauss' and rq is not None:
            zp = torch.randn(1 << 16, n, generator=gen)
            rp = np.sort(np.linalg.norm((zp @ At + mt).double().numpy(), axis=1))
        Wl = W[l - 1].float()
        s1 = np.zeros(n); s2 = np.zeros((n, n)); radii = []; c = None; done = 0
        while done < N:
            k = min(CH, N - done)
            h = torch.randn(k, n, generator=gen) @ At + mt
            if model == 'radgauss' and rq is not None:
                r = np.linalg.norm(h.double().numpy(), axis=1)
                u = np.clip(np.searchsorted(rp, r) / len(rp), 0.5 / len(rq), 1 - 0.5 / len(rq))
                rt = np.quantile(rq, u)
                h = h * torch.from_numpy(rt / np.maximum(r, 1e-300)).float()[:, None]
            y = torch.relu(h @ Wl.T).double().numpy()
            if c is None:
                c = y.mean(0)
            D = y - c[None, :]
            s1 += D.sum(0)
            if l < L:
                s2 += D.T @ D
                if model == 'radgauss':
                    radii.append(np.linalg.norm(y, axis=1))
            done += k
        dm = s1 / N
        m = c + dm
        merr.append(float(((m - tmean[l - 1]) ** 2).sum() / tvarsum[l - 1]))
        if l < L:
            C = (s2 - N * np.outer(dm, dm)) / (N - 1)
            if model == 'radgauss':
                rq = np.sort(np.concatenate(radii))
    return m, merr


res = dict(n=n, L=L, seed=seed, log2N=lN, V=V, N_truth=N_t, models={})
for mi, model in enumerate(('gauss', 'radgauss')):
    ests, merrs = [], []
    for r in (0, 1):
        e, me = run(model, 921_000 + seed * 10 + 2 * mi + r)
        ests.append(e); merrs.append(me)
    b2 = float(np.dot(ests[0] - Y, ests[1] - Y) / V)
    noise = float(np.dot(ests[0] - ests[1], ests[0] - ests[1]) / (2 * V))
    res['models'][model] = dict(b2=b2, noise_var=noise, layer_mean_err=[float(np.mean(x)) for x in zip(*merrs)])
    print(f'n={n} L={L} s={seed} {model}: full-recursion nMSE {b2:.3e} (replicate noise var {noise:.1e}) '
          f'({time.time() - t0:.0f}s)', flush=True)
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f"{res['secs']:.0f}s", flush=True)
