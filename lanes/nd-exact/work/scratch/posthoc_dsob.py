"""Post hoc (raised by the gpt-6-astra review): a deterministic point set. DSOB = the unscrambled Sobol net of N = 2^m
points shifted by 1/(2N) (no random numbers), mapped through the inverse normal to the sphere, through layers 1..48
and the exact tail J_48 (as RQMCJ). Compared with RQMCJ's distribution over 64 independent scramblings at the same N:
mean, median and the fraction of scramblings that beat DSOB. Writes runs/posthoc_dsob_s{seed}.json.
Usage: posthoc_dsob.py SEED MMAX REPS"""
import json
import sys

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
C = 48


def tail_jacobian(Ws, c, u):
    h = u.copy()
    J = np.eye(8)
    for k in range(c, len(Ws)):
        z = Ws[k] @ h
        act = z > 0
        h = np.where(act, z, 0.0)
        J = act[:, None] * (Ws[k] @ J)
    return J


def est_from_U(Ws, U01):
    X = norm.ppf(np.clip(U01, 1e-300, 1 - 1e-16))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    H = ndx.fwd(Ws, X, 0, C)
    us = H[:64].mean(0)
    us /= np.linalg.norm(us)
    J = tail_jacobian(Ws, C, us)
    return J @ (ndx.chi_mean(8) * H.mean(0))


def main():
    seed, mmax, reps = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    Ws = ndx.make_weights(seed)
    tr = json.load(open(BASE + f'runs/truth_s{seed}.json'))
    mu, trV = np.array(tr['trunc_mean']), tr['trV']
    rng = np.random.default_rng([8128, seed])
    out = dict(seed=seed, rows=[])
    for m in range(6, mmax + 1):
        N = 1 << m
        U = qmc.Sobol(d=8, scramble=False).random_base2(m) + 0.5 / N
        e_det = ndx.nmse(est_from_U(Ws, U), mu, trV)
        er = np.array([ndx.nmse(est_from_U(Ws, qmc.Sobol(d=8, scramble=True, seed=rng).random_base2(m)), mu, trV)
                       for _ in range(reps)])
        row = dict(m=m, N=N, cost_mv=(256 - C) * 8.0 + N * (C + 7.0), dsob=e_det, rqmcj_mean=float(er.mean()),
                   rqmcj_median=float(np.median(er)), rqmcj_q10=float(np.quantile(er, 0.1)),
                   frac_rqmcj_better=float((er < e_det).mean()))
        out['rows'].append(row)
        print(seed, 'N 2^%d DSOB %.2e | RQMCJ mean %.2e median %.2e q10 %.2e | share of scramblings better %.2f' % (
            m, e_det, row['rqmcj_mean'], row['rqmcj_median'], row['rqmcj_q10'], row['frac_rqmcj_better']), flush=True)
        json.dump(out, open(BASE + f'runs/posthoc_dsob_s{seed}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
