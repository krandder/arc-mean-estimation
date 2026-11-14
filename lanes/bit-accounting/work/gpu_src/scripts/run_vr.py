"""Phase 1 (Kelvin 02:55Z): the best bits-vs-accuracy curve of every layer, with one lambda-conditioned variable-rate
code per (net, layer, class) and certificates on every curve. Registered as PREREG Part P1.

Code (S7 'gfix' family, real-valued): y = E(x, t), z = y + N(0, I_K), rate = log2 q(z | x) - log2 p(z | t) summed over
the K latents (a one-draw estimate of KL(q || p) >= I(h; z) in bits), t = (log10 lambda + 2) / 2 in [-1, 1].
E, the decoder D(z, t) and the prior p(. | t) are all conditioned on t by FiLM: every hidden layer is
act(g(t) * (W x + b) + c(t)) and the encoder output is exp(s(t)) * (W x + b) + o(t), with (g - 1, c, s, o) produced by
a small MLP on t (zero at initialisation). Classes: unres = 3 hidden layers of width 256 on (whitened h_l, whitened
exact output a); local = ONE ReLU layer of width n on the whitened h_l, then affine; for every fixed t the local
encoder is in the registered class L^1(n) (FiLM only rescales and shifts that layer's pre-activations and the affine
output). Prior: per latent a mixture of C = 4 Gaussians whose parameters are a base vector plus an MLP of t.
Decoder: 3 hidden layers of width 256 -> whitened state -> h_hat = m + S^{1/2} out -> the real rest of the net.
Loss per example: d / lambda + rate, d = |g_l(h_hat) - a|^2 / tr Var(a), log10 lambda ~ U[-4, 0] per example
(variable-rate models) or fixed (spot-check models).

Per cell, in one process:
  G1 (M = 6, batched): r0, r1, r2 = variable-rate restarts; f1, f2, f3 = separately trained fixed-lambda models at
     lambda = 0.1, 0.01, 0.001 (the spot check); S steps.
  G2 wide: widths x2 (unres 512; local hidden 2n, which leaves L^1(n)), decoder 512, C = 8; S steps.
  G3 long: base architecture, 2S steps.
Evaluation on P_eval fresh held-out samples: every variable-rate model on a 17-point lambda grid (log10 lambda = -4 ..
0 step 0.25): rate, nMSE, output-mean error; fixed models at their lambda. Certificates on r0: fresh priors refitted
on held-out codes (half A; factorised mixture with 8 components, and a full-covariance Gaussian), rate on half B; a
centroid test at lambda = 0.1, 0.01, 0.001: an output-space regressor E[a | z] (MLP 3 x 512) trained on 98304 fresh
samples, its held-out nMSE against the model's on the same codes. Also the Gaussian bound R_G(D) of the output
(reverse water-filling over the eigenvalues of Cov(a)).
usage: run_vr.py --configs 16x16 --seeds 5000 --out /root/runs/P1 [--netkind relu|tanh4|feistel|linear]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x16')
ap.add_argument('--seeds', default='5000')
ap.add_argument('--classes', default='local,unres')
ap.add_argument('--layers', default='')            # default: {0, L/4, L/2, 3L/4, L-1} and the output L
ap.add_argument('--steps', type=int, default=6000)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--C', type=int, default=4)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--cent_steps', type=int, default=2000)
ap.add_argument('--refit_steps', type=int, default=600)
ap.add_argument('--groups', default='G1,G2,G3')
ap.add_argument('--certs', type=int, default=1)     # 0: skip refit/centroid (phase-2 cells that only need the code)
ap.add_argument('--netkind', default='relu')
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--squash', type=int, default=-1)   # -1: on for feistel only (decoded state = tanh(...))
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
torch.set_num_threads(args.threads)
DEV, DT = sn.DEV, sn.DT
LOG2 = math.log(2.0)
FIXED = [0.1, 0.01, 0.001]
GRID = [10 ** (-4 + 0.25 * i) for i in range(17)]
DGRID = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
CH = 8192
SQUASH = (args.netkind == 'feistel') if args.squash < 0 else bool(args.squash)


def state(fr, zh):
    """Decoded whitened state -> state at layer l (clipped to [-1, 1] for the Boolean feistel net: products stay bounded)."""
    h = fr['m'] + zh @ fr['S12']
    return h.clamp(-1.0, 1.0) if SQUASH else h     # feistel: identity on [-1, 1] (actual states +-1), never above 1
T0 = time.time()


def tof(lam):
    return (math.log10(lam) + 2.0) / 2.0


class FMLP(nn.Module):
    """M independent MLPs with FiLM conditioning on t (M, B, 1). x (M, B, d_in) -> (M, B, d_out)."""

    def __init__(self, M, d_in, d_out, width, depth, act='gelu', last_scale=1.0, out_film=False, skip=None):
        super().__init__()
        dims = [d_in] + [width] * depth + [d_out]
        self.skip = None if skip is None else nn.Parameter(skip.to(DEV).expand(M, d_in, d_out).clone())
        self.Ws, self.bs = nn.ParameterList(), nn.ParameterList()
        for i in range(len(dims) - 1):
            w = torch.randn(M, dims[i], dims[i + 1], device=DEV) * math.sqrt(2.0 / dims[i])
            if i == len(dims) - 2:
                w = w * last_scale
            self.Ws.append(nn.Parameter(w))
            self.bs.append(nn.Parameter(torch.zeros(M, 1, dims[i + 1], device=DEV)))
        self.depth, self.width, self.d_out, self.out_film = depth, width, d_out, out_film
        nf = 2 * width * depth + (2 * d_out if out_film else 0)
        self.film = sn.BMLP(M, 1, nf, 64, 2, last_scale=0.0)
        self.act = nn.GELU() if act == 'gelu' else nn.ReLU()

    def forward(self, x, t, gain=None, gain_mode=None):
        """gain (M, B, d) multiplies: 'skip_out' the skip term's output, 'skip_in' the skip term's input, 'all' the
        whole output before the output FiLM."""
        f = self.film(t)
        w = self.width
        x0 = x
        for i in range(self.depth):
            g, c = f[..., 2 * i * w:(2 * i + 1) * w], f[..., (2 * i + 1) * w:(2 * i + 2) * w]
            x = self.act((1.0 + g) * torch.baddbmm(self.bs[i], x, self.Ws[i]) + c)
        y = torch.baddbmm(self.bs[-1], x, self.Ws[-1])
        if self.skip is not None:
            if gain_mode == 'skip_out':
                y = y + gain * torch.bmm(x0, self.skip)
            elif gain_mode == 'skip_in':
                y = y + torch.bmm(gain * x0, self.skip)
            else:
                y = y + torch.bmm(x0, self.skip)
        if gain_mode == 'all':
            y = gain * y
        if self.out_film:
            o0 = 2 * self.depth * w
            s, o = f[..., o0:o0 + self.d_out], f[..., o0 + self.d_out:o0 + 2 * self.d_out]
            y = torch.exp(s.clamp(-6, 6)) * y + o
        return y


class CPrior(nn.Module):
    """Per (model, latent) a mixture of C Gaussians; parameters = base + MLP(t). log2 density of z (M, B, K)."""

    def __init__(self, M, K, C, hid=64, scale0=1.0):
        super().__init__()
        self.K, self.C = K, C
        self.mu = nn.Parameter(torch.randn(M, 1, K, C, device=DEV) * 0.3 * scale0)
        self.ls = nn.Parameter(torch.full((M, 1, K, C), math.log(scale0), device=DEV))
        self.lw = nn.Parameter(torch.zeros(M, 1, K, C, device=DEV))
        self.net = sn.BMLP(M, 1, 3 * K * C, hid, 2, last_scale=0.0)
        self.tri0 = nn.Parameter(torch.zeros(M, 1, K, K, device=DEV))
        self.tnet = sn.BMLP(M, 1, K * K, hid, 2, last_scale=0.0)
        self.register_buffer('mask', torch.tril(torch.ones(K, K, device=DEV), -1))

    def log2p(self, z, t, ls_add=None):
        M, B, K = z.shape
        T = (self.tri0 + self.tnet(t).view(M, B, K, K)) * self.mask      # strictly lower: u = z + T z, |det| = 1
        z = z + (T @ z.unsqueeze(-1)).squeeze(-1)
        d = self.net(t).view(M, B, K, self.C, 3)
        ls = self.ls + d[..., 1] + (0.0 if ls_add is None else ls_add.unsqueeze(-1))
        mu, ls, lw = self.mu + d[..., 0], ls.clamp(-4.6, 9.0), self.lw + d[..., 2]
        s = torch.exp(ls)
        ze = z.unsqueeze(-1)
        lp = -0.5 * ((ze - mu) / s) ** 2 - ls - 0.5 * math.log(2 * math.pi)
        return torch.logsumexp(lp + torch.log_softmax(lw, -1), -1) / LOG2


SHIFT, AMAX = 8.0, 16.0


class VR(nn.Module):
    """Analytic anchor (Kelvin 03:20Z: identity anchor at high budget, shed the least important directions first as
    the price rises, checked against the linear reference). Code y = a~(lambda) * y~(x), z = y + N(0, I):
      y~ = unit-scale encoder output, initialised to U^T x (x = whitened h_l; U, g = eigenpairs of G = E[J^T J]);
      a~ = a + c(lambda): a_i = min(16, sqrt(max(0, g_i / theta - 1))), theta = lambda V / (2 ln 2) (the water-filled
      power that minimises the linearised Lagrangian, capped at SNR 256 = Kelvin's identity anchor at about 4 bits per
      direction; the cap keeps optimiser steps small against the unit noise), c a learned correction (zero at
      initialisation; can raise the power or switch on directions the linear code leaves off);
      decoder input b~ * z with b~ = a~ / (a~^2 + 1) (the linear-MMSE scaling), output MLP + U b~ z (MLP zero at init);
      prior on the standardised code z / sqrt(a~^2 + 1) (unit lower-triangular map + factorised mixture), with the
      Jacobian term -sum log2 sqrt(a~^2 + 1).
    At initialisation the code at every lambda IS the linear reference code; at high budget it reconstructs every
    direction the output depends on almost perfectly. local: u = relu(x + SHIFT) (exact for x > -SHIFT), y~ =
    (u - SHIFT) U, so for every fixed lambda y = a~ * (A2 u + b2) is affine in u: the class stays L^1(n)."""

    def __init__(self, M, n, cls, K, width, C, anchor, local_width):
        super().__init__()
        self.cls = cls
        U, ev, V = anchor
        Uf = U.float().cpu()
        self.register_buffer('g', ev.float().to(DEV).view(1, 1, -1))
        self.V = V
        if cls == 'local':
            self.enc = FMLP(M, n, K, local_width, 1, act='relu')
            with torch.no_grad():
                W1 = torch.randn(n, local_width) * 0.01
                W1[:, :n] = torch.eye(n)
                self.enc.Ws[0].copy_(W1.to(DEV).expand(M, n, local_width))
                b1 = torch.zeros(1, local_width)
                b1[:, :n] = SHIFT
                self.enc.bs[0].copy_(b1.to(DEV).expand(M, 1, local_width))
                Wo = torch.zeros(local_width, K)
                Wo[:n, :] = Uf
                self.enc.Ws[1].copy_(Wo.to(DEV).expand(M, local_width, K))
                self.enc.bs[1].copy_((-SHIFT * Uf.sum(0, keepdim=True)).to(DEV).expand(M, 1, K))
        else:
            Es = torch.zeros(2 * n, K)
            Es[:n] = Uf
            self.enc = FMLP(M, 2 * n, K, width, 3, last_scale=0.0, skip=Es)
        self.cnet = sn.BMLP(M, 1, K, 64, 2, last_scale=0.0)
        self.dec = FMLP(M, K, n, width, 3, last_scale=0.0, skip=Uf.T.contiguous())
        self.prior = CPrior(M, K, C, scale0=1.0)

    def gain(self, t):
        th = (10.0 ** (2.0 * t - 2.0)) * self.V / (2.0 * LOG2)              # (M, B, 1)
        a = torch.sqrt(torch.relu(self.g / th - 1.0)).clamp(max=AMAX)        # (M, B, K); capped: SNR <= AMAX^2
        return a + self.cnet(t)

    def encode(self, x, t):
        return self.gain(t) * self.enc(x, t)

    def decode(self, z, t):
        at = self.gain(t)
        return self.dec(z * (at / (at * at + 1.0)), t)

    def log2p(self, z, t):
        at = self.gain(t)
        sd = torch.sqrt(at * at + 1.0)
        return self.prior.log2p(z / sd, t) - torch.log2(sd)

    def forward(self, x, t, g):
        y = self.encode(x, t)
        z = y + torch.randn(y.shape, generator=g, device=DEV)
        logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
        rate = (logq - self.log2p(z, t)).sum(-1)
        return self.decode(z, t), rate, z, logq.sum(-1)


def rate_at(rates, nmse, eps):
    """Rate where the monotone envelope of (rate, nMSE) crosses eps (log-linear interpolation); None if unreached."""
    pts = sorted(zip(rates, nmse))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return float(r)
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return float(r0 + f * (r - r0))
    return None


def rwf_rate(evals, D):
    """Gaussian reverse water-filling: rate (bits) for total distortion D * sum(evals)."""
    ev = np.sort(np.maximum(np.asarray(evals, float), 0.0))[::-1]
    tot = D * ev.sum()
    if tot >= ev.sum():
        return 0.0
    lo, hi = 0.0, ev.max()
    for _ in range(200):
        th = 0.5 * (lo + hi)
        if np.minimum(th, ev).sum() > tot:
            hi = th
        else:
            lo = th
    th = 0.5 * (lo + hi)
    return float(sum(0.5 * math.log2(e / th) for e in ev if e > th))


def train(model, M, n, net, l, L, V, fr, fr_a, cls, steps, lam_mode, gseed):
    """lam_mode: list of M entries, None = variable rate (log-uniform per example), float = fixed lambda."""
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, betas=(0.9, 0.99))
    warm = max(1, steps // 50)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
        0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, steps) / steps))))
    gt = torch.Generator(device=DEV).manual_seed(gseed)
    B = args.batch
    fixed_t = torch.tensor([0.0 if m is None else tof(m) for m in lam_mode], device=DEV).view(M, 1, 1)
    is_var = torch.tensor([m is None for m in lam_mode], device=DEV).view(M, 1, 1)
    NB = 16
    ema = torch.zeros(M, NB, device=DEV)
    for step in range(steps):
        Hb, Ab = net.sample(B, {l}, gt)
        hb = Ab if l == L else Hb[l]
        x = inp(hb, Ab, fr, fr_a, cls, M)
        ramp = min(1.0, step / max(1.0, 0.25 * steps))         # lambda annealed upward from 1e-4 (t = -1)
        tr = -1.0 + ramp * 2.0 * torch.rand(M, B, 1, generator=gt, device=DEV)
        t = torch.where(is_var, tr, -1.0 + ramp * (fixed_t + 1.0))
        lam = 10.0 ** (2.0 * t - 2.0)
        zh, rate, _, _ = model(x, t, gt)
        ah = net.run(state(fr, zh), l)
        d = ((ah - Ab) ** 2).sum(-1) / V
        lag = d + lam.squeeze(-1) * rate                          # Lagrangian per example
        with torch.no_grad():                                     # per-lambda scale (EMA by t-bin): each lambda counts
            bi = ((t.squeeze(-1) + 1.0) * 0.5 * NB).long().clamp(0, NB - 1)      # equally; the optimum of each
            tot = torch.zeros(M, NB, device=DEV).scatter_add_(1, bi, lag)       # lambda is unchanged
            cnt = torch.zeros(M, NB, device=DEV).scatter_add_(1, bi, torch.ones_like(lag))
            mean_b = tot / cnt.clamp(min=1)
            upd = cnt > 0
            ema = torch.where(upd & (ema == 0), mean_b, torch.where(upd, 0.95 * ema + 0.05 * mean_b, ema))
            wgt = 1.0 / ema.gather(1, bi).clamp(min=1e-6)
        loss = (lag * wgt).mean(-1).sum()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 100.0)
        opt.step()
        sched.step()


def inp(h, a, fr, fr_a, cls, M):
    x = (h - fr['m']) @ fr['Sm12']
    if cls == 'unres':
        x = torch.cat([x, (a - fr_a['m']) @ fr_a['Sm12']], -1)
    return x.unsqueeze(0).expand(M, *x.shape)


@torch.no_grad()
def evaluate(model, M, xe, Ae, net, l, V, fr, lam_list, gseed):
    """lam_list: per lambda value, one evaluation of all M models at that lambda. Returns rate/nmse/mean_err (M, G)."""
    out = dict(rate=[], nmse=[], mean_err=[])
    P = xe.shape[1]
    for lam in lam_list:
        g = torch.Generator(device=DEV).manual_seed(gseed)
        se = torch.zeros(M, dtype=torch.float64, device=DEV)
        sd = torch.zeros(M, Ae.shape[1], dtype=torch.float64, device=DEV)
        sr = torch.zeros(M, dtype=torch.float64, device=DEV)
        for c0 in range(0, P, CH):
            xc = xe[:, c0:c0 + CH]
            t = torch.full((M, xc.shape[1], 1), tof(lam), device=DEV)
            zh, rate, _, _ = model(xc, t, g)
            ah = net.run(state(fr, zh), l)
            dd = (ah - Ae[c0:c0 + CH]).double()
            se += (dd * dd).sum(-1).sum(-1)
            sd += dd.sum(1)
            sr += rate.double().sum(1)
        out['nmse'].append((se / P / V).tolist())
        md = sd / P
        out['mean_err'].append(((md * md).sum(-1) / V).tolist())
        out['rate'].append((sr / P).tolist())
    return {k: np.array(v).T.tolist() for k, v in out.items()}       # (M, G)


def enc_codes(model, mi, x1, lam, g):
    """x1 (B, d) -> codes z (B, K) of model mi at lambda (fresh noise), log2 q(z | x) (B,), and t (M, B, 1)."""
    M = model.enc.Ws[0].shape[0]
    t = torch.full((M, x1.shape[0], 1), tof(lam), device=DEV)
    y = model.encode(x1.unsqueeze(0).expand(M, -1, -1), t)[mi]
    z = y + torch.randn(y.shape, generator=g, device=DEV)
    logq = ((-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2).sum(-1)
    return z, logq, t


def refit(model, mi, xe, lam, gseed):
    """Rates on half B of the held-out codes: trained prior, refitted factorised 8-mixture, refitted full Gaussian."""
    with torch.no_grad():
        g = torch.Generator(device=DEV).manual_seed(gseed)
        zs, lqs, lps = [], [], []
        for c0 in range(0, xe.shape[1], CH):
            z, lq, t = enc_codes(model, mi, xe[0, c0:c0 + CH], lam, g)
            M = t.shape[0]
            lp = model.log2p(z.unsqueeze(0).expand(M, -1, -1), t)[mi].sum(-1)
            zs.append(z)
            lqs.append(lq)
            lps.append(lp)
        z, logq, lp_tr = torch.cat(zs), torch.cat(lqs), torch.cat(lps)
    h = z.shape[0] // 2
    zA, zB = z[:h], z[h:]
    K = z.shape[1]
    mu = nn.Parameter(zA[torch.randint(0, h, (8,), generator=torch.Generator(device=DEV).manual_seed(gseed + 1),
                                       device=DEV)].T.clone().contiguous())
    ls = nn.Parameter(torch.log(zA.std(0, keepdim=True).T.expand(K, 8).clone() * 0.5 + 1e-3))
    lw = nn.Parameter(torch.zeros(K, 8, device=DEV))
    opt = torch.optim.Adam([mu, ls, lw], lr=0.05)

    def lp(zz):
        s = torch.exp(ls.clamp(-6, 6))
        e = -0.5 * ((zz.unsqueeze(-1) - mu) / s) ** 2 - torch.log(s) - 0.5 * math.log(2 * math.pi)
        return (torch.logsumexp(e + torch.log_softmax(lw, -1), -1) / LOG2).sum(-1)

    for _ in range(args.refit_steps):
        loss = -lp(zA).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        r_mix = float((logq[h:] - lp(zB)).mean())
        zc = zA.double() - zA.double().mean(0)
        S = zc.T @ zc / (h - 1) + 1e-9 * torch.eye(K, device=DEV, dtype=torch.float64)
        Li = torch.linalg.cholesky(S)
        e = torch.linalg.solve_triangular(Li, (zB.double() - zA.double().mean(0)).T, upper=False)
        lpg = (-0.5 * (e ** 2).sum(0) - torch.log(torch.diagonal(Li)).sum() - 0.5 * K * math.log(2 * math.pi)) / LOG2
        r_gauss = float((logq[h:].double() - lpg).mean())
        r_tr = float((logq[h:] - lp_tr[h:]).mean())
    return dict(lam=lam, rate_trained_B=r_tr, rate_refit_mix8=r_mix, rate_refit_fullgauss=r_gauss)


def centroid(model, mi, net, l, L, V, fr, fr_a, cls, n, lam, gseed):
    """Output-space regressor E[a | z] (MLP 3 x 512) on 98304 fresh samples (fresh noise each step); held-out nMSE on
    32768 samples against the model's nMSE on the same codes."""
    g = torch.Generator(device=DEV).manual_seed(gseed)
    H, A = net.sample(131072, {l}, g)
    h = A if l == L else H[l]
    x = inp(h, A, fr, fr_a, cls, 1)[0]
    nA = 98304
    Kz = model.dec.Ws[0].shape[1]
    reg = sn.BMLP(1, Kz, n, 512, 3)
    opt = torch.optim.Adam(reg.parameters(), lr=1e-3)
    steps = args.cent_steps
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * s / steps)))
    Aw = (A - fr_a['m']) @ fr_a['Sm12']
    for _ in range(steps):
        idx = torch.randint(0, nA, (4096,), generator=g, device=DEV)
        with torch.no_grad():
            zb, _, _ = enc_codes(model, mi, x[idx], lam, g)
        loss = ((reg(zb.unsqueeze(0))[0] - Aw[idx]) ** 2).sum(-1).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
    with torch.no_grad():
        se_c, se_m = 0.0, 0.0
        for c0 in range(nA, x.shape[0], CH):
            z, _, t = enc_codes(model, mi, x[c0:c0 + CH], lam, g)
            a_c = fr_a['m'] + reg(z.unsqueeze(0))[0] @ fr_a['S12']
            se_c += float(((a_c - A[c0:c0 + CH]) ** 2).sum())
            M = t.shape[0]
            zh = model.decode(z.unsqueeze(0).expand(M, -1, -1), t)[mi]
            ah = net.run(state(fr, zh), l)
            se_m += float(((ah - A[c0:c0 + CH]) ** 2).sum())
        nB = x.shape[0] - nA
    return dict(lam=lam, nmse_model=se_m / nB / V, nmse_centroid=se_c / nB / V)


def linref(net, l, L, V, fr, He, Ae, gseed, P=16384, NT=40):
    """Analytic reference per layer (Kelvin 03:20Z). G = E[J^T J], J = d a / d x_w at the actual states (x_w = whitened
    h_l; P samples): the cloud-averaged, forward-propagated (future-weighted) Jacobian Gram. Eigenvectors u_i, values
    g_i. At water level theta: send u_i^T x_w with power p_i = g_i / theta - 1 (g_i > theta) through the unit-noise
    channel, decode by linear MMSE (x_hat = sum_i u_i sqrt(p_i) / (p_i + 1) z_i; x_w has unit-variance uncorrelated
    coordinates), run the REAL rest of the net on the held-out states. Rate = sum_i 0.5 log2(1 + p_i) (the capacity
    formula, an upper bound on the code's information for any input law). Also the linearised prediction
    sum_i min(theta, g_i) / V (reverse water-filling; exact if the future were linear and the states Gaussian)."""
    g = torch.Generator(device=DEV).manual_seed(gseed)
    H, A = net.sample(P, {l}, g)
    h = A if l == L else H[l]
    xw = ((h - fr['m']) @ fr['Sm12']).detach().requires_grad_(True)
    a = net.run(fr['m'] + xw @ fr['S12'], l)                         # Jacobian at the actual states (no squash)
    G = torch.zeros(xw.shape[1], xw.shape[1], device=DEV, dtype=torch.float64)
    for j in range(a.shape[1]):
        gr, = torch.autograd.grad(a[:, j].sum(), xw, retain_graph=(j < a.shape[1] - 1))
        G += (gr.double().T @ gr.double()) / P
    ev, U = torch.linalg.eigh(G)
    ev, U = ev.clamp(min=0).flip(0), U.flip(1)
    xe = (He[l] - fr['m']) @ fr['Sm12'] if l < L else (Ae - fr['m']) @ fr['Sm12']
    proj = (xe.double() @ U)                                            # (P_eval, n) coordinates u_i^T x_w
    gmax = float(ev[0]) if float(ev[0]) > 0 else 1.0
    out = dict(evals=ev.tolist(), theta=[], rate=[], nmse=[], nmse_lin=[])
    anchor = (U.detach(), ev.detach(), V)
    ge = torch.Generator(device=DEV).manual_seed(gseed + 1)
    for th in np.logspace(math.log10(gmax), math.log10(gmax) - 7, NT):
        p = (ev / th - 1.0).clamp(min=0.0)
        z = proj * p.sqrt() + torch.randn(proj.shape, generator=ge, device=DEV, dtype=torch.float64)
        xh = (z * (p.sqrt() / (p + 1.0))) @ U.T
        se = 0.0
        with torch.no_grad():
            for c0 in range(0, xh.shape[0], CH):
                ah = net.run(state(fr, xh[c0:c0 + CH].float()), l)
                se += float(((ah - Ae[c0:c0 + CH]) ** 2).sum())
        out['theta'].append(float(th))
        out['rate'].append(float((0.5 * torch.log2(1.0 + p)).sum()))
        out['nmse'].append(se / xh.shape[0] / V)
        out['nmse_lin'].append(float(torch.minimum(ev, torch.tensor(th, device=DEV, dtype=torch.float64)).sum()) / V)
    return out, anchor


def summarise(rate, nmse):
    cr = {str(D): rate_at(rate, nmse, D) for D in DGRID}
    sl = {}
    for D1, D2 in zip(DGRID[:-1], DGRID[1:]):
        r1, r2 = cr[str(D1)], cr[str(D2)]
        sl[f'{D1}->{D2}'] = (None if (r1 is None or r2 is None) else (r2 - r1) / math.log2(D1 / D2))
    return cr, sl


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])) if not args.layers else \
        [int(v) for v in args.layers.split(',') if int(v) < L]
    K = max(16, n)
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L, kind=args.netkind)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        Hp[L] = Ap
        V = float(Ap.double().var(0).sum())
        fr_a = sn.frame(Ap)
        ev_a = np.linalg.eigvalsh(np.cov(Ap.double().cpu().numpy(), rowvar=False))
        RG = {str(D): rwf_rate(ev_a, D) for D in DGRID}
        ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
        He, Ae = net.sample(args.P_eval, set(layers), ge)
        He[L] = Ae
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        cell_layers = layers + [L] if not args.layers or str(L) in args.layers.split(',') else layers
        for l in cell_layers:
            fr = sn.frame(Hp[l]) if l < L else fr_a
            h_star_w = (Hp[l][i_star] - fr['m']) @ fr['Sm12']
            for cls in (args.classes.split(',') if l < L else ['unres']):
                tag = f'P_{args.netkind}_n{n}_L{L}_s{seed}_l{l}_{cls}'
                path = os.path.join(args.out, tag + '.json')
                if os.path.exists(path):
                    continue
                t1 = time.time()
                res = dict(n=n, L=L, seed=seed, l=l, cls=cls, netkind=args.netkind, squash=SQUASH, V=V, K=K, steps=args.steps,
                           batch=args.batch, grid=GRID, fixed=FIXED, RG=RG, evals_a=ev_a[::-1].tolist(), groups={})
                tl = time.time()
                res['linref'], anchor = linref(net, l, L, V, fr, He, Ae, 99_000 + seed)
                res['linref_seconds'] = time.time() - tl
                base = 77_000 + seed * 7 + n * 13 + L * 101 + l * 3 + (0 if cls == 'local' else 1)
                gev = 88_000 + seed
                xe6 = inp(He[l], Ae, fr, fr_a, cls, 6)
                models = {}
                if 'G1' in args.groups:
                    torch.manual_seed(base)
                    m1 = VR(6, n, cls, K, args.width, args.C, anchor, n)
                    train(m1, 6, n, net, l, L, V, fr, fr_a, cls, args.steps, [None, None, None] + FIXED, base)
                    ev = evaluate(m1, 6, xe6, Ae, net, l, V, fr, GRID, gev)
                    evf = evaluate(m1, 6, xe6, Ae, net, l, V, fr, FIXED, gev)
                    curves = {f'r{i}': {k: ev[k][i] for k in ev} for i in range(3)}
                    fixed = [dict(lam=lam, rate=evf['rate'][3 + j][j], nmse=evf['nmse'][3 + j][j],
                                  mean_err=evf['mean_err'][3 + j][j],
                                  vr_rate=evf['rate'][0][j], vr_nmse=evf['nmse'][0][j]) for j, lam in enumerate(FIXED)]
                    res['groups']['G1'] = dict(curves=curves, fixed=fixed, seconds=time.time() - t1)
                    models['G1'] = m1
                    print(f'  {tag} G1 {time.time() - t1:.0f}s', flush=True)
                if 'G2' in args.groups:
                    t2 = time.time()
                    torch.manual_seed(base + 5)
                    m2 = VR(1, n, cls, K, 2 * args.width, 2 * args.C, anchor, 2 * n)
                    train(m2, 1, n, net, l, L, V, fr, fr_a, cls, args.steps, [None], base + 5)
                    ev = evaluate(m2, 1, xe6[:1], Ae, net, l, V, fr, GRID, gev)
                    res['groups']['G2'] = dict(curves={'wide': {k: ev[k][0] for k in ev}}, seconds=time.time() - t2)
                    del m2
                    print(f'  {tag} G2 {time.time() - t2:.0f}s', flush=True)
                if 'G3' in args.groups:
                    t3 = time.time()
                    torch.manual_seed(base + 7)
                    m3 = VR(1, n, cls, K, args.width, args.C, anchor, n)
                    train(m3, 1, n, net, l, L, V, fr, fr_a, cls, 2 * args.steps, [None], base + 7)
                    ev = evaluate(m3, 1, xe6[:1], Ae, net, l, V, fr, GRID, gev)
                    res['groups']['G3'] = dict(curves={'long': {k: ev[k][0] for k in ev}}, seconds=time.time() - t3)
                    del m3
                    print(f'  {tag} G3 {time.time() - t3:.0f}s', flush=True)
                if 'G1' in args.groups and args.certs:
                    t4 = time.time()
                    m1 = models['G1']
                    res['refit'] = [refit(m1, 0, xe6, lam, gev + 1) for lam in GRID]
                    res['centroid'] = [centroid(m1, 0, net, l, L, V, fr, fr_a, cls, n, lam, gev + 2) for lam in FIXED]
                    res['cert_seconds'] = time.time() - t4
                summ = {}
                for gname, gd in res['groups'].items():
                    for cname, c in gd['curves'].items():
                        cr, sl = summarise(c['rate'], c['nmse'])
                        summ[cname] = dict(cross=cr, slope=sl)
                cr, sl = summarise(res['linref']['rate'], res['linref']['nmse'])
                summ['linref'] = dict(cross=cr, slope=sl)
                cr, sl = summarise(res['linref']['rate'], res['linref']['nmse_lin'])
                summ['linref_linearised'] = dict(cross=cr, slope=sl)
                if 'refit' in res:
                    rb = [min(x['rate_trained_B'], x['rate_refit_mix8'], x['rate_refit_fullgauss']) for x in res['refit']]
                    cr, sl = summarise(rb, res['groups']['G1']['curves']['r0']['nmse'])
                    summ['r0_refit'] = dict(cross=cr, slope=sl)
                res['summary'] = summ
                res['seconds'] = time.time() - t1
                json.dump(res, open(path, 'w'))
                if 'G1' in models:
                    torch.save(models['G1'].state_dict(), path.replace('.json', '.pt'))
                    del models['G1']
                fm = lambda v: '-' if v is None else f'{v:.2f}'  # noqa: E731
                msg = ' | '.join(f'{c}: R(0.1)={fm(sm["cross"]["0.1"])} R(0.01)={fm(sm["cross"]["0.01"])}'
                                 for c, sm in summ.items())
                print(f'{tag}: {res["seconds"]:.0f}s | RG(0.1)={RG["0.1"]:.2f} RG(0.01)={RG["0.01"]:.2f} | {msg}', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
