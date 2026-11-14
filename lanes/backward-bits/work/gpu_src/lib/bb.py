"""Backward-bits lane library (torch; CPU for dev and tests, CUDA for scored runs).

Model S nets (as the bit-accounting S4 runs): h_0 = x ~ N(0, I_n); h_l = relu(W_l h_{l-1}) + sigma xi_l (l = 1..L-1);
h_L = a = relu(W_L h_{L-1}) (no output noise); W_l = st.W_layer(seed, n, l).
Codes: deterministic maps of h_l into {0..K-1}.
  OutCode   k-means quantiser of the output a (the "last layer, trained to convergence"); as a code of h_{L-1} it is
            Q(relu(W_L h)), with no noise between L-1 and L.
  LayerCode posterior predictor q(h) (MLP -> softmax over the target code's values) followed by the deterministic
            information-bottleneck quantiser: c(h) = argmax_k [q(h) . log mu_k + log(pi_k) / beta].
Monte Carlo posteriors: for each point h_l, M fresh draws of the next layer's noise give counts of the next code
(one noisy layer) or of the output code (the whole future). Entropies in bits with the Miller-Madow correction.
"""
import hashlib
import math

import numpy as np
import torch
import torch.nn as nn

DT = torch.float32
LN2 = math.log(2.0)


# ----------------------------------------------------------------------------------------------------------------------
# Seeds and nets
# ----------------------------------------------------------------------------------------------------------------------

def W_layer(seed, n, l):
    """Identical to work/stationary/lib/st.W_layer (checked in tests/test_bb.py)."""
    rng = np.random.default_rng([77123, int(seed), int(n), int(l) + 10 ** 7])
    return rng.standard_normal((n, n)) * math.sqrt(2.0 / n)


def seed_of(*parts):
    h = hashlib.sha256(repr(parts).encode()).digest()
    return int.from_bytes(h[:8], 'little') & ((1 << 62) - 1)


def make_gen(device, *parts):
    g = torch.Generator(device=device)
    g.manual_seed(seed_of(*parts))
    return g


class Net:
    def __init__(self, seed, n, L, sigma, device='cpu'):
        self.seed, self.n, self.L, self.sigma, self.device = int(seed), int(n), int(L), float(sigma), device
        self.WT = [torch.tensor(np.ascontiguousarray(W_layer(seed, n, l).T), dtype=DT, device=device)
                   for l in range(1, L + 1)]

    def pre(self, h, l):
        """Noise-free part of layer l (l = 1..L) applied to h = h_{l-1}."""
        return torch.relu(h @ self.WT[l - 1])

    def noisy(self, l):
        return l < self.L and self.sigma > 0

    def step(self, h, l, g):
        z = self.pre(h, l)
        if self.noisy(l):
            z = z + self.sigma * torch.randn(z.shape, generator=g, device=z.device, dtype=DT)
        return z

    def run(self, h, l0, l1, g):
        """State at layer l1 from h at layer l0 (fresh noise)."""
        for l in range(l0 + 1, l1 + 1):
            h = self.step(h, l, g)
        return h

    def run_xi(self, h, l0, xis):
        """Same with given noises: xis[l] (shape of h) used at hidden layer l (dict or list indexed by layer)."""
        for l in range(l0 + 1, self.L + 1):
            z = self.pre(h, l)
            if self.noisy(l):
                z = z + self.sigma * xis[l]
            h = z
        return h

    @torch.no_grad()
    def sample(self, P, l, g):
        x = torch.randn(P, self.n, generator=g, device=self.device, dtype=DT)
        return self.run(x, 0, l, g)

    @torch.no_grad()
    def sample_all(self, P, g):
        """[h_0, ..., h_L] for P independent inputs (one forward path each)."""
        h = torch.randn(P, self.n, generator=g, device=self.device, dtype=DT)
        H = [h]
        for l in range(1, self.L + 1):
            h = self.step(h, l, g)
            H.append(h)
        return H


# ----------------------------------------------------------------------------------------------------------------------
# Entropies
# ----------------------------------------------------------------------------------------------------------------------

def ent_rows(p):
    """Entropy in bits of each row of a probability matrix (0 log 0 = 0)."""
    p = p.to(torch.float64)
    return -(p * torch.log2(p.clamp_min(1e-300))).sum(-1)


def ent_counts(counts, mm=True):
    """Per-row entropy (bits) of empirical laws given integer counts; Miller-Madow correction if mm."""
    c = counts.to(torch.float64)
    M = c.sum(-1)
    H = ent_rows(c / M.clamp_min(1)[..., None])
    if mm:
        m = (c > 0).sum(-1).to(torch.float64)
        H = H + (m - 1) / (2 * M.clamp_min(1) * LN2)
    return H


def ent_counts_grassberger(counts):
    """Grassberger (2003) estimator per row (bits)."""
    n = counts.to(torch.float64)
    M = n.sum(-1)
    dg = torch.special.digamma
    G = dg(n.clamp_min(1)) + 0.5 * torch.where(n.long() % 2 == 0, 1.0, -1.0) * (dg((n + 1) / 2) - dg(n.clamp_min(1) / 2))
    G = torch.where(n > 0, G, torch.zeros_like(G))
    return (torch.log(M) - (n * G).sum(-1) / M) / LN2


def ent_of_marginal(counts):
    c = counts.to(torch.float64).sum(0)
    K = float((c > 0).sum())
    N = float(c.sum())
    return float(ent_rows(c / N)) + (K - 1) / (2 * N * LN2)


def target_stats(counts):
    """T = H(next) - E H(next | h) from per-point counts (N, K) with M draws per point. Returns dict (bits)."""
    N = counts.shape[0]
    Hn = ent_of_marginal(counts)
    Hi = ent_counts(counts, mm=True)
    Hi_pl = ent_counts(counts, mm=False)
    Hi_gr = ent_counts_grassberger(counts)
    E = float(Hi.mean())
    return dict(T=Hn - E, se=float(Hi.std()) / math.sqrt(N), H_next=Hn, erased=E, erased_plugin=float(Hi_pl.mean()),
                erased_gr=float(Hi_gr.mean()), T_gr=Hn - float(Hi_gr.mean()), mm_corr=float((Hi - Hi_pl).mean()),
                N=N, M=int(counts[0].sum()))


@torch.no_grad()
def boot_se_T(P, Hrow, B=200, seed=0):
    """Bootstrap SE over points of T = H(mean of rows P) - mean(Hrow), both terms resampled together (review r1 #4)."""
    N = P.shape[0]
    g = torch.Generator(device='cpu')
    g.manual_seed(seed)
    Ts = []
    for _ in range(B):
        idx = torch.randint(N, (N,), generator=g).to(P.device)
        Ts.append(float(ent_rows(P[idx].mean(0)[None])) - float(Hrow[idx].mean()))
    return float(torch.tensor(Ts, dtype=torch.float64).std())


def relevance(codes, counts, K):
    """Rate H(c) and relevance I(c; next) of a deterministic code (codes (N,) in [0, K)) from per-point counts of the
    next code (N, Kn), cell posteriors = pooled counts of the points in the cell. Split-half Richardson bias check."""
    def one(idx):
        cc = codes[idx]
        C = counts[idx].to(torch.float64)
        S = torch.zeros(K, C.shape[1], dtype=torch.float64, device=C.device).index_add_(0, cc, C)
        nk = torch.bincount(cc, minlength=K).to(torch.float64)
        tot = S.sum(1)
        pi = nk / nk.sum()
        used = tot > 0
        mu = S[used] / tot[used, None]
        Hc = float(ent_rows(pi[pi > 0][None]))
        Hn = float(ent_rows((S.sum(0) / S.sum())[None]))
        Hcond = float((pi[used] * ent_rows(mu)).sum())
        return Hc, Hn - Hcond, int((nk > 0).sum())
    N = codes.shape[0]
    allidx = torch.arange(N, device=codes.device)
    Hc, I, k_used = one(allidx)
    g = torch.Generator(device='cpu')
    g.manual_seed(12345)
    perm = torch.randperm(N, generator=g).to(codes.device)
    _, Ia, _ = one(perm[: N // 2])
    _, Ib, _ = one(perm[N // 2:])
    Ibc = 2 * I - 0.5 * (Ia + Ib)
    Hc_mm = Hc + (k_used - 1) / (2 * N * LN2)
    return dict(H=Hc_mm, H_plugin=Hc, I=Ibc, I_plugin=I, I_half=0.5 * (Ia + Ib), K_used=k_used)


# ----------------------------------------------------------------------------------------------------------------------
# k-means (output code) and the deterministic information bottleneck (layer codes)
# ----------------------------------------------------------------------------------------------------------------------

@torch.no_grad()
def kmeans(X, K, g, restarts=5, iters=500, tol=1e-9, chunk=1 << 16):
    """Euclidean k-means++ then Lloyd to convergence; best of `restarts` by distortion. Returns (C, dist, info)."""
    N = X.shape[0]
    best = None
    info = []
    for r in range(restarts):
        idx = torch.randint(N, (1,), generator=g, device=X.device)
        C = X[idx].clone()
        d2 = ((X - C[0]) ** 2).sum(1)
        for k in range(1, K):
            pr = d2 / d2.sum()
            j = torch.multinomial(pr, 1, generator=g)
            C = torch.cat([C, X[j]], 0)
            d2 = torch.minimum(d2, ((X - X[j]) ** 2).sum(1))
        prev = None
        for it in range(iters):
            a = assign_euclid(X, C, chunk)
            S = torch.zeros_like(C).index_add_(0, a, X)
            nk = torch.bincount(a, minlength=K).to(DT)
            empty = nk == 0
            if bool(empty.any()):        # re-seed empty cells at the worst-fit points
                dd = ((X - C[a]) ** 2).sum(1)
                far = torch.topk(dd, int(empty.sum())).indices
                S[empty] = X[far]
                nk[empty] = 1.0
            C = S / nk[:, None]
            dist = float(((X - C[a]) ** 2).sum(1).mean())
            if prev is not None and abs(prev - dist) <= tol * max(prev, 1e-30):
                break
            prev = dist
        a = assign_euclid(X, C, chunk)
        dist = float(((X - C[a]) ** 2).sum(1).mean())
        info.append(dict(restart=r, dist=dist, iters=it + 1))
        if best is None or dist < best[1]:
            best = (C.clone(), dist)
    return best[0], best[1], info


@torch.no_grad()
def assign_euclid(X, C, chunk=1 << 16):
    cc = (C * C).sum(1)
    out = []
    for i in range(0, X.shape[0], chunk):
        out.append(torch.argmax(2 * X[i:i + chunk] @ C.T - cc, 1))
    return torch.cat(out)


def _logmu(P, a, K, floor=1e-12):
    S = torch.zeros(K, P.shape[1], dtype=P.dtype, device=P.device).index_add_(0, a, P)
    nk = torch.bincount(a, minlength=K).to(P.dtype)
    mu = S / nk.clamp_min(1)[:, None]
    return torch.log(mu.clamp_min(floor)), nk


@torch.no_grad()
def ib_stats(P, a, K):
    """Training-side rate and relevance of assignments a for target posteriors P (rows sum to 1)."""
    nk = torch.bincount(a, minlength=K).to(torch.float64)
    pi = nk / nk.sum()
    S = torch.zeros(K, P.shape[1], dtype=torch.float64, device=P.device).index_add_(0, a, P.to(torch.float64))
    used = nk > 0
    mu = S[used] / nk[used, None]
    Hn = float(ent_rows(P.to(torch.float64).mean(0)[None]))
    I = Hn - float((pi[used] * ent_rows(mu)).sum())
    return float(ent_rows(pi[used][None])), I


@torch.no_grad()
def kl_kmeanspp(P, K, g):
    """KL-k-means++ seeding on posterior rows: next centre drawn with probability proportional to the KL distance to
    the nearest centre."""
    N = P.shape[0]
    logP = torch.log(P.clamp_min(1e-12))
    negH = (P * logP).sum(1)
    j = int(torch.randint(N, (1,), generator=g, device=P.device))
    cent = [j]
    d = negH - P @ torch.log(P[j].clamp_min(1e-12))
    for _ in range(1, K):
        pr = d.clamp_min(0)
        if float(pr.sum()) <= 0:
            break
        j = int(torch.multinomial(pr / pr.sum(), 1, generator=g))
        cent.append(j)
        d = torch.minimum(d, negH - P @ torch.log(P[j].clamp_min(1e-12)))
    return torch.log(P[cent].clamp_min(1e-12))


@torch.no_grad()
def dib_lloyd(P, logmu, beta, logpi=None, iters=100, tol_frac=1e-4):
    """Deterministic IB Lloyd iterations: assign = argmax_k [P . logmu_k + logpi_k / beta]; re-estimate; drop empty
    cells. beta = inf gives KL k-means. Stops when at most tol_frac of the assignments change (a few points can
    oscillate between cells forever). Returns (a, logmu, logpi, iters)."""
    K = logmu.shape[0]
    if logpi is None:
        logpi = torch.full((K,), -math.log(K), device=P.device, dtype=P.dtype)
    prev = None
    for it in range(iters):
        sc = P @ logmu.T
        if math.isfinite(beta):
            sc = sc + logpi[None] / beta
        a = torch.argmax(sc, 1)
        used = torch.unique(a)
        remap = torch.full((K,), -1, dtype=torch.long, device=P.device)
        remap[used] = torch.arange(used.numel(), device=P.device)
        a = remap[a]
        K = used.numel()
        logmu, nk = _logmu(P, a, K)
        logpi = torch.log(nk / nk.sum())
        if prev is not None and prev.shape == a.shape and int((prev != a).sum()) <= tol_frac * a.shape[0]:
            break
        prev = a
    return a, logmu, logpi, it + 1


@torch.no_grad()
def dib_path(P, K0, g, beta_hi=1e4, beta_lo=0.3, factor=0.85, min_H=0.0):
    """One annealed DIB path: KL-k-means++ with K0 cells, Lloyd at beta = inf, then beta decreasing geometrically.
    Returns a list of solutions dict(beta, H, I, K, logmu, logpi) (training-side H, I on P)."""
    logmu = kl_kmeanspp(P, K0, g)
    a, logmu, logpi, _ = dib_lloyd(P, logmu, math.inf)
    sols = []
    H, I = ib_stats(P, a, logmu.shape[0])
    sols.append(dict(beta=math.inf, H=H, I=I, K=logmu.shape[0], logmu=logmu.clone(), logpi=logpi.clone()))
    beta = beta_hi
    while beta >= beta_lo and logmu.shape[0] > 1:
        a, logmu, logpi, _ = dib_lloyd(P, logmu, beta, logpi, iters=30)
        H, I = ib_stats(P, a, logmu.shape[0])
        sols.append(dict(beta=beta, H=H, I=I, K=logmu.shape[0], logmu=logmu.clone(), logpi=logpi.clone()))
        if H < min_H:
            break
        beta *= factor
    return sols


@torch.no_grad()
def two_cell_family(P, logmu2, probs=(0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5), iters=15):
    """Entropy-constrained 2-cell codes: threshold the log-likelihood ratio d = P . (log mu_0 - log mu_1) at the
    quantile that gives the small cell probability p (both sides), re-estimating the centroids (Lloyd with a fixed
    cell size). Encoded as logpi = [-tau, 0], beta = 1, so that argmax reproduces the threshold."""
    out = []
    N = P.shape[0]
    if logmu2.shape[0] < 2:                       # the 2-cell clustering collapsed: nothing to threshold (review r1 #9)
        return out
    for p in probs:
        for side in (0, 1):
            lm = logmu2.clone()
            ok = True
            for _ in range(iters):
                d = P @ (lm[0] - lm[1])
                tau = torch.quantile(d.float(), 1 - p if side == 0 else p).to(d.dtype)
                a = (d <= tau).long()            # cell 0 = d > tau
                if int(a.sum()) in (0, N):
                    ok = False
                    break
                lm, nk = _logmu(P, a, 2)
            if not ok:
                continue
            # the returned pair (lm, tau) is exactly what produces the assignment a (review r1 #10)
            d = P @ (lm[0] - lm[1])
            tau = torch.quantile(d.float(), 1 - p if side == 0 else p).to(d.dtype)
            a = (d <= tau).long()
            if int(a.sum()) in (0, N):
                continue
            H, I = ib_stats(P, a, 2)
            out.append(dict(kind='two', K0=2, beta=1.0, H=H, I=I, K=2, logmu=lm.clone(),
                            logpi=torch.tensor([-float(tau), 0.0], dtype=P.dtype, device=P.device)))
    return out


@torch.no_grad()
def candidates(P, g, K_list, restarts=3, dib_K0=None, dib_restarts=1, dib_K0s=(8,)):
    """Candidate codes for target rows P: KL-k-means (beta = inf) for each K in K_list (best of `restarts` by training
    relevance), the entropy-constrained 2-cell threshold family, and annealed DIB paths from several initial sizes
    (dib_K0s and dib_K0). List of dicts."""
    N = P.shape[0]
    mean = P.mean(0, keepdim=True)
    out = [dict(kind='const', K0=1, beta=math.inf, H=0.0, I=0.0, K=1,           # the 0-bit code (review r1 #9)
                logmu=torch.log(mean.clamp_min(1e-12)), logpi=torch.zeros(1, dtype=P.dtype, device=P.device))]
    for K in K_list:
        if K > N:
            continue
        best = None
        for r in range(restarts):
            logmu = kl_kmeanspp(P, K, g)
            a, logmu, logpi, _ = dib_lloyd(P, logmu, math.inf)
            H, I = ib_stats(P, a, logmu.shape[0])
            if best is None or I > best['I']:
                best = dict(kind='kmeans', K0=K, beta=math.inf, H=H, I=I, K=logmu.shape[0], logmu=logmu.clone(),
                            logpi=logpi.clone())
        out.append(best)
        if K == 2 and best['K'] == 2:
            out += two_cell_family(P, best['logmu'])
    if dib_K0:
        dib = []
        for K0 in sorted(set([k for k in dib_K0s if k < dib_K0] + [dib_K0])):
            for r in range(dib_restarts):
                for s_ in dib_path(P, K0, g, factor=0.8):
                    s_['kind'] = 'dib'
                    s_['K0'] = K0
                    dib.append(s_)
        keep = envelope(dib)                    # dominated DIB solutions (on the training rows) are dropped
        out += [dib[i] for i in keep]
    return out


def envelope(points, hkey='H', ikey='I'):
    """Indices of the upper-left envelope (no other point has lower-or-equal rate and higher relevance)."""
    order = sorted(range(len(points)), key=lambda i: (points[i][hkey], -points[i][ikey]))
    keep, best = [], -1e9
    for i in order:
        if points[i][ikey] > best + 1e-12:
            keep.append(i)
            best = points[i][ikey]
    return keep


# ----------------------------------------------------------------------------------------------------------------------
# Codes
# ----------------------------------------------------------------------------------------------------------------------

def fix_table(Q, fallback):
    """Rows of a cell table that are empty (no points) get the fallback distribution; every row is normalised to sum 1.
    Returns (Q, number of filled rows)."""
    Q = Q.clone()
    s = Q.sum(1)
    bad = s <= 1e-12
    Q[bad] = fallback.to(Q.dtype)
    Q = Q / Q.sum(1, keepdim=True)
    return Q, int(bad.sum())


class OutCode:
    """k-means quantiser of the output; as a code of h_{L-1}: Q(relu(W_L h))."""

    def __init__(self, C, net):
        self.C = C
        self.cc = (C * C).sum(1)
        self.K = C.shape[0]
        self.net = net

    @torch.no_grad()
    def assign_out(self, a):
        return torch.argmax(2 * a @ self.C.T - self.cc, 1)

    @torch.no_grad()
    def assign(self, h):
        return self.assign_out(self.net.pre(h, self.net.L))


class MLP(nn.Module):
    def __init__(self, d_in, d_out, width, depth):
        super().__init__()
        layers, d = [], d_in
        for _ in range(depth):
            layers += [nn.Linear(d, width), nn.GELU()]
            d = width
        layers.append(nn.Linear(d, d_out))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class Predictor(nn.Module):
    """Posterior predictor q(h) over the target code's values (logits); inputs standardised."""

    def __init__(self, n, Kt, width, depth, mu, sd):
        super().__init__()
        self.mlp = MLP(n, Kt, width, depth)
        self.register_buffer('mu', mu.clone())
        self.register_buffer('sd', sd.clone())
        self.cfg = dict(n=n, Kt=Kt, width=width, depth=depth)

    def forward(self, h):
        return self.mlp((h - self.mu) / self.sd)


class LayerCode:
    def __init__(self, pred, logmu, logpi, beta):
        self.pred = pred
        self.logmu = logmu.to(DT)
        self.logpi = logpi.to(DT)
        self.beta = float(beta)
        self.K = logmu.shape[0]
        self.bias = (self.logpi / self.beta) if math.isfinite(self.beta) else torch.zeros_like(self.logpi)

    @torch.no_grad()
    def assign(self, h, chunk=1 << 18):
        out = []
        for i in range(0, h.shape[0], chunk):
            q = torch.softmax(self.pred(h[i:i + chunk]), 1)
            out.append(torch.argmax(q @ self.logmu.T + self.bias, 1))
        return torch.cat(out)

    @torch.no_grad()
    def assign_q(self, q):
        return torch.argmax(q @ self.logmu.T + self.bias, 1)

    def state(self):
        return dict(type='layer', pred=self.pred.state_dict(), cfg=self.pred.cfg, logmu=self.logmu.cpu(),
                    logpi=self.logpi.cpu(), beta=self.beta)

    @staticmethod
    def load(st, device):
        cfg = st['cfg']
        pred = Predictor(cfg['n'], cfg['Kt'], cfg['width'], cfg['depth'], torch.zeros(cfg['n']), torch.ones(cfg['n']))
        pred.load_state_dict(st['pred'])
        pred.to(device).eval()
        return LayerCode(pred, st['logmu'].to(device), st['logpi'].to(device), st['beta'])


class CompCode:
    """Kelvin's 'use the last encoding': c(h) = c_next(relu(W_{l+1} h)) (noise-free composition). Stacked reuses make
    the encoder deeper, one layer of the net per reuse."""

    def __init__(self, nxt, net, l):
        self.nxt, self.net, self.l = nxt, net, l
        self.K = nxt.K
        self.depth = 1 + getattr(nxt, 'depth', 0)

    @torch.no_grad()
    def assign(self, h):
        return self.nxt.assign(self.net.pre(h, self.l + 1))

    def state(self):
        return dict(type='comp', l=self.l, depth=self.depth)


def load_code(path_of, l, L, net, out_code, device):
    """The saved code at layer l of a chain (path_of(l) -> code_l{l}.pt); reuse codes are rebuilt recursively."""
    if l == L - 1:
        return out_code
    st = torch.load(path_of(l), map_location=device)['code']
    if st.get('type') == 'comp':
        return CompCode(load_code(path_of, l + 1, L, net, out_code, device), net, l)
    return LayerCode.load(st, device)


# ----------------------------------------------------------------------------------------------------------------------
# Monte Carlo posteriors
# ----------------------------------------------------------------------------------------------------------------------

@torch.no_grad()
def mc_counts_next(net, l, h, code_next, M, g, max_rows=1 << 21):
    """Counts (N, K_next) of c_{l+1} = code_next(h_{l+1}) over M fresh draws of xi_{l+1}, for points h = h_l."""
    N, n = h.shape
    K = code_next.K
    out = torch.zeros(N, K, dtype=torch.int32, device=h.device)
    B = max(1, max_rows // M)
    for i0 in range(0, N, B):
        z = net.pre(h[i0:i0 + B], l + 1)
        b = z.shape[0]
        zz = z[:, None, :].expand(b, M, n).reshape(b * M, n)
        if net.noisy(l + 1):
            zz = zz + net.sigma * torch.randn(zz.shape, generator=g, device=h.device, dtype=DT)
        c = code_next.assign(zz)
        idx = torch.arange(b, device=h.device).repeat_interleave(M) * K + c
        out[i0:i0 + b] = torch.bincount(idx, minlength=b * K).view(b, K).to(torch.int32)
    return out


@torch.no_grad()
def mc_counts_out(net, l, h, out_code, M, g, max_rows=1 << 21):
    """Counts (N, K_L) of the output code over M draws of the whole future noise (layers l+1..L-1), points h = h_l."""
    N, n = h.shape
    K = out_code.K
    out = torch.zeros(N, K, dtype=torch.int32, device=h.device)
    B = max(1, max_rows // M)
    for i0 in range(0, N, B):
        z = net.pre(h[i0:i0 + B], l + 1)
        b = z.shape[0]
        zz = z[:, None, :].expand(b, M, n).reshape(b * M, n)
        if net.noisy(l + 1):
            zz = zz + net.sigma * torch.randn(zz.shape, generator=g, device=h.device, dtype=DT)
        a = net.run(zz, l + 1, net.L, g)
        c = out_code.assign_out(a)
        idx = torch.arange(b, device=h.device).repeat_interleave(M) * K + c
        out[i0:i0 + b] = torch.bincount(idx, minlength=b * K).view(b, K).to(torch.int32)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Predictor training
# ----------------------------------------------------------------------------------------------------------------------

def train_predictor(h_tr, P_tr, h_va, P_va, width=256, depth=2, steps=3000, batch=4096, lr=3e-3, seed=0,
                    device='cpu', log_every=0):
    """Soft-label cross-entropy (bits) of q(h) against target rows P (probabilities). Returns (pred, info)."""
    torch.manual_seed(seed)
    mu = h_tr.mean(0)
    sd = h_tr.std(0).clamp_min(1e-6)
    pred = Predictor(h_tr.shape[1], P_tr.shape[1], width, depth, mu, sd).to(device)
    opt = torch.optim.Adam(pred.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=lr, total_steps=steps, pct_start=0.05,
                                                final_div_factor=300)
    g = torch.Generator(device=device)
    g.manual_seed(seed + 17)
    N = h_tr.shape[0]
    for s in range(steps):
        idx = torch.randint(N, (batch,), generator=g, device=device)
        logq = torch.log_softmax(pred(h_tr[idx]), 1)
        loss = -(P_tr[idx] * logq).sum(1).mean() / LN2
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        if log_every and s % log_every == 0:
            print(f'  step {s} ce {float(loss):.4f}', flush=True)
    pred.eval()
    ce_va = cross_entropy_bits(pred, h_va, P_va)
    ce_tr = cross_entropy_bits(pred, h_tr, P_tr)
    return pred, dict(ce_va=ce_va, ce_tr=ce_tr, steps=steps, width=width, depth=depth)


@torch.no_grad()
def cross_entropy_bits(pred, h, P, chunk=1 << 17):
    tot = 0.0
    for i in range(0, h.shape[0], chunk):
        logq = torch.log_softmax(pred(h[i:i + chunk]), 1)
        tot += float(-(P[i:i + chunk] * logq).sum()) / LN2
    return tot / h.shape[0]


@torch.no_grad()
def predict(pred, h, chunk=1 << 17):
    return torch.cat([torch.softmax(pred(h[i:i + chunk]), 1) for i in range(0, h.shape[0], chunk)])
