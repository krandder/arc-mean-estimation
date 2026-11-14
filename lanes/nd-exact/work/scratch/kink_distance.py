"""Why certified cells are out of reach at width 8: the distance from a random input direction to the boundary of its
activation region (layers 1..k), d_k(u) = min over layers l <= k and units j of |w_lj . u| / |w_lj|, where w_lj is the
pre-activation row of the region's linear map (this equals the distance to the nearest facet). A cell around u is
certifiable only if it fits inside that ball, so covering the sphere with certifiable cells takes about
E[(r0 / d_k(u))^7] cells of radius r0-scale; we report quantiles of d_k and E[d_k^-7] relative to the sphere.
Usage: kink_distance.py SEED LOG2N OUT.json"""
import json
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

DEPTHS = [1, 2, 4, 8, 16, 32]


def main():
    seed, m, outp = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    N = 1 << m
    Ws = ndx.make_weights(seed)
    rng = np.random.default_rng([1618, seed])
    X = rng.standard_normal((N, 8))
    U = X / np.linalg.norm(X, axis=1, keepdims=True)
    A = np.broadcast_to(np.eye(8), (N, 8, 8)).copy()   # linear map of each input's region so far
    h = U.copy()
    dmin = np.full(N, np.inf)
    out = dict(seed=seed, N=N, depths={})
    for l in range(1, 33):
        Wl = Ws[l - 1]
        M = np.einsum('ij,njk->nik', Wl, A)              # pre-activation rows (N, 8, 8)
        z = np.einsum('nik,nk->ni', M, U)
        nr = np.linalg.norm(M, axis=2)
        live = nr > 0
        d = np.where(live, np.abs(z) / np.where(live, nr, 1.0), np.inf)
        dmin = np.minimum(dmin, d.min(1))
        act = z > 0
        A = act[:, :, None] * M
        if l in DEPTHS:
            dd = dmin[np.isfinite(dmin)]
            q = np.quantile(dd, [0.01, 0.1, 0.5, 0.9])
            out['depths'][str(l)] = dict(q01=float(q[0]), q10=float(q[1]), median=float(q[2]), q90=float(q[3]),
                                         mean_inv7=float(np.mean(dd ** -7.0)), dead_frac=float((~np.isfinite(dmin)).mean()))
            print(seed, 'depth', l, 'distance to region boundary: q01 %.2e q10 %.2e median %.2e q90 %.2e; E[d^-7] %.2e'
                  % (q[0], q[1], q[2], q[3], np.mean(dd ** -7.0)), flush=True)
    json.dump(out, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
