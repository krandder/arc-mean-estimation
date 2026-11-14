"""Amendment 5 runs: the variance profile and the bits at layer l on configurations not measured before.
Usage: python scratch/run_bits5.py N L SEED [--dev] -> runs5/bits5_n{N}_L{L}_s{SEED}.json (runs5_dev/ with --dev).
Per net (unit input directions, 2048 fit + 2048 test, as in scratch/run_eval.py):
- the log-radius profile: Var_u log|h_j(u)| for every layer j = 0..L over all 4096 inputs (zero states excluded and
  counted);
- V_ang = tr Var_U A and E|A|^2 on the test split;
- E1 at the cuts l in {L/8, L/4, L/2, 3L/4} with scratch/run_eval.e1_layer (forward-only k-means references,
  M in {1, 4, 16, 64, 256}; no two-sided references): PR, median pairwise angle, the M = 1 spread, D_R(M), D_F(M),
  D_best(M), D_rule(M)."""
import os
import sys
import json
import math
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
sys.path.insert(0, HERE)
import bb
import run_eval


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    dev = '--dev' in sys.argv
    outdir = os.path.join(HERE, '..', 'runs5_dev' if dev else 'runs5')
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    W = bb.make_weights(seed, n, L)
    rng = np.random.default_rng([seed, n, L, 7])
    Nfit = 2048
    U = bb.sphere(rng, 2 * Nfit, n)
    fit, test = U[:Nfit], U[Nfit:]
    cuts = sorted(set([max(1, L // 8), max(1, L // 4), L // 2, (3 * L) // 4]))
    # log-radius profile over all 4096 inputs, every layer
    H = U.copy()
    prof, dead = [0.0], [0]
    for j in range(L):
        H = np.maximum(H @ W[j].T, 0.0)
        r = np.linalg.norm(H, axis=1)
        ok = r > 0
        prof.append(float(np.var(np.log(r[ok]))) if ok.sum() > 1 else None)
        dead.append(int((~ok).sum()))
    keep = set(cuts) | {L}
    Hf = bb.forward_keep(W, fit, keep)
    Ht = bb.forward_keep(W, test, keep)
    Af, At = Hf[L], Ht[L]
    Vang = float(np.sum(At.var(axis=0)))
    mu = At.mean(axis=0)
    res = {'n': n, 'L': L, 'seed': seed, 'Nfit': Nfit, 'Vang': Vang, 'mu2': float(mu @ mu),
           'EA2': float(np.mean(np.sum(At * At, axis=1))), 'logr_var_profile': prof, 'dead_profile': dead,
           'dead': bool(Vang <= 1e-300), 'E1': []}
    if not res['dead']:
        for l in cuts:
            res['E1'].append(run_eval.e1_layer(W, l, Hf, Ht, Af, At, Vang, rng, [1, 4, 16, 64, 256], []))
            print(f'E1 l={l} done {time.time() - t0:.0f}s', flush=True)
    res['seconds'] = time.time() - t0
    json.dump(res, open(os.path.join(outdir, f'bits5_n{n}_L{L}_s{seed}.json'), 'w'), indent=1)
    print(f'done {res["seconds"]:.0f}s', flush=True)


if __name__ == '__main__':
    main()
