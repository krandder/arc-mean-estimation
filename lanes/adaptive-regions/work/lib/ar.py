"""adaptive-regions library: region families, stratification gains, certified bounds (IBP, CROWN), gate-cone tools.

Nets: ARC's family through arc-update's au.weights (arc-noisy weight stream; W_l iid N(0, 2/n), no bias, x ~ N(0, I_n),
h_l = relu(W_l h_{l-1})). One forward pass = 2 n^2 L flops (the cost unit). Everything here is my own code; no
third-party verification library is used.

Contents
- forward / forward_gates / vjp / jvp: batched passes (float32 matmuls; float64 where stated).
- frames: Haar, W_1 SVD (right singular vectors), polar (rows of U V^T), mean-Jacobian (Stein: E[f x^T]), active
  subspace (top eigenvectors of E[J^T J] from VJPs with random output vectors).
- cell statistics: oracle Neyman and proportional gains from held-out samples and given p_k; concentration.
- frame boxes: exact Gaussian mass and centroid (product form).
- gate cones: orthant probabilities and centroids of {sign(W_S x) = s} by cheap k-dimensional sampling (charged in
  flops) or Genz (scipy) for single patterns.
- CART: best-first greedy tree over candidate hyperplanes, Neyman objective on training samples.
- IBP and CROWN (backward linear relaxation with adaptive lower slopes and full CROWN intermediate bounds) from any
  layer l to the output, over input sets h = c + P a, a in [-r, r]^d (axis boxes: P = I).
- pick-freeze closed Sobol index of a subspace; collision (birthday) estimate of the number of gate patterns.
"""
import math, os, sys, time
import numpy as np
import torch

AU = '/home/agent/workspaces/mats/work/arc-update/lib'
if AU not in sys.path:
    sys.path.insert(0, AU)
import au  # noqa: E402

torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))


# ----------------------------------------------------------------------------------------------------------------
# nets and passes
def weights(seed, n, L, dtype=torch.float32):
    return [w.to(dtype).contiguous() for w in au.weights(seed, n, L)]


def pass_flops(n, L):
    return 2.0 * n * n * L


@torch.no_grad()
def forward(W, X, l0=0, l1=None, keep=None):
    """Push X (m, n) at layer l0 through layers l0+1..l1. keep: set of layers whose post-ReLU states are returned."""
    l1 = len(W) if l1 is None else l1
    h = X
    out = {}
    for l in range(l0, l1):
        h = torch.relu(h @ W[l].T)
        if keep is not None and (l + 1) in keep:
            out[l + 1] = h.clone()
    return (h, out) if keep is not None else h


@torch.no_grad()
def forward_z1(W, X):
    """Output and first-layer pre-activations."""
    z1 = X @ W[0].T
    h = torch.relu(z1)
    for l in range(1, len(W)):
        h = torch.relu(h @ W[l].T)
    return h, z1


@torch.no_grad()
def gate_hashes(W, X, seed=12345):
    """Per-layer cumulative hashes of the gate pattern (layers 1..l), as int64 (L, m). Two random 64-bit projections of
    the bit pattern combined; collisions of different patterns have probability ~2^-60 per pair."""
    m = X.shape[0]
    n = W[0].shape[0]
    g = np.random.RandomState(seed)
    out = np.zeros((len(W), m), dtype=np.int64)
    acc = np.zeros(m, dtype=np.int64)
    h = X
    for l in range(len(W)):
        z = h @ W[l].T
        h = torch.relu(z)
        bits = (z > 0).numpy().astype(np.int64)
        r = g.randint(1, 2 ** 62, size=n, dtype=np.int64)
        layer = (bits * r[None, :]).sum(1)                 # wraps mod 2^64: fine for hashing
        acc = acc * np.int64(1_000_003) + layer
        out[l] = acc
    return out


def collision_stats(hashes):
    """Collision estimate per layer: pairs with equal hash C, total pairs P = m(m-1)/2; sum p^2 ~ C/P; N_eff = P/C.
    With C = 0, the 95% bound sum p^2 <= 3/P gives N_eff >= P/3."""
    L, m = hashes.shape
    P = m * (m - 1) / 2.0
    res = []
    for l in range(L):
        _, cnt = np.unique(hashes[l], return_counts=True)
        C = float((cnt * (cnt - 1) / 2.0).sum())
        res.append(dict(layer=l + 1, pairs=P, collisions=C, distinct=int(len(cnt)),
                        n_eff=(P / C if C > 0 else None), n_eff_lower95=(P / 3.0 if C == 0 else None)))
    return res


@torch.no_grad()
def vjp(W, X, V):
    """Rows of J(x)^T v for x = rows of X, v = rows of V (float32)."""
    hs = [X]
    masks = []
    h = X
    for w in W:
        z = h @ w.T
        masks.append(z > 0)
        h = torch.relu(z)
        hs.append(h)
    g = V
    for l in range(len(W) - 1, -1, -1):
        g = (g * masks[l]) @ W[l]
    return g


@torch.no_grad()
def jvp(W, X, T):
    """Rows of J(x) t (directional derivative along t with x's own gates), and f(x)."""
    h, t = X, T
    for w in W:
        z = h @ w.T
        m = z > 0
        h = torch.relu(z)
        t = (t @ w.T) * m
    return t, h


# ----------------------------------------------------------------------------------------------------------------
# frames (columns are directions, ordered as returned)
def haar(n, seed):
    g = np.random.RandomState(seed)
    A = g.standard_normal((n, n))
    Q, R = np.linalg.qr(A)
    Q = Q * np.sign(np.diag(R))[None, :]
    return Q


def svd_frame(W1):
    U, s, Vt = np.linalg.svd(np.asarray(W1, dtype=np.float64))
    return Vt.T, s            # columns = right singular vectors, descending singular values


def polar_frame(W1):
    U, s, Vt = np.linalg.svd(np.asarray(W1, dtype=np.float64))
    Q = U @ Vt                # W1 = P Q, P = U S U^T
    return Q.T                # column i = q_i (row i of Q): s_i = q_i . x


def meanjac_frame(X, F):
    """Stein: E[J] = E[f x^T]; right singular vectors of the sample estimate."""
    M = (np.asarray(F, dtype=np.float64).T @ np.asarray(X, dtype=np.float64)) / X.shape[0]
    U, s, Vt = np.linalg.svd(M)
    return Vt.T, s, M


@torch.no_grad()
def active_frame(W, m, seed, chunk=4096):
    """Top eigenvectors of C = E[J^T J] from m VJPs with v ~ N(0, I) (E[(J^T v)(J^T v)^T] = E[J^T J]).
    Cost: m forward + m backward passes (~3 passes each, charged by the caller)."""
    n = W[0].shape[0]
    gen = torch.Generator().manual_seed(int(seed))
    C = np.zeros((n, n))
    done = 0
    while done < m:
        k = min(chunk, m - done)
        X = torch.randn(k, n, generator=gen)
        V = torch.randn(k, n, generator=gen)
        G = vjp(W, X, V).double().numpy()
        C += G.T @ G
        done += k
    C /= m
    ev, U = np.linalg.eigh(C)
    return U[:, ::-1].copy(), ev[::-1].copy(), C


# ----------------------------------------------------------------------------------------------------------------
# cell statistics
def cell_moments(labels, F, K):
    """Per-cell counts, sums and sums of squared norms (trace) of rows of F (numpy float64)."""
    labels = np.asarray(labels, dtype=np.int64)
    cnt = np.bincount(labels, minlength=K).astype(np.float64)
    S = np.zeros((K, F.shape[1]))
    np.add.at(S, labels, F)
    Q = np.bincount(labels, weights=(F * F).sum(1), minlength=K)
    return cnt, S, Q


def within_var(cnt, S, Q):
    """Unbiased per-cell trace variance (nan where count < 2)."""
    with np.errstate(invalid='ignore', divide='ignore'):
        v = (Q - (S * S).sum(1) / cnt) / (cnt - 1)
    v[cnt < 2] = np.nan
    return np.maximum(v, 0.0)


def gains(p, labels_te, F_te, K, V=None, min_count=2):
    """Oracle Neyman and proportional gains on held-out samples given exact (or accurate) p_k.
    Cells with fewer than min_count held-out samples use the pooled within-variance of the sparse cells (reported)."""
    cnt, S, Q = cell_moments(labels_te, F_te, K)
    v = within_var(cnt, S, Q)
    if V is None:
        mu = F_te.mean(0)
        V = float(((F_te - mu) ** 2).sum(1).sum() / (F_te.shape[0] - 1))
    sparse = cnt < min_count
    p = np.asarray(p, dtype=np.float64)
    p_sparse = float(p[sparse].sum())
    if sparse.any():
        # pooled within-variance over sparse cells with >= 2 samples, else the global V (conservative)
        vv = v[(~sparse) & ~np.isnan(v)]
        fill = float(np.nanmean(vv)) if len(vv) else V
        v = np.where(sparse, fill, v)
    sig = np.sqrt(v)
    ney = float((p * sig).sum())
    prop = float((p * v).sum())
    ps = p * sig
    order = np.argsort(-ps)
    cum = np.cumsum(ps[order]) / max(ps.sum(), 1e-300)
    conc = {}
    for q in (0.01, 0.1, 0.5):
        k = max(1, int(round(q * K)))
        conc[q] = float(cum[k - 1])
    # mass carried by the top cells
    return dict(V=V, G_N=V / ney ** 2, G_P=V / prop, ratio=prop / ney ** 2, p_sparse=p_sparse,
                n_sparse=int(sparse.sum()), conc=conc, K=K, min_count_te=int(cnt.min()),
                med_count_te=float(np.median(cnt)))


def tr_var(F):
    mu = F.mean(0)
    return float(((F - mu) ** 2).sum(1).sum() / (F.shape[0] - 1))


# ----------------------------------------------------------------------------------------------------------------
# frame boxes (exact product form)
def Phi(x):
    from scipy.special import ndtr
    return ndtr(x)


def phi(x):
    return np.exp(-0.5 * np.asarray(x) ** 2) / math.sqrt(2 * math.pi)


def interval_mass_mean(a, b):
    """For y ~ N(0,1): P(a < y < b) and E[y | a < y < b] (vectorised)."""
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    pm = Phi(b) - Phi(a)
    with np.errstate(invalid='ignore', divide='ignore'):
        mean = (phi(a) - phi(b)) / pm
    return pm, mean


def sign_cells_in_frame(Y, k):
    """Labels of sign patterns of the first k columns of Y (coordinates in a frame): label = sum_j [y_j > 0] 2^j.
    Exact p = 2^-k for every cell (independent N(0,1) coordinates); centroid = sqrt(2/pi) sum_j s_j u_j."""
    bits = (Y[:, :k] > 0).astype(np.int64)
    return (bits << np.arange(k, dtype=np.int64)[None, :]).sum(1)


# ----------------------------------------------------------------------------------------------------------------
# gate cones
def gate_cell_labels(Z, units):
    bits = (Z[:, units] > 0).astype(np.int64)
    return (bits << np.arange(len(units), dtype=np.int64)[None, :]).sum(1)


def gate_cone_probs(W1, units, m, seed, chunk=1 << 20, centroids=False):
    """p_k for the 2^k sign patterns of z_S = W_S x by cheap k-dimensional sampling: z_S ~ N(0, C), C = W_S W_S^T.
    Cost: m (k^2 + k) flops for the draws (charged by the caller), negligible against passes when k << n.
    If centroids: also E[x | cone] = W_S^T C^{-1} E[z_S | cone] (exact identity for Gaussian x)."""
    WS = np.asarray(W1, dtype=np.float64)[units]
    C = WS @ WS.T
    A = np.linalg.cholesky(C)
    k = len(units)
    g = np.random.RandomState(seed)
    cnt = np.zeros(1 << k)
    zs = np.zeros((1 << k, k)) if centroids else None
    done = 0
    while done < m:
        b = min(chunk, m - done)
        z = g.standard_normal((b, k)) @ A.T
        lab = ((z > 0).astype(np.int64) << np.arange(k, dtype=np.int64)[None, :]).sum(1)
        cnt += np.bincount(lab, minlength=1 << k)
        if centroids:
            np.add.at(zs, lab, z)
        done += b
    p = cnt / m
    out = dict(p=p, flops=float(m) * (2 * k * k + k))
    if centroids:
        with np.errstate(invalid='ignore', divide='ignore'):
            ez = zs / cnt[:, None]
        out['centroid'] = (WS.T @ np.linalg.solve(C, ez.T)).T     # E[x | cone], (2^k, n)
    return out


def orthant_prob_genz(C, signs, abseps=1e-6):
    """P(s_i z_i > 0 for all i), z ~ N(0, C), by scipy's Genz integration (single pattern)."""
    from scipy.stats import multivariate_normal
    s = np.asarray(signs, dtype=np.float64)
    Cs = C * s[:, None] * s[None, :]
    k = len(s)
    mvn = multivariate_normal(mean=np.zeros(k), cov=Cs, allow_singular=False, abseps=abseps, releps=abseps,
                              maxpts=200000 * k)
    # P(z > 0) = P(-z < 0) = cdf at 0 of -z, which has the same covariance
    return float(mvn.cdf(np.zeros(k)))


# ----------------------------------------------------------------------------------------------------------------
# certified bounds: IBP and CROWN from layer l to the output over h = c + P a, a in [-r, r]^d
def _as64(t):
    return t.to(torch.float64)


@torch.no_grad()
def ibp(W, l, c, P, r):
    """Interval bound propagation. c (B, n) centres at layer l, P (n, d) basis (or None for identity), r (B,) or
    (B, d) half-widths. Returns per-layer pre-activation bounds [(lo, hi)] for layers l+1..L and output bounds."""
    c = _as64(c)
    B, n = c.shape
    if P is None:
        rad = r[:, None].expand(B, n) if r.dim() == 1 else r
        lo, hi = c - rad, c + rad
    else:
        P = _as64(P)
        rr = r[:, None].expand(B, P.shape[1]) if r.dim() == 1 else r
        rad = rr @ P.abs().T
        lo, hi = c - rad, c + rad
    pre = []
    for k in range(l, len(W)):
        w = _as64(W[k])
        mid, rad = (lo + hi) / 2, (hi - lo) / 2
        zm = mid @ w.T
        zr = rad @ w.abs().T
        zlo, zhi = zm - zr, zm + zr
        pre.append((zlo, zhi))
        lo, hi = torch.relu(zlo), torch.relu(zhi)
    return pre, (lo, hi)


@torch.no_grad()
def crown(W, l, c, P, r, out_rows=None, alpha_mode='adaptive', inter=None, return_linear=False):
    """CROWN (backward linear relaxation) from layer l to the output, with CROWN intermediate bounds for every layer
    (full CROWN). Input set: h_l = c + P a, a in [-r, r]^d (P None = identity, d = n). Batch of B sets.
    Lower relaxation slope of an unstable unit: 1 if u >= -lo else 0 ('adaptive', CROWN-Ada); upper: u/(u - lo).
    Returns (pre, (lo, hi)): pre[j] = (zlo, zhi) for layer l+1+j; (lo, hi) bounds on out_rows @ h_L (default all
    outputs). Float64. Cost ~ t^2 n^3 flops per set (t = L - l)."""
    c = _as64(c)
    B, n = c.shape
    t = len(W) - l
    Ws = [_as64(W[k]) for k in range(l, len(W))]
    if P is None:
        Pm = None
        rr = r[:, None].expand(B, n) if r.dim() == 1 else r
    else:
        Pm = _as64(P)
        rr = r[:, None].expand(B, Pm.shape[1]) if r.dim() == 1 else r
    rr = _as64(rr)

    def concretize(Lam_u, bias_u, Lam_l, bias_l):
        # Lam (B, m, n) acting on h_l; bounds over the input set
        if Pm is None:
            up = (Lam_u @ c[:, :, None]).squeeze(-1) + (Lam_u.abs() * rr[:, None, :]).sum(-1) + bias_u
            lo = (Lam_l @ c[:, :, None]).squeeze(-1) - (Lam_l.abs() * rr[:, None, :]).sum(-1) + bias_l
        else:
            LPu = Lam_u @ Pm
            LPl = Lam_l @ Pm
            up = (Lam_u @ c[:, :, None]).squeeze(-1) + (LPu.abs() * rr[:, None, :]).sum(-1) + bias_u
            lo = (Lam_l @ c[:, :, None]).squeeze(-1) - (LPl.abs() * rr[:, None, :]).sum(-1) + bias_l
        return lo, up

    if inter is None:          # IBP bounds are sound too: intersect (standard practice; never looser than either)
        inter, _ = ibp(W, l, c, P, r)
    pre = []
    relax = []        # per layer j (0-based within tail): (su, tu, sl) slopes/intercepts for h = relu(z)
    for j in range(t):
        # bound z_{l+1+j} = W_{l+1+j} h_{l+j}
        A = Ws[j].unsqueeze(0).expand(B, n, n)
        Lam_u = A.clone(); Lam_l = A.clone()
        bias_u = torch.zeros(B, n, dtype=torch.float64); bias_l = torch.zeros(B, n, dtype=torch.float64)
        for i in range(j - 1, -1, -1):
            su, tu, sl = relax[i]
            # upper bound of Lam h_i (h_i = relu(z_i)): positive coeffs use upper relaxation, negative the lower
            Lp, Ln = Lam_u.clamp(min=0), Lam_u.clamp(max=0)
            bias_u = bias_u + (Lp * tu[:, None, :]).sum(-1)
            Lam_u = (Lp * su[:, None, :] + Ln * sl[:, None, :]) @ Ws[i]
            Lp, Ln = Lam_l.clamp(min=0), Lam_l.clamp(max=0)
            bias_l = bias_l + (Ln * tu[:, None, :]).sum(-1)
            Lam_l = (Lp * sl[:, None, :] + Ln * su[:, None, :]) @ Ws[i]
        zlo, zhi = concretize(Lam_u, bias_u, Lam_l, bias_l)
        if inter is not None and j < len(inter):          # optional tighter given bounds
            zlo = torch.maximum(zlo, inter[j][0]); zhi = torch.minimum(zhi, inter[j][1])
        pre.append((zlo, zhi))
        # relaxation of relu on [zlo, zhi]
        act = zlo >= 0
        dead = zhi <= 0
        uns = ~(act | dead)
        denom = torch.where(uns, zhi - zlo, torch.ones_like(zhi))
        su = torch.where(act, torch.ones_like(zhi), torch.where(uns, zhi / denom, torch.zeros_like(zhi)))
        tu = torch.where(uns, -zhi * zlo / denom, torch.zeros_like(zhi))
        if alpha_mode == 'adaptive':
            a = (zhi >= -zlo).to(torch.float64)
        else:
            a = torch.zeros_like(zhi)
        sl = torch.where(act, torch.ones_like(zhi), torch.where(uns, a, torch.zeros_like(zhi)))
        relax.append((su, tu, sl))
    # output: rows of out_rows applied to h_L = relu(z_L)
    m = n if out_rows is None else out_rows.shape[0]
    C0 = torch.eye(n, dtype=torch.float64) if out_rows is None else _as64(out_rows)
    Lam_u = C0.unsqueeze(0).expand(B, m, n).clone(); Lam_l = Lam_u.clone()
    bias_u = torch.zeros(B, m, dtype=torch.float64); bias_l = torch.zeros(B, m, dtype=torch.float64)
    for i in range(t - 1, -1, -1):
        su, tu, sl = relax[i]
        Lp, Ln = Lam_u.clamp(min=0), Lam_u.clamp(max=0)
        bias_u = bias_u + (Lp * tu[:, None, :]).sum(-1)
        Lam_u = (Lp * su[:, None, :] + Ln * sl[:, None, :]) @ Ws[i]
        Lp, Ln = Lam_l.clamp(min=0), Lam_l.clamp(max=0)
        bias_l = bias_l + (Ln * tu[:, None, :]).sum(-1)
        Lam_l = (Lp * sl[:, None, :] + Ln * su[:, None, :]) @ Ws[i]
    lo, up = concretize(Lam_u, bias_u, Lam_l, bias_l)
    if out_rows is None:       # outputs are relu values: intersect with the IBP range of relu(z_L)
        zlo, zhi = pre[-1]
        lo = torch.maximum(lo, torch.relu(zlo)); up = torch.minimum(up, torch.relu(zhi))
    if return_linear:          # linear bounds on h_l: Lam_l h + bias_l <= out <= Lam_u h + bias_u on the set
        return pre, (lo, up), (Lam_l, bias_l, Lam_u, bias_u)
    return pre, (lo, up)


def crown_flops(n, t, d=None, m=None):
    """Approximate flops of crown() per input set: intermediate layer j needs j backward steps of two (n x n)(n x n)
    products; the output needs t steps; concretisation one more product per bound."""
    d = n if d is None else d
    m = n if m is None else m
    inter = sum(2 * j * 2 * n ** 3 for j in range(t))
    outp = 2 * t * 2 * m * n * n
    conc = 2 * (t + 1) * 2 * n * n * d
    return float(inter + outp + conc)


def stable_counts(pre):
    """Per layer: number of units certified active (lo >= 0), dead (hi <= 0), unstable."""
    res = []
    for zlo, zhi in pre:
        act = (zlo >= 0).sum(-1)
        dead = (zhi <= 0).sum(-1)
        res.append((act, dead, zlo.shape[-1] - act - dead))
    return res


# ----------------------------------------------------------------------------------------------------------------
# pick-freeze closed index of a subspace (Jansen): Sbar_S = 1 - E|f(x) - f(x~)|^2 / (2 V), x~ = (x_S, x'_{S-perp})
@torch.no_grad()
def closed_index(W, U_S, m, seed, V=None, chunk=1 << 13):
    """U_S (n, s) orthonormal columns. Returns (Sbar, se, V_hat) with V estimated from the same draws if None."""
    n = W[0].shape[0]
    gen = torch.Generator().manual_seed(int(seed))
    US = torch.from_numpy(np.asarray(U_S, dtype=np.float32))
    d2 = []; F1 = []
    done = 0
    while done < m:
        k = min(chunk, m - done)
        x = torch.randn(k, n, generator=gen)
        xp = torch.randn(k, n, generator=gen)
        xs = (x @ US) @ US.T
        xt = xs + (xp - (xp @ US) @ US.T)
        f1 = forward(W, x); f2 = forward(W, xt)
        d2.append(((f1 - f2).double() ** 2).sum(1).numpy())
        F1.append(f1.double().numpy())
        done += k
    d2 = np.concatenate(d2)
    if V is None:
        V = tr_var(np.concatenate(F1))
    S = 1.0 - d2.mean() / (2 * V)
    se = d2.std() / math.sqrt(len(d2)) / (2 * V)
    return float(S), float(se), float(V)


# ----------------------------------------------------------------------------------------------------------------
# CART (best-first) over candidate hyperplanes; Neyman objective on training samples
class Tree:
    """Cells are leaves of a binary tree; node splits on (direction index, threshold): left = proj <= thr."""

    def __init__(self):
        self.nodes = []      # (dir, thr, left, right) for internal; None for leaves
        self.leaf_of_node = {}

    def route(self, Pfun, m):
        """Assign leaf ids. Pfun(idx, dirs) returns projections (len(idx), len(dirs)) of samples idx on dirs."""
        leaf = np.full(m, -1, dtype=np.int64)
        stack = [(0, np.arange(m))]
        while stack:
            node, idx = stack.pop()
            spec = self.nodes[node]
            if spec is None or spec[0] is None:
                leaf[idx] = self.leaf_of_node[node]
                continue
            d, thr, lft, rgt = spec
            pr = Pfun(idx, [d])[:, 0]
            go_l = pr <= thr
            stack.append((lft, idx[go_l]))
            stack.append((rgt, idx[~go_l]))
        return leaf


def _sd_obj(cnt, s, q):
    """p-weighted sd proxy: count * sqrt(within variance) (Neyman objective up to the 1/m factor)."""
    if cnt < 2:
        return 0.0
    v = max((q - (s * s).sum() / cnt) / (cnt - 1), 0.0)
    return cnt * math.sqrt(v)


def grow_cart(Proj, Fsel, Kmax, min_leaf=32, quantiles=(0.25, 0.5, 0.75), fixed_thr=None, sub=1 << 14, seed=0,
              checkpoints=None, objective='neyman'):
    """Best-first CART on training data. Proj (m, C) projections of training inputs on C candidate directions;
    Fsel (m, r) outputs (projected) used for the objective; fixed_thr: optional (C,) array of a fixed threshold per
    direction (e.g. 0 for gate normals; nan = use quantiles). Returns (tree, leaf labels of training samples, history)
    where history lists the tree after each checkpoint K (deep copies of node lists)."""
    rng = np.random.RandomState(seed)
    m, C = Proj.shape
    q_all = (Fsel * Fsel).sum(1)
    tree = Tree()
    tree.nodes.append(None)
    leaves = {0: np.arange(m)}
    best = {}

    def score(idx):
        cnt = len(idx)
        s = Fsel[idx].sum(0); q = q_all[idx].sum()
        if objective == 'neyman':
            return _sd_obj(cnt, s, q)
        v = max((q - (s * s).sum() / cnt) / max(cnt - 1, 1), 0.0)
        return cnt * v

    def best_split(idx):
        if len(idx) < 2 * min_leaf:
            return None
        sidx = idx if len(idx) <= sub else rng.choice(idx, sub, replace=False)
        scale = len(idx) / len(sidx)
        Pm = Proj[sidx]                         # (ms, C)
        Fm = Fsel[sidx]; qm = q_all[sidx]
        S_tot = Fm.sum(0); Q_tot = qm.sum(); n_tot = len(sidx)
        base = score(idx)
        best_gain, best_spec = 0.0, None
        thr_list = []
        if fixed_thr is not None:
            thr_list.append(np.where(np.isnan(fixed_thr), np.nan, fixed_thr))
        for qq in quantiles:
            thr_list.append(np.quantile(Pm, qq, axis=0))
        for thr in thr_list:
            valid = ~np.isnan(thr)
            if not valid.any():
                continue
            thr_v = np.where(valid, thr, 0.0)
            L = (Pm <= thr_v[None, :]).astype(np.float64)          # (ms, C)
            nL = L.sum(0)
            SL = L.T @ Fm                                          # (C, r)
            QL = L.T @ qm
            nR = n_tot - nL; SR = S_tot[None, :] - SL; QR = Q_tot - QL
            ok = valid & (nL * scale >= min_leaf) & (nR * scale >= min_leaf)
            if not ok.any():
                continue
            with np.errstate(invalid='ignore', divide='ignore'):
                vL = np.maximum((QL - (SL * SL).sum(1) / nL) / (nL - 1), 0)
                vR = np.maximum((QR - (SR * SR).sum(1) / nR) / (nR - 1), 0)
                if objective == 'neyman':
                    obj = scale * (nL * np.sqrt(vL) + nR * np.sqrt(vR))
                else:
                    obj = scale * (nL * vL + nR * vR)
            obj = np.where(ok, obj, np.inf)
            j = int(np.argmin(obj))
            g = base - obj[j]
            if g > best_gain:
                best_gain, best_spec = g, (j, float(thr_v[j]))
        return (best_gain, best_spec) if best_spec is not None else None

    best[0] = best_split(leaves[0])
    hist = {}
    K = 1
    checkpoints = sorted(checkpoints or [])
    while K < Kmax:
        cand = [(b[0], node) for node, b in best.items() if b is not None and node in leaves]
        if not cand:
            break
        g, node = max(cand)
        d, thr = best[node][1]
        idx = leaves.pop(node)
        pr = Proj[idx, d]
        li, ri = idx[pr <= thr], idx[pr > thr]
        lnode = len(tree.nodes); tree.nodes.append(None)
        rnode = len(tree.nodes); tree.nodes.append(None)
        tree.nodes[node] = (d, thr, lnode, rnode)
        leaves[lnode] = li; leaves[rnode] = ri
        best.pop(node, None)
        best[lnode] = best_split(li); best[rnode] = best_split(ri)
        K += 1
        if K in checkpoints:
            hist[K] = (list(tree.nodes), sorted(leaves.keys()))
    hist[K] = (list(tree.nodes), sorted(leaves.keys()))
    return tree, hist


def tree_from_hist(nodes, leaf_nodes):
    t = Tree()
    t.nodes = list(nodes)
    # leaves are nodes that are None or listed
    for i, node in enumerate(leaf_nodes):
        t.leaf_of_node[node] = i
    for node in leaf_nodes:
        t.nodes[node] = None
    return t
