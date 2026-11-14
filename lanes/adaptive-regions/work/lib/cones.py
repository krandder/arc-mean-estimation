"""Gaussian measures and first moments of polyhedral cones {x : G x >= 0}, x ~ N(0, I_n).

first_moment(G) = E[x 1_C] = (2 pi)^{-1/2} sum_j g_j/|g_j| P_{n-1}(F_j)    (divergence theorem; FORMAL.md E1 [A])
measure(H) = P(H y >= 0), y ~ N(0, I_k):
  - rank(H) = r < k: the cone is a product with a lineality space; reduce to the row space of H (dimension r);
  - m <= r constraints (simplicial or fewer): orthant probability of z = H y ~ N(0, H H^T) (Genz, scipy);
  - otherwise: vertex enumeration of the bounded cross-section {c.y = 1, H y >= 0} (c = sum of unit normals), Delaunay
    triangulation into simplices, each simplex a simplicial cone {R a, a >= 0} = {R^{-1} y >= 0}: orthant probability
    of N(0, R^{-1} R^{-T}).
Numerical (Genz abseps), not symbolic: NUMERICAL label in the report.
"""
import math
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import HalfspaceIntersection, Delaunay, ConvexHull, QhullError
from scipy.stats import multivariate_normal

ABSEPS = 1e-9
METHOD = 'plackett'
GENZ_CALLS = 0
GENZ_BUDGET = None            # raise BudgetExceeded after this many Genz calls (set per cell by callers)


class BudgetExceeded(Exception):
    pass
          # 'plackett' (quadrature) or 'genz' (scipy)


def _unit_dedupe(G, tol=1e-9):
    G = G[np.linalg.norm(G, axis=1) > 1e-12]
    if len(G) == 0:
        return G
    G = G / np.linalg.norm(G, axis=1, keepdims=True)
    keep = []
    for i in range(len(G)):
        if all(np.abs(G[i] - G[j]).max() > tol for j in keep):
            keep.append(i)
    return G[keep]


_GL_X, _GL_W = np.polynomial.legendre.leggauss(32)
_GL_T = 0.5 * (_GL_X + 1); _GL_W = 0.5 * _GL_W


def _p_closed_batch(C):
    """Closed-form orthant probabilities for a batch of correlation matrices of size 2 or 3: (B, k, k) -> (B,)."""
    k = C.shape[-1]
    if k == 2:
        return 0.25 + np.arcsin(np.clip(C[:, 0, 1], -1, 1)) / (2 * math.pi)
    return 0.125 + (np.arcsin(np.clip(C[:, 0, 1], -1, 1)) + np.arcsin(np.clip(C[:, 0, 2], -1, 1))
                    + np.arcsin(np.clip(C[:, 1, 2], -1, 1))) / (4 * math.pi)


def orthant_plackett_fast(R):
    """Vectorised Plackett for k = 4, 5 (inner orthant probability in closed form)."""
    k = R.shape[0]
    T = _GL_T[:, None, None]
    Rt = (1 - T) * np.eye(k)[None] + T * R[None]                          # (G, k, k)
    tot = 2.0 ** -k
    for i in range(k):
        for j in range(i + 1, k):
            rho = R[i, j]
            if abs(rho) < 1e-15:
                continue
            rest = [a for a in range(k) if a != i and a != j]
            # substitution t = sin(alpha) / rho, alpha in [0, asin(rho)]: removes the 1/sqrt(1 - t^2 rho^2) peak
            asr = math.asin(float(np.clip(rho, -1, 1)))
            Tt = (np.sin(_GL_T * asr) / rho)[:, None, None]
            Rt = (1 - Tt) * np.eye(k)[None] + Tt * R[None]
            Sij = Rt[:, [i, j]][:, :, [i, j]]; Srj = Rt[:, rest][:, :, [i, j]]
            C = Rt[:, rest][:, :, rest] - Srj @ np.linalg.solve(Sij, np.transpose(Srj, (0, 2, 1)))
            dg = np.sqrt(np.clip(np.diagonal(C, axis1=1, axis2=2), 1e-300, None)); C = C / (dg[:, :, None] * dg[:, None, :])
            tot += asr * float((_GL_W * _p_closed_batch(C)).sum()) / (2 * math.pi)
    return float(tot)


def orthant_plackett(R):
    """P(z >= 0), z ~ N(0, R), R a correlation matrix, by Plackett's identity along R(t) = (1 - t) I + t R:
    P_k(R) = 2^-k + sum_{i<j} int_0^1 R_ij phi2(0, 0; t R_ij) P_{k-2}(conditional on z_i = z_j = 0) dt,
    with closed forms for k <= 3 and 32-node Gauss-Legendre in t (NUMERICAL)."""
    k = R.shape[0]
    if k == 0:
        return 1.0
    if k == 1:
        return 0.5
    if k == 2:
        return 0.25 + math.asin(float(np.clip(R[0, 1], -1, 1))) / (2 * math.pi)
    if k == 3:
        return 0.125 + (math.asin(float(np.clip(R[0, 1], -1, 1))) + math.asin(float(np.clip(R[0, 2], -1, 1)))
                        + math.asin(float(np.clip(R[1, 2], -1, 1)))) / (4 * math.pi)
    tot = 2.0 ** -k
    I = np.eye(k)
    for i in range(k):
        for j in range(i + 1, k):
            rho = R[i, j]
            if abs(rho) < 1e-15:
                continue
            rest = [a for a in range(k) if a != i and a != j]
            acc = 0.0
            asr = math.asin(float(np.clip(rho, -1, 1)))
            for a_, w in zip(_GL_T * asr, _GL_W):
                t = math.sin(a_) / rho
                Rt = (1 - t) * I + t * R
                phi2 = asr / (2 * math.pi * rho)                     # d alpha = rho phi2 dt (2 pi); weight folded
                Sij = Rt[np.ix_([i, j], [i, j])]; Srj = Rt[np.ix_(rest, [i, j])]
                C = Rt[np.ix_(rest, rest)] - Srj @ np.linalg.solve(Sij, Srj.T)
                dg = np.sqrt(np.clip(np.diag(C), 1e-300, None)); C = C / np.outer(dg, dg)
                acc += w * phi2 * orthant_plackett(C)
            tot += rho * acc
    return float(tot)


def _orthant(S):
    k = S.shape[0]
    d = np.sqrt(np.diag(S)); S = S / np.outer(d, d)                      # orthant probability is scale-free
    if k > 3:
        ev = np.linalg.eigvalsh(S)
        if ev[0] < 1e-12:      # (near) singular: Genz with allow_singular (review 2 item 2: returning 0 was wrong
            mv = multivariate_normal(mean=np.zeros(k), cov=S + 1e-14 * np.eye(k), allow_singular=True,   # for e.g.
                                     abseps=ABSEPS, releps=0, maxpts=200000 * k)                      # rho -> 1)
            return float(mv.cdf(np.zeros(k)))
        if ev[0] < 1e-4 or METHOD != 'plackett':                         # ill-conditioned: Plackett's quadrature is
            global GENZ_CALLS
            GENZ_CALLS += 1
            if GENZ_BUDGET is not None and GENZ_CALLS > GENZ_BUDGET:
                raise BudgetExceeded()
            mv = multivariate_normal(mean=np.zeros(k), cov=S + 1e-14 * np.eye(k), allow_singular=True,
                                     abseps=ABSEPS, releps=0, maxpts=200000 * k)     # inaccurate near |rho| = 1: Genz
            return float(mv.cdf(np.zeros(k)))
    if k == 1:
        return 0.5
    if k == 2:
        rho = S[0, 1] / math.sqrt(S[0, 0] * S[1, 1])
        return 0.25 + math.asin(np.clip(rho, -1, 1)) / (2 * math.pi)
    if k == 3:
        d = np.sqrt(np.diag(S)); R = S / np.outer(d, d)
        R = np.clip(R, -1, 1)
        return 0.125 + (math.asin(R[0, 1]) + math.asin(R[0, 2]) + math.asin(R[1, 2])) / (4 * math.pi)
    if METHOD == 'plackett':
        return orthant_plackett_fast(S) if k in (4, 5) else orthant_plackett(S)
    mv = multivariate_normal(mean=np.zeros(k), cov=S, allow_singular=False, abseps=ABSEPS, releps=0, maxpts=200000 * k)
    return float(mv.cdf(np.zeros(k)))


def _interior(H):
    """Chebyshev-like interior point of {H y >= 0, |y|_inf <= 1}; returns (y, margin)."""
    m, k = H.shape
    c = np.zeros(k + 1); c[-1] = -1.0
    A = np.c_[-H, np.ones(m)]
    r = linprog(c, A_ub=A, b_ub=np.zeros(m), bounds=[(-1, 1)] * k + [(0, 1)], method='highs')
    if r.status != 0:
        return None, 0.0
    return r.x[:k], r.x[-1]


def measure(H, stats=None):
    H = _unit_dedupe(np.atleast_2d(H))
    if len(H) == 0:
        return 1.0
    k = H.shape[1]
    y0, marg = _interior(H)
    if y0 is None or marg < 1e-10:
        return 0.0                                                       # empty or lower-dimensional
    # lineality: reduce to the row space
    U, s, Vt = np.linalg.svd(H, full_matrices=False)
    r = int((s > 1e-10 * s[0]).sum())
    if r < k:
        H = H @ Vt[:r].T; H = _unit_dedupe(H); k = r
        if len(H) == 0:
            return 1.0
        y0, marg = _interior(H)                                          # review 2 item 2: interior point in the
        if y0 is None or marg < 1e-10:                                   # reduced coordinates
            return 0.0
    if len(H) <= k:
        return _orthant(H @ H.T)
    if k == 1:                                          # several constraints on a line: a half-line or empty
        return 0.5 if (np.all(H[:, 0] > 0) or np.all(H[:, 0] < 0)) else 0.0
    if k == 2:                                          # a planar wedge: extreme rays are constraint-line directions
        cand = np.concatenate([np.c_[-H[:, 1], H[:, 0]], np.c_[H[:, 1], -H[:, 0]]])
        feas = [c / np.linalg.norm(c) for c in cand if (H @ c >= -1e-12).all()]
        if len(feas) < 2:
            return 0.0
        F = np.array(feas); G2 = F @ F.T
        i, j = np.unravel_index(np.argmin(G2), G2.shape)
        return math.acos(float(np.clip(G2[i, j], -1, 1))) / (2 * math.pi)
    # pointed, non-simplicial: triangulate the cross-section
    c = H.sum(0); c /= np.linalg.norm(c)
    Q, _ = np.linalg.qr(np.c_[c, np.eye(k)]); B = Q[:, 1:k]               # plane coordinates: y = c + B t
    # H (c + B t) >= 0  ->  -(H B) t - H c <= 0  (Qhull form A t + b <= 0)
    A = -(H @ B); b = -(H @ c)
    # interior point of the cross-section from y0 scaled onto the plane
    y0 = y0 / (c @ y0); t0 = B.T @ (y0 - c)
    try:
        hs = HalfspaceIntersection(np.c_[A, b], t0)
        V = hs.intersections
        V = V[np.isfinite(V).all(1)]
        if len(V) < k:
            return 0.0
        if k - 1 == 1:
            simplices = [np.argsort(V[:, 0])[[0, -1]]]
        else:
            V = V[ConvexHull(V).vertices]                      # drop duplicate / non-extreme intersection points
            simplices = Delaunay(V).simplices
    except (QhullError, ValueError):
        if stats is not None:
            stats['qhull_fail'] = stats.get('qhull_fail', 0) + 1
        return float('nan')
    tot = 0.0
    for sx in simplices:
        R = (c[:, None] + B @ V[sx].T)                                     # k rays as columns
        try:
            Ri = np.linalg.inv(R)
        except np.linalg.LinAlgError:
            continue
        tot += _orthant(Ri @ Ri.T)
    if stats is not None:
        stats['simplices'] = stats.get('simplices', 0) + len(simplices)
    return tot


def first_moment(G, stats=None):
    G = _unit_dedupe(np.atleast_2d(G))
    n = G.shape[1]
    out = np.zeros(n)
    for j in range(len(G)):
        g = G[j]
        Q, _ = np.linalg.qr(np.c_[g, np.eye(n)]); B = Q[:, 1:n]
        p = measure(np.delete(G, j, 0) @ B, stats)
        out += g * p
    return out / math.sqrt(2 * math.pi)
