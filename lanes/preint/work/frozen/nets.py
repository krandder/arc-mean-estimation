"""Nets and references for lane preint, identical to the earlier lanes' (so exponents compare directly).

- ARC family (He-ReLU, W_l iid N(0, 2/n), no bias, square n x n, input dim d = n): arc-noisy anet.make_weights
  (numpy RandomState(1_000_003 + 7919 seed)); nets 200-204 at 256 x 32 (truths arc-noisy truth/truth_256_32_s0_seed*.npz,
  2^26 paths) and the arc-update ladder seeds 300-307 at (32, 4), (64, 8), (128, 16) (truths arc-update
  runs/truth_n*_L*_s*.npz, 2^24 paths).
- Narrow-deep 8 x 256 (nd-exact ndx.make_weights == narrow-deep nd.make_weights('plain', seed, 8, 256)); truths
  nd-exact runs/truth_s*.json (J_64 E[h_64], replicate SE 3e-10 to 9e-10 in nMSE).
- Small nets for asymptotic checks: same ARC stream at small n.
Cost unit: one forward pass = 2 n^2 L FLOPs (au.pass_flops); for 8 x 256 one pass = 256 nd-exact mv.
"""
import json
import math
import os

import numpy as np

ARC_NOISY = '/home/agent/workspaces/mats/work/arc-noisy'
ARC_UPDATE = '/home/agent/workspaces/mats/work/arc-update'
ND_EXACT = '/home/agent/workspaces/mats/work/nd-exact'


def arc_weights(seed, n, L):
    """anet.make_weights(seed, n, L) as float64 numpy (same stream: RandomState(1_000_003 + 7919 seed))."""
    rs = np.random.RandomState(1_000_003 + 7919 * seed)
    return [rs.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(L)]


def nd_weights(seed, n=8, L=256):
    """ndx.make_weights(seed) (narrow-deep 'plain' stream)."""
    rs = np.random.RandomState((2_000_003 + 7919 * seed + 104729 * n + 0) % (2 ** 32))
    lm = max(256, L)
    return [rs.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(lm)][:L]


def pass_flops(n, L):
    return 2.0 * n * n * L


def arc_truth(seed, n, L):
    """(mean (n,), per-unit variance (n,), N paths) of the output h_L."""
    if (n, L) == (256, 32):
        d = np.load(os.path.join(ARC_NOISY, 'truth', f'truth_{n}_{L}_s0_seed{seed}.npz'))
        N = float(d['N'])
        S1, S2 = d['S1'], d['S2']
        if S1.ndim == 2:
            S1, S2 = S1[-1], S2[-1]
        mean = S1 / N
        return mean, S2 / N - mean ** 2, N
    d = np.load(os.path.join(ARC_UPDATE, 'runs', f'truth_n{n}_L{L}_s{seed}.npz'))
    keys = list(d.keys())
    if 'mean' in keys:
        mean, var = d['mean'], d['var']
        if mean.ndim == 2:
            mean, var = mean[-1], var[-1]
        return mean, var, float(d['N']) if 'N' in keys else float('nan')
    N = float(d['N'])
    S1 = d['S1A'] + d['S1B'] if 'S1A' in keys else d['S1']
    S2 = d['S2A'] + d['S2B'] if 'S2A' in keys else d['S2']
    if S1.ndim == 2:
        S1, S2 = S1[-1], S2[-1]
    mean = S1 / N
    return mean, S2 / N - mean ** 2, N


def nd_truth(seed):
    """nd-exact truth: (mean (8,), tr Var(a))."""
    d = json.load(open(os.path.join(ND_EXACT, 'runs', f'truth_s{seed}.json')))
    return d


def mean_radius(n):
    """E|x| for x ~ N(0, I_n) (same as unrestricted nets.mean_radius; mlmc.py imports it by name)."""
    from scipy.special import gammaln
    return math.exp(0.5 * math.log(2.0) + gammaln((n + 1) / 2.0) - gammaln(n / 2.0))


def sphere_from_gauss(G):
    return G / np.linalg.norm(G, axis=1, keepdims=True)
