"""Amendment 1 runs (F1): dyadic multilevel samplers with radial merges at M forward-only references per level, against
the one-reference (random direction) multilevel sampler of the unrestricted lane. Usage:
    python scratch/run_ml.py N L SEED
Writes runs/ml_n{N}_L{L}_s{SEED}.json. Unit input directions; A(U) = h_L(U); V_ang = tr Var A (test split).
Levels: r in {L/2^j : j = 1..J, r >= 1} (dyadic), merges radial: F_r(U) = |h_r(U)| g_r(c_k)/|c_k| with c_k the
reference assigned to U's direction at r (k-means on the fit split, M per level; M = 1 is the central reference,
"rand" is one random reference direction propagated through the net, shared by all levels as in lib/mlmc.py;
"trajM" uses M reference trajectories chosen by k-means at the deepest level and shared by all levels, each sample
merged at each level with its nearest reference state).
For every subset S of the dyadic levels (the final exact level always included) the ideal cost-variance product
(sum_j sqrt(V_j C_j))^2 / V_ang is computed, V_j the variance of consecutive differences within S (the first level is
F_{r_min} itself), C_j = r_j / L (prefix), C_final = 1. The best subset is reported (optimistic: selected on the same
test split) together with the full dyadic set. Setup per level: M future passes of length L - r (one per reference)."""
import os
import sys
import json
import math
import itertools
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import bb


def unit(X):
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-300)


def nearest_members(Ufit, centres, labels):
    idx = np.zeros(centres.shape[0], dtype=int)
    for k in range(centres.shape[0]):
        sel = np.where(labels == k)[0]
        idx[k] = int(sel[np.argmax(Ufit[sel] @ centres[k])]) if sel.size else int(np.argmax(Ufit @ centres[k]))
    return idx


def best_hierarchy(F, A, levels, L, Vang):
    """F: dict r -> (N, n) merged estimates; A: (N, n) outputs. Returns (best ratio, best subset, full ratio)."""
    rs = sorted(levels)
    best = (float('inf'), None)
    full = None
    for k in range(1, len(rs) + 1):
        for S in itertools.combinations(rs, k):
            terms = []
            prev = None
            for r in S:
                X = F[r] if prev is None else F[r] - F[prev]
                V = float(np.sum(X.var(axis=0)) / Vang)
                terms.append(math.sqrt(V * r / L))
                prev = r
            V = float(np.sum((A - F[prev]).var(axis=0)) / Vang)
            terms.append(math.sqrt(V * 1.0))
            val = sum(terms) ** 2
            if val < best[0]:
                best = (val, list(S))
            if k == len(rs):
                full = val
    return best[0], best[1], full


def main():
    n, L, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    t0 = time.time()
    W = bb.make_weights(seed, n, L)
    rng = np.random.default_rng([seed, n, L, 11])
    Nfit = 2048
    U = bb.sphere(rng, 2 * Nfit, n)
    fit, test = U[:Nfit], U[Nfit:]
    levels = []
    r = L // 2
    while r >= 1 and len(levels) < 7:
        levels.append(r)
        r //= 2
    keep = set(levels) | {L}
    Hf = bb.forward_keep(W, fit, keep)
    Ht = bb.forward_keep(W, test, keep)
    A = Ht[L]
    Vang = float(np.sum(A.var(axis=0)))
    out = {'n': n, 'L': L, 'seed': seed, 'levels': levels, 'Vang': Vang}
    if Vang <= 1e-300:
        out['dead'] = True
        json.dump(out, open(f'runs/ml_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
        return
    # random reference direction (shared by all levels)
    q = bb.sphere(rng, 1, n)
    Q = bb.forward_keep(W, q, keep)
    variants = {}
    F = {}
    for r in levels:
        cq = Q[r][0]
        gq = bb.forward(W, cq[None, :], r)[0]
        F[r] = (np.linalg.norm(Ht[r], axis=1) / max(np.linalg.norm(cq), 1e-300))[:, None] * gq[None, :]
    variants['rand'] = best_hierarchy(F, A, levels, L, Vang) + (1.0,)
    # M reference trajectories: fit points nearest the k-means centres of the fit cloud at the deepest level r_max,
    # propagated through the whole net; at each level U is merged with its nearest reference state (by direction).
    rmax = max(levels)
    for M in [4, 16, 64, 256]:
        Uf = unit(Hf[rmax])
        C, lab = bb.kmeans_dirs(Uf, M, rng)
        idx = nearest_members(Uf, C, lab)
        Rt = {r: Hf[r][idx] for r in levels}
        gR = Hf[L][idx]
        F = {}
        for r in levels:
            a_t = np.argmax(unit(Ht[r]) @ unit(Rt[r]).T, axis=1)
            ratio = np.linalg.norm(Ht[r], axis=1) / np.maximum(np.linalg.norm(Rt[r][a_t], axis=1), 1e-300)
            F[r] = ratio[:, None] * gR[a_t]
        # setup: M full reference passes (already among the fit points' passes; charged anyway)
        variants[f'traj{M}'] = best_hierarchy(F, A, levels, L, Vang) + (float(M),)
    out['variants'] = {k: {'best': v[0], 'best_levels': v[1], 'full_dyadic': v[2], 'setup_passes': v[3]}
                       for k, v in variants.items()}
    out['seconds'] = time.time() - t0
    json.dump(out, open(f'runs/ml_n{n}_L{L}_s{seed}.json', 'w'), indent=1)
    print(json.dumps(out['variants']), flush=True)


if __name__ == '__main__':
    main()
