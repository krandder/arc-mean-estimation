"""Sampling baselines at equal compute (mv; 1 mv = 128 FLOPs, flopscope conventions), all setup charged.

  MC      plain Monte Carlo, full depth: 256 mv + 1 mv (8 normal draws) per path; nMSE = 1/N exactly (not simulated)
  RQMC    scrambled Sobol on the 8 inputs (inverse normal), full depth: 256 mv + 6 mv (8 inverse-normal evaluations)
  RQMCJ   the same structure as the deterministic code: E[a] = J_c E|x| mean f_c(x/|x|) over scrambled Sobol points,
          c mv + 6 mv + 1 mv (normalisation) per point; setup = one Jacobian pass of layers c+1..256 along u*
          (8 mv per layer), u* = normalised mean of h_c over the first 64 points (reused, no extra cost)
  RADQ    the relevance lane's estimator: g(u*) E|h_32| with scrambled Sobol inputs, 32 mv + 6 mv per point; setup = 64
          pilot paths to layer 32 (64 x 32 mv) for u* and one tail pass g(u*) (224 mv)
nMSE against the reference truth (runs/truth_s{seed}.json, trunc_mean). Writes runs/baselines_s{seed}.json.
Usage: baselines.py SEED C OUT.json
"""
import json
import math
import sys
import time

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/frozen')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
L, n = 256, 8
PPF_MV = 8 * 96 / 128.0
NORM_MV = 1.0
BUDGETS = [2 ** k for k in range(12, 27, 2)]


def reps_for(C):
    return 40 if C <= 2 ** 18 else (16 if C <= 2 ** 22 else 8)


def sobol_normal(m, rng):
    eng = qmc.Sobol(d=n, scramble=True, seed=rng)
    return norm.ppf(np.clip(eng.random(m), 1e-300, 1 - 1e-16))


def tail_jacobian(Ws, c, u):
    h = u.copy()
    J = np.eye(n)
    for k in range(c, L):
        z = Ws[k] @ h
        act = z > 0
        h = np.where(act, z, 0.0)
        J = act[:, None] * (Ws[k] @ J)
    return J


def p2floor(x):
    return 1 << int(math.floor(math.log2(max(x, 1))))


def main():
    seed, c, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    cE = ndx.chi_mean(n)
    rng = np.random.default_rng([31337, seed])
    out = dict(seed=seed, c=c, budgets=BUDGETS, res={})
    t0 = time.time()
    for C in BUDGETS:
        R = reps_for(C)
        e = {k: [] for k in ('RQMC', 'RQMCJ', 'RADQ')}
        cost = {}
        for r in range(R):
            # RQMC full depth
            m = p2floor(C / (L + PPF_MV))
            X = sobol_normal(m, rng)
            e['RQMC'].append(ndx.nmse(ndx.fwd(Ws, X).mean(0), mu, trV))
            cost['RQMC'] = m * (L + PPF_MV)
            # RQMCJ
            setup = (L - c) * 8.0
            m = p2floor((C - setup) / (c + PPF_MV + 1)) if C > setup else 0
            if m >= 64:
                U = sobol_normal(m, rng)
                U /= np.linalg.norm(U, axis=1, keepdims=True)
                H = ndx.fwd(Ws, U, 0, c)
                us = H[:64].mean(0)
                us /= np.linalg.norm(us)
                J = tail_jacobian(Ws, c, us)
                e['RQMCJ'].append(ndx.nmse(J @ (cE * H.mean(0)), mu, trV))
                cost['RQMCJ'] = setup + m * (c + PPF_MV + 1)
            # RADQ
            setup = 64 * 32 + 224.0
            m = p2floor((C - setup) / (32 + PPF_MV)) if C > setup else 0
            if m >= 2:
                hp = ndx.fwd(Ws, rng.standard_normal((64, n)), 0, 32)
                us = hp[np.linalg.norm(hp, axis=1) > 0].mean(0)
                us /= np.linalg.norm(us)
                g = ndx.fwd(Ws, us[None, :], 32, L)[0]
                rad = np.linalg.norm(ndx.fwd(Ws, sobol_normal(m, rng), 0, 32), axis=1).mean()
                e['RADQ'].append(ndx.nmse(rad * g, mu, trV))
                cost['RADQ'] = setup + m * (32 + PPF_MV)
        rec = {k: dict(nmse=float(np.mean(v)), nmse_se=float(np.std(v, ddof=1) / math.sqrt(len(v))),
                       cost_mv=cost.get(k), R=len(v)) for k, v in e.items() if v}
        m = C / (L + NORM_MV)
        rec['MC'] = dict(nmse=1.0 / math.floor(m), cost_mv=math.floor(m) * (L + NORM_MV), R=0)
        out['res'][str(C)] = rec
        print(seed, C, {k: '%.2e' % v['nmse'] for k, v in rec.items()}, 'time %.0f' % (time.time() - t0), flush=True)
        json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
