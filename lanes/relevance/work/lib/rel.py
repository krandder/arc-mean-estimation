"""Relevance-accounting lane library (float64 numpy; run with OPENBLAS_NUM_THREADS=1).

Model S: hidden layers h_k = relu(W_k h_{k-1}) + sigma xi_k, output a = relu(W_L h_{L-1}) (no output noise).
A Future holds the weights W_{l+1..L} of the map from the layer-l state to the output and the noise scale of its hidden
layers (all but the last). States are stacked as (G, P, n): G trajectory groups of P samples. Hidden-layer noise is drawn
per stream; group g reads stream share[g], so groups with the same stream share the future noise (pick-freeze copies).

Definitions: work/relevance/DEFINITIONS.md. Weight streams:
  stationary nets: st.W_layer(seed, n, l), the stationary lane's stream (target layer 0, past negative, output layer 1);
  input nets (ARC 256 x 32 family): layers 1..L of the same stream (input-bits lane's ib.Net);
  narrow-deep 8 x 256: the narrow-deep lane's nd.make_weights('plain', seed, 8, 256).
"""
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import st  # noqa: E402


def relu(z):
    return np.maximum(z, 0.0)


# ----------------------------------------------------------------------------------------------------------------------
# Nets and clouds
# ----------------------------------------------------------------------------------------------------------------------

def stationary_future(seed, n, s, sigma=1.0):
    """Future of the stationary-lane state h_{-s}: noisy layers -s+1..0, output layer 1. t = s + 1 weight layers."""
    Ws = [st.W_layer(seed, n, l) for l in range(-s + 1, 2)]
    return Future(Ws, sigma)


def stationary_cloud(seed, n, s, P, rng, burn=None, sigma=1.0, chunk=4096):
    """P independent samples of h_{-s} under the fixed-weight stationary law (burn-in from h = 0 at layer -s - burn).
    burn defaults to 8n (>= the stationary lane's B_6 on its nets)."""
    burn = 8 * n if burn is None else burn
    out = []
    Wc = {}
    for c0 in range(0, P, chunk):
        p = min(chunk, P - c0)
        h = np.zeros((p, n))
        for l in range(-s - burn + 1, -s + 1):
            W = Wc.get(l)
            if W is None:
                W = st.W_layer(seed, n, l)
                if len(Wc) < 4096:
                    Wc[l] = W
            h = np.maximum(h @ W.T, 0.0) + sigma * rng.standard_normal((p, n))
        out.append(h)
    return np.concatenate(out, 0)


def stationary_clouds(seed, n, ss, P, rng, burn=None, sigma=1.0, chunk=4096):
    """Samples of h_{-s} for every s in ss from the same P stationary paths (one burn-in of `burn` layers before the
    deepest requested layer). Returns dict s -> (P, n) array. Paths are independent across samples."""
    burn = 8 * n if burn is None else burn
    smax, smin = max(ss), min(ss)
    want = set(ss)
    out = {s: [] for s in ss}
    for c0 in range(0, P, chunk):
        p = min(chunk, P - c0)
        h = np.zeros((p, n))
        for l in range(-smax - burn + 1, -smin + 1):
            h = np.maximum(h @ st.W_layer(seed, n, l).T, 0.0) + sigma * rng.standard_normal((p, n))
            if -l in want:
                out[-l].append(h.copy())
    return {s: np.concatenate(v, 0) for s, v in out.items()}


def input_weights(seed, n, L):
    """ARC-family input net: W_1..W_L of the stationary lane's stream (the input-bits lane's ib.Net)."""
    return [st.W_layer(seed, n, l) for l in range(1, L + 1)]


def narrow_deep_weights(seed, n=8, L=256):
    sys.path.insert(0, '/home/agent/workspaces/mats/work/narrow-deep/lib')
    import nd  # noqa
    W, _ = nd.make_weights('plain', seed, n, L)
    return [w.numpy().copy() for w in W]


def input_cloud(Ws, l, P, rng):
    """Samples of h_l = (noiseless) layers 1..l applied to x ~ N(0, I_n). Ws = [W_1..W_L]. Returns (X, x)."""
    n = Ws[0].shape[1]
    x = rng.standard_normal((P, n))
    h = x
    for k in range(l):
        h = np.maximum(h @ Ws[k].T, 0.0)
    return h, x


def gaussian_frame(X):
    """Mean, covariance and symmetric square roots (Sigma^{1/2}, Sigma^{-1/2} on its range) of cloud samples X (P, n)."""
    m = X.mean(0)
    C = np.cov(X, rowvar=False)
    w, U = np.linalg.eigh(C)
    w = np.maximum(w, 0.0)
    tol = w.max() * 1e-12
    S12 = (U * np.sqrt(w)) @ U.T
    inv = np.where(w > tol, 1.0 / np.sqrt(np.maximum(w, tol)), 0.0)
    Sm12 = (U * inv) @ U.T
    return dict(m=m, C=C, evals=w[::-1].copy(), evecs=U[:, ::-1].copy(), S12=S12, Sm12=Sm12)


# ----------------------------------------------------------------------------------------------------------------------
# Future map
# ----------------------------------------------------------------------------------------------------------------------

class Future:
    def __init__(self, Ws, sigma):
        self.Ws = [np.ascontiguousarray(W, dtype=float) for W in Ws]
        self.WT = [np.ascontiguousarray(W.T) for W in self.Ws]
        self.t = len(Ws)
        self.sigma = float(sigma)
        self.n = self.Ws[0].shape[1]

    def _add_noise(self, h, rng, share):
        if self.sigma > 0:
            S = int(np.max(share)) + 1
            xi = rng.standard_normal((S,) + h.shape[1:])
            h = h + self.sigma * xi[share]
        return h

    def forward(self, X, rng=None, share=None):
        """X (G, P, n) -> a (G, P, n_out)."""
        X = X if X.ndim == 3 else X[None]
        share = np.zeros(X.shape[0], int) if share is None else np.asarray(share)
        h = X
        for k in range(self.t):
            h = np.maximum(h @ self.WT[k], 0.0)
            if k < self.t - 1:
                h = self._add_noise(h, rng, share)
        return h

    def jvp(self, X, V, rng=None, share=None):
        """Tangent propagation along each trajectory: V (G, P, n) or (G, P, q, n) (q tangents per sample).
        Returns (a, J V)."""
        X = X if X.ndim == 3 else X[None]
        share = np.zeros(X.shape[0], int) if share is None else np.asarray(share)
        multi = V.ndim == 4
        h, v = X, V
        for k in range(self.t):
            z = h @ self.WT[k]
            d = z > 0
            h = np.maximum(z, 0.0)
            v = (v @ self.WT[k]) * (d[:, :, None, :] if multi else d)
            if k < self.t - 1:
                h = self._add_noise(h, rng, share)
        return h, v

    def vjp(self, X, R, rng=None, share=None):
        """Returns (a, J(X)^T R) for R (G, P, n_out) (one cotangent per sample) or (G, P, q, n_out)."""
        X = X if X.ndim == 3 else X[None]
        share = np.zeros(X.shape[0], int) if share is None else np.asarray(share)
        multi = R.ndim == 4
        h = X
        masks = []
        for k in range(self.t):
            z = h @ self.WT[k]
            masks.append(np.packbits(z > 0, axis=-1))
            h = np.maximum(z, 0.0)
            if k < self.t - 1:
                h = self._add_noise(h, rng, share)
        u = R
        nn = self.Ws[-1].shape[0]
        for k in reversed(range(self.t)):
            mk = np.unpackbits(masks[k], axis=-1, count=self.Ws[k].shape[0]).astype(bool)
            u = (u * (mk[:, :, None, :] if multi else mk)) @ self.Ws[k]
        return h, u

    def decompose(self, X, m, rng=None):
        """Exact pathwise identity for X (P, n) against the mean point m (n,), shared future noise (one stream):
          a(X) - a(m) = J^m (X - m) + sum_k J^m_{k->L} f_k(X),  f_k = |z_k(X)| 1[sign z_k(X) != sign z_k(m)].
        Returns dict: da = a(X) - a(m); lin = J^m (X - m); fo = first-order hinge model (flips of the linearised
        preactivations, propagated through m's frozen gates); per-layer mean counts of exact and first-order flips."""
        P, n = X.shape
        hx = X.copy()
        hm = np.broadcast_to(m, X.shape).copy()
        dl = X - m
        d1 = X - m
        nfx, nf1 = [], []
        for k in range(self.t):
            WT = self.WT[k]
            zx = hx @ WT
            zm = hm @ WT
            dm = zm > 0
            zl = zm + dl @ WT
            fx_mask = (zx > 0) != dm
            f1_mask = (zl > 0) != dm
            f1 = np.abs(zl) * f1_mask
            dl = (dl @ WT) * dm
            d1 = (d1 @ WT) * dm + f1
            hx = np.maximum(zx, 0.0)
            hm = np.maximum(zm, 0.0)
            if k < self.t - 1 and self.sigma > 0:
                xi = self.sigma * rng.standard_normal(hx.shape)
                hx = hx + xi
                hm = hm + xi
            nfx.append(fx_mask.sum(1).mean())
            nf1.append(f1_mask.sum(1).mean())
        return dict(da=hx - hm, lin=dl, fo=d1, a_x=hx, a_m=hm, nflip=np.array(nfx), nflip1=np.array(nf1))


# ----------------------------------------------------------------------------------------------------------------------
# Estimators (all unbiased or consistent as stated; see DEFINITIONS.md section 5)
# ----------------------------------------------------------------------------------------------------------------------

def pair_sq(fut, XA, XB, rng, r=None):
    """Per-sample estimate of |g(XA) - g(XB)|^2 (g = noise-averaged future map), unbiased:
    sigma > 0: (a(XA,Xi) - a(XB,Xi)) . (a(XA,Xi') - a(XB,Xi')) with two independent future noises, each shared by
    the pair; sigma = 0: |a(XA) - a(XB)|^2. Returns per-sample values (P,); with a readout r (n_out,), returns
    (vector values, scalar values for r.g)."""
    if fut.sigma > 0:
        a = fut.forward(np.stack([XA, XB, XA, XB]), rng, share=[0, 0, 1, 1])
        d1, d2 = a[0] - a[1], a[2] - a[3]
    else:
        a = fut.forward(np.stack([XA, XB]))
        d1 = d2 = a[0] - a[1]
    qv = np.einsum('pi,pi->p', d1, d2)
    if r is None:
        return qv
    return qv, (d1 @ r) * (d2 @ r)


def v_l(fut, X1, X2, rng):
    """V_l = (1/2) E |g(X) - g(X')|^2, X, X' independent cloud samples. Returns (estimate, SE)."""
    q = 0.5 * pair_sq(fut, X1, X2, rng)
    return q.mean(), q.std(ddof=1) / math.sqrt(len(q))


def total_var(fut, X1, X2, rng):
    """tr Var(a) = (1/2) E|a(X,Xi) - a(X',Xi')|^2 (independent noises). Returns (estimate, SE)."""
    a = fut.forward(np.stack([X1, X2]), rng, share=[0, 1])
    d = a[0] - a[1]
    q = 0.5 * np.einsum('pi,pi->p', d, d)
    return q.mean(), q.std(ddof=1) / math.sqrt(len(q))


def gaussian_sample(fr, P, rng):
    Z = rng.standard_normal((P, len(fr['m'])))
    return fr['m'] + Z @ fr['S12'], Z


def subspace_residuals(fut, fr, basis, ks, P, rng, true_X=None):
    """Residual of the top-k columns of `basis` (whitened coordinates, orthonormal n x n) for each k in ks:
    Gaussian convention (pick-freeze): (1/2) E|g(X) - g(X_k)|^2, X_k sharing the basis-k coordinates of Z, independent
    complement; common random numbers across k. If true_X is given (samples of the true law), also the true-law
    projection residual E|g(X) - g(X_hat_k)|^2 with X_hat_k = m + S12 Pi_k Z, Z = Sm12 (X - m).
    Returns dict k -> (res, se) [and 'true' k -> (res, se)]."""
    n = len(fr['m'])
    Z = rng.standard_normal((P, n))
    Zp = rng.standard_normal((P, n))
    cz, czp = Z @ basis, Zp @ basis
    X = fr['m'] + Z @ fr['S12']
    out = {}
    for k in ks:
        mix = np.concatenate([cz[:, :k], czp[:, k:]], 1) @ basis.T
        Xk = fr['m'] + mix @ fr['S12']
        q = 0.5 * pair_sq(fut, X, Xk, rng)
        out[k] = (q.mean(), q.std(ddof=1) / math.sqrt(P))
    res = dict(gauss=out)
    if true_X is not None:
        Zt = (true_X - fr['m']) @ fr['Sm12']
        ct = Zt @ basis
        tr = {}
        for k in ks:
            Xh = fr['m'] + (ct[:, :k] @ basis[:, :k].T) @ fr['S12']
            q = pair_sq(fut, true_X, Xh, rng)
            tr[k] = (q.mean(), q.std(ddof=1) / math.sqrt(len(q)))
        res['true'] = tr
    return res


def mehler_curve(fut, fr, rhos, P, rng, X_true=None):
    """Noise-sensitivity curve D(rho) = (1/2) E|g(X) - g(X_rho)|^2 = sum_d (1 - rho^d) V_d under gamma_l
    (X_rho = m + S12 (rho Z + sqrt(1 - rho^2) Z')). Returns dict rho -> (D, se)."""
    n = len(fr['m'])
    Z = rng.standard_normal((P, n))
    Zp = rng.standard_normal((P, n))
    X = fr['m'] + Z @ fr['S12']
    out = {}
    for r in rhos:
        Xr = fr['m'] + (r * Z + math.sqrt(max(0.0, 1 - r * r)) * Zp) @ fr['S12']
        q = 0.5 * pair_sq(fut, X, Xr, rng)
        out[r] = (q.mean(), q.std(ddof=1) / math.sqrt(P))
    return out


def ustat_sq(a, Z, blocks=16):
    """Unbiased U-statistic for |E[a Z^T]|_F^2 from iid rows (a_p, Z_p): sum over p != q of (a_p . a_q)(Z_p . Z_q)
    / (P(P-1)), with a delete-a-group jackknife SE. a should be centred (reduces variance; bias O(1/P))."""
    P = a.shape[0]
    A = a.T @ Z
    diag = np.einsum('pi,pi->p', a, a) * np.einsum('pi,pi->p', Z, Z)
    U = (np.sum(A * A) - diag.sum()) / (P * (P - 1))
    s = P // blocks
    jk = []
    for b in range(blocks):
        sl = slice(b * s, (b + 1) * s)
        Ab = A - a[sl].T @ Z[sl]
        Pb = P - s
        jk.append((np.sum(Ab * Ab) - (diag.sum() - diag[sl].sum())) / (Pb * (Pb - 1)))
    jk = np.array(jk)
    se = math.sqrt((blocks - 1) / blocks * np.sum((jk - jk.mean()) ** 2))
    return float(U), se, A / P


def stein_linear(fut, X, Z, rng):
    """Degree-1 (best linear) part: B~ = E[g(X) Z^T] (n_out x n), Z the whitened (uncorrelated) coordinates of X
    (Gaussian: Stein's B~ = E[grad g] Sigma^{1/2}; any law: the regression coefficients). V_1 = |B~|_F^2 by an unbiased
    U-statistic (one future-noise draw per sample is unbiased for g). Returns (V1, se, B~)."""
    if fut.sigma > 0:
        a = fut.forward(np.stack([X]), rng)[0]
    else:
        a = fut.forward(np.stack([X]))[0]
    a = a - a.mean(0)
    return ustat_sq(a, Z)


def active_subspace(fut, fr, P, rng, X=None, q=4):
    """C = E[S12 grad g^T grad g S12] (whitened), grad g the noise-averaged Jacobian, from VJPs with q random output
    cotangents per sample; sigma > 0 uses two independent future noises per sample (unbiased for E[grad g^T grad g]).
    X: samples to average over (default: Gaussian samples). Returns (C, evals desc, evecs)."""
    n = len(fr['m'])
    if X is None:
        X, _ = gaussian_sample(fr, P, rng)
    P = X.shape[0]
    nout = fut.Ws[-1].shape[0]
    R = rng.standard_normal((1, P, q, nout))
    if fut.sigma > 0:
        _, u = fut.vjp(np.stack([X, X]), np.concatenate([R, R]), rng, share=[0, 1])
        uA = u[0] @ fr['S12']
        uB = u[1] @ fr['S12']
        C = (np.einsum('pqi,pqj->ij', uA, uB) + np.einsum('pqi,pqj->ij', uB, uA)) / (2 * P * q)
    else:
        _, u = fut.vjp(np.stack([X]), R)
        uA = u[0] @ fr['S12']
        C = np.einsum('pqi,pqj->ij', uA, uA) / (P * q)
    w, U = np.linalg.eigh(C)
    return C, w[::-1].copy(), U[:, ::-1].copy()


def gradient_energy(fut, fr, P, rng, X=None):
    """J(1) = E tr(grad g Sigma grad g^T) (noise-averaged gradient) from JVPs along v ~ N(0, I) whitened directions:
    E[(J(X,Xi) S12 v) . (J(X,Xi') S12 v)]. Returns (estimate, se)."""
    n = len(fr['m'])
    if X is None:
        X, _ = gaussian_sample(fr, P, rng)
    P = X.shape[0]
    V = rng.standard_normal((P, n)) @ fr['S12']
    if fut.sigma > 0:
        _, jv = fut.jvp(np.stack([X, X]), np.stack([V, V]), rng, share=[0, 1])
        q = np.einsum('pi,pi->p', jv[0], jv[1])
    else:
        _, jv = fut.jvp(np.stack([X]), np.stack([V]))
        q = np.einsum('pi,pi->p', jv[0], jv[0])
    return q.mean(), q.std(ddof=1) / math.sqrt(P)


def parts_shares(fut, X, m, rng):
    """Variance accounting of the exact identity on samples X (any law). For sigma > 0 the noise-averaged parts are
    obtained from two independent future noises per sample (products of the two copies). Returns dict of
    variances (traces) of: total da (= V_l), lin, gate (= da - lin), fo_gate (= fo - lin), inter (= da - fo), and the
    cross term 2 Cov(lin, gate); plus mean flip counts per layer."""
    P = X.shape[0]
    if fut.sigma > 0:
        r1 = fut.decompose(X, m, rng)
        r2 = fut.decompose(X, m, rng)
    else:
        r1 = fut.decompose(X, m)
        r2 = r1

    def comp(r):
        return dict(da=r['da'], lin=r['lin'], gate=r['da'] - r['lin'], fo_gate=r['fo'] - r['lin'],
                    inter=r['da'] - r['fo'], fo=r['fo'])

    c1, c2 = comp(r1), comp(r2)

    def cov(a1, b1, a2, b2):
        # Var/Cov over X of the noise-averaged parts: E[a(X,1) . b(X,2)] - E a . E b (symmetrised)
        e = 0.5 * (np.einsum('pi,pi->', a1, b2) + np.einsum('pi,pi->', a2, b1)) / P
        ma = 0.5 * (a1.mean(0) + a2.mean(0))
        mb = 0.5 * (b1.mean(0) + b2.mean(0))
        return float(e - ma @ mb)

    out = {}
    for key in ['da', 'lin', 'gate', 'fo_gate', 'inter', 'fo']:
        out['V_' + key] = cov(c1[key], c1[key], c2[key], c2[key])
    out['C_lin_gate'] = 2 * cov(c1['lin'], c1['gate'], c2['lin'], c2['gate'])
    out['C_fo_inter'] = 2 * cov(c1['fo'], c1['inter'], c2['fo'], c2['inter'])
    out['nflip'] = r1['nflip']
    out['nflip1'] = r1['nflip1']
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Theory helpers
# ----------------------------------------------------------------------------------------------------------------------

def kappa(c):
    """Arc-cosine (ReLU, He-normalised) kernel map on correlations: E relu(u) relu(v) * 2 for unit-variance u, v."""
    c = np.clip(c, -1.0, 1.0)
    return (np.sqrt(np.maximum(1.0 - c * c, 0.0)) + (math.pi - np.arccos(c)) * c) / math.pi


def jacobian_overlap_annealed(theta0, t, rhos, exact=True):
    """Infinite-width annealed Jacobian overlap J(rho)/J(1) for a cloud whose independent points sit at angle theta0,
    t weight layers to go, noiseless future: prod over the t layers of (1 - theta_k(rho)/pi), with theta at the first
    future layer theta0 sqrt(1 - rho) (angle between rho-correlated cloud points, small-cloud approximation) and the
    exact kernel map (exact=True) or the small-angle law theta' = theta / (1 + theta/(3 pi)) for later layers."""
    out = []
    for r in np.atleast_1d(rhos):
        th = theta0 * math.sqrt(max(0.0, 1 - r))
        c = math.cos(th)
        val = 1.0
        for _ in range(t):
            th = math.acos(min(1.0, max(-1.0, c)))
            val *= 1.0 - th / math.pi
            if exact:
                c = float(kappa(c))
            else:
                th = th / (1 + th / (3 * math.pi))
                c = math.cos(th)
        out.append(val)
    return np.array(out)
