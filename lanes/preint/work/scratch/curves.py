"""MSE-vs-compute curves for one net (dev and scored runs use this same script).

Usage: curves.py FAMILY N L SEED OUT.json --methods M1,M2,... [--reps R] [--pmin a --pmax b] [--cut c]
  FAMILY arc | nd | small (small = arc stream at small n). Methods:
  MC RB RQMC RQMCRB PI_rand PI_as PI_rand_mc (outer iid) PI_rand_w (eps window) RQMCJ PIJ_rand PIJ_as
  Point methods use N = 2^p points for p in [pmin, pmax]; PI methods use 2^p lines for p in [pmin_pi, pmax_pi]
  (--pimin/--pimax). Each (method, p) is run R times with independent randomisation (scrambling, u, tails).
Writes per (method, p): mean cost (passes), replicate estimates' trace variance / trV (MSE by replicate variance),
and, if a truth exists, per-replicate nMSE against it and the bias z-score of the replicate mean.
"""
import argparse
import json
import math
import os
import sys
import time
import zlib

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import est as E  # noqa: E402
import line as LN  # noqa: E402
import nets  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('family')
    ap.add_argument('n', type=int)
    ap.add_argument('L', type=int)
    ap.add_argument('seed', type=int)
    ap.add_argument('out')
    ap.add_argument('--methods', default='MC,RQMC,RQMCRB,PI_rand')
    ap.add_argument('--reps', type=int, default=8)
    ap.add_argument('--pmin', type=int, default=6)
    ap.add_argument('--pmax', type=int, default=14)
    ap.add_argument('--pimin', type=int, default=2)
    ap.add_argument('--pimax', type=int, default=8)
    ap.add_argument('--cut', type=int, default=48)
    ap.add_argument('--eps', type=float, default=1e-8)
    ap.add_argument('--trv_paths', type=int, default=1 << 16)
    a = ap.parse_args()
    fam, n, L, seed = a.family, a.n, a.L, a.seed
    Ws = nets.nd_weights(seed, n, L) if fam == 'nd' else nets.arc_weights(seed, n, L)
    pf = nets.pass_flops(n, L)
    truth, trV, truth_info = None, None, {}
    try:
        if fam == 'nd':
            tr = nets.nd_truth(seed)
            truth, trV = np.array(tr['trunc_mean']), float(tr['trV'])
            truth_info = dict(source='nd-exact truth', se2_nmse=tr.get('trunc_se2_nmse'))
        else:
            mean, var, Nt = nets.arc_truth(seed, n, L)
            truth, trV = mean, float(var.sum())
            truth_info = dict(source='MC truth', N=Nt, floor_nmse=1.0 / Nt)
    except (FileNotFoundError, OSError, KeyError):
        rng0 = np.random.default_rng([777, seed, n, L])
        F = E.forward(Ws, rng0.standard_normal((a.trv_paths, n)))
        trV = float(F.var(0).sum())
        truth_info = dict(source='no truth; trV from %d MC paths' % a.trv_paths)
    J = None
    Wc = Ws
    methods = a.methods.split(',')
    res = dict(family=fam, n=n, L=L, seed=seed, trV=trV, truth=truth_info, reps=a.reps, pass_flops=pf,
               methods={}, eps=a.eps, cut=a.cut)
    t0 = time.time()
    for meth in methods:
        res['methods'][meth] = []
        is_pi = meth.startswith('PI')
        prange = range(a.pimin, a.pimax + 1) if is_pi else range(a.pmin, a.pmax + 1)
        for p in prange:
            ests, costs, infos = [], [], []
            for r in range(a.reps):
                rng = np.random.default_rng([90210, seed, n, L, zlib.crc32(meth.encode()), p, r])
                if meth in ('MC', 'RB', 'RQMC', 'RQMCRB'):
                    e, c, info = E.point_estimator(Ws, p, rng, meth)
                elif meth == 'RQMCJ' or meth.startswith('PIJ'):
                    c_cut = a.cut
                    # nd-exact RQMCJ: u* from the first 64 points' mean of h_c, J_c along u* (setup charged)
                    Wc = Ws[:c_cut]
                    X0 = E.sobol(n, 6, rng)
                    from scipy.special import ndtri
                    U0 = ndtri(np.clip(X0, 1e-300, 1 - 1e-16))
                    U0 /= np.linalg.norm(U0, axis=1, keepdims=True)
                    H0 = E.forward(Wc, U0)
                    us = H0.mean(0)
                    us /= np.linalg.norm(us)
                    Jc = E.tail_jacobian(Ws, c_cut, us)
                    setup = 64 * (E.mv_flops(Wc) + n * 96 + 3 * n) + (L - c_cut) * (n * (2 * n - 1) * (n + 1) + n)
                    if meth == 'RQMCJ':
                        e, c, info = E.point_estimator(Wc, p, rng, 'RQMCRB', J=Jc)
                    else:
                        e, c, info = E.pi_estimator(Wc, p, rng, u_mode=meth.split('_')[1], J=Jc)
                    c += setup
                elif meth.startswith('MLMC'):
                    r_lev = int(meth.split('_')[1]) if '_' in meth else L // 2
                    e, c, info = E.mlmc_estimator(Ws, p, rng, r_lev)
                elif is_pi:
                    parts = meth.split('_')
                    u_mode = parts[1]
                    outer = 'mc' if 'mc' in parts[2:] else 'rqmc'
                    eps = a.eps if 'w' in parts[2:] else None
                    e, c, info = E.pi_estimator(Ws, p, rng, u_mode=u_mode, outer=outer, eps=eps)
                else:
                    raise ValueError(meth)
                ests.append(e)
                costs.append(c / pf)
                infos.append(info)
            ests = np.array(ests)
            m = ests.mean(0)
            rv = float(((ests - m) ** 2).sum(1).mean() * a.reps / (a.reps - 1) / trV) if a.reps > 1 else float('nan')
            row = dict(p=p, N=1 << p, cost=float(np.mean(costs)), nmse_rep=rv)
            if truth is not None:
                tn = ((ests - truth[None, :]) ** 2).sum(1) / trV
                row['nmse_truth'] = [float(v) for v in tn]
                row['nmse_truth_mean'] = float(tn.mean())
                # bias check: |mean - truth|^2 vs its expectation rv / R (+ truth floor)
                row['bias_ratio'] = float(((m - truth) ** 2).sum() / trV / max(rv / a.reps, 1e-300))
            if infos and 'vertices_mean' in infos[0]:
                row['vertices_mean'] = float(np.mean([i['vertices_mean'] for i in infos]))
                row['line_var_ratio'] = float(np.mean([i['line_var'] for i in infos]) / trV)
            res['methods'][meth].append(row)
            print('%s n=%d L=%d s=%d %-10s p=%2d cost %10.1f passes  nMSE(rep) %.3e  C*nMSE %.3e %s  [%.0fs]' % (
                fam, n, L, seed, meth, p, row['cost'], rv, rv * row['cost'],
                ('truth %.2e bias_ratio %.2f' % (row['nmse_truth_mean'], row['bias_ratio'])) if truth is not None else '',
                time.time() - t0), flush=True)
            json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
