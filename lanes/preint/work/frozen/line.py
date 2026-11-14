"""Exact pre-integration of a bias-free ReLU net along lines, with the radius integrated too (lane preint).

Net: h_0 = x in R^d, h_l = relu(W_l h_{l-1}) (W_l of shape n_l x n_{l-1}), f(x) = h_L, optionally followed by a
fixed linear map J (the exact linear tail of narrow-deep nets, nd-exact's RQMCJ). f is continuous, piecewise linear
and positively homogeneous: f(r x) = r f(x) for r > 0.

Line + radius (notes/READING.md D1b). For x ~ N(0, I_d) and a unit vector u, write x = rho (yhat + s u) with yhat
uniform on the unit sphere of u-perp, rho ~ chi_{d-1} and s = t / rho. Then, exactly,
    E[f(x) | yhat] = int_R f(yhat + s u) w_k(s) ds,  w_k(s) = k / sqrt(2 pi) (1 + s^2)^(-(k+2)/2),  k = d - 1,
with int w_k = E chi_k (w_k is E chi_k times the density of T / sqrt(k+1), T Student-t with k+1 degrees of freedom).
weight='gauss' gives the classic pre-integration int f(y + t u) phi(t) dt for an unnormalised base y (D1a).

Exact algorithm (D2b). On the half-plane {a yhat + b u : a >= 0} the net is piecewise linear on cones. Each line
keeps an ordered list of vertices (a, b) (vectors a yhat + b u, angle increasing). Full mode starts from -u, yhat,
+u; window mode from e(-psi0), yhat, e(psi0) (e(psi) = cos psi yhat + sin psi u). Layer by layer: one matvec per
vertex gives the pre-activations; along the chord between consecutive vertices every pre-activation is linear, so a
strict sign change of unit j on a segment gives a new vertex at the chord point where z_j = 0, with its
pre-activation vector interpolated exactly (no matvec); then ReLU. After the last layer f is linear on each cone
between consecutive vertices, so f(yhat + s u) is linear in s between the vertices' s = b / a; in full mode the two
end pieces are rays with slopes f(+u) and -f(-u). The integral is a sum of closed forms in the Student-t (or normal)
cdf: exact up to floating point. In window mode the two tails |s| > tan psi0 (relative weight eps) are estimated by
one forward pass each line at a point drawn from the tail weight, which keeps the estimator unbiased.

Cost: FLOPs are counted as they are spent (flopscope conventions of earlier lanes: matvec n (2m - 1), elementwise
1, normal cdf 96, Student-t cdf 200 (nominal), power 16, normal inverse 96). One forward pass = 2 n^2 L FLOPs.
The two end vertices are pushed per line (in full mode they are the same for all lines; charging them per line
overcharges by 2 vertices per line).
"""
import math

import numpy as np
from scipy.special import gammaln, ndtr, ndtri, stdtr, stdtrit

F_NCDF, F_TCDF, F_POW, F_NINV = 96, 200, 16, 96


def chi_mean(k):
    """E|y| for y ~ N(0, I_k)."""
    return math.sqrt(2.0) * math.exp(gammaln((k + 1) / 2.0) - gammaln(k / 2.0))


class Weight:
    """Weight on the line parameter s and its antiderivatives.
    kind 'student' (line + radius, k = d - 1) or 'gauss' (standard normal density in t)."""

    def __init__(self, kind, k=None):
        self.kind = kind
        if kind == 'student':
            assert k is not None and k >= 1
            self.k = int(k)
            self.nu = float(k + 1)
            self.sq = math.sqrt(self.nu)
            self.total = chi_mean(k)
            self.c1 = 1.0 / math.sqrt(2.0 * math.pi)
            self.f_cdf = F_TCDF
        elif kind == 'gauss':
            self.total = 1.0
            self.f_cdf = F_NCDF
        else:
            raise ValueError(kind)

    def upper(self, s):
        """int_s^inf w (s may be +-inf)."""
        s = np.asarray(s, dtype=float)
        if self.kind == 'student':
            return self.total * stdtr(self.nu, -s * self.sq)
        return ndtr(-s)

    def upper_inv(self, q):
        """s with upper(s) = q * total (0 < q < 1)."""
        q = np.asarray(q, dtype=float)
        if self.kind == 'student':
            return -stdtrit(self.nu, q) / self.sq
        return -ndtri(q)

    def w1(self, s):
        """Antiderivative of s w(s) that vanishes at +-inf."""
        s = np.asarray(s, dtype=float)
        if self.kind == 'student':
            with np.errstate(over='ignore'):
                return -self.c1 * np.power(1.0 + s * s, -0.5 * self.k)
        return -np.exp(-0.5 * s * s) / math.sqrt(2.0 * math.pi)

    def mass(self, a, b):
        """int_a^b w for a <= b, without cancellation in either tail."""
        a = np.asarray(a, dtype=float)
        b = np.asarray(b, dtype=float)
        ua, ub = self.upper(a), self.upper(b)
        la, lb = self.upper(-a), self.upper(-b)          # lower tails: int_-inf^a w = upper(-a)
        return np.where(a >= 0, ua - ub, np.where(b <= 0, lb - la, self.total - la - ub))

    def window(self, eps):
        """s0 > 0 with relative weight eps outside [-s0, s0]."""
        return float(self.upper_inv(0.5 * eps))


def orth_basis(u):
    """d x (d-1) orthonormal basis of u-perp."""
    d = u.shape[0]
    Q, _ = np.linalg.qr(np.concatenate([u[:, None], np.eye(d)], axis=1)[:, :d])
    if np.dot(Q[:, 0], u) < 0:
        Q[:, 0] = -Q[:, 0]
    return Q[:, 1:]


def _propagate(Ws, Yb, u, V0):
    """Push the vertex lists of m lines through the layers. Yb (m, d) bases, V0 (3, 2) initial vertex coords shared
    by all lines (a, b): vertex a yb + b u. Returns final states H (P, n_L), coords V (P, 2), line ids lid (P,),
    per-line vertex counts after each layer (m, L+1) and per-line FLOPs (m,)."""
    m, d = Yb.shape
    L = len(Ws)
    nv0 = V0.shape[0]
    V = np.tile(V0, (m, 1))
    lid = np.repeat(np.arange(m), nv0)
    H = V[:, :1] * np.repeat(Yb, nv0, axis=0) + V[:, 1:] * u[None, :]
    counts = np.zeros((m, L + 1), dtype=np.int64)
    counts[:, 0] = nv0
    flops = np.zeros(m)
    for li, W in enumerate(Ws):
        nout, nin = W.shape
        P = H.shape[0]
        Z = H @ W.T                                     # one matvec per vertex
        np.add.at(flops, lid, nout * (2 * nin - 1))
        # segments (p, p+1) within a line, indexed by their left vertex p
        segL = np.nonzero(lid[1:] == lid[:-1])[0]
        segR = segL + 1
        pos = Z > 0.0
        neg = Z < 0.0
        # strict sign change inside a segment (a zero at a vertex keeps the sign constant inside)
        cross = (pos[segL] & neg[segR]) | (neg[segL] & pos[segR])
        np.add.at(flops, lid[segL], 2 * nout)
        js, qs = np.nonzero(cross)
        del cross, pos, neg
        C = js.shape[0]
        if C:
            pl = segL[js]                                # left vertex of the segment of each crossing
            zaj = Z[pl, qs]
            zbj = Z[pl + 1, qs]
            lam = zaj / (zaj - zbj)
            order = np.lexsort((lam, pl))
            pl, qs, lam = pl[order], qs[order], lam[order]
            nafter = np.bincount(pl, minlength=P)        # crossings inserted after vertex p
            cum_excl = np.cumsum(nafter) - nafter
            first = np.searchsorted(pl, pl)              # first crossing of the same segment (pl is sorted)
            r = np.arange(C) - first
            oldpos = np.arange(P) + cum_excl
            newpos = pl + cum_excl[pl] + 1 + r
            Pn = P + C
            Zn = np.empty((Pn, nout))
            Vn = np.empty((Pn, 2))
            lidn = np.empty(Pn, dtype=np.int64)
            Zn[oldpos] = Z
            Vn[oldpos] = V
            lidn[oldpos] = lid
            lamc = lam[:, None]
            Zc = (1.0 - lamc) * Z[pl] + lamc * Z[pl + 1]
            Zc[np.arange(C), qs] = 0.0                   # exact zero of the crossing unit
            Zn[newpos] = Zc
            Vn[newpos] = (1.0 - lamc) * V[pl] + lamc * V[pl + 1]
            lidn[newpos] = lid[pl]
            np.add.at(flops, lid[pl], 3 * nout + 9)
            Z, V, lid = Zn, Vn, lidn
        H = np.maximum(Z, 0.0)
        np.add.at(flops, lid, nout)
        counts[:, li + 1] = np.bincount(lid, minlength=m)
    return H, V, lid, counts, flops


def _integrate(F, V, lid, m, weight, flops):
    """Sum of closed-form piece integrals over each line's vertex list. F (P, n_out) values at the vertices,
    V (P, 2) coords (a, b). A vertex with a == 0 is +-u (full mode): it closes the line with a ray."""
    a, b = V[:, 0], V[:, 1]
    n_out = F.shape[1]
    starts = np.searchsorted(lid, np.arange(m))
    ends = np.searchsorted(lid, np.arange(m), side='right') - 1
    fin = a > 0
    with np.errstate(divide='ignore', invalid='ignore'):
        s = np.where(fin, b / np.where(fin, a, 1.0), 0.0)
    G = np.where(fin[:, None], F / np.where(fin, a, 1.0)[:, None], 0.0)
    np.add.at(flops, lid, n_out + 2 * weight.f_cdf + F_POW + 4)
    out = np.zeros((m, n_out))
    # finite pieces between consecutive finite vertices of the same line
    same = (lid[1:] == lid[:-1]) & fin[1:] & fin[:-1]
    ia = np.nonzero(same)[0]
    ib = ia + 1
    sa, sb = s[ia], s[ib]
    M0 = weight.mass(sa, sb)
    M1 = weight.w1(sb) - weight.w1(sa)
    ds = sb - sa
    with np.errstate(divide='ignore', invalid='ignore'):
        beta = np.where(ds > 0, (M1 - sa * M0) / np.where(ds > 0, ds, 1.0), 0.0)
    np.add.at(out, lid[ia], G[ia] * M0[:, None] + (G[ib] - G[ia]) * beta[:, None])
    np.add.at(flops, lid[ia], 4 * n_out + 8)
    # rays (full mode): left end -u at starts, right end +u at ends
    left_ray = ~fin[starts]
    if left_ray.any():
        i0 = starts[left_ray]
        i1 = i0 + 1                                      # first finite vertex
        s1 = s[i1]
        M0 = weight.mass(np.full(s1.shape, -np.inf), s1)
        M1 = weight.w1(s1)
        out[left_ray] += G[i1] * M0[:, None] + F[i0] * (s1 * M0 - M1)[:, None]
    right_ray = ~fin[ends]
    if right_ray.any():
        i0 = ends[right_ray]
        i1 = i0 - 1
        sK = s[i1]
        M0 = weight.mass(sK, np.full(sK.shape, np.inf))
        M1 = -weight.w1(sK)
        out[right_ray] += G[i1] * M0[:, None] + F[i0] * (M1 - sK * M0)[:, None]
    return out


def forward(Ws, X, J=None):
    h = X
    for W in Ws:
        h = np.maximum(h @ W.T, 0.0)
    return h if J is None else h @ J.T


def pass_flops_dims(Ws, J=None):
    fl = sum(W.shape[0] * (2 * W.shape[1] - 1) + W.shape[0] for W in Ws)
    if J is not None:
        fl += J.shape[0] * (2 * J.shape[1] - 1)
    return fl


def line_integrals(Ws, Yb, u, weight, J=None, eps=None, rng=None, max_vertices=1 << 16, chunk=None):
    """int f(yb + s u) w(s) ds for each base yb (rows of Yb, orthogonal to u; unit norm for 'student').
    eps None: exact over the whole line (full mode). eps > 0: exact on the window |s| <= s0 holding all but eps of
    the weight, plus an unbiased one-point estimate of the two tails (needs rng).
    Returns I (m, n_out), flops (m,), counts (m, L+1) (vertices after each layer, ends included)."""
    m = Yb.shape[0]
    if eps is None:
        V0 = np.array([[0.0, -1.0], [1.0, 0.0], [0.0, 1.0]])
    else:
        s0 = weight.window(eps)
        c0 = 1.0 / math.sqrt(1.0 + s0 * s0)
        V0 = np.array([[c0, -s0 * c0], [1.0, 0.0], [c0, s0 * c0]])
    n_out = (Ws[-1].shape[0] if J is None else J.shape[0])
    I = np.zeros((m, n_out))
    FL = np.zeros(m)
    CNT = np.zeros((m, len(Ws) + 1), dtype=np.int64)
    if chunk is None:
        chunk = max(1, min(m, 16))
    i = 0
    while i < m:
        j = min(m, i + chunk)
        H, V, lid, counts, flops = _propagate(Ws, Yb[i:j], u, V0)
        F = H if J is None else H @ J.T
        if J is not None:
            np.add.at(flops, lid, J.shape[0] * (2 * J.shape[1] - 1))
        I[i:j] = _integrate(F, V, lid, j - i, weight, flops)
        FL[i:j] = flops
        CNT[i:j] = counts
        per_line = max(1.0, counts[:, -1].mean())
        chunk = int(max(1, min(4 * chunk, max_vertices / per_line)))
        i = j
    if eps is not None:
        # tails: with prob 1/2 each side; point s drawn from the tail weight; estimate = (tail mass) f(yb + s u)
        q = rng.random(m) * (0.5 * eps)
        side = np.where(rng.random(m) < 0.5, -1.0, 1.0)
        st = side * weight.upper_inv(q)
        X = Yb + st[:, None] * u[None, :]
        I += (eps * weight.total) * forward(Ws, X, J)
        FL += pass_flops_dims(Ws, J) + weight.f_cdf + 3 * Yb.shape[1] + 2 * n_out
    return I, FL, CNT


def setup_flops(d):
    """Per-line cost of turning a (d-1)-dim uniform point into a unit base on u-perp: inverse normals, the basis map
    and the normalisation."""
    return (d - 1) * F_NINV + d * (2 * (d - 1) - 1) + 3 * d


def bases_from_uniform(Uu, B, normalise=True):
    """Map uniform points (m, d-1) to bases on u-perp: B Phi^{-1}(U) (normalised for the line + radius weight)."""
    Z = ndtri(np.clip(Uu, 1e-300, 1 - 1e-16))
    Y = Z @ B.T
    if normalise:
        Y /= np.linalg.norm(Y, axis=1, keepdims=True)
    return Y
