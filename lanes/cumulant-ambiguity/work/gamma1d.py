"""Gamma_d(mu): 1D moment-problem ambiguity of E relu(t) given the first d moments of t ~ mu.
MEASURED (grid LP; numerically stable via the discrete Stieltjes procedure).

mu = empirical law of t (a sample with weights w).  Orthonormal polynomials p_0..p_d of mu are built
by the Stieltjes three-term recurrence on the sample; they are evaluated on a candidate support
(grid on the sign-range of t, plus the sample, plus the kink t=0).  LP:
    max / min  sum_j q_j relu(t_j)   s.t. q >= 0, sum_j q_j p_k(t_j) = [k == 0], k = 0..d.
Gamma_d = max - min.  Restricting the support to a grid makes max-min a slight under-estimate of the
true sup-inf over all laws on the range.
"""
import math, numpy as np
from scipy.optimize import linprog


def stieltjes(t, w, d):
    """Recurrence coefficients (alpha_k, beta_k) of the orthonormal polys of sum_j w_j delta_{t_j}."""
    al, be = np.zeros(d + 1), np.zeros(d + 1)
    p_prev = np.zeros_like(t); p = np.ones_like(t) / math.sqrt(w.sum())
    for k in range(d + 1):
        al[k] = w @ (t * p * p)
        q = (t - al[k]) * p - (be[k] * p_prev if k > 0 else 0)
        nb = math.sqrt(max(w @ (q * q), 0.0))
        if k < d:
            be[k + 1] = nb
            p_prev, p = p, q / nb
    return al, be


def eval_orth(x, al, be, d, w0sum=1.0):
    P = np.empty((d + 1, len(x)))
    P[0] = 1.0 / math.sqrt(w0sum)
    if d >= 1:
        P[1] = (x - al[0]) * P[0] / be[1]
    for k in range(1, d):
        P[k + 1] = ((x - al[k]) * P[k] - be[k] * P[k - 1]) / be[k + 1]
    return P


def gamma_d(t, w, d, G=2001, nsup=500):
    mu = float(w @ t); s = float(np.sqrt(w @ (t - mu) ** 2))
    r = np.maximum(t, 0.0); sdr = float(np.sqrt(w @ (r - w @ r) ** 2))
    if s < 1e-12 or sdr < 1e-12:
        return 0.0, sdr
    y = (t - mu) / s
    k0 = -mu / s
    lo, hi = y.min(), y.max()
    span = hi - lo
    glo = lo - 0.5 * span if t.min() < -1e-12 else k0
    ghi = hi + 0.5 * span if t.max() > 1e-12 else k0
    grid = np.linspace(glo, ghi, G)
    sub = y[np.random.default_rng(0).choice(len(y), min(nsup, len(y)), replace=False)]
    pts = np.unique(np.concatenate([grid, sub, [k0]]))
    al, be = stieltjes(y, w, d)
    if np.any(be[1:] < 1e-10):
        return None, sdr  # mu has <= d support points: not handled (co-prover r1: Gamma is not 0)
    A = eval_orth(pts, al, be, d)
    b = np.zeros(d + 1); b[0] = 1.0
    f = np.maximum(pts * s + mu, 0.0)
    r1 = linprog(-f, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    r2 = linprog(f, A_eq=A, b_eq=b, bounds=(0, None), method="highs")
    if r1.status or r2.status:
        return None, sdr
    return float(-r1.fun - r2.fun), sdr


if __name__ == "__main__":
    t = np.random.default_rng(0).standard_normal(20000); w = np.full(20000, 1 / 20000)
    for d in (2, 4, 8, 12, 16):
        g, s = gamma_d(t, w, d); print(d, g / s)
