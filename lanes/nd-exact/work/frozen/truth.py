"""Reference E[a] for one net (sigma = 0), two independent constructions.

(1) TRUNC: E[a] = J_c E[h_c] with E[h_c] = E|x| * mean f_c(x/|x|) over R scrambled-Sobol replicates of 2^m points
    (radius exact by homogeneity). J_c = Jacobian of layers c+1..256 on the downstream class of the reference
    direction u* (the normalised mean of h_c over the first replicate). Valid when all live states at c share that
    class; checked on (2)'s samples.
(2) FULL: plain full-depth MC with 2^m2 Gaussian inputs: E[a], tr Var(a), and the fraction (by |a| mass and by count) of
    inputs whose downstream pattern at c differs from u*'s, with their contribution to E[a].
Usage: truth.py SEED C LOG2M R LOG2M2 OUT.json
"""
import json
import sys
import time

import numpy as np
from scipy.stats import norm, qmc

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/frozen')
import ndx  # noqa: E402


def tail_jacobian(Ws, c, u):
    """Downstream pattern of state u at cut c and the Jacobian J of layers c+1..L on that class."""
    L = len(Ws)
    h = u.copy()
    J = np.eye(len(u))
    pat = []
    for k in range(c, L):
        z = Ws[k] @ h
        act = z > 0
        pat.append(act)
        h = np.where(act, z, 0.0)
        J = act[:, None] * (Ws[k] @ J)
    return J, np.array(pat), h


def main():
    seed, c, m, R, m2, outp = [int(v) for v in sys.argv[1:6]] + [sys.argv[6]]
    Ws = ndx.make_weights(seed)
    n = 8
    cE = ndx.chi_mean(n)
    t0 = time.time()
    reps = []
    ustar = None
    J = None
    chunk = 1 << 18
    for r in range(R):
        eng = qmc.Sobol(d=n, scramble=True, seed=np.random.default_rng([9001, seed, r]))
        s = np.zeros(n)
        for _ in range((1 << m) // chunk if (1 << m) >= chunk else 1):
            M = min(chunk, 1 << m)
            X = norm.ppf(np.clip(eng.random(M), 1e-300, 1 - 1e-16))
            U = X / np.linalg.norm(X, axis=1, keepdims=True)
            s += ndx.fwd(Ws, U, 0, c).sum(0)
        Ehc = cE * s / (1 << m)
        if ustar is None:
            ustar = Ehc / np.linalg.norm(Ehc)
            J, tpat, _ = tail_jacobian(Ws, c, ustar)
        reps.append(J @ Ehc)
        print('rep', r, 'time %.0f' % (time.time() - t0), flush=True)
    reps = np.array(reps)
    trunc_mean = reps.mean(0)
    trunc_se2 = float(reps.var(0, ddof=1).sum() / R) if R > 1 else float('nan')
    # (2) full-depth MC with downstream-class check
    rng = np.random.default_rng([9002, seed])
    s, s2, rest, n_out, a_out, a_tot = np.zeros(n), np.zeros(n), np.zeros(n), 0, 0.0, 0.0
    N2 = 1 << m2
    for _ in range(max(N2 // chunk, 1)):
        M = min(chunk, N2)
        X = rng.standard_normal((M, n))
        hc = ndx.fwd(Ws, X, 0, c)
        a, pat = ndx.fwd_patterns(Ws, hc, c, len(Ws))
        alive = np.linalg.norm(hc, axis=1) > 0
        refp = np.packbits(tpat, axis=1, bitorder='little')[:, 0]
        same = (pat == refp[None, :]).all(1)
        out = alive & ~same
        s += a.sum(0)
        s2 += (a * a).sum(0)
        rest += a[out].sum(0)
        n_out += int(out.sum())
        na = np.linalg.norm(a, axis=1)
        a_out += float(na[out].sum())
        a_tot += float(na.sum())
    full_mean = s / N2
    trV = float((s2 / N2 - full_mean ** 2).sum() * N2 / (N2 - 1))
    res = dict(seed=seed, c=c, log2m=m, R=R, log2m2=m2, trunc_mean=trunc_mean.tolist(),
               trunc_reps=reps.tolist(), trunc_se2_nmse=trunc_se2 / trV, full_mean=full_mean.tolist(), trV=trV,
               full_vs_trunc_nmse=ndx.nmse(full_mean, trunc_mean, trV), full_mc_nmse_expected=1.0 / N2,
               out_of_class_count=n_out, out_of_class_amass=a_out / a_tot,
               out_of_class_contrib_nmse=float(np.sum((rest / N2) ** 2) / trV),
               J=J.tolist(), J_singular_values=np.linalg.svd(J, compute_uv=False).tolist(), ustar=ustar.tolist(),
               seconds=time.time() - t0)
    json.dump(res, open(outp, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ('trunc_reps', 'J')}, indent=0))


if __name__ == '__main__':
    main()
