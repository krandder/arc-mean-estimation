"""Amendment 1 (E5): RQMC replicate variances at extra sizes for rate exponents, one net: scrambled Sobol, radius
exact, standard and polar frames, at N = 2^8 (R = 32) and N = 2^18 (R = 8). Together with E1 (2^10, 2^12, 2^14;
R = 16) and E2 (2^16; R = 16) this gives N = 2^8..2^18 for the exponent fits in scratch/rate_fit.py.
Usage: rates.py seed [--n 256 --L 32] [--out PATH]
"""
import argparse
import json
import math
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import rnd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int)
ap.add_argument('--n', type=int, default=256); ap.add_argument('--L', type=int, default=32)
ap.add_argument('--out', default=None)
a = ap.parse_args()
t0 = time.time()
n, L = a.n, a.L
net = rnd.Net(a.seed, n, L)
truth = rnd.load_truth(a.seed, n, L)
V = truth['V']
Qp = rnd.basis_polar(net.W64[0].numpy())
res = dict(seed=a.seed, n=n, L=L, V=V, series={})
for mlog, R in ((8, 32), (18, 8)):
    for frame, Q in (('std', None), ('polar', Qp)):
        ests = []
        for r in range(R):
            Pu = rnd.sobol_unit(mlog, n, scramble=True, seed=70_000 * a.seed + 1000 * mlog + r + (0 if Q is None else 500))
            Z = rnd.gauss_from_unit(Pu)
            U = rnd.to_sphere(Z if Q is None else rnd.apply_basis(Z, Q))
            ests.append(rnd.rb_estimate(net, U))
        ests = np.array(ests)
        N = 1 << mlog
        var = float(np.sum(ests.var(0, ddof=1)))
        errs = np.sum((ests - truth['mean']) ** 2, axis=1) / V
        res['series'].setdefault(f'rqmc_{frame}', []).append(dict(N=N, R=R, var_x_N_over_V=var * N / V,
                                                                  nmse_mean=float(errs.mean()), reps=ests.tolist()))
        print(f'[{time.time() - t0:7.1f}s] seed={a.seed} rqmc_{frame} N=2^{mlog}: var*N/V={var * N / V:.3f} '
              f'nmse*N={errs.mean() * N:.3f}', flush=True)
out = a.out or os.path.join(os.path.dirname(__file__), '..', 'runs', f'rates_n{n}_L{L}_s{a.seed}.json')
with open(out, 'w') as fh:
    json.dump(res, fh)
print('done ->', out, flush=True)
