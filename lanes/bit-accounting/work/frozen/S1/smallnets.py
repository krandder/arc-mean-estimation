"""Small-width bit accounting (GPU or CPU, torch): batched bottleneck trainings for fixed random ReLU nets.

Nets: plain critical He-ReLU, no biases, x ~ N(0, I_n), h_k = relu(W_k h_{k-1}), output a = h_L, W_k = st.W_layer(seed,
n, k) for k = 1..L (the stationary lane's stream; the ARC 256 x 32 nets are the same family).
Bottleneck at layer l (M models trained side by side on the same inputs, each with its own rate):
  encoder E: class 'local' = one ReLU layer of width n then a linear map (z = A2 relu(A1 x + b1) + b2), x the whitened
             h_l; class 'linear' = z = A x + b; class 'unres' = an MLP (3 hidden layers of width 256) that sees the
             whitened h_l and the whitened exact output a = g_l(h_l), i.e. an encoder that contains the future net.
  code:      'bin'  : c = sign(z_1..z_b) (b bits, straight-through tanh gradient); exactly 2^b cells.
             'gauss': u = per-channel unit-power normalisation of z (batch statistics, running statistics at test),
                      capacities C_i = max(0, (1/2) log2(gamma_i/theta)) by water-filling of learned importances with
                      sum_i C_i = C, y_i = u_i + N(0, 1/SNR_i), SNR_i = 2^{2 C_i} - 1; decoder sees (MMSE-scaled y, r_i).
  decoder:   MLP (3 hidden layers of width 256) -> whitened state -> h_hat = m + S^{1/2} z_hat -> fixed future g_l.
  loss:      |g_l(h_hat) - a|^2 / V, V = tr Var(a).
"""
import math
import os
import sys

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import st  # noqa: E402

DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
DT = torch.float32


class Net:
    def __init__(self, seed, n, L):
        self.seed, self.n, self.L = seed, n, L
        self.W64 = [st.W_layer(seed, n, k) for k in range(1, L + 1)]
        self.WT = [torch.tensor(np.ascontiguousarray(W.T), dtype=DT, device=DEV) for W in self.W64]

    def run(self, h, l0, l1=None):
        l1 = self.L if l1 is None else l1
        for k in range(l0, l1):
            h = torch.relu(h @ self.WT[k])
        return h

    @torch.no_grad()
    def sample(self, P, layers, gen):
        x = torch.randn(P, self.n, generator=gen, device=DEV, dtype=DT)
        H = {}
        h = x
        for k in range(self.L + 1):
            if k in layers:
                H[k] = h
            if k < self.L:
                h = torch.relu(h @ self.WT[k])
        return H, h


def frame(H, floor=1e-8):
    """Mean and symmetric square roots of the covariance (float64 numpy) of samples H (torch)."""
    X = H.double().cpu().numpy()
    m = X.mean(0)
    S = np.cov(X, rowvar=False)
    w, U = np.linalg.eigh(S)
    w = np.maximum(w, 0.0)
    keep = w > floor * max(w.max(), 1e-300)
    S12 = (U[:, keep] * np.sqrt(w[keep])) @ U[:, keep].T
    Sm12 = (U[:, keep] / np.sqrt(w[keep])) @ U[:, keep].T
    t = lambda a: torch.tensor(a, dtype=DT, device=DEV)  # noqa: E731
    return dict(m=t(m), S12=t(S12), Sm12=t(Sm12), rank=int(keep.sum()), evals=w[::-1].copy())


class BMLP(nn.Module):
    """M independent MLPs evaluated with batched matmuls. x (M, B, d_in) -> (M, B, d_out)."""

    def __init__(self, M, d_in, d_out, width, depth, act='gelu', last_scale=1.0):
        super().__init__()
        dims = [d_in] + [width] * depth + [d_out]
        self.Ws = nn.ParameterList()
        self.bs = nn.ParameterList()
        for i in range(len(dims) - 1):
            w = torch.randn(M, dims[i], dims[i + 1], device=DEV) * math.sqrt((2.0 if i > 0 or True else 1.0) / dims[i])
            if i == len(dims) - 2:
                w = w * last_scale
            self.Ws.append(nn.Parameter(w))
            self.bs.append(nn.Parameter(torch.zeros(M, 1, dims[i + 1], device=DEV)))
        self.act = nn.GELU() if act == 'gelu' else nn.ReLU()

    def forward(self, x):
        n = len(self.Ws)
        for i in range(n):
            x = torch.baddbmm(self.bs[i], x, self.Ws[i])
            if i < n - 1:
                x = self.act(x)
        return x


def waterfill_rows(eta, C):
    """Per-row water-filling: eta (M, K) log-importances, C (M,) bits -> capacities (M, K), rows summing to C."""
    M, K = eta.shape
    srt, idx = torch.sort(eta, dim=1, descending=True)
    cs = torch.cumsum(srt, 1)
    k = torch.arange(1, K + 1, device=eta.device, dtype=eta.dtype)[None, :]
    two_ln2 = 2.0 * math.log(2.0)
    lt = (cs - two_ln2 * C[:, None]) / k
    valid = srt > lt
    kk = (valid * k).max(1).values.long()
    lt_sel = lt.gather(1, (kk - 1).clamp(min=0)[:, None])
    Cs = torch.clamp((srt - lt_sel) / two_ln2, min=0.0)
    out = torch.empty_like(Cs)
    out.scatter_(1, idx, Cs)
    return out


class Bottlenecks(nn.Module):
    """M bottlenecks of one kind ('bin' or 'gauss') and one encoder class at one layer; rates (M,)."""

    def __init__(self, n, kind, enc_class, rates, fr, fr_a, h_star_w, K=32, width=256, depth=3):
        super().__init__()
        self.n, self.kind, self.enc_class = n, kind, enc_class
        M = len(rates)
        self.M, self.K = M, K
        self.register_buffer('rates', torch.tensor(rates, dtype=DT, device=DEV))
        self.fr, self.fr_a = fr, fr_a
        if enc_class == 'local':
            self.enc = BMLP(M, n, K, n, 1, act='relu')
        elif enc_class == 'linear':
            self.enc = BMLP(M, n, K, n, 0)
        elif enc_class == 'unres':
            self.enc = BMLP(M, 2 * n, K, width, depth)
        else:
            raise ValueError(enc_class)
        d_code = K if kind == 'bin' else 2 * K
        self.dec = BMLP(M, d_code, n, width, depth, last_scale=0.0)
        with torch.no_grad():
            self.dec.bs[-1].copy_(h_star_w.view(1, 1, n).expand(M, 1, n))
        if kind == 'bin':
            j = torch.arange(K, device=DEV)[None, None, :]
            self.register_buffer('mask', (j < self.rates.view(M, 1, 1)).to(DT))
        else:
            self.eta = nn.Parameter(torch.zeros(M, K, device=DEV))
            self.register_buffer('run_mean', torch.zeros(M, 1, K, device=DEV))
            self.register_buffer('run_var', torch.ones(M, 1, K, device=DEV))

    def whiten(self, h, a):
        x = (h - self.fr['m']) @ self.fr['Sm12']
        if self.enc_class == 'unres':
            xa = (a - self.fr_a['m']) @ self.fr_a['Sm12']
            x = torch.cat([x, xa], -1)
        return x

    def encode(self, h, a):
        x = self.whiten(h, a)
        return self.enc(x.unsqueeze(0).expand(self.M, *x.shape))

    def code(self, z, gen=None):
        if self.kind == 'bin':
            t = torch.tanh(z)
            c = t + (torch.sign(z) - t).detach()
            return c * self.mask
        if self.training:
            mu = z.mean(1, keepdim=True)
            var = z.var(1, keepdim=True)
            with torch.no_grad():
                self.run_mean.mul_(0.99).add_(0.01 * mu)
                self.run_var.mul_(0.99).add_(0.01 * var)
        else:
            mu, var = self.run_mean, self.run_var
        u = (z - mu) / torch.sqrt(var + 1e-6)
        Ci = waterfill_rows(self.eta, self.rates)                       # (M, K)
        snr = (torch.pow(2.0, 2.0 * Ci) - 1.0).unsqueeze(1)             # (M, 1, K)
        noise = torch.randn(u.shape, generator=gen, device=DEV, dtype=DT) if gen is not None else torch.randn_like(u)
        r = snr / (1.0 + snr)
        y = u + noise / torch.sqrt(snr.clamp(min=1e-12))
        return torch.cat([r * y, r.expand_as(y)], -1)

    def decode(self, cin):
        zh = self.dec(cin)
        return self.fr['m'] + zh @ self.fr['S12']

    def forward(self, h, a, gen=None):
        return self.decode(self.code(self.encode(h, a), gen))

    def capacities(self):
        if self.kind == 'bin':
            return self.rates.clone()
        return waterfill_rows(self.eta, self.rates).sum(1)


def crossing(rates, y, eps):
    """Interpolated rate (log nMSE linear in rate) where the curve first reaches eps; None if never."""
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None
