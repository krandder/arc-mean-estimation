"""future-aware lane library.

Nets, truths and forward passes come from the arc-update library (work/arc-update/lib/au.py, imported read-only; its
sha256 is recorded with this lane's pre-registration). Conventions as there: He-ReLU, W_l iid N(0, 2/n), x ~ N(0, I),
float32 matmuls with float64 accumulation, nMSE = |est - Y|^2 / tr Var(h_L).

Contents
- load_net: weights, per-layer true means and variances (arc-noisy 2^26-path truths at 256 x 32; arc-update 2^24-path
  truths at n = 64, 128; dev nets 100, 101 use the sigma = 0.001 truths as approximate noiseless truths).
- true_samples, push_halves: true layer-l samples; push model samples (optionally weighted) through layers l+1..L,
  accumulating weighted output sums in two independent halves (unbiased squared-error cross products).
- relevance statistics of the future map g_l on a cloud: vjp_rows (rows J(h_j)^T v_j, v_j ~ N(0, I)),
  jbar (cloud-averaged Jacobian E[J] by basis-vector VJPs), so that R = E[J^T J] = E[B^T B] and the nonlinear part's
  R_nl = R - Jbar^T Jbar.
- feature maps A (n x k) defining k linear features a = A^T h:
  'fut'   whitened active subspace of g_l: top eigenvectors w of S^{1/2} R S^{1/2}, features v = S^{-1/2} w,
  'futnl' the same for the nonlinear part R_nl (the part of g_l that a mean-matching closure's defect can excite),
  'futu'  unwhitened active subspace (top eigenvectors of R),
  'pca'   top-k cloud covariance axes (past-measurable),
  'rand'  a Haar k-frame (past-measurable, structure-free).
- projections at a cut (oracle single cut or one recursion step), all in a common random-number design:
  cond   keep the features a = A^T x of a sample x of the target cloud, regenerate the rest as the linear-Gaussian
         conditional h = mu + S A (A^T S A)^{-1} (a - A^T mu) + xi, xi ~ N(0, S_res), S_res = S - S A (A^T S A)^{-1} A^T S
         (A^T xi = 0, so the k-dim marginal is exact and the joint mean and covariance match);
  rad    then scale the residual xi per sample so that |h| follows the target radius law (rank transport within the
         batch), which keeps a = A^T h exact;
  k = 0 gives the Gaussian (cond) and a radius-corrected Gaussian (rad) projection.
- edgeworth weights: Gram-Charlier weight 1 + (1/6) sum kappa_abc He_abc(z) on whitened features z (signed measure).
"""
import math, os, sys
import numpy as np
import torch

AU_LIB = '/home/agent/workspaces/mats/work/arc-update/lib'
if AU_LIB not in sys.path:
    sys.path.insert(0, AU_LIB)
import au  # noqa: E402

torch.set_num_threads(int(os.environ.get('FA_THREADS', '2')))
AU_RUNS = '/home/agent/workspaces/mats/work/arc-update/runs'


def load_net(n, L, seed):
    """Weights and truth: dict(W, n, L, mean (L, n), var (L, n), Y, V, Ntruth, truth_path)."""
    W = au.weights(seed, n, L)
    if n == 256 and L == 32:
        tk = 's0' if seed >= 200 else 's0.001'
        p = os.path.join(au.ARC_NOISY, 'truth', f'truth_{n}_{L}_{tk}_seed{seed}.npz')
        d = np.load(p)
        N = float(d['N']); S1 = d['S1']; S2 = d['S2']
    else:
        p = os.path.join(AU_RUNS, f'truth_n{n}_L{L}_s{seed}.npz')
        d = np.load(p)
        N = float(d['N']); S1 = d['S1A'] + d['S1B']; S2 = d['S2A'] + d['S2B']
    mean = S1 / N
    var = S2 / N - mean ** 2
    return dict(W=W, n=n, L=L, seed=seed, mean=mean, var=var, Y=mean[-1].copy(), V=float(var[-1].sum()),
                Ntruth=N, truth_path=p)


@torch.no_grad()
def true_samples(W, l, N, seed):
    """N true layer-l samples as a float32 torch tensor (l = 0: the input)."""
    n = W[0].shape[0]
    gen = torch.Generator().manual_seed(int(seed))
    x = torch.randn(N, n, generator=gen)
    return au.forward(W, x, l0=0, l1=l) if l > 0 else x


@torch.no_grad()
def push_halves(W, l, H, wts=None, half=None):
    """Push model samples H (m, n) at layer l through layers l+1..L. Returns (sumA, sumB, wA, wB): weighted output
    sums and weight totals of the two halves (first half of the rows = A unless 'half' is given: 0 -> all to A,
    1 -> all to B)."""
    out = au.forward(W, H, l0=l, l1=len(W)).double()
    if wts is None:
        wts = torch.ones(H.shape[0], dtype=torch.float64)
    wts = wts.double()
    m = H.shape[0]
    if half is None:
        k = m // 2
        sA = (wts[:k, None] * out[:k]).sum(0).numpy(); sB = (wts[k:, None] * out[k:]).sum(0).numpy()
        return sA, sB, float(wts[:k].sum()), float(wts[k:].sum())
    s = (wts[:, None] * out).sum(0).numpy()
    return (s, np.zeros_like(s), float(wts.sum()), 0.0) if half == 0 else (np.zeros_like(s), s, 0.0, float(wts.sum()))


def fwd_grad(W, h, l0, l1):
    """Forward through layers l0+1..l1 with autograd enabled (au.forward is no_grad)."""
    for j in range(l0, l1):
        h = torch.relu(h @ W[j].T.float())
    return h


def vjp_rows(W, l, H, seed, chunk=2048):
    """Rows J(h_j)^T v_j (float64 numpy, (m, n)) for the future map g_l at samples H, v_j ~ N(0, I_n).
    Returns (rows, v)."""
    gen = torch.Generator().manual_seed(int(seed))
    rows, vs = [], []
    for i in range(0, H.shape[0], chunk):
        h = H[i:i + chunk].clone().float().requires_grad_(True)
        with torch.enable_grad():
            out = fwd_grad(W, h, l, len(W))
            v = torch.randn(out.shape, generator=gen)
            (out * v).sum().backward()
        rows.append(h.grad.double().numpy()); vs.append(v.double().numpy())
    return np.concatenate(rows, 0), np.concatenate(vs, 0)


def jbar(W, l, H, chunk=32):
    """Cloud-averaged Jacobian E[J] (n_out x n) of g_l over samples H, by basis-vector VJPs (n per sample)."""
    n = W[0].shape[0]
    acc = np.zeros((n, n))
    m = H.shape[0]
    for i in range(0, m, chunk):
        h0 = H[i:i + chunk].float()
        b = h0.shape[0]
        # replicate each sample n times, one output basis vector each
        h = h0.repeat_interleave(n, dim=0).clone().requires_grad_(True)
        with torch.enable_grad():
            out = fwd_grad(W, h, l, len(W))
            E = torch.eye(n).repeat(b, 1)
            (out * E).sum().backward()
        G = h.grad.double().numpy().reshape(b, n, n)   # [sample, out i, in j] = dg_i/dh_j
        acc += G.sum(0)
    return acc / m


def psd_sqrt(S, floor=0.0):
    S = 0.5 * (S + S.T)
    ev, U = np.linalg.eigh(S)
    ev = np.clip(ev, floor, None)
    return U, ev


def features(kind, k, S, R=None, seed=0):
    """Feature matrix A (n x k), columns are linear functionals a_i = A[:, i] . h.
    S: cloud covariance; R: E[J^T J] (or its nonlinear part) of the future map on the cloud."""
    n = S.shape[0]
    if k == 0:
        return np.zeros((n, 0))
    if kind == 'pca':
        U, ev = psd_sqrt(S)
        return U[:, ::-1][:, :k].copy()
    if kind == 'rand':
        rng = np.random.RandomState(int(seed))
        Q, _ = np.linalg.qr(rng.randn(n, k))
        return Q
    if kind == 'futu':
        U, ev = psd_sqrt(R)
        return U[:, ::-1][:, :k].copy()
    if kind in ('fut', 'futnl'):
        U, ev = psd_sqrt(S)
        Sh = (U * np.sqrt(ev)) @ U.T                     # S^{1/2}
        M = Sh @ R @ Sh
        Uw, lw = psd_sqrt(M)
        w = Uw[:, ::-1][:, :k]; lam = lw[::-1][:k]
        A = R @ Sh @ w / np.maximum(lam, 1e-300)[None, :]  # = S^{-1/2} w when S is invertible
        # normalise features to unit variance under S
        var = np.einsum('ik,ij,jk->k', A, S, A)
        return A / np.sqrt(np.maximum(var, 1e-300))[None, :]
    raise ValueError(kind)


class CondProjector:
    """Linear-Gaussian conditional projection keeping the features a = A^T h exact (see module docstring)."""

    def __init__(self, mu, S, A):
        self.mu = np.asarray(mu, float); self.S = 0.5 * (S + S.T); self.A = A
        n, k = A.shape
        if k > 0:
            SA = self.S @ A
            G = A.T @ SA
            Gi = np.linalg.pinv(G, rcond=1e-12)
            self.Kg = SA @ Gi                              # n x k regression map
            Sres = self.S - SA @ Gi @ SA.T
        else:
            self.Kg = np.zeros((n, 0)); Sres = self.S
        U, ev = psd_sqrt(Sres)
        self.Rt = torch.from_numpy((U * np.sqrt(ev)).T.copy()).float()   # xi = z @ Rt, z ~ N(0, I)
        self.mut = torch.from_numpy(self.mu).float()
        self.Kgt = torch.from_numpy(self.Kg.T.copy()).float()             # (k, n)
        self.At = torch.from_numpy(A.copy()).float()
        self.Amu = torch.from_numpy(A.T @ self.mu).float()

    def sample_feats(self, a, Z):
        """As sample, with the features a = A^T x (m, k) given directly."""
        xi = Z @ self.Rt
        if self.A.shape[1] == 0:
            return self.mut[None, :].expand_as(xi), xi
        return self.mut[None, :] + (a - self.Amu[None, :]) @ self.Kgt, xi

    def sample(self, X, Z):
        """X: target-cloud samples (m, n) supplying the features (ignored when k = 0); Z: (m, n) standard normals.
        Returns (base, xi): h = base + xi with base = E[h | a], xi the regenerated residual."""
        xi = Z @ self.Rt
        if self.A.shape[1] == 0:
            base = self.mut[None, :].expand_as(xi)
        else:
            a = X @ self.At
            base = self.mut[None, :] + (a - self.Amu[None, :]) @ self.Kgt
        return base, xi


def sorted_quantile(xs, probs):
    """Quantiles of an already sorted 1-d array (numpy 'linear' method), without np.quantile's partition cost."""
    pos = np.asarray(probs) * (len(xs) - 1)
    return np.interp(pos, np.arange(len(xs)), xs)


def radius_fix(base, xi, r_target_sorted):
    """Scale xi per sample (s >= 0) so that |base + s xi| equals the target radius assigned by rank within the
    batch (the j-th smallest radius gets the ((j - 1/2)/m)-quantile of r_target_sorted). Keeps A^T h (A^T xi = 0)."""
    m = base.shape[0]
    h0 = (base + xi).double()
    r0 = torch.linalg.norm(h0, dim=1).numpy()
    q = sorted_quantile(r_target_sorted, (np.arange(m) + 0.5) / m)
    rt = np.empty(m); rt[np.argsort(r0)] = q
    b = base.double(); x = xi.double()
    bb = (b * b).sum(1).numpy(); bx = (b * x).sum(1).numpy(); xx = np.maximum((x * x).sum(1).numpy(), 1e-300)
    # |b + s x|^2 = rt^2  ->  xx s^2 + 2 bx s + (bb - rt^2) = 0, positive root (clip if no real root)
    disc = bx * bx - xx * (bb - rt * rt)
    s = (-bx + np.sqrt(np.maximum(disc, 0.0))) / xx
    s = np.maximum(s, 0.0)
    nfail = int((disc < 0).sum())
    return (b + torch.from_numpy(s)[:, None] * x).float(), nfail


def radius_scale(h, r_target_sorted):
    """arc-update's radial transport: rescale whole samples to the target radius law (rank within the batch)."""
    m = h.shape[0]
    r0 = torch.linalg.norm(h.double(), dim=1).numpy()
    q = sorted_quantile(r_target_sorted, (np.arange(m) + 0.5) / m)
    rt = np.empty(m); rt[np.argsort(r0)] = q
    return h * torch.from_numpy(rt / np.maximum(r0, 1e-300)).float()[:, None]


def edgeworth_weights(Zf, kappa3):
    """Gram-Charlier order-3 weight for whitened features Zf (m, k) with third-cumulant tensor kappa3 (k, k, k):
    w = 1 + (1/6) sum_abc kappa_abc He_abc(z), He_abc = z_a z_b z_c - z_a d_bc - z_b d_ac - z_c d_ab."""
    z = Zf.double().numpy()
    t3 = np.einsum('abc,ma,mb,mc->m', kappa3, z, z, z, optimize=True)
    tr = np.einsum('abb->a', kappa3) + np.einsum('bab->a', kappa3) + np.einsum('bba->a', kappa3)
    t1 = z @ tr
    return torch.from_numpy(1.0 + (t3 - t1) / 6.0)


def third_cumulant(Zc):
    """Third cumulant tensor of centred, whitened samples Zc (m, k): mean of z_a z_b z_c (k x k x k)."""
    z = Zc.double().numpy()
    return np.einsum('ma,mb,mc->abc', z, z, z, optimize=True) / z.shape[0]
