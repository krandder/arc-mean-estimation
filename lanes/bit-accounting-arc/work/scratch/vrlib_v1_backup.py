"""bit-accounting-arc: one lambda-conditioned variable-rate code per (net, layer, class), batched over M models.

Nets (noiseless He-ReLU stacks, no biases, x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), output a = h_L):
  arc  256 x 32, W_l = st.W_layer(seed, 256, l) (input-bits / relevance lanes' nets);
  nd   8 x 256, nd.make_weights('plain', seed, 8, 256), rescaled per layer by constants (nMSE-invariant), from
       weights/nd_<seed>.npy (made by scratch/make_nd_weights.py with the sibling lane's rescale_weights);
  toy  planted future of k known directions: state h ~ N(0, I_256) at layer 0, future a = G_d ... G_1 Q' Q^T h (linear,
       rank k), so a is Gaussian of rank k and its rate-distortion function is reverse water-filling over its spectrum.
Code: z = g(t) * nu(h; t) + eps, eps ~ N(0, I_K) fixed; t = log10(lambda); the encoder chooses the scale via g.
Rate (bits) = E log2 q(z|h) - log2 p(z|t) with E log2 q = -(K/2) log2(2 pi e) exactly and
  p(z_k | t) = sum_j pi_kj N(z_k; g_k m_kj, g_k^2 s_kj^2 + 1) (factorised mixture in the normalised coordinate).
Distortion: D = |g_l(h_hat) - a|^2 / V, V = tr Var(a), h_hat decoded state at layer l, g_l the real future.
Loss per (model, lambda group): (R + D / lambda) / running mean of the same in its t bin.
Classes: 'local' (one ReLU layer of width n then affine, anchored in t), 'unres' (residual FiLM MLP on whitened h_l and
the whitened exact output, width W), 'out' (layer L: the output's own code, encoder sees a). Decoder: residual FiLM
MLP + linear path in every class, then the fixed future.
"""
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import st  # noqa: E402

DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
DT = torch.float32
LN2 = math.log(2.0)
LOG2PIE = math.log(2 * math.pi * math.e)
WDIR = os.path.join(HERE, '..', 'weights')


class fp32:
    """Full-precision matmuls inside (the fixed net); TF32 may be on elsewhere (MLPs)."""

    def __enter__(self):
        self.prev = torch.backends.cuda.matmul.allow_tf32
        torch.backends.cuda.matmul.allow_tf32 = False

    def __exit__(self, *a):
        torch.backends.cuda.matmul.allow_tf32 = self.prev


# ----------------------------------------------------------------------------------------------------------------------
# Nets
# ----------------------------------------------------------------------------------------------------------------------

def toy_weights(k, seed, n=256, depth=4):
    """Planted future: layers [Q' Q^T, G_1, ..., G_depth] (no activation). Q, Q' (n x k) random orthonormal; G He-scaled
    Gaussian. Returns (Ws, Q) with Q the k known directions."""
    rng = np.random.default_rng([31337, k, seed, n, depth])
    Q = np.linalg.qr(rng.standard_normal((n, k)))[0]
    Qp = np.linalg.qr(rng.standard_normal((n, k)))[0]
    Ws = [Qp @ Q.T] + [rng.standard_normal((n, n)) * math.sqrt(1.0 / n) for _ in range(depth)]
    return Ws, Q


def family_weights(family, seed, toy_k=None):
    if family == 'arc':
        return [st.W_layer(seed, 256, k) for k in range(1, 33)], 'relu'
    if family == 'nd':
        W = np.load(os.path.join(WDIR, f'nd_{seed}.npy'))
        return [W[k] for k in range(W.shape[0])], 'relu'
    if family == 'toy':
        return toy_weights(toy_k, seed)[0], 'linear'
    raise ValueError(family)


class BNet:
    """S fixed nets (one per seed) applied to M = S * R models' batches with one batched matmul per layer."""

    def __init__(self, Ws_list, act):
        self.S = len(Ws_list)
        self.L = len(Ws_list[0])
        self.n = Ws_list[0][0].shape[1]
        self.act = act
        self.WT = [torch.tensor(np.stack([np.ascontiguousarray(Ws[k].T) for Ws in Ws_list]), dtype=DT, device=DEV)
                   for k in range(self.L)]
        self.W64 = Ws_list

    def run(self, h, l0, l1=None):
        """Apply layers l0+1..l1 (default L) to h (M, B, n), M = S * R (model m uses seed m // R)."""
        l1 = self.L if l1 is None else l1
        M, B, n = h.shape
        R = M // self.S
        h = h.reshape(self.S, R * B, n)
        with fp32():
            for k in range(l0, l1):
                h = torch.bmm(h, self.WT[k])
                if self.act == 'relu':
                    h = torch.relu(h)
        return h.reshape(M, B, n)


def sym_frames(X, floor=1e-8):
    """Mean, symmetric S^{1/2}, S^{-1/2} (float64 numpy) and descending PCA of samples X (P, n) float64."""
    m = X.mean(0)
    S = np.cov(X, rowvar=False)
    w, U = np.linalg.eigh(S)
    w = np.maximum(w, 0.0)
    keep = w > floor * max(w.max(), 1e-300)
    S12 = (U[:, keep] * np.sqrt(w[keep])) @ U[:, keep].T
    Sm12 = (U[:, keep] / np.sqrt(w[keep])) @ U[:, keep].T
    # decoder-side frame: full rank, so reconstructions may leave the data's affine span (dead units have zero
    # variance in the data, but preimages of reconstructed outputs need not): T = S^{1/2} + c P_null
    Pn = U[:, ~keep] @ U[:, ~keep].T
    c = float(np.sqrt(np.median(w[keep]))) if keep.any() else 1.0
    order = np.argsort(w)[::-1]
    return dict(m=m, S12=S12, Sm12=Sm12, T=S12 + c * Pn, Tinv=Sm12 + Pn / c, Pkeep=U[:, keep] @ U[:, keep].T,
                evals=w[order], U=U[:, order], keep=keep[order])


@torch.no_grad()
def pilot_stats(Ws, act, l, P=65536, seed=12345, state='gauss'):
    """float64 statistics for one net at layer l: frames of h_l, h_{l+1} (if l < L), a; V; h_star."""
    rng = np.random.default_rng([seed, l])
    L = len(Ws)
    n = Ws[0].shape[1]
    X = rng.standard_normal((P, n))
    H = {0: X}
    h = X
    for k in range(L):
        h = h @ Ws[k].T
        if act == 'relu':
            h = np.maximum(h, 0.0)
        H[k + 1] = h
    a = H[L]
    out = dict(V=float(a.var(0).sum()), Ea2=float((a * a).sum(1).mean()))
    out['h'] = sym_frames(H[l])
    out['a'] = sym_frames(a)
    if l < L:
        out['h1'] = sym_frames(H[l + 1])
    i_star = int(((a - a.mean(0)) ** 2).sum(1).argmin())
    out['h_star'] = H[l][i_star].copy()
    # gradient energy E tr(J S_l J^T) of the future at layer l (finite differences, exact on linear pieces)
    if l < L:
        PJ, dl = 2048, 1e-6
        h0 = H[l][:PJ]
        xi = rng.standard_normal((PJ, n)) @ out['h']['S12']
        h1 = h0 + dl * xi
        for k in range(l, L):
            h0 = h0 @ Ws[k].T
            h1 = h1 @ Ws[k].T
            if act == 'relu':
                h0, h1 = np.maximum(h0, 0.0), np.maximum(h1, 0.0)
        out['EJ'] = float((((h1 - h0) / dl) ** 2).sum(1).mean())
    else:
        out['EJ'] = out['V']
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Batched building blocks (leading axis M = models)
# ----------------------------------------------------------------------------------------------------------------------

def hat(t, anchors):
    """Piecewise-linear interpolation weights: t (M, G) -> (M, G, J) over uniformly spaced anchors."""
    J = len(anchors)
    a0, da = anchors[0], anchors[1] - anchors[0]
    pos = ((t - a0) / da).clamp(0.0, J - 1.0)
    i0 = torch.floor(pos).clamp(max=J - 2).long()
    f = pos - i0.to(pos.dtype)
    w = torch.zeros(*t.shape, J, device=t.device, dtype=t.dtype)
    w.scatter_(-1, i0.unsqueeze(-1), (1.0 - f).unsqueeze(-1))
    w.scatter_add_(-1, (i0 + 1).unsqueeze(-1), f.unsqueeze(-1))
    return w


class BLin(nn.Module):
    def __init__(self, M, din, dout, scale=1.0, zero=False):
        super().__init__()
        w = torch.randn(M, din, dout, device=DEV) * (scale / math.sqrt(din))
        if zero:
            w.zero_()
        self.w = nn.Parameter(w)
        self.b = nn.Parameter(torch.zeros(M, 1, dout, device=DEV))

    def forward(self, x):  # x (M, N, din)
        return torch.baddbmm(self.b, x, self.w)


class FiLMMLP(nn.Module):
    """x (M, G, Bg, din) -> (M, G, Bg, dout): Lin(din, W); depth x [h += gelu(FiLM_t(Lin(LN h)))]; Lin(LN h, dout).
    FiLM scale/shift per hidden unit, anchored in t (zero at init)."""

    def __init__(self, M, din, dout, W, depth, J, zero_out=True):
        super().__init__()
        self.inp = BLin(M, din, W)
        self.lins = nn.ModuleList([BLin(M, W, W) for _ in range(depth)])
        self.film = nn.Parameter(torch.zeros(M, depth, J, 2 * W, device=DEV))
        self.out = BLin(M, W, dout, zero=zero_out)
        self.W, self.depth = W, depth

    def forward(self, x, phi):
        M, G, Bg, din = x.shape
        W = self.W
        h = self.inp(x.reshape(M, G * Bg, din))
        fl = torch.einsum('mgj,mdjw->mdgw', phi, self.film)          # (M, depth, G, 2W)
        for i, lin in enumerate(self.lins):
            u = lin(F.layer_norm(h, (W,))).reshape(M, G, Bg, W)
            s, b = fl[:, i, :, None, :W], fl[:, i, :, None, W:]
            h = h + F.gelu(u * (1.0 + s) + b).reshape(M, G * Bg, W)
        return self.out(F.layer_norm(h, (W,))).reshape(M, G, Bg, -1)


class EncLocal(nn.Module):
    """One ReLU layer of width nh then affine, every weight anchored in t: for each lambda exactly in the class."""

    def __init__(self, M, n, nh, K, Je, A1=None, b1=None, A2=None, b2=None):
        super().__init__()

        def rep(x):
            return x.unsqueeze(1).repeat(1, Je, *([1] * (x.dim() - 1))).contiguous()
        self.A1 = nn.Parameter(rep(A1))   # (M, Je, n, nh)
        self.b1 = nn.Parameter(rep(b1))   # (M, Je, nh)
        self.A2 = nn.Parameter(rep(A2))   # (M, Je, nh, K)
        self.b2 = nn.Parameter(rep(b2))   # (M, Je, K)

    def forward(self, y, phi):  # y (M, G, Bg, n), phi (M, G, Je)
        M, G, Bg, n = y.shape
        A1 = torch.einsum('mgj,mjab->mgab', phi, self.A1)
        b1 = torch.einsum('mgj,mja->mga', phi, self.b1)
        u = torch.relu(torch.matmul(y, A1) + b1.unsqueeze(2))
        A2 = torch.einsum('mgj,mjab->mgab', phi, self.A2)
        b2 = torch.einsum('mgj,mja->mga', phi, self.b2)
        return torch.matmul(u, A2) + b2.unsqueeze(2)


class VRCode(nn.Module):
    def __init__(self, M, cls, n, K, W, depth, t_range, init, Jt=13, Je=7, Jp=8, lin_src='xa'):
        super().__init__()
        self.M, self.cls, self.n, self.K, self.Jp = M, cls, n, K, Jp
        self.lin_src = lin_src                       # unres/out linear path: 'xa' (output PCA) or 'y' (identity)
        t0, t1 = t_range
        self.anch_t = [t0 + (t1 - t0) * j / (Jt - 1) for j in range(Jt)]
        self.anch_e = [t0 + (t1 - t0) * j / (Je - 1) for j in range(Je)]
        if cls == 'local':
            self.enc = EncLocal(M, n, init['nh'], K, Je, init['A1'], init['b1'], init['A2'], init['b2'])
        else:
            din = n if cls == 'out' else 2 * n
            self.enc = FiLMMLP(M, din, K, W, depth, Jt)
        self.n_lin = min(n, K)
        self.gamma = nn.Parameter(init['gamma'])                                  # (M, Jt, K) log gains
        self.p_logit = nn.Parameter(torch.zeros(M, Jt, K, Jp, device=DEV))
        q = torch.linspace(-1.8, 1.8, Jp, device=DEV)
        self.p_mean = nn.Parameter(q.view(1, 1, 1, Jp).repeat(M, Jt, K, 1).contiguous())
        self.p_lsd = nn.Parameter(torch.full((M, Jt, K, Jp), math.log(0.5), device=DEV))
        self.dec = FiLMMLP(M, K, n, W, depth, Jt)
        with torch.no_grad():
            self.dec.out.b.copy_(init['dec_bias'].view(M, 1, n))
        self.Blin = nn.Parameter(init['B'])                                       # (M, K, n)

    def gains(self, phi):                     # phi (M, G, Jt) -> g (M, G, K)
        return torch.exp(torch.einsum('mgj,mjk->mgk', phi, self.gamma))

    def prior_params(self, phi):
        pl = torch.einsum('mgj,mjkc->mgkc', phi, self.p_logit)
        pm = torch.einsum('mgj,mjkc->mgkc', phi, self.p_mean)
        ps = torch.einsum('mgj,mjkc->mgkc', phi, self.p_lsd)
        return pl, pm, ps

    def encode(self, y, xa, t):
        """nu (M, G, Bg, K) for whitened state y and PCA-whitened output xa (both (M, G, Bg, n))."""
        if self.cls == 'local':
            return self.enc(y, hat(t, self.anch_e))
        phi = hat(t, self.anch_t)
        xin = xa if self.cls == 'out' else torch.cat([y, xa], -1)
        nu = self.enc(xin, phi)
        lin = (xa if self.lin_src == 'xa' else y)[..., :self.n_lin]
        if self.n_lin < self.K:
            lin = F.pad(lin, (0, self.K - self.n_lin))
        return nu + lin

    def log_prior(self, z, g, phi):
        """natural-log density per latent (M, G, Bg, K)."""
        pl, pm, ps = self.prior_params(phi)                      # (M, G, K, Jp)
        gg = g.unsqueeze(-1)                                     # (M, G, K, 1)
        var = (gg * torch.exp(ps)) ** 2 + 1.0
        mean = gg * pm
        lw = torch.log_softmax(pl, -1)
        zz = z.unsqueeze(-1)                                     # (M, G, Bg, K, 1)
        lp = (-0.5 * (zz - mean.unsqueeze(2)) ** 2 / var.unsqueeze(2) - 0.5 * torch.log(2 * math.pi * var.unsqueeze(2))
              + lw.unsqueeze(2))
        return torch.logsumexp(lp, -1)

    def forward(self, y, xa, t, gen=None):
        phi = hat(t, self.anch_t)
        nu = self.encode(y, xa, t)
        g = self.gains(phi)                                      # (M, G, K)
        eps = torch.randn(nu.shape, generator=gen, device=nu.device, dtype=nu.dtype)
        z = g.unsqueeze(2) * nu + eps
        lp = self.log_prior(z, g, phi)
        rate_k = (-0.5 * LOG2PIE - lp) / LN2                      # (M, G, Bg, K) bits per latent
        rate = rate_k.sum(-1)
        zt = z * (g / (1.0 + g * g)).unsqueeze(2)
        yhat = self.dec(zt, phi) + torch.matmul(zt, self.Blin.unsqueeze(1))
        return yhat, rate, dict(z=z, nu=nu, g=g, rate_k=rate_k)


# ----------------------------------------------------------------------------------------------------------------------
# Initialisation from pilot statistics
# ----------------------------------------------------------------------------------------------------------------------

def wf_gains(evals, V, t_anchors, K, floor=1e-2):
    """log gains (Jt, K) by reverse water-filling over evals at theta = lambda V / (2 ln 2)."""
    ev = np.zeros(K)
    kk = min(K, len(evals))
    ev[:kk] = np.maximum(evals[:kk], 0.0)
    out = []
    for t in t_anchors:
        th = (10.0 ** t) * V / (2 * LN2)
        g2 = np.maximum(ev / th - 1.0, floor)
        out.append(0.5 * np.log(g2))
    return np.array(out)


def identity_gains(EJ, V, n, t_anchors, K, kk, floor=1e-2):
    """log gains (Jt, K) of a scaled identity code of the whitened state: uniform SNR 2 ln2 D / (n lambda) - 1 on the
    first kk latents (D = EJ / V the future's gradient energy per unit whitened noise), floor elsewhere."""
    D = EJ / V
    out = []
    for t in t_anchors:
        g2 = np.full(K, floor)
        g2[:kk] = max(2 * LN2 * D / (n * 10.0 ** t) - 1.0, floor)
        out.append(0.5 * np.log(g2))
    return np.array(out)


def build_init(stats_list, Ws_list, l, cls, K, R, t_anchors, toy=False, seed=0, mode=None):
    """Per-model init tensors (M = S * R) from per-seed pilot statistics.
    mode: 'identity' (scaled identity of the whitened state, decoder its inverse; default for local),
          'h1' (local: the hidden layer computes h_{l+1}, linear code of h_{l+1}), 'outpca' (unres/out: the output's
          linear analog code; default for unres and out), 'random' (toy local)."""
    S = len(stats_list)
    n = Ws_list[0][0].shape[1]
    L = len(Ws_list[0])
    if mode is None:
        mode = ('random' if toy else 'identity') if cls == 'local' else 'outpca'
    rng = np.random.default_rng([4242, seed, l, K])
    per = []
    for s in range(S):
        stt, Ws = stats_list[s], Ws_list[s]
        fa = stt['a']
        gam = wf_gains(fa['evals'], stt['V'], t_anchors, K)
        fh = stt['h'] if l < L else fa
        d = dict(gamma=gam)
        B = np.zeros((K, n))
        bias = (stt['h_star'] - fh['m']) @ fh['Tinv'] if l < L else np.zeros(n)
        kk = min(n, K)
        if mode == 'identity':
            d['gamma'] = identity_gains(stt['EJ'], stt['V'], int(fh['keep'].sum()), t_anchors, K, kk)
            B[:kk, :kk] = fh['Pkeep'][:kk, :kk] if kk == n else np.eye(kk)
            bias = np.zeros(n)
            if cls == 'local':
                if l == 0:                          # x is not nonnegative: shift into the linear region of relu
                    c = 8.0
                    A1, b1 = np.eye(n), np.full(n, c)
                    A2 = np.zeros((n, K))
                    A2[:kk, :kk] = np.eye(kk)
                    b2 = -c * A2.sum(0)
                else:                               # h_l >= 0: relu(h_l) = h_l exactly
                    A1, b1 = fh['S12'], fh['m']
                    A2 = np.zeros((n, K))
                    A2[:, :kk] = fh['Sm12'][:, :kk]
                    b2 = -fh['m'] @ A2
                d.update(A1=A1, b1=b1, A2=A2, b2=b2)
        elif cls == 'local':
            if mode == 'random':
                A1 = rng.standard_normal((n, n)) * math.sqrt(2.0 / n)
                b1 = np.zeros(n)
                Hp = rng.standard_normal((4096, n)) @ A1
                Hp = np.maximum(Hp, 0.0)
                f1 = sym_frames(Hp)
            else:
                Wn = Ws[l]                                     # W_{l+1}
                A1 = fh['S12'] @ Wn.T
                b1 = fh['m'] @ Wn.T
                f1 = stt['h1']
            U, ev = f1['U'][:, :K], f1['evals'][:K]
            ok = ev > 1e-10 * max(ev.max(), 1e-300)
            A2 = np.zeros((n, K))
            A2[:, :U.shape[1]] = np.where(ok[None, :], U / np.sqrt(np.where(ok, ev, 1.0))[None, :], 0.0)
            b2 = -f1['m'] @ A2
            d.update(A1=A1, b1=b1, A2=A2, b2=b2)
            if mode == 'h1':
                Winv = np.linalg.inv(Ws[l])                    # h_l = W^{-1} h_{l+1}
                Bk = np.zeros((K, n))
                Bk[:U.shape[1]] = (np.sqrt(np.where(ok, ev, 0.0))[:, None] * U.T)   # z~ -> h_{l+1} - m_{l+1}
                B = Bk @ Winv.T @ fh['Tinv']
                bias = (f1['m'] @ Winv.T - fh['m']) @ fh['Tinv']
        else:
            Ua, eva = fa['U'][:, :K], fa['evals'][:K]
            Bk = np.zeros((K, n))
            Bk[:Ua.shape[1]] = np.sqrt(np.maximum(eva, 0.0))[:, None] * Ua.T      # z~ -> a - m_a
            if l == L:
                B = Bk @ fa['Tinv']
                bias = np.zeros(n)
            elif l == L - 1 and not toy:
                Winv = np.linalg.inv(Ws[L - 1])
                B = Bk @ Winv.T @ fh['Tinv']
                bias = (fa['m'] @ Winv.T - fh['m']) @ fh['Tinv']
        d.update(B=B, bias=bias)
        d['mode'] = mode
        per.append(d)
    t = lambda key: torch.tensor(np.stack([per[m // R][key] for m in range(S * R)]), dtype=DT, device=DEV)  # noqa
    init = dict(gamma=t('gamma'), B=t('B'), dec_bias=t('bias'), mode=mode)
    if cls == 'local':
        init.update(A1=t('A1'), b1=t('b1'), A2=t('A2'), b2=t('b2'), nh=n)
    return init


class Frames:
    """Per-model whitening tensors (M = S * R)."""

    def __init__(self, stats_list, l, L, R):
        def T(f):
            return torch.tensor(np.stack([f(stats_list[m // R]) for m in range(len(stats_list) * R)]), dtype=DT,
                                device=DEV)
        fh = (lambda s: s['h']) if l < L else (lambda s: s['a'])
        self.m = T(lambda s: fh(s)['m'])[:, None, :]
        self.S12 = T(lambda s: fh(s)['T'])           # decoder side: full rank (see sym_frames)
        self.Sm12 = T(lambda s: fh(s)['Sm12'])       # encoder side: whitening of the data's span
        self.ma = T(lambda s: s['a']['m'])[:, None, :]
        self.Pa = T(lambda s: np.where(s['a']['keep'][None, :], s['a']['U'] / np.sqrt(np.where(s['a']['keep'],
                                                                                              s['a']['evals'], 1.0))[None, :], 0.0))
        self.V = T(lambda s: np.array(s['V']))

    def white(self, h):
        return torch.bmm(h - self.m, self.Sm12)

    def unwhite(self, y):
        return self.m + torch.bmm(y, self.S12)

    def pca_a(self, a):
        return torch.bmm(a - self.ma, self.Pa)


# ----------------------------------------------------------------------------------------------------------------------
# Training
# ----------------------------------------------------------------------------------------------------------------------

def out_clip(bnet, ah):
    """Output-space decoder: ReLU nets have a >= 0, so clipping the reconstruction to R_+^n never hurts (the free and
    the nonnegative output problems have the same optimum) and gives the output cell the same final ReLU as layer L-1."""
    return torch.relu(ah) if bnet.act == 'relu' else ah


def sample_batch(bnet, l, M, B, gen, toy=False):
    with torch.no_grad():
        x = torch.randn(M, B, bnet.n, generator=gen, device=DEV, dtype=DT)
        h = x if l == 0 else bnet.run(x, 0, l)
        a = bnet.run(h, l) if l < bnet.L else h
    return h, a


def stratified_t(M, G, t_range, gen):
    t0, t1 = t_range
    u = torch.rand(M, G, generator=gen, device=DEV, dtype=DT)
    return t0 + (t1 - t0) * (torch.arange(G, device=DEV, dtype=DT)[None, :] + u) / G


def anchored_params(model):
    """(param, anchor axis, anchor positions) for every lambda-anchored parameter."""
    out = [(model.gamma, 1, model.anch_t), (model.p_logit, 1, model.anch_t), (model.p_mean, 1, model.anch_t),
           (model.p_lsd, 1, model.anch_t), (model.dec.film, 2, model.anch_t)]
    if model.cls == 'local':
        out += [(model.enc.A1, 1, model.anch_e), (model.enc.b1, 1, model.anch_e), (model.enc.A2, 1, model.anch_e),
                (model.enc.b2, 1, model.anch_e)]
    else:
        out.append((model.enc.film, 2, model.anch_t))
    return out


def n_in_use(anchors, t_hi):
    """anchors needed to interpolate every t <= t_hi: j = 0 and every j with anchors[j-1] < t_hi."""
    return 1 + sum(1 for j in range(1, len(anchors)) if anchors[j - 1] < t_hi - 1e-9)


@torch.no_grad()
def continue_anchors(model, opt, t_hi, state):
    """Warm-start newly used anchors from the next-lower one (parameters and Adam moments): continuation in lambda."""
    for (p, ax, anc) in anchored_params(model):
        key = id(p)
        nu = n_in_use(anc, t_hi)
        prev = state.get(key, nu)
        for j in range(prev, nu):
            p.narrow(ax, j, 1).copy_(p.narrow(ax, j - 1, 1))
            st_ = opt.state.get(p, {})
            for mk in ('exp_avg', 'exp_avg_sq'):
                if mk in st_:
                    st_[mk].narrow(ax, j, 1).copy_(st_[mk].narrow(ax, j - 1, 1))
        state[key] = max(prev, nu)


def train(model, bnet, fr, l, steps, B, G, t_range, seed, lr=1e-3, lr_lin=1e-4, lr_enc=3e-4, fixed_t=None,
          log_every=500, nbins=24, clip=10.0, tf32=True, logf=None, anneal=0.4):
    """anneal: fraction of the steps over which the upper end of the lambda range rises from t_min + one anchor
    spacing to t_max (Kelvin 03:20Z: start at a high budget, raise the bit price, shed directions); newly used anchors
    are warm-started from the next-lower lambda. 0 = the full range from the start."""
    M = model.M
    L = bnet.L
    Bg = B // G
    torch.backends.cuda.matmul.allow_tf32 = tf32
    lin_names = {'Blin', 'enc.out.w', 'enc.out.b', 'dec.out.w', 'dec.out.b'}
    enc_names = {'enc.A1', 'enc.b1', 'enc.A2', 'enc.b2'}
    named = list(model.named_parameters())
    groups = [dict(params=[p for nm, p in named if nm not in lin_names and nm not in enc_names], lr=lr),
              dict(params=[p for nm, p in named if nm in lin_names], lr=lr_lin),
              dict(params=[p for nm, p in named if nm in enc_names], lr=lr_enc)]
    groups = [g_ for g_ in groups if g_['params']]
    base_lr = [g_['lr'] for g_ in groups]
    opt = torch.optim.Adam(groups)
    warm = max(1, steps // 50)

    def sched(s):
        return min(1.0, (s + 1) / warm) * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, steps) / steps)))
    sp = model.anch_t[1] - model.anch_t[0]
    anneal_steps = int(anneal * steps) if (anneal and fixed_t is None) else 0
    astate = {}
    gen = torch.Generator(device=DEV).manual_seed(seed)
    edges = torch.linspace(t_range[0], t_range[1], nbins + 1, device=DEV)
    Lbar = torch.full((M, nbins), float('nan'), device=DEV)
    log = []
    t0 = time.time()
    for step in range(steps):
        for gi, pg in enumerate(opt.param_groups):
            pg['lr'] = base_lr[gi] * sched(step)
        h, a = sample_batch(bnet, l, M, B, gen)
        y = fr.white(h)
        xa = fr.pca_a(a)
        if fixed_t is None:
            if anneal_steps:
                t_hi = min(t_range[1], t_range[0] + sp + (t_range[1] - t_range[0] - sp) * step / anneal_steps)
                continue_anchors(model, opt, t_hi, astate)
                t = stratified_t(M, G, (t_range[0], t_hi), gen)
            else:
                t = stratified_t(M, G, t_range, gen)
        else:
            t = fixed_t.view(M, 1).expand(M, G).contiguous()
        yhat, rate, _ = model(y.view(M, G, Bg, -1), xa.view(M, G, Bg, -1), t, gen)
        hh = fr.unwhite(yhat.reshape(M, B, -1))
        ah = bnet.run(hh, l) if l < L else out_clip(bnet, hh)
        D = ((ah - a) ** 2).sum(-1) / fr.V.view(M, 1)
        Rg = rate.mean(-1)
        Dg = D.view(M, G, Bg).mean(-1)
        Lg = Rg + Dg / torch.pow(10.0, t)
        bi = torch.bucketize(t, edges[1:-1])
        with torch.no_grad():
            cur = Lbar.gather(1, bi)
            fresh = torch.isnan(cur)
            norm = torch.where(fresh, Lg.detach(), cur).clamp(min=1e-3)
        loss = (Lg / norm).sum() / G
        opt.zero_grad(set_to_none=True)
        loss.backward()
        with torch.no_grad():
            sq = torch.zeros(M, device=DEV)
            for p in model.parameters():
                if p.grad is not None:
                    sq += p.grad.pow(2).flatten(1).sum(1)
            fac = (clip / (sq.sqrt() + 1e-12)).clamp(max=1.0)
            for p in model.parameters():
                if p.grad is not None:
                    p.grad.mul_(fac.view(M, *([1] * (p.grad.dim() - 1))))
        opt.step()
        with torch.no_grad():
            Ld = Lg.detach()
            sums = torch.zeros(M, nbins, device=DEV).scatter_add_(1, bi, Ld)
            cnts = torch.zeros(M, nbins, device=DEV).scatter_add_(1, bi, torch.ones_like(Ld))
            mean_b = sums / cnts.clamp(min=1)
            new = torch.where(torch.isnan(Lbar), mean_b, 0.95 * Lbar + 0.05 * mean_b)
            Lbar = torch.where(cnts > 0, new, Lbar)
        if step % log_every == 0 or step == steps - 1:
            with torch.no_grad():
                rec = dict(step=step, sec=round(time.time() - t0, 1),
                           R=[round(float(v), 3) for v in Rg.mean(0)[::max(1, G // 8)]],
                           D=[float('%.4g' % float(v)) for v in Dg.mean(0)[::max(1, G // 8)]],
                           t=[round(float(v), 2) for v in t.mean(0)[::max(1, G // 8)]])
            log.append(rec)
            if logf is not None:
                print(f'step {step} {rec["sec"]}s R {rec["R"]} D {rec["D"]}', file=logf, flush=True)
    return log


# ----------------------------------------------------------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------------------------------------------------------

def mix_logpdf(z, mu, var, logw):
    """z (P, K); mu, var, logw (K, J) -> natural log density (P, K)."""
    zz = z.unsqueeze(-1)
    lp = -0.5 * (zz - mu) ** 2 / var - 0.5 * torch.log(2 * math.pi * var) + logw
    return torch.logsumexp(lp, -1)


def fit_mixture(z, J=8, iters=150, var_floor=1.0):
    """EM fit of an independent 1-D Gaussian mixture per column of z (P, K), variances >= var_floor (the same family as
    the trained prior: components N(g m, g^2 s^2 + 1)). Returns (mu, var, logw), each (K, J)."""
    P, K = z.shape
    qs = torch.linspace(0.5 / J, 1 - 0.5 / J, J, device=z.device)
    mu = torch.quantile(z.T.contiguous(), qs, dim=1).T.contiguous()                    # (K, J)
    sd = z.std(0).clamp(min=1e-6)
    var = ((2.0 * sd / J) ** 2).clamp(min=var_floor).view(K, 1).repeat(1, J)
    logw = torch.full((K, J), -math.log(J), device=z.device)
    for _ in range(iters):
        zz = z.unsqueeze(-1)
        lp = -0.5 * (zz - mu) ** 2 / var - 0.5 * torch.log(2 * math.pi * var) + logw     # (P, K, J)
        r = torch.softmax(lp, -1)
        nk = r.sum(0) + 1e-9                                                              # (K, J)
        mu = (r * zz).sum(0) / nk
        var = ((r * (zz - mu) ** 2).sum(0) / nk).clamp(min=var_floor)
        logw = torch.log(nk / P)
    return mu, var, logw


def mix_cdf(z, mu, var, logw):
    zz = z.unsqueeze(-1)
    return (torch.exp(logw) * 0.5 * (1 + torch.erf((zz - mu) / torch.sqrt(2 * var)))).sum(-1)


def heldout_x(net_seed, P, n):
    """The held-out inputs of one net: the same for every process, variant and restart (paired comparisons)."""
    gen = torch.Generator(device=DEV).manual_seed(88_000 + int(net_seed))
    return torch.randn(P, n, generator=gen, device=DEV, dtype=DT)


@torch.no_grad()
def evaluate(model, bnet, fr, l, t_grid, P, seeds, chunk=4096, refit_every=1, tc=True):
    """Curve per model on P held-out inputs (fixed per net seed, see heldout_x). Returns list (per model) of lists
    (per t) of dicts."""
    M, K = model.M, model.K
    L = bnet.L
    S = bnet.S
    R = M // S
    seed = int(seeds[0])
    torch.backends.cuda.matmul.allow_tf32 = False
    x = torch.stack([heldout_x(s, P, bnet.n) for s in seeds]).unsqueeze(1).expand(S, R, P, bnet.n).reshape(M, P, bnet.n)
    hs, as_ = [], []
    for c0 in range(0, P, chunk):
        xc = x[:, c0:c0 + chunk].contiguous()
        h = xc if l == 0 else bnet.run(xc, 0, l)
        hs.append(h)
        as_.append(bnet.run(h, l) if l < L else h)
    h = torch.cat(hs, 1)
    a = torch.cat(as_, 1)
    V = fr.V.view(M, 1)
    out = [[] for _ in range(M)]
    for ti, tv in enumerate(t_grid):
        ngen = torch.Generator(device=DEV).manual_seed(seed + 1000 + ti)
        rates, Ds, zs = [], [], []
        rk_sum = torch.zeros(M, K, device=DEV, dtype=torch.float64)
        dsum = torch.zeros(M, bnet.n, device=DEV, dtype=torch.float64)
        dsq = torch.zeros(M, bnet.n, device=DEV, dtype=torch.float64)
        for c0 in range(0, P, chunk):
            hc, ac = h[:, c0:c0 + chunk], a[:, c0:c0 + chunk]
            Bc = hc.shape[1]
            y = fr.white(hc).view(M, 1, Bc, -1)
            xa = fr.pca_a(ac).view(M, 1, Bc, -1)
            t = torch.full((M, 1), float(tv), device=DEV)
            yhat, rate, ex = model(y, xa, t, ngen)
            hh = fr.unwhite(yhat.view(M, Bc, -1))
            ah = bnet.run(hh, l) if l < L else out_clip(bnet, hh)
            d = ah - ac
            Ds.append((d * d).sum(-1) / V)
            dsum += d.double().sum(1)
            dsq += (d.double() ** 2).sum(1)
            rates.append(rate.view(M, Bc))
            zs.append(ex['z'].view(M, Bc, K))
            rk_sum += ex['rate_k'].view(M, Bc, K).double().sum(1)
        D = torch.cat(Ds, 1).double()
        Rt = torch.cat(rates, 1).double()
        Z = torch.cat(zs, 1)
        RK = rk_sum / P                                                                   # (M, K)
        md = dsum / P
        mean_err = (md * md).sum(-1) / V.view(M).double()
        floor = ((dsq / P - md * md) * P / (P - 1)).sum(-1) / P / V.view(M).double()
        g = model.gains(hat(torch.full((M, 1), float(tv), device=DEV), model.anch_t)).view(M, K)
        for m in range(M):
            rec = dict(t=float(tv), rate=float(Rt[m].mean()), rate_se=float(Rt[m].std() / math.sqrt(P)),
                       nmse=float(D[m].mean()), nmse_se=float(D[m].std() / math.sqrt(P)),
                       mean_err=float(mean_err[m]), mean_floor=float(floor[m]),
                       n_active=int((RK[m] > 0.05).sum()), lat_rates=[round(float(v), 4) for v in
                                                                      torch.sort(RK[m], descending=True)[0][:32]],
                       gain_max=float(g[m].max()))
            if ti % refit_every == 0 or ti == len(t_grid) - 1:
                act = RK[m] > 0.01
                zm = Z[m]
                h2 = P // 2
                rr = []
                tcs = []
                for (A_, B_) in ((zm[:h2], zm[h2:]), (zm[h2:], zm[:h2])):
                    mu, var, lw = fit_mixture(A_)
                    lpB = mix_logpdf(B_, mu, var, lw)                                      # (P/2, K)
                    rr.append(float(((-0.5 * LOG2PIE - lpB) / LN2).sum(-1).mean()))
                    if tc and int(act.sum()) >= 2:
                        u = mix_cdf(B_[:, act], mu[act], var[act], lw[act]).clamp(1e-6, 1 - 1e-6)
                        gq = math.sqrt(2.0) * torch.erfinv(2 * u - 1)
                        C = torch.corrcoef(gq.T.double())
                        sign, logdet = torch.linalg.slogdet(C)
                        ka = int(act.sum())
                        bias = ka * (ka - 1) / (4.0 * B_.shape[0])                       # null E[-1/2 ln det C]
                        tcs.append(float((-0.5 * logdet - bias) / LN2))
                # trained-prior rate on the same halves (for a paired ratio)
                rec['rate_refit'] = float(np.mean(rr))
                if tcs:
                    rec['tc_copula'] = float(np.mean(tcs))
            out[m].append(rec)
    torch.backends.cuda.matmul.allow_tf32 = True
    return out


def curve_R_at(curve, eps, key='nmse', rkey='rate'):
    """Rate at which the monotone lower envelope of (rate, nMSE) reaches eps (log-linear interpolation); None if not
    reached within the curve."""
    pts = sorted([(c[rkey], c[key]) for c in curve if c[key] > 0])
    env = []
    best = float('inf')
    for r, d in pts:
        if d < best:
            env.append((r, d))
            best = d
    for i, (r, d) in enumerate(env):
        if d <= eps:
            if i == 0:
                return r
            r0, d0 = env[i - 1]
            f = (math.log(d0) - math.log(eps)) / (math.log(d0) - math.log(d))
            return r0 + f * (r - r0)
    return None
