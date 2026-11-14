"""1D moment-problem bound for one last-layer unit.  MEASURED (grid LP).

PROVEN (elementary): if Q and P0 have equal moments up to order d at the last hidden layer h_{L-1},
then for t = w . h_{L-1} (any fixed w) the 1D laws of t under Q and P0 have equal moments up to
order d.  Hence for f = relu(t),
    |E_Q f - E_P0 f| <= Gamma_d(mu) := sup_{nu : m_k(nu) = m_k(mu), k <= d, supp nu in range(t)} E_nu relu
                                       - inf_{same} E_nu relu,
and the layer-wise matched gap of the full-network LP is <= Gamma_d(law of t under P0), whatever
the depth and whatever is matched at lower layers.  For a readout f = sum_i a_i relu(t_i) the bound is
sum_i |a_i| Gamma_d(mu_i).

Gamma_d is computed by LP on a grid of [-R, R] (intersected with the sign-range of t, estimated from a
2^16 Gaussian sample) plus the sample points themselves.  Grid truncation makes this an
approximation of the sup (not a certified bound).
"""
import math, numpy as np
from scipy.optimize import linprog


def gamma_d(t, w0, d, G=4001):
    mu = float(w0 @ t); s = float(np.sqrt(w0 @ (t - mu) ** 2))
    if s < 1e-12:
        return 0.0, 0.0
    y = (t - mu) / s
    R = 4 + 2 * math.sqrt(d) + float(np.max(np.abs(y)))
    grid = np.linspace(-R, R, G)
    lo_ok, hi_ok = (t.min() >= -1e-12), (t.max() <= 1e-12)
    pts = np.concatenate([grid, y])
    tt = pts * s + mu
    if lo_ok:
        pts = pts[tt >= -1e-12]
    if hi_ok:
        pts = pts[tt <= 1e-12]
    pts = np.union1d(pts, [(-mu) / s])  # the kink
    H = np.empty((d + 1, len(pts))); H[0] = 1
    if d >= 1:
        H[1] = pts
    for k in range(1, d):
        H[k + 1] = pts * H[k] - k * H[k - 1]
    for k in range(d + 1):
        H[k] /= math.sqrt(math.factorial(k))
    Hs = np.empty((d + 1, len(y))); Hs[0] = 1
    if d >= 1:
        Hs[1] = y
    for k in range(1, d):
        Hs[k + 1] = y * Hs[k] - k * Hs[k - 1]
    for k in range(d + 1):
        Hs[k] /= math.sqrt(math.factorial(k))
    b = Hs @ w0
    f = np.maximum(pts * s + mu, 0.0)
    r1 = linprog(-f, A_eq=H, b_eq=b, bounds=(0, None), method="highs")
    r2 = linprog(f, A_eq=H, b_eq=b, bounds=(0, None), method="highs")
    if r1.status or r2.status:
        return None, float(np.sqrt(w0 @ (np.maximum(t, 0) - w0 @ np.maximum(t, 0)) ** 2))
    sdf = float(np.sqrt(w0 @ (np.maximum(t, 0) - w0 @ np.maximum(t, 0)) ** 2))
    return float(-r1.fun - r2.fun), sdf
