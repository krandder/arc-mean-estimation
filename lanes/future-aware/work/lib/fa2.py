"""Part 2 helpers (width extension to n = 512, L = 64): truth loading from this lane's runs/ for widths not covered by
the arc-update truths; everything else is lib/fa.py (frozen for Part 1)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fa  # noqa: E402

FA_RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')


def load_net(n, L, seed):
    p = os.path.join(FA_RUNS, f'truth_n{n}_L{L}_s{seed}.npz')
    if not os.path.exists(p):
        return fa.load_net(n, L, seed)
    W = fa.au.weights(seed, n, L)
    d = np.load(p)
    N = float(d['N']); S1 = d['S1A'] + d['S1B']; S2 = d['S2A'] + d['S2B']
    mean = S1 / N
    var = S2 / N - mean ** 2
    return dict(W=W, n=n, L=L, seed=seed, mean=mean, var=var, Y=mean[-1].copy(), V=float(var[-1].sum()),
                Ntruth=N, truth_path=p)
