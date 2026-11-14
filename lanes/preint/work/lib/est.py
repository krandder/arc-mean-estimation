"""Estimators of E_x f(x), x ~ N(0, I_d), for lane preint, each returning (estimate, cost in FLOPs, info).

All are unbiased (PI-J and RQMCJ under nd-exact's one-downstream-class premise), so MSE = variance and can be
estimated from independent replicates. Costs are counted FLOPs (flopscope conventions: matvec n (2m - 1), ReLU 1 per
unit, inverse normal 96, normal draw 16, Student-t cdf 200); one forward pass = 2 n^2 L.

  MC        f(x), x iid N(0, I)
  RB        E chi_d f(x / |x|) (radius exact by homogeneity), iid directions
  RQMC      f(x), x = Phi^{-1}(scrambled Sobol in d dims) (as arc-update's au.rqmc)
  RQMCRB    E chi_d f(x / |x|) with x from scrambled Sobol (nd-exact's sphere convention)
  PI        mean over lines of int f(yhat + s u) w(s) ds (line + radius exact, lib/line.py); yhat from scrambled
            Sobol in d - 1 dims (outer='rqmc') or iid (outer='mc'); u random per replicate ('rand') or the top
            eigenvector of a pilot estimate of E[J^T J] ('as', Liu-Owen active subspace; pilot charged)
  RQMCJ, PIJ (narrow-deep): the same with the net cut at layer c and the tail map J_c (nd-exact RQMCJ)
"""
import math

import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc

import line as LN

F_NINV, F_DRAW = 96, 16


def mv_flops(Ws):
    return sum(W.shape[0] * (2 * W.shape[1] - 1) + W.shape[0] for W in Ws)


def forward(Ws, X, chunk=1 << 13):
    out = []
    for i in range(0, X.shape[0], chunk):
        h = X[i:i + chunk]
        for W in Ws:
            h = np.maximum(h @ W.T, 0.0)
        out.append(h)
    return np.concatenate(out, axis=0)


def sobol(d, m_pow, rng):
    eng = qmc.Sobol(d=d, scramble=True, seed=rng)
    return eng.random_base2(m_pow)


def tail_jacobian(Ws, c, ustar):
    """nd-exact's J_c: Jacobian of layers c+1..L along the downstream class of ustar."""
    n = Ws[0].shape[0]
    h = ustar.copy()
    J = np.eye(n)
    for k in range(c, len(Ws)):
        z = Ws[k] @ h
        act = z > 0
        h = np.where(act, z, 0.0)
        J = act[:, None] * (Ws[k] @ J)
    return J


def point_estimator(Ws, N_pow, rng, kind, chunk=1 << 13, J=None):
    """MC, RB, RQMC, RQMCRB with N = 2^N_pow points; Ws may be a prefix (cut) with J applied at the end."""
    d = Ws[0].shape[1]
    N = 1 << N_pow
    radius = kind in ('RB', 'RQMCRB')
    if kind in ('RQMC', 'RQMCRB'):
        eng = qmc.Sobol(d=d, scramble=True, seed=rng)
    s = None
    done = 0
    while done < N:
        k = min(chunk, N - done)
        if kind in ('RQMC', 'RQMCRB'):
            X = ndtri(np.clip(eng.random(k), 1e-300, 1 - 1e-16))
        else:
            X = rng.standard_normal((k, d))
        if radius:
            X /= np.linalg.norm(X, axis=1, keepdims=True)
        H = forward(Ws, X)
        acc = H.sum(0)
        s = acc if s is None else s + acc
        done += k
    est = s / N
    if radius:
        est = est * LN.chi_mean(d)
    per = mv_flops(Ws) + d * (F_NINV if kind.startswith('RQMC') else F_DRAW) + (3 * d if radius else 0)
    cost = N * per
    if J is not None:
        est = J @ est
        cost += J.shape[0] * (2 * J.shape[1] - 1)
    return est, float(cost), {}


def vjp_directions(Ws, X, R):
    """Rows J(x_i)^T r_i for a bias-free ReLU net (forward with masks, then backward)."""
    masks = []
    h = X
    for W in Ws:
        z = h @ W.T
        masks.append(z > 0)
        h = np.maximum(z, 0.0)
    g = R.copy()
    for W, M in zip(reversed(Ws), reversed(masks)):
        g = (g * M) @ W
    return g


def active_direction(Ws, P, rng):
    """Top eigenvector of the pilot estimate (1/P) sum_i g_i g_i^T, g_i = J(x_i)^T r_i, r_i ~ N(0, I); x_i iid.
    Cost: P forward + P backward passes, draws, and an SVD of the d x P matrix (nominal 4 d P^2)."""
    d = Ws[0].shape[1]
    n_out = Ws[-1].shape[0]
    X = rng.standard_normal((P, d))
    Rr = rng.standard_normal((P, n_out))
    G = vjp_directions(Ws, X, Rr)
    _, _, Vt = np.linalg.svd(G, full_matrices=False)
    u = Vt[0] / np.linalg.norm(Vt[0])
    cost = 2 * P * mv_flops(Ws) + P * (d + n_out) * F_DRAW + 4 * d * P * P
    return u, float(cost)


def pi_estimator(Ws, N_pow, rng, u_mode='rand', outer='rqmc', eps=None, J=None, P_as=64, u=None):
    """PI: line + radius exact on N = 2^N_pow lines. Returns (estimate, cost, info with vertex counts)."""
    d = Ws[0].shape[1]
    N = 1 << N_pow
    cost = 0.0
    if u is None:
        if u_mode == 'rand':
            u = rng.standard_normal(d)
            u /= np.linalg.norm(u)
            cost += d * F_DRAW + 3 * d
        elif u_mode == 'as':
            u, c = active_direction(Ws if J is None else Ws, P_as, rng)
            cost += c
        elif u_mode == 'jac':
            u, c = jacobian_direction(Ws, P_as, rng)
            cost += c
        else:
            raise ValueError(u_mode)
    B = LN.orth_basis(u)
    cost += 2.0 * d ** 3                                 # QR for the basis of u-perp (nominal)
    Uu = sobol(d - 1, N_pow, rng) if outer == 'rqmc' else rng.random((N, d - 1))
    Y = LN.bases_from_uniform(Uu, B)
    wt = LN.Weight('student', d - 1)
    I, fl, cnt = LN.line_integrals(Ws, Y, u, wt, J=J, eps=eps, rng=rng)
    cost += float(fl.sum()) + N * LN.setup_flops(d)
    return I.mean(0), cost, dict(vertices_mean=float(cnt[:, -1].mean()), line_var=float(I.var(0).sum()))


def mlmc_estimator(Ws, budget_pow, rng, r, P_pilot=256):
    """Two-level shared-trajectory sampler (unrestricted lane, lib/mlmc.py): levels [0, r]; pilot allocation charged.
    budget 2^budget_pow passes for the levels. Returns (estimate, cost in FLOPs, info)."""
    import sys as _s
    p = '/home/agent/workspaces/mats/work/unrestricted/lib'
    if p not in _s.path:
        _s.path.insert(0, p)
    import mlmc as ML
    n, L = Ws[0].shape[0], len(Ws)
    ref = ML.ReferencePath(Ws, rng)
    levels = [0, r]
    V, C = ML.pilot_level_stats(Ws, ref, levels, rng, P=P_pilot)
    Nj = ML.allocate(V, C, float(2 ** budget_pow))
    est, cost = ML.mlmc_estimate(Ws, ref, levels, Nj, rng)
    cost += P_pilot * sum(C)
    return est, float(cost * 2.0 * n * n * L), dict(Nj=[int(x) for x in Nj])


def jacobian_direction(Ws, P, rng, iters=12):
    """Top right singular vector of the cloud-averaged Jacobian E[J(x)] (main's 'top future-relevant direction'),
    by power iteration on a fixed pilot of P iid inputs: forward-mode products J(x) v and backward J(x)^T w with the
    pilot's stored masks. Cost charged: P forward passes + 2 P passes per iteration + draws. (Post hoc; not in PREREG.)"""
    d = Ws[0].shape[1]
    X = rng.standard_normal((P, d))
    masks = []
    h = X
    for W in Ws:
        z = h @ W.T
        masks.append(z > 0)
        h = np.maximum(z, 0.0)
    v = rng.standard_normal(d)
    v /= np.linalg.norm(v)
    for _ in range(iters):
        t = np.repeat(v[None, :], P, axis=0)
        for W, M in zip(Ws, masks):
            t = (t @ W.T) * M
        w = t.mean(0)                                  # E[J] v
        g = np.repeat(w[None, :], P, axis=0)
        for W, M in zip(reversed(Ws), reversed(masks)):
            g = (g * M) @ W
        v = g.mean(0)                                  # E[J]^T E[J] v
        v /= np.linalg.norm(v)
    cost = (1 + 2 * iters) * P * mv_flops(Ws) + P * d * F_DRAW
    return v, float(cost)
