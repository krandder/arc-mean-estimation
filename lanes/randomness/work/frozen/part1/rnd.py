"""randomness lane: nets, structured designs and estimators for the output mean of bias-free He-ReLU nets.

Nets: ARC's family (W_l iid N(0, 2/n), no bias, x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), output h_L in R^n), with the
arc-noisy weight stream (anet.make_weights), so nets 200-204 at 256 x 32 match arc-noisy's noiseless 2^26-path truths
and seeds 300-307 at n = 32, 64, 128 (L = n/8) match arc-update's 2^24-path truths.

Positive homogeneity: f(x) = |x| g(x/|x|). A "radius-exact" (RB) rule evaluates g at unit vectors and multiplies by
m_n = E|x|, so the radial variance is removed for free.

Designs (unit vectors on S^{n-1}, equal weights unless stated):
  mc            iid uniform directions
  anti          antipodal pairs (u, -u)
  onb           a Haar-random orthonormal basis (kills harmonic degree 2)
  simplex       n + 1 vertices of a regular simplex, Haar-rotated (spherical 2-design)
  cross         +-e_i, Haar-rotated (antipodal spherical 3-design, 2n points)
  kerdock       129 mutually unbiased bases of R^256 with antipodes (antipodal 5-design, 66048 points; n = 256 only)
  mub           the same 129 bases without antipodes, random signs (kills degrees 2 and 4; 33024 points)
  sobol         Sobol points -> inverse normal cdf -> sphere (scrambled: LMS + digital shift; unscrambled: centred)
  lattice       rank-1 Korobov lattice (random shift or centred, optional baker transform) -> sphere
  kwise         exact k-wise independent discretised Gaussians from degree-(k-1) polynomials over GF(q) (Gaussian
                points, not on the sphere)
Any design can be rotated by a basis Q: x = Q^T s (Haar for black-box randomisation; gate-aligned bases from W_1 for
the white-box designs: polar, svd).
Cost convention: one forward pass = 2 n^2 L flops; designs' generation costs are reported separately.
"""
import math
import os
import sys
import numpy as np
import torch
from scipy.special import ndtri, gammaln

ARC_NOISY = '/home/agent/workspaces/mats/work/arc-noisy'
ARC_UPDATE = '/home/agent/workspaces/mats/work/arc-update'
if ARC_NOISY not in sys.path:
    sys.path.insert(0, ARC_NOISY)
import anet  # noqa: E402

torch.set_num_threads(int(os.environ.get('RND_THREADS', '1')))


# ----------------------------------------------------------------------------------------------------------- nets
def weights(seed, n, L):
    """float64 torch weights (list of L (n, n) tensors), arc-noisy stream."""
    return anet.make_weights(seed, n, L)


def mean_radius(n):
    return math.exp(0.5 * math.log(2.0) + gammaln((n + 1) / 2.0) - gammaln(n / 2.0))


def pass_flops(n, L):
    return 2.0 * n * n * L


class Net:
    def __init__(self, seed, n, L, dtype=torch.float32):
        self.seed, self.n, self.L = int(seed), int(n), int(L)
        self.W64 = weights(seed, n, L)
        self.dtype = dtype
        self.Wt = [w.T.to(dtype).contiguous() for w in self.W64]
        self.mn = mean_radius(n)

    @torch.no_grad()
    def forward(self, X, l1=None):
        """X: (P, n) numpy or torch -> h_{l1} (P, n) torch (dtype)."""
        h = torch.as_tensor(X).to(self.dtype)
        l1 = self.L if l1 is None else l1
        for l in range(l1):
            h = torch.relu(h @ self.Wt[l])
        return h

    @torch.no_grad()
    def sum_out(self, X, chunk=1 << 13, weights=None):
        """sum_i c_i f(x_i) in float64 (c = 1 if weights is None)."""
        X = np.asarray(X)
        s = np.zeros(self.n)
        for i in range(0, X.shape[0], chunk):
            out = self.forward(X[i:i + chunk]).double().numpy()
            if weights is None:
                s += out.sum(0)
            else:
                s += weights[i:i + chunk] @ out
        return s

    @torch.no_grad()
    def outs(self, X, chunk=1 << 13):
        X = np.asarray(X)
        return np.concatenate([self.forward(X[i:i + chunk]).double().numpy() for i in range(0, X.shape[0], chunk)])


def load_truth(seed, n, L):
    """Noiseless truth mean (n,), per-sample variance V = tr Var f, and the truth's own nMSE floor (1/N)."""
    if n == 256 and L == 32:
        p = os.path.join(ARC_NOISY, 'truth', f'truth_256_32_s0_seed{seed}.npz')
        if not os.path.exists(p):
            p = os.path.join(ARC_NOISY, 'truth', f'truth_256_32_s0.001_seed{seed}.npz')   # dev: sigma = 1e-3 truth
            if not os.path.exists(p) or os.environ.get('RND_NOISY_TRUTH', '0') != '1':
                return None
        d = np.load(p)
        N = float(d['N'])
        mean = d['S1'][-1] / N
        var = d['S2'][-1] / N - mean ** 2
    else:
        p = os.path.join(ARC_UPDATE, 'runs', f'truth_n{n}_L{L}_s{seed}.npz')
        if not os.path.exists(p):
            return None
        d = np.load(p)
        N = float(d['N'])
        mean = (d['S1A'][-1] + d['S1B'][-1]) / N
        var = (d['S2A'][-1] + d['S2B'][-1]) / N - mean ** 2
    return dict(mean=mean, V=float(var.sum()), N=N, floor=1.0 / N)


# -------------------------------------------------------------------------------------------------- basic geometry
def haar(n, rng):
    """Haar-random orthogonal matrix (QR of a Gaussian matrix with the sign fix)."""
    A = rng.standard_normal((n, n))
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R))[None, :]


def to_sphere(Z):
    return Z / np.linalg.norm(Z, axis=1, keepdims=True)


def rotate(U, Q):
    """Rows u -> Q u."""
    return U @ Q.T


# ------------------------------------------------------------------------------------------------------- designs
def d_mc(m, n, rng):
    return to_sphere(rng.standard_normal((m, n)))


def d_anti(m, n, rng):
    U = to_sphere(rng.standard_normal((m // 2, n)))
    return np.concatenate([U, -U])


def d_onb(n, rng):
    return haar(n, rng).T.copy()          # rows: an orthonormal basis


def simplex_base(n):
    """n + 1 unit vectors in R^n with pairwise inner products -1/n (regular simplex)."""
    E = np.eye(n + 1) - 1.0 / (n + 1)                      # centred standard basis of R^{n+1}
    # orthonormal basis of the hyperplane sum = 0: QR of the first n centred vectors
    B, _ = np.linalg.qr(E[:, :n])                          # (n+1, n)
    V = E @ B                                              # coordinates in the hyperplane
    return to_sphere(V)


def cross_base(n):
    I = np.eye(n)
    return np.concatenate([I, -I])


_KERDOCK = {}


def kerdock_bases(n=256):
    """(n/2 + 1, n, n) mutually unbiased bases (rows are vectors); cached; n = 256 via arc-noisy's GR(4,7) build,
    n = 64 via the general construction in kerdock_gen.py if available."""
    if n in _KERDOCK:
        return _KERDOCK[n]
    if n == 256:
        import kerdock as K
        B = K.build()
    else:
        sys.path.insert(0, os.path.dirname(__file__))
        import kerdock_gen as KG
        B = KG.build(n)
    _KERDOCK[n] = B
    return B


def kerdock_base(n=256, antipodal=True, rng=None):
    B = kerdock_bases(n)
    V = B.reshape(-1, n)
    if antipodal:
        return np.concatenate([V, -V])
    s = rng.choice([-1.0, 1.0], size=V.shape[0]) if rng is not None else 1.0
    return V * (s[:, None] if rng is not None else 1.0)


def sobol_unit(m_log2, n, scramble, seed=None):
    """2^m Sobol points in [0,1)^n; unscrambled: centred by 2^-(m+1) (unrestricted lane's convention)."""
    from scipy.stats import qmc
    eng = qmc.Sobol(d=n, scramble=scramble, seed=seed)
    if scramble:
        P = eng.random_base2(m_log2)
    else:
        P = eng.random(1 << m_log2) + 2.0 ** (-(m_log2 + 1))
    return np.clip(P, 1e-15, 1 - 1e-15)


_KOROBOV = {}


def korobov_a(N, n, cand=512, seed=0):
    """Korobov generator a for an N-point rank-1 lattice in n dims, chosen among `cand` random odd candidates by the
    P_2 criterion with product weights gamma_j = 1/j^2 (smaller is better). Deterministic given (N, n, seed)."""
    key = (N, n, cand, seed)
    if key in _KOROBOV:
        return _KOROBOV[key]
    rng = np.random.default_rng([4242, N, n, seed])
    k = np.arange(N, dtype=np.int64)
    gam = 1.0 / np.arange(1, n + 1) ** 2
    best, best_a = np.inf, 1
    for a in rng.integers(1, N, size=cand) | 1:
        z = np.ones(n, dtype=np.int64)
        for j in range(1, n):
            z[j] = (z[j - 1] * a) % N
        prod = np.ones(N)
        for j in range(n):
            x = (k * z[j] % N) / N
            b2 = x * x - x + 1.0 / 6.0                    # Bernoulli B2
            prod *= 1.0 + gam[j] * 2 * math.pi ** 2 * b2
        val = float(prod.mean() - 1.0)
        if val < best:
            best, best_a = val, int(a)
    _KOROBOV[key] = (best_a, best)
    return best_a, best


def lattice_unit(N, n, shift=None, baker=False, a=None):
    """N-point Korobov lattice in [0,1)^n; shift: None (centred, 1/(2N)) or a vector in [0,1)^n."""
    if a is None:
        a, _ = korobov_a(N, n)
    z = np.ones(n, dtype=np.int64)
    for j in range(1, n):
        z[j] = (z[j - 1] * a) % N
    k = np.arange(N, dtype=np.int64)[:, None]
    P = (k * z[None, :] % N) / N
    P = (P + (0.5 / N if shift is None else shift[None, :])) % 1.0
    if baker:
        P = 1.0 - np.abs(2.0 * P - 1.0)
    return np.clip(P, 1e-15, 1 - 1e-15)


def gauss_from_unit(P):
    return ndtri(P)


def kwise_levels(q, k):
    """q symmetric equal-probability levels whose even moments match N(0, 1) up to degree min(k, 6) (odd moments vanish
    by symmetry): levels = sum_j a_j y^(2j+1) with y the midpoint quantiles Phi^-1((v + 1/2)/q), coefficients solved
    by Newton's method on the moment equations E lev^2 = 1, E lev^4 = 3, E lev^6 = 15."""
    y = ndtri((np.arange(q) + 0.5) / q)
    targets = [1.0, 3.0, 15.0]
    J = max(1, min(3, k // 2))
    c = np.zeros(J); c[0] = 1.0 / math.sqrt(np.mean(y ** 2))
    basis = np.stack([y ** (2 * j + 1) for j in range(J)], 1)
    for _ in range(100):
        lev = basis @ c
        F = np.array([np.mean(lev ** (2 * (r + 1))) - targets[r] for r in range(J)])
        if np.max(np.abs(F)) < 1e-13:
            break
        Jm = np.array([[np.mean(2 * (r + 1) * lev ** (2 * r + 1) * basis[:, j]) for j in range(J)] for r in range(J)])
        c = c - np.linalg.solve(Jm, F)
    lev = basis @ c
    assert all(abs(np.mean(lev ** (2 * (r + 1))) - targets[r]) < 1e-9 for r in range(J)), 'moment match failed'
    return lev


def kwise_gauss(k, n, q, seeds=None, rescale=True):
    """Exact k-wise independent q-level discretised Gaussians: for a seed (a_0..a_{k-1}) in GF(q)^k, coordinate j
    (j = 1..n, q prime > n) gets v_j = sum_t a_t j^t mod q, mapped to the midpoint quantile Phi^-1((v + 1/2)/q),
    rescaled to unit variance (rescale=True) so all moments of degree <= min(k, 3) match N(0, I) exactly (odd
    moments vanish by symmetry). seeds: (S, k) int array; default all q^k seeds (the full design)."""
    assert q > n
    lev = kwise_levels(q, k) if rescale else ndtri((np.arange(q) + 0.5) / q)
    if seeds is None:
        grids = np.meshgrid(*[np.arange(q)] * k, indexing='ij')
        seeds = np.stack([g.reshape(-1) for g in grids], axis=1)
    j = np.arange(1, n + 1, dtype=np.int64)
    V = np.zeros((seeds.shape[0], n), dtype=np.int64)
    jp = np.ones(n, dtype=np.int64)
    for t in range(k):
        V = (V + seeds[:, t:t + 1] * jp[None, :]) % q
        jp = (jp * j) % q
    return lev[V]


# --------------------------------------------------------------------------------------------- gate-aligned bases
def basis_polar(W1):
    """Orthogonal Q (rows = basis) with W1 = (W1 W1^T)^{1/2} Q: in coordinates s = Q x the first-layer
    pre-activations are z = (W1 W1^T)^{1/2} s, each mostly carried by its own coordinate."""
    W1 = np.asarray(W1, dtype=float)
    U, S, Vt = np.linalg.svd(W1)
    return U @ Vt                                          # polar factor: W1 = (U S U^T)(U V^T)


def basis_svd(W1):
    """Rows = right singular vectors of W1, by decreasing singular value (|W1 x|^2 = sum sigma_j^2 s_j^2)."""
    W1 = np.asarray(W1, dtype=float)
    _, _, Vt = np.linalg.svd(W1)
    return Vt


def apply_basis(S, Qrows):
    """Points given in basis coordinates s (rows) -> x = Q^T s."""
    return S @ Qrows


# ------------------------------------------------------------------------------------------------------ estimates
def rb_estimate(net, U, weights=None):
    """Radius-exact estimate m_n sum_i c_i g(u_i) (c = 1/m if weights is None)."""
    m = U.shape[0]
    if weights is None:
        return net.mn * net.sum_out(U) / m
    return net.mn * net.sum_out(U, weights=weights)


def plain_estimate(net, X):
    return net.sum_out(X) / X.shape[0]


def nmse(est, truth):
    return float(np.sum((est - truth['mean']) ** 2) / truth['V'])


# ------------------------------------------------------------------------------------------- Gegenbauer utilities
def gegen_P(d, n, t):
    """Normalised Gegenbauer (Legendre) polynomial of degree d in dimension n, P_d(1) = 1, by the three-term
    recurrence P_{k+1} = ((2k + n - 2) t P_k - k P_{k-1}) / (k + n - 2)."""
    t = np.asarray(t, dtype=float)
    P0 = np.ones_like(t)
    if d == 0:
        return P0
    P1 = t.copy()
    for k in range(1, d):
        P0, P1 = P1, ((2 * k + n - 2) * t * P1 - k * P0) / (k + n - 2)
    return P1


def aliasing(U, d_max, weights=None, block=4096):
    """A_d(D) = sum_ij c_i c_j P_d(u_i . u_j) for d = 0..d_max (c = 1/m by default), by blocks."""
    m, n = U.shape
    c = np.full(m, 1.0 / m) if weights is None else np.asarray(weights)
    A = np.zeros(d_max + 1)
    for i in range(0, m, block):
        G = U[i:i + block] @ U.T
        G = np.clip(G, -1.0, 1.0)
        ci = c[i:i + block]
        P0 = np.ones_like(G)
        A[0] += ci @ P0 @ c
        P1 = G.copy()
        if d_max >= 1:
            A[1] += ci @ P1 @ c
        for k in range(1, d_max):
            P0, P1 = P1, ((2 * k + n - 2) * G * P1 - k * P0) / (k + n - 2)
            A[k + 1] += ci @ P1 @ c
    return A
