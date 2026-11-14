"""Amendment 3 (C4 cheapest test): the exact single-Gaussian recursion (lib/closure.py) against the truth along
L = alpha n. Usage: python scratch/run_closure.py N L SEED -> runs/closure_n{N}_L{L}_s{SEED}.json.
Truth: two independent Monte Carlo estimates mu1, mu2 of E h_L(x), x ~ N(0, I), each with Nmc inputs; the closure's
squared error is estimated without the samplers' noise by (a - mu1).(a - mu2) (unbiased for |a - mu|^2); normalised by
V = tr Var h_L(x) (pooled samples). Cost of the closure in single-input forward passes (2 n^2 L FLOPs each): the two
n x n x n products per layer for W S W^T give 2 n passes (the asymptotic cost, reported as cost_passes_matmul and used
for the gain, generous to the closure); the pairwise moments of this implementation add about (60 q + 1130)/2 passes at
flopscope-like rates (q = 48 nodes of 60 FLOPs, 8 normal cdf at 96 and 6 pdf at 54 FLOPs per pair), reported as
cost_passes_impl."""
import os
import sys
import json
import math
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb
import closure


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t0 = time.time()
    W = bb.make_weights(seed, n, L)
    a = closure.gaussian_recursion(W, q=48)
    tc = time.time() - t0
    rng = np.random.default_rng([seed, n, L, 17])
    Nmc = 1 << 16 if n <= 64 else 1 << 15
    est = []
    s1 = np.zeros(n)
    s2 = 0.0
    tot = 0
    for rep in range(2):
        acc = np.zeros(n)
        done = 0
        while done < Nmc:
            b = min(8192, Nmc - done)
            X = rng.standard_normal((b, n))
            H = bb.forward(W, X)
            acc += H.sum(axis=0)
            s1 += H.sum(axis=0)
            s2 += float(np.sum(H * H))
            done += b
        est.append(acc / Nmc)
        tot += Nmc
    mean_all = s1 / tot
    V = s2 / tot - float(mean_all @ mean_all)
    cross = float((a - est[0]) @ (a - est[1]))
    out = {'n': n, 'L': L, 'seed': seed, 'Nmc_each': Nmc, 'V': V, 'closure_sqerr_unbiased': cross,
           'nMSE_closure': cross / V if V > 0 else None,
           'mc_halves_sqdiff_over_V': float(np.sum((est[0] - est[1]) ** 2) / V) if V > 0 else None,
           'cost_passes_matmul': 2 * n, 'cost_passes_impl': 2 * n + (60 * 48 + 1130) / 2, 'closure_seconds': tc, 'seconds': time.time() - t0}
    json.dump(out, open(f'runs/closure_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
