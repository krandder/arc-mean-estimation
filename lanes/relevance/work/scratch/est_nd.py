"""Estimation where N is small: narrow-deep 8 x 256 (sigma = 0) after synchronisation.
Relevance result: for l >= l_sync the layer-l state is (to precision 1e-6 .. 1e-29) a ray, so a(x) = |h_l(x)| g(u*) with
u* the synchronised direction and g = F_{l->L}. Estimators of E a at equal compute (cost in mv; one layer = 1 mv):
  MC      plain Monte Carlo, L mv per sample
  RQMC    scrambled Sobol over the 8 Gaussian input coordinates (inverse normal), L mv per point
  RAD     g(u*) x mean |h_l(x)| (l mv per sample; one tail pass for g(u*); u* from 64 pilot paths), biased by the residual
  RADQ    the same with scrambled Sobol inputs
  ML2     unbiased two-level: RAD with N0 samples + full-depth correction a - |h_l| g(u*) with N1 samples (N1 = N0/64)
nMSE = |estimate - truth|^2 / tr Var(a), mean over R repetitions; truth from 2^22 MC samples per net.
Writes runs/est_nd.json."""
import json
import math
import sys

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
L, n = 256, 8


def fwd(Ws, x, a=0, b=None):
    b = len(Ws) if b is None else b
    h = x
    for k in range(a, b):
        h = np.maximum(h @ Ws[k].T, 0.0)
    return h


def truth(Ws, rng, N=1 << 22, chunk=1 << 18):
    s = np.zeros(n)
    s2 = np.zeros(n)
    for _ in range(N // chunk):
        a = fwd(Ws, rng.standard_normal((chunk, n)))
        s += a.sum(0)
        s2 += (a ** 2).sum(0)
    mu = s / N
    var = s2 / N - mu ** 2
    return mu, float(var.sum())


def sobol_normal(m, rng):
    eng = qmc.Sobol(d=n, scramble=True, seed=rng)
    u = eng.random(m)
    return norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))


def main():
    seeds = [203, 216, 217, 220, 221, 223]
    ls = [16, 32]
    budgets = [2 ** k for k in range(12, 21, 2)]  # in mv
    R = 40
    out = []
    for seed in seeds:
        rng = np.random.default_rng([777, seed])
        Ws = rel.narrow_deep_weights(seed, n, L)
        mu, trV = truth(Ws, rng)
        rec = dict(seed=seed, trV=trV, res={})
        for l in ls:
            hp = fwd(Ws, rng.standard_normal((64, n)), 0, l)
            us = hp[np.linalg.norm(hp, axis=1) > 0]
            ustar = us.mean(0) / np.linalg.norm(us.mean(0))
            gstar = fwd(Ws, ustar[None, :], l, L)[0]   # g(u*) (homogeneous: g(r u*) = r g(u*))
            rec['res'][f'bias_l{l}'] = None
            for C in budgets:
                errs = {k: [] for k in ('MC', 'RQMC', f'RAD{l}', f'RADQ{l}', f'ML2_{l}')}
                for r in range(R):
                    m = max(C // L, 2)
                    x = rng.standard_normal((m, n))
                    errs['MC'].append(np.sum((fwd(Ws, x).mean(0) - mu) ** 2) / trV)
                    mq = 2 ** int(math.log2(max(m, 2)))
                    xq = sobol_normal(mq, rng)
                    errs['RQMC'].append(np.sum((fwd(Ws, xq).mean(0) - mu) ** 2) / trV)
                    m0 = max(C // l, 2)
                    x0 = rng.standard_normal((m0, n))
                    rad = np.linalg.norm(fwd(Ws, x0, 0, l), axis=1).mean()
                    errs[f'RAD{l}'].append(np.sum((rad * gstar - mu) ** 2) / trV)
                    mq0 = 2 ** int(math.log2(max(m0, 2)))
                    radq = np.linalg.norm(fwd(Ws, sobol_normal(mq0, rng), 0, l), axis=1).mean()
                    errs[f'RADQ{l}'].append(np.sum((radq * gstar - mu) ** 2) / trV)
                    # two-level: spend C0 = C * 64 l / (64 l + L) on level 0, rest on level 1 (N1 = N0/64)
                    N0 = max(int(C / (l + L / 64.0)), 64)
                    N1 = max(N0 // 64, 2)
                    xa = rng.standard_normal((N0, n))
                    lev0 = np.linalg.norm(fwd(Ws, xa, 0, l), axis=1).mean() * gstar
                    xb = rng.standard_normal((N1, n))
                    hb = fwd(Ws, xb, 0, l)
                    corr = (fwd(Ws, hb, l, L) - np.linalg.norm(hb, axis=1)[:, None] * gstar[None, :]).mean(0)
                    errs[f'ML2_{l}'].append(np.sum((lev0 + corr - mu) ** 2) / trV)
                for k, v in errs.items():
                    rec['res'].setdefault(k, {})[str(C)] = float(np.mean(v))
            # deterministic bias of RAD at this l (large-sample)
            xbig = rng.standard_normal((1 << 20, n))
            radbig = np.linalg.norm(fwd(Ws, xbig, 0, l), axis=1).mean()
            rec['res'][f'bias_l{l}'] = float(np.sum((radbig * gstar - mu) ** 2) / trV)
        out.append(rec)
        print(seed, 'trV %.3g' % trV, {k: (v if not isinstance(v, dict) else {c: '%.2e' % e for c, e in v.items()})
                                       for k, v in rec['res'].items()}, flush=True)
        json.dump(out, open(BASE + 'runs/est_nd.json', 'w'))


if __name__ == '__main__':
    main()
