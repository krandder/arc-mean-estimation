"""POST HOC (GPT-6 review round 2, finding 1): score the H1 hybrid estimates directly.

run_hyb.py (frozen, registered) stored, per replicate, |x|^2 / V with x = mean_RQMC(h_L - c) - (Y - E_P[c]) (the residual
against a reference mean) and, separately, beta = |d|^2 / V with d = E_Q[c] - E_P[c]; the registered P9(c) added the two.
The actual hybrid estimate is est_Q = E_Q[c] + mean_RQMC(h_L - c), whose error est_Q - Y = x + d also has the cross term
2 x.d. This script rebuilds the same surrogates with the same seeds (code copied from run_hyb.py, unchanged), reruns
the same scrambled-Sobol replicates (same seeds) at N = 2^8 .. 2^14 and adds N = 2^15, 2^16 (so the 6.5e4-pass point
needs no extrapolation of the residual curve), and stores per replicate:
  old  = |x|^2 / V                         (must reproduce runs/hyb_*.json 'rqmc')
  dir  = |est_Q - Y|^2 / V for Q = eg, k2  (the hybrid estimator's actual error against the truth Y)
  cross = 2 x.d / V                        (dir = old + beta + cross)
  plain = |mean_RQMC(h_L) - Y|^2 / V        (same scrambles)
For the linear controls the hybrid estimate does not depend on the centring mean mu (it cancels), so no reference mean
enters 'dir'. usage: run_hyb_direct.py N L SEED -> runs/hybd_n{N}_L{L}_s{SEED}.json"""
import argparse, json, os, sys, time
import numpy as np
import torch
from scipy.special import ndtr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
sys.path.insert(0, '/home/agent/workspaces/mats/work/bits-bounds/lib')
import fa  # noqa: E402
import closure as CL  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--layers', default='1,2,4,8,16,24')
ap.add_argument('--log2fit', type=int, default=15); ap.add_argument('--log2ev', type=int, default=15)
ap.add_argument('--qk', type=int, default=16); ap.add_argument('--rqmc', default='8,10,12,14,15,16')
ap.add_argument('--R', type=int, default=8); ap.add_argument('--chunk', type=int, default=1 << 13)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
layers = [int(x) for x in args.layers.split(',') if int(x) < L]
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'hybd_n{n}_L{L}_s{seed}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
t0 = time.time()
res = dict(n=n, L=L, seed=seed, V=V, args=vars(args), layers={})

# ---- surrogate construction: copied from run_hyb.py without change ----
Wn = [w.double().numpy() for w in W]
eg = {}; m = np.zeros(n); S = np.eye(n)
for l in range(1, L + 1):
    m, S = CL.relu_moments(Wn[l - 1] @ m, Wn[l - 1] @ S @ Wn[l - 1].T, 48)
    eg[l] = (m.copy(), S.copy())
k2 = fa.au.arc_kprop(W, 2, kind='simple', keep_states=tuple(layers))


def jac_mf(l):
    J = np.eye(n)
    for j in range(L, l, -1):
        mprev, Sprev = eg[j - 1] if j - 1 >= 1 else (np.zeros(n), np.eye(n))
        mu = Wn[j - 1] @ mprev
        s = np.sqrt(np.maximum(np.einsum('ij,jk,ik->i', Wn[j - 1], Sprev, Wn[j - 1]), 1e-300))
        p = ndtr(mu / s)
        J = J @ (p[:, None] * Wn[j - 1])
    return J


@torch.no_grad()
def samples(Nn, sd):
    gen = torch.Generator().manual_seed(int(sd))
    x = torch.randn(Nn, n, generator=gen)
    _, keep = fa.au.forward(W, x, l0=0, l1=L, keep=set(layers) | {L})
    return keep


fit = samples(1 << args.log2fit, 61_000_000 + seed)
ev = samples(1 << args.log2ev, 62_000_000 + seed)
fL, eL = fit[L].numpy(), ev[L].numpy()
SURR = {}
for l in layers:
    mu = net['mean'][l - 1]
    Xl = fa.true_samples(W, l, 1 << 16, seed=63_000_000 + seed * 100 + l).double().numpy()
    D = Xl - mu[None, :]
    Sl = D.T @ D / (D.shape[0] - 1)
    row = dict(l=l, surrogates={})
    hf, he = fit[l].numpy(), ev[l].numpy()
    Jb = fa.jbar(W, l, torch.from_numpy(Xl[:128]).float())
    Jmf = jac_mf(l)
    Df = hf - mu[None, :]
    Cxx = Df.T @ Df / len(Df); Cfx = (fL - fL.mean(0)).T @ Df / len(Df)
    Breg = Cfx @ np.linalg.pinv(Cxx, rcond=1e-10)
    Bv, Vv = fa.vjp_rows(W, l, torch.from_numpy(Xl[:1 << 12]).float(), seed=64_000_000 + seed * 100 + l)
    Bn = Bv - Vv @ Jb
    Rnl = Bn.T @ Bn / len(Bn)
    A = fa.features('futnl', args.qk, Sl, Rnl)
    Ca = A.T @ Sl @ A; ev_, U_ = np.linalg.eigh(0.5 * (Ca + Ca.T))
    A = A @ (U_ / np.sqrt(np.clip(ev_, 1e-300, None))) @ U_.T
    iu = np.triu_indices(args.qk)

    def qfeat(h, A=A, mu=mu, iu=iu):
        a = (h - mu[None, :]) @ A
        return (a[:, :, None] * a[:, None, :])[:, iu[0], iu[1]]
    Qf = qfeat(hf); Qm = Qf.mean(0)
    Xf = np.concatenate([Df, Qf - Qm], 1)
    Bq = ((fL - fL.mean(0)).T @ Xf / len(Xf)) @ np.linalg.pinv(Xf.T @ Xf / len(Xf), rcond=1e-10)
    Qtrue = qfeat(Xl).mean(0)
    del Xl, D
    for name, B in (('jac', Jb), ('jacmf', Jmf), ('reg', Breg), (f'regq{args.qk}', Bq)):
        quad = name.startswith('regq')
        if quad:
            Bl, Bqq = B[:, :n], B[:, n:]
            cfun = (lambda h, Bl=Bl, Bqq=Bqq, mu=mu, qfeat=qfeat, Qm=Qm:
                    (h - mu[None, :]) @ Bl.T + (qfeat(h) - Qm) @ Bqq.T)
        else:
            Bl, Bqq = B, None
            cfun = lambda h, B=B, mu=mu: (h - mu[None, :]) @ B.T
        r = eL - cfun(he)
        eta = float(r.var(0).sum() / V)
        cP = Bqq @ (Qtrue - Qm) if quad else np.zeros(n)
        betas = {}; cQs = {}
        for qn, (mq, Sq) in (('eg', eg[l]), ('k2', k2['states'][l])):
            cQ = (mq - mu) @ Bl.T
            if quad:
                am = (mq - mu) @ A
                EQ = A.T @ Sq @ A + np.outer(am, am)
                cQ = cQ + Bqq @ (EQ[iu[0], iu[1]] - Qm)
            betas[qn] = float(((cQ - cP) ** 2).sum() / V)
            cQs[qn] = cQ
        row['surrogates'][name] = dict(eta=eta, beta=betas, rqmc={})
        SURR[(l, name)] = dict(cfun=cfun, cP=cP, cQ=cQs, Bl=Bl, Bqq=Bqq, mu=mu, qfeat=(qfeat if quad else None), Qm=Qm)
        print(f'l={l} {name}: eta {eta:.3f} beta_eg {betas["eg"]:.2e} beta_k2 {betas["k2"]:.2e} '
              f'({time.time() - t0:.0f}s)', flush=True)
    res['layers'][str(l)] = row
del fit, ev, fL, eL

# ---- RQMC: same scrambles as run_hyb.py (seed * 1000 + 17 * m + r), plus m = 15, 16; per-replicate records ----
from scipy.stats import qmc
from scipy.special import ndtri
res['plain'] = {}
for mm in [int(x) for x in args.rqmc.split(',')]:
    Nn = 1 << mm
    rec = {key: dict(old=[], cross=[], dir_eg=[], dir_k2=[]) for key in SURR}; ep = []
    for r in range(args.R):
        eng = qmc.Sobol(d=n, scramble=True, seed=int(seed) * 1000 + 17 * mm + r)
        u = np.clip(eng.random(Nn), 1e-12, 1 - 1e-12)
        # every control is linear in h_l and in the quadratic features, so sum_i c(h_i) needs only the sums of h_l and
        # of the features (v2, 15:27Z; identical up to rounding to summing c per sample as v1 did for seed 200 at n = 256)
        sL = np.zeros(n); sh = {l: np.zeros(n) for l in layers}
        sq = {key: np.zeros(len(d['Qm'])) for key, d in SURR.items() if d['qfeat'] is not None}
        with torch.no_grad():
            for i0 in range(0, Nn, args.chunk):
                x = torch.from_numpy(ndtri(u[i0:i0 + args.chunk])).float()
                _, keep = fa.au.forward(W, x, l0=0, l1=L, keep=set(layers) | {L})
                sL += keep[L].sum(0, dtype=torch.float64).numpy()
                for l in layers:
                    sh[l] += keep[l].sum(0, dtype=torch.float64).numpy()
                for key in sq:
                    sq[key] += SURR[key]['qfeat'](keep[key[0]].numpy().astype(np.float64)).sum(0)
        sres = {}
        for key, d in SURR.items():
            csum = (sh[key[0]] - Nn * d['mu']) @ d['Bl'].T
            if d['qfeat'] is not None:
                csum = csum + (sq[key] - Nn * d['Qm']) @ d['Bqq'].T
            sres[key] = sL - csum
        ep.append(float(((sL / Nn - Y) ** 2).sum() / V))
        for key, d in SURR.items():
            resid = sres[key] / Nn
            x_ = resid - (Y - d['cP'])
            rec[key]['old'].append(float((x_ ** 2).sum() / V))
            for qn in ('eg', 'k2'):
                est = d['cQ'][qn] + resid
                rec[key][f'dir_{qn}'].append(float(((est - Y) ** 2).sum() / V))
            rec[key]['cross'].append(float(2.0 * x_ @ (d['cQ']['eg'] - d['cP']) / V))
    res['plain'][str(mm)] = ep
    for (l, name), v in rec.items():
        res['layers'][str(l)]['surrogates'][name]['rqmc'][str(mm)] = v
    print(f'RQMC N=2^{mm}: plain {np.mean(ep):.2e}; ' + ' '.join(
        f'{l}/{name} old {np.mean(v["old"]):.2e} dir {np.mean(v["dir_eg"]):.2e}' for (l, name), v in rec.items() if l in (1, 8, 24))
        + f' ({time.time() - t0:.0f}s)', flush=True)
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
