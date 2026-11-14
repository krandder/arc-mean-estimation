"""Bit-accounting lane library (torch, CPU). Learned per-layer bottlenecks for fixed random ReLU nets.

Nets (reused, not rewritten):
  ARC 256 x 32: W_l = st.W_layer(seed, 256, l), l = 1..32 (the stationary lane's stream; input-bits lane's ib.Net and the
    relevance lane's rel.input_weights), input x ~ N(0, I_n), sigma = 0, output a = h_L = relu(W_L h_{L-1}).
  narrow-deep 8 x 256: nd.make_weights('plain', seed, 8, 256) (the narrow-deep lane's generator; relevance lane's
    rel.narrow_deep_weights), same model.
Layer l = 0..L-1: h_0 = x, h_l = relu(W_l h_{l-1}); the future g_l = layers l+1..L, a = g_l(h_l).

Bottleneck at layer l: code = Q(E(h_l)); h_hat = D(code); output a_hat = g_l(h_hat); loss |a_hat - a|^2 / V,
V = tr Var(a) (nMSE, the earlier lanes' convention).
  Binary (nested): K sign bits with a straight-through tanh gradient; a code of b bits keeps bits 1..b and sets the rest
    to 0 ("unknown"); b is drawn per example during training, so one model gives the whole rate curve (successive
    refinement). Rate = b bits exactly (at most b bits of information).
  Gaussian channel (nested): K channels, each normalised to unit power (batch statistics), additive noise
    N(0, 1/SNR_i); capacities C_i = max(0, (1/2) log2(gamma_i / theta)) by water-filling of learned importances gamma_i
    with sum_i C_i = C (exact, differentiable projection); C drawn per example. Reported rate C = (1/2) sum_i
    log2(1 + SNR_i), an upper bound on I(h_l; channel output).
Encoders: 'local' (sees h_l only) or 'ahead' (sees h_l and the exact output a = g_l(h_l), i.e. an encoder that contains
the future net; it realises the layer-independent optimum of FORMAL.md section 1).
"""
import math
import sys

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import st  # noqa: E402

DT = torch.float32


# ----------------------------------------------------------------------------------------------------------------------
# Fixed nets
# ----------------------------------------------------------------------------------------------------------------------

def arc_weights(seed, n=256, L=32):
    return [st.W_layer(seed, n, l) for l in range(1, L + 1)]


def nd_weights(seed, n=8, L=256):
    sys.path.insert(0, '/home/agent/workspaces/mats/work/narrow-deep/lib')
    import nd  # noqa
    W, _ = nd.make_weights('plain', seed, n, L)
    return [w.numpy().copy() for w in W]


class FixedNet:
    """Noiseless He-ReLU stack, weights frozen. Ws = [W_1..W_L] (numpy float64), stored as float32 and float64."""

    def __init__(self, Ws, name=''):
        self.L = len(Ws)
        self.n = Ws[0].shape[1]
        self.name = name
        self.WT = [torch.tensor(np.ascontiguousarray(W.T), dtype=DT) for W in Ws]
        self.WT64 = [np.ascontiguousarray(W.T) for W in Ws]

    def run(self, h, l0, l1=None):
        """Apply layers l0+1..l1 (default L) to the state h at layer l0 (torch, differentiable)."""
        l1 = self.L if l1 is None else l1
        for k in range(l0, l1):
            h = torch.relu(h @ self.WT[k])
        return h

    def run64(self, h, l0, l1=None):
        l1 = self.L if l1 is None else l1
        for k in range(l0, l1):
            h = np.maximum(h @ self.WT64[k], 0.0)
        return h

    @torch.no_grad()
    def sample(self, P, l, gen, need_out=True):
        """P inputs x ~ N(0, I_n) (torch generator gen) -> (h_l, a)."""
        x = torch.randn(P, self.n, generator=gen, dtype=DT)
        h = self.run(x, 0, l)
        a = self.run(h, l) if need_out else None
        return h, a


def make_net(kind, seed):
    if kind == 'arc':
        return FixedNet(arc_weights(seed), f'arc_s{seed}')
    if kind == 'nd':
        return FixedNet(nd_weights(seed), f'nd_s{seed}')
    raise ValueError(kind)


# ----------------------------------------------------------------------------------------------------------------------
# Networks
# ----------------------------------------------------------------------------------------------------------------------

class MLP(nn.Module):
    def __init__(self, d_in, d_out, width, depth, act=nn.GELU):
        super().__init__()
        layers = []
        d = d_in
        for _ in range(depth):
            layers += [nn.Linear(d, width), act()]
            d = width
        layers.append(nn.Linear(d, d_out))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def waterfill(eta, C):
    """Capacities C_i = max(0, (eta_i - log theta) / (2 ln 2)) with sum_i C_i = C (per row of C).
    eta (K,) log-importances, C (B,) total capacities in bits. Differentiable in eta (the active set is fixed by the
    forward pass; inside it the projection is exact). Returns (B, K)."""
    K = eta.shape[0]
    srt, idx = torch.sort(eta, descending=True)
    cs = torch.cumsum(srt, 0)                                   # (K,)
    k = torch.arange(1, K + 1, dtype=eta.dtype)
    two_ln2 = 2.0 * math.log(2.0)
    # candidate log theta for each active-set size k: (cs_k - 2 ln2 C) / k  -> (B, K)
    lt = (cs[None, :] - two_ln2 * C[:, None]) / k[None, :]
    # valid if srt_k > lt_k (the k-th channel is active) ; the largest valid k is the solution
    valid = srt[None, :] > lt
    kk = (valid * k[None, :]).max(1).values.long()              # (B,) active-set size
    lt_sel = lt.gather(1, (kk - 1).clamp(min=0)[:, None])        # (B, 1)
    Cs = torch.clamp((srt[None, :] - lt_sel) / two_ln2, min=0.0)  # (B, K) in sorted order
    out = torch.empty_like(Cs)
    out[:, idx] = Cs
    return out


class Bottleneck(nn.Module):
    """Encoder -> quantiser/channel -> decoder -> state at layer l. kind in {'bin', 'gauss'}; enc_mode in
    {'local', 'ahead'}."""

    def __init__(self, n, K, kind, enc_mode, width, depth, h_mean, h_std, a_mean, a_std, h_star=None):
        super().__init__()
        self.n, self.K, self.kind, self.enc_mode = n, K, kind, enc_mode
        d_in = n if enc_mode == 'local' else 2 * n
        self.enc = MLP(d_in, K, width, depth)
        d_code = K if kind == 'bin' else 2 * K
        self.dec = MLP(d_code, n, width, depth)
        nn.init.zeros_(self.dec.net[-1].weight)
        nn.init.zeros_(self.dec.net[-1].bias)
        if h_star is not None:   # start every reconstruction at the sample state whose output is nearest E a
            with torch.no_grad():
                self.dec.net[-1].bias.copy_((torch.as_tensor(h_star, dtype=DT) - torch.as_tensor(h_mean, dtype=DT))
                                            / torch.as_tensor(h_std, dtype=DT))
        self.register_buffer('h_mean', torch.as_tensor(h_mean, dtype=DT))
        self.register_buffer('h_std', torch.as_tensor(h_std, dtype=DT))
        self.register_buffer('a_mean', torch.as_tensor(a_mean, dtype=DT))
        self.register_buffer('a_std', torch.as_tensor(a_std, dtype=DT))
        self.bn = nn.BatchNorm1d(K, affine=False, momentum=0.01)
        if kind == 'gauss':
            self.eta = nn.Parameter(torch.zeros(K))

    def encode(self, h, a=None):
        x = (h - self.h_mean) / self.h_std
        if self.enc_mode == 'ahead':
            x = torch.cat([x, (a - self.a_mean) / self.a_std], 1)
        return self.bn(self.enc(x))

    def code(self, z, rate, gen=None):
        """rate: (B,) bits (binary: integer b; gauss: total capacity C). Returns the decoder input and the realised rate."""
        B = z.shape[0]
        if self.kind == 'bin':
            t = torch.tanh(z)
            c = t + (torch.sign(z) - t).detach()
            j = torch.arange(self.K)[None, :]
            mask = (j < rate[:, None]).to(DT)
            return c * mask, rate.to(DT)
        Ci = waterfill(self.eta, rate.to(DT))                    # (B, K)
        snr = torch.pow(2.0, 2.0 * Ci) - 1.0
        noise = torch.randn(z.shape, generator=gen, dtype=DT) if gen is not None else torch.randn_like(z)
        r = snr / (1.0 + snr)                                    # MMSE gain (reliability), 0 for closed channels
        y = z + noise / torch.sqrt(snr.clamp(min=1e-12))
        u_hat = r * y                                            # = 0 where snr = 0
        Creal = 0.5 * torch.log2(1.0 + snr).sum(1)
        return torch.cat([u_hat, r], 1), Creal

    def decode(self, cin):
        return self.h_mean + self.h_std * self.dec(cin)

    def forward(self, h, a, rate, gen=None):
        z = self.encode(h, a)
        cin, Creal = self.code(z, rate, gen)
        return self.decode(cin), Creal


# ----------------------------------------------------------------------------------------------------------------------
# Rate sampling and loss balancing
# ----------------------------------------------------------------------------------------------------------------------

def sample_rates(B, kind, rmax, gen):
    u = torch.rand(B, generator=gen, dtype=torch.float64)
    if kind == 'bin':
        b = torch.floor(torch.exp(u * math.log(rmax + 1.0))).long()
        return b.clamp(1, rmax)
    return torch.exp(u * math.log(rmax)).to(DT)              # C in [1, rmax]


class RateBalancer:
    """Running nMSE per log-rate bin; the loss weight of an example is 1 / (running nMSE of its bin), so every rate
    contributes about equally in relative terms (the sum of log-distortions)."""

    def __init__(self, rmax, nbins=24, mom=0.02, floor=1e-5):
        self.edges = np.exp(np.linspace(0, math.log(rmax + 1.0), nbins + 1))
        self.ema = np.ones(nbins)
        self.mom, self.floor = mom, floor

    def bins(self, rate):
        return np.clip(np.searchsorted(self.edges, rate.detach().double().numpy(), side='right') - 1, 0,
                       len(self.ema) - 1)

    def weights(self, rate):
        bi = self.bins(rate)
        return torch.tensor(1.0 / np.maximum(self.ema[bi], self.floor), dtype=DT), bi

    def update(self, bi, err):
        e = err.detach().double().numpy()
        for b in np.unique(bi):
            self.ema[b] = (1 - self.mom) * self.ema[b] + self.mom * e[bi == b].mean()


# ----------------------------------------------------------------------------------------------------------------------
# Statistics of the layer state and output
# ----------------------------------------------------------------------------------------------------------------------

@torch.no_grad()
def layer_stats(net, l, P, seed):
    gen = torch.Generator().manual_seed(seed)
    hs, as_ = [], []
    for c0 in range(0, P, 8192):
        h, a = net.sample(min(8192, P - c0), l, gen)
        hs.append(h)
        as_.append(a)
    h = torch.cat(hs)
    a = torch.cat(as_)
    V = float(a.double().var(0).sum())
    hm, hsd = h.mean(0), h.std(0).clamp(min=1e-6)
    am, asd = a.mean(0), a.std(0).clamp(min=1e-6)
    i_star = int(((a - am) ** 2).sum(1).argmin())
    return dict(V=V, h_mean=hm, h_std=hsd, a_mean=am, a_std=asd, h_star=h[i_star].clone())


# ----------------------------------------------------------------------------------------------------------------------
# Evaluation
# ----------------------------------------------------------------------------------------------------------------------

def bin_grid(rmax):
    g = list(range(1, 17)) + list(range(18, 33, 2)) + list(range(36, 65, 4)) + list(range(72, 129, 8)) + \
        list(range(144, 257, 16))
    return [b for b in g if b <= rmax]


def gauss_grid(rmax):
    g = [1, 1.5, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256]
    return [c for c in g if c <= rmax]


@torch.no_grad()
def evaluate(model, net, l, V, rates, P, seed, chunk=4096):
    """nMSE and mean error at each rate on P held-out inputs (fixed seed). Returns list of dicts."""
    model.eval()
    gen = torch.Generator().manual_seed(seed)
    hs, as_ = [], []
    for c0 in range(0, P, chunk):
        h, a = net.sample(min(chunk, P - c0), l, gen)
        hs.append(h)
        as_.append(a)
    h = torch.cat(hs)
    a = torch.cat(as_)
    z = torch.cat([model.encode(h[c0:c0 + chunk], a[c0:c0 + chunk]) for c0 in range(0, P, chunk)])
    power = z.double().pow(2).mean(0)          # per-channel power on the held-out inputs (constraint: about 1)
    out = []
    ngen = torch.Generator().manual_seed(seed + 1)
    for r in rates:
        errs, diffs, Cr = [], [], []
        for c0 in range(0, P, chunk):
            zz = z[c0:c0 + chunk]
            rr = torch.full((zz.shape[0],), r, dtype=torch.long if model.kind == 'bin' else DT)
            cin, Creal = model.code(zz, rr, ngen)
            ah = net.run(model.decode(cin), l)
            d = (ah - a[c0:c0 + chunk]).double()
            errs.append((d * d).sum(1))
            diffs.append(d)
            Cr.append(Creal.double())
        e = torch.cat(errs) / V
        dd = torch.cat(diffs)
        md = dd.mean(0)
        mean_err = float((md * md).sum()) / V
        # noise floor of the squared mean difference: tr Cov(d) / P / V
        floor = float(dd.var(0).sum()) / P / V
        out.append(dict(rate=float(r), C=float(torch.cat(Cr).mean()), nmse=float(e.mean()),
                        se=float(e.std() / math.sqrt(P)), mean_err=mean_err, mean_floor=floor,
                        power_max=float(power.max()), power_mean=float(power.mean())))
    model.train()
    return out


def crossing(curve, eps, key='nmse'):
    """Smallest rate on the grid with nMSE <= eps (grid upper bound) and the log-linear interpolated crossing."""
    rs = [c['rate'] for c in curve]
    ys = [c[key] for c in curve]
    for i, (r, y) in enumerate(zip(rs, ys)):
        if y <= eps:
            if i == 0:
                return r, r
            r0, y0 = rs[i - 1], ys[i - 1]
            f = (math.log(y0) - math.log(eps)) / (math.log(y0) - math.log(max(y, 1e-30)))
            return r, r0 + f * (r - r0)
    return None, None


# ----------------------------------------------------------------------------------------------------------------------
# v2: bottleneck initialised at the linear transform code (lib/lincodes.py), with a residual MLP on top
# ----------------------------------------------------------------------------------------------------------------------

def fsq_table(lam, K, Bmax=256, bmax=12):
    """Integer bit allocations q(B) for B = 0..Bmax (greedy over importances lam), as a (Bmax + 1, K) int tensor."""
    import lincodes as lc
    lam = np.asarray(lam, float)
    tab = np.zeros((Bmax + 1, K), int)
    bits = np.zeros(K, int)
    gain = lam * (1.0 - lc.lm_dist(1))
    for B in range(1, Bmax + 1):
        k = int(np.argmax(gain))
        if gain[k] > 0:
            bits[k] += 1
            gain[k] = -1.0 if bits[k] >= bmax else lam[k] * (lc.lm_dist(bits[k]) - lc.lm_dist(bits[k] + 1))
        tab[B] = bits
    return torch.tensor(tab)


def lm_tensors(bmax=12):
    """Lloyd-Max levels/thresholds of N(0, 1) for 1..bmax bits, padded: levels (bmax+1, 2^bmax), thresholds."""
    import lincodes as lc
    Lmax = 2 ** bmax
    lev = torch.zeros(bmax + 1, Lmax)
    thr = torch.full((bmax + 1, Lmax - 1), float('inf'))
    for b in range(1, bmax + 1):
        lv, th, _ = lc.lloyd_max(b)
        lev[b, :len(lv)] = torch.tensor(lv, dtype=DT)
        thr[b, :len(th)] = torch.tensor(th, dtype=DT)
    return lev, thr


class Bottleneck2(nn.Module):
    """Local bottleneck at layer l initialised at the linear code of basis Q (n x n, columns by importance lam).
    kind: 'gauss' (water-filled channel), 'bin' (nested sign bits in basis order), 'fsq' (Lloyd-Max scalar quantisers
    with greedy integer bits by lam, nested in the total B). Encoder z = x Q_K + MLP(x), x the whitened state;
    decoder z_hat = c B + MLP(c), h_hat = m + z_hat S12. K channels (K <= n uses the first K basis vectors; extra
    channels start at zero and are left to the MLP)."""

    def __init__(self, n, K, kind, width, depth, m, S12, Sm12, Q, lam):
        super().__init__()
        self.n, self.K, self.kind = n, K, kind
        self.register_buffer('m', torch.as_tensor(m, dtype=DT))
        self.register_buffer('S12', torch.as_tensor(S12, dtype=DT))
        self.register_buffer('Sm12', torch.as_tensor(Sm12, dtype=DT))
        Qt = torch.zeros(n, K, dtype=DT)
        kk = min(n, K)
        Qt[:, :kk] = torch.as_tensor(Q[:, :kk], dtype=DT)
        lam_t = torch.zeros(K, dtype=DT)
        lam_t[:kk] = torch.as_tensor(np.maximum(lam[:kk], 0.0), dtype=DT)
        self.register_buffer('lam', lam_t)
        self.enc_lin = nn.Parameter(Qt.clone())
        self.enc_mlp = MLP(n, K, width, depth)
        nn.init.zeros_(self.enc_mlp.net[-1].weight)
        nn.init.zeros_(self.enc_mlp.net[-1].bias)
        d_code = K if kind == 'bin' else 2 * K
        Bm = torch.zeros(d_code, n, dtype=DT)
        Bm[:K] = Qt.T * (math.sqrt(2.0 / math.pi) if kind == 'bin' else 1.0)
        self.dec_lin = nn.Parameter(Bm)
        self.dec_mlp = MLP(d_code, n, width, depth)
        nn.init.zeros_(self.dec_mlp.net[-1].weight)
        nn.init.zeros_(self.dec_mlp.net[-1].bias)
        self.bn = nn.BatchNorm1d(K, affine=False, momentum=0.01)
        if kind == 'gauss':
            lmax = float(lam_t.max())
            self.eta = nn.Parameter(torch.log(lam_t.clamp(min=lmax * 1e-9)))
        if kind == 'fsq':
            self.register_buffer('qtab', fsq_table(lam_t.numpy(), K))
            lev, thr = lm_tensors()
            self.register_buffer('lev', lev)
            self.register_buffer('thr', thr)

    def encode(self, h, a=None):
        x = (h - self.m) @ self.Sm12
        return self.bn(x @ self.enc_lin + self.enc_mlp(x))

    def code(self, z, rate, gen=None):
        B = z.shape[0]
        if self.kind == 'bin':
            t = torch.tanh(z)
            c = t + (torch.sign(z) - t).detach()
            mask = (torch.arange(self.K)[None, :] < rate[:, None]).to(DT)
            return c * mask, rate.to(DT)
        if self.kind == 'gauss':
            Ci = waterfill(self.eta, rate.to(DT))
            snr = torch.pow(2.0, 2.0 * Ci) - 1.0
            noise = torch.randn(z.shape, generator=gen, dtype=DT) if gen is not None else torch.randn_like(z)
            r = snr / (1.0 + snr)
            y = z + noise / torch.sqrt(snr.clamp(min=1e-12))
            return torch.cat([r * y, r], 1), 0.5 * torch.log2(1.0 + snr).sum(1)
        # fsq
        q = self.qtab[rate.long().clamp(0, self.qtab.shape[0] - 1)]          # (B, K) bits per channel
        zc = z.detach()
        lv = torch.zeros_like(zc)
        for b in range(1, self.lev.shape[0]):
            msk = q == b
            if bool(msk.any()):
                nl = 2 ** b
                th = self.thr[b, :nl - 1].contiguous()
                idx = torch.searchsorted(th, zc[msk].contiguous())
                lv[msk] = self.lev[b, :nl][idx]
        zq = torch.where(q > 0, z, torch.zeros_like(z))
        c = zq + (lv - zq).detach()
        return torch.cat([c, q.to(DT) / 12.0], 1), q.sum(1).to(DT)

    def decode(self, cin):
        return self.m + (cin @ self.dec_lin + self.dec_mlp(cin)) @ self.S12

    def forward(self, h, a, rate, gen=None):
        z = self.encode(h, a)
        cin, Creal = self.code(z, rate, gen)
        return self.decode(cin), Creal
