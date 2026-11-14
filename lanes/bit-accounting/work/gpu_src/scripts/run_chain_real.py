"""Part S9 (Kelvin 02:10Z): the scrambling test for real-valued codes, the continuous analogue of the Walsh test.
Jointly trained chains of real-valued codes with fixed unit Gaussian noise: at grid layer l_i, mu_i = E_i(h_{l_i}) in
R^K, z_i = mu_i + eps (eps ~ N(0, I) fixed), rate = information estimate E[log2 q(z|h) - log2 p_i(z)] with a learned
prior; decoder D_i -> state -> real future; transitions T_i: z_i -> predicted mu_{i+1} (MLP). Loss = sum_i [nMSE_i +
lambda rate_i] + sum_i |T_i(z_i) - mu_{i+1}|^2 / tr Var(mu_{i+1}) + chain nMSE along z_0 -> T -> (+eps) -> ...
Analysis of each T_i (per model), in the Gaussian convention (z ~ N(m_i, Sigma_i), the data's mean and covariance,
z = m_i + Sigma_i^{1/2} u, u ~ N(0, I)): noise stability S(rho) = Cov(T(z), T(z_rho)) / tr Var T(z) with
z_rho from rho u + sqrt(1 - rho^2) g, Hermite weights W_d (d = 1..6, NNLS fit of S(rho) = sum_d rho^d W_d), the exact
degree-1 share (|E[T(z) u^T]|_F^2 / tr Var T), and per-input total effects (Jansen: resample one u coordinate).
Basis: the fixed isotropic noise defines the code coordinates up to rotations and shifts; the Gaussian convention and
these statistics are invariant to both. Baselines with the same K: a random linear map and a random high-degree map
B sin(3 C u + c), C with N(0, 1/K) entries (each feature has variance 9 inside the sine: almost no low-degree weight).
usage: run_chain_real.py --configs 16x16 --seeds 5000 --classes local,unres --out /root/runs/S_real
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
ap.add_argument('--lambdas', default='0.03,0.01,0.003')
ap.add_argument('--K', type=int, default=8)
ap.add_argument('--steps', type=int, default=2000)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--netkind', default='relu')
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
LAMS = [float(v) for v in args.lambdas.split(',')]
M, K = len(LAMS), args.K
LOG2 = math.log(2.0)
RHOS = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99]
T0 = time.time()


class GPrior(nn.Module):
    def __init__(self):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(M, 1, K, 3, device=DEV))
        self.ls = nn.Parameter(torch.full((M, 1, K, 3), 0.7, device=DEV))
        self.lw = nn.Parameter(torch.zeros(M, 1, K, 3, device=DEV))

    def log2p(self, z):
        ze = z.unsqueeze(-1)
        s = torch.exp(self.ls).clamp(min=1e-2)
        lp = -0.5 * ((ze - self.mu) / s) ** 2 - torch.log(s) - 0.5 * math.log(2 * math.pi)
        return torch.logsumexp(lp + torch.log_softmax(self.lw, -1), -1) / LOG2


class Chain(nn.Module):
    def __init__(self, n, layers, cls, frames, fr_a, starts):
        super().__init__()
        self.cls, self.frames, self.fr_a = cls, frames, fr_a
        m = len(layers)
        mk = lambda d_in: (sn.BMLP(M, d_in, K, n, 1, act='relu') if cls == 'local' else sn.BMLP(M, d_in, K, 256, 3))  # noqa
        self.enc = nn.ModuleList([mk(n if cls == 'local' else 2 * n) for _ in range(m)])
        self.dec = nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in range(m)])
        with torch.no_grad():
            for i in range(m):
                self.dec[i].bs[-1].copy_(starts[i].view(1, 1, n).expand(M, 1, n))
        self.T = nn.ModuleList([sn.BMLP(M, K, K, 256, 2) for _ in range(m - 1)])
        self.prior = nn.ModuleList([GPrior() for _ in range(m)])

    def mu(self, i, h, a):
        fr = self.frames[i]
        x = (h - fr['m']) @ fr['Sm12']
        if self.cls == 'unres':
            x = torch.cat([x, (a - self.fr_a['m']) @ self.fr_a['Sm12']], -1)
        return self.enc[i](x.unsqueeze(0).expand(M, *x.shape))

    def decode(self, i, z):
        fr = self.frames[i]
        return fr['m'] + self.dec[i](z) @ fr['S12']

    def rate(self, i, z, mu):
        logq = (-0.5 * (z - mu) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
        return (logq - self.prior[i].log2p(z)).sum(-1)


def stability(f, m, S12, n_s=16384, g=None):
    """Hermite analysis of f: R^K -> R^K under z = m + S12 u, u ~ N(0, I)."""
    u = torch.randn(n_s, K, generator=g, device=DEV)
    fz = f(m + u @ S12)
    fz = fz - fz.mean(0)
    var = float((fz ** 2).sum(1).mean())
    S = []
    for rho in RHOS:
        u2 = rho * u + math.sqrt(1 - rho * rho) * torch.randn(n_s, K, generator=g, device=DEV)
        f2 = f(m + u2 @ S12)
        f2 = f2 - f2.mean(0)
        S.append(float((fz * f2).sum(1).mean()) / max(var, 1e-30))
    A = np.array([[r ** d for d in range(1, 7)] for r in RHOS])
    b = np.array(S)
    W = np.zeros(A.shape[1])
    lr = 1.0 / np.linalg.norm(A, 2) ** 2
    for _ in range(20000):                                   # projected gradient NNLS (6 unknowns)
        W = np.maximum(0.0, W - lr * (A.T @ (A @ W - b)))
    coef = (fz.T @ u) / n_s                                   # E[f u^T]
    W1 = float((coef ** 2).sum()) / max(var, 1e-30)
    te = []
    for k in range(K):
        u3 = u.clone()
        u3[:, k] = torch.randn(n_s, generator=g, device=DEV)
        f3 = f(m + u3 @ S12)
        te.append(float(((f(m + u @ S12) - f3) ** 2).sum(1).mean()) / 2 / max(var, 1e-30))
    te = np.array(te)
    return dict(S=S, W=W.tolist(), W1_exact=W1, total_effects=te.tolist(), n_inputs_1pct=int((te > 0.01).sum()),
                te_PR=float(te.sum() ** 2 / max((te ** 2).sum(), 1e-30)))


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    m_ = len(layers)
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L, kind=args.netkind)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        V = float(Ap.double().var(0).sum())
        frames = [sn.frame(Hp[l]) for l in layers]
        fr_a = sn.frame(Ap)
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        starts = [(Hp[l][i_star] - frames[i]['m']) @ frames[i]['Sm12'] for i, l in enumerate(layers)]
        for cls in args.classes.split(','):
            tag = f'R_n{n}_L{L}_s{seed}_{cls}'
            path = os.path.join(args.out, tag + '.json')
            if os.path.exists(path):
                continue
            t1 = time.time()
            ch = Chain(n, layers, cls, frames, fr_a, starts)
            lam = torch.tensor(LAMS, device=DEV).view(M, 1)
            opt = torch.optim.Adam(ch.parameters(), lr=1e-3)
            sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 40) * (
                0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
            gt = torch.Generator(device=DEV).manual_seed(99_000 + seed * 7 + n * 13 + L + (0 if cls == 'local' else 1))
            for step in range(args.steps):
                Hb, Ab = net.sample(args.batch, set(layers), gt)
                mus = [ch.mu(i, Hb[l], Ab) for i, l in enumerate(layers)]
                zs = [mu + torch.randn(mu.shape, generator=gt, device=DEV) for mu in mus]
                loss = 0.0
                zc = zs[0]
                for i, l in enumerate(layers):
                    rec = net.run(ch.decode(i, zs[i]), l)
                    loss = loss + (((rec - Ab) ** 2).sum(-1).mean(-1) / V).sum()
                    loss = loss + (lam * ch.rate(i, zs[i], mus[i])).mean(-1).sum()
                    if i > 0:
                        rc = net.run(ch.decode(i, zc), l)
                        loss = loss + (((rc - Ab) ** 2).sum(-1).mean(-1) / V).sum()
                    if i < m_ - 1:
                        pred = ch.T[i](zs[i])
                        tv = mus[i + 1].detach().var(1).sum(-1).clamp(min=1e-6)
                        loss = loss + (((pred - mus[i + 1]) ** 2).sum(-1).mean(-1) / tv).sum()
                        zc = ch.T[i](zc) + torch.randn(zc.shape, generator=gt, device=DEV)
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(ch.parameters(), 10.0)
                opt.step()
                sched.step()
            ch.eval()
            res = dict(n=n, L=L, seed=seed, cls=cls, layers=layers, lambdas=LAMS, K=K, V=V, per_model=[])
            ge = torch.Generator(device=DEV).manual_seed(98_000 + seed)
            with torch.no_grad():
                He, Ae = net.sample(32768, set(layers), ge)
                mus = [ch.mu(i, He[l], Ae) for i, l in enumerate(layers)]
                zs = [mu + torch.randn(mu.shape, generator=ge, device=DEV) for mu in mus]
                own = [(((net.run(ch.decode(i, zs[i]), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist() for i, l in enumerate(layers)]
                rates = [ch.rate(i, zs[i], mus[i]).mean(-1).tolist() for i in range(m_)]
                chain, zc = [], zs[0]
                for i, l in enumerate(layers):
                    chain.append((((net.run(ch.decode(i, zc), l) - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    if i < m_ - 1:
                        zc = ch.T[i](zc) + torch.randn(zc.shape, generator=ge, device=DEV)
                r2 = []
                for i in range(m_ - 1):
                    pred = ch.T[i](zs[i])
                    r2.append((1 - ((pred - mus[i + 1]) ** 2).sum(-1).mean(-1) / mus[i + 1].var(1).sum(-1)).tolist())
            rngb = torch.Generator(device=DEV).manual_seed(5)
            for mi in range(M):
                trans = []
                for i in range(m_ - 1):
                    zi = zs[i][mi].double()
                    mm = zi.mean(0).float()
                    C = torch.cov(zi.T)
                    w, U = torch.linalg.eigh(C)
                    S12 = ((U * w.clamp(min=0).sqrt()) @ U.T).float()
                    f = lambda z, i=i, mi=mi: ch.T[i](z.unsqueeze(0).expand(M, *z.shape))[mi]  # noqa: E731
                    with torch.no_grad():
                        st = stability(f, mm, S12, g=rngb)
                        A = torch.randn(K, K, generator=rngb, device=DEV)
                        Bm = torch.randn(4 * K, K, generator=rngb, device=DEV) / math.sqrt(4 * K)
                        Cm = torch.randn(K, 4 * K, generator=rngb, device=DEV) / math.sqrt(K)
                        cb = 6.28 * torch.rand(4 * K, generator=rngb, device=DEV)
                        Si = torch.linalg.inv(S12.double()).float()
                        lin = stability(lambda z: ((z - mm) @ Si) @ A.T, mm, S12, g=rngb)
                        hd = stability(lambda z: torch.sin(3 * ((z - mm) @ Si) @ Cm + cb) @ Bm, mm, S12, g=rngb)
                    trans.append(dict(learned=st, base_linear=lin, base_highdeg=hd, R2_T=r2[i][mi]))
                res['per_model'].append(dict(lam=LAMS[mi], own=[o[mi] for o in own], chain=[c[mi] for c in chain],
                                             rate=[r[mi] for r in rates], transitions=trans))
            res['seconds'] = time.time() - t1
            json.dump(res, open(path, 'w'))
            for pm in res['per_model']:
                print(f'{tag} lam={pm["lam"]}: rate {[round(r, 1) for r in pm["rate"]]} own {[round(o, 3) for o in pm["own"]]} '
                      f'chain {[round(c, 3) for c in pm["chain"]]} | W1 learned '
                      f'{[round(t["learned"]["W1_exact"], 2) for t in pm["transitions"]]} highdeg '
                      f'{[round(t["base_highdeg"]["W1_exact"], 2) for t in pm["transitions"]]} | inputs '
                      f'{[t["learned"]["n_inputs_1pct"] for t in pm["transitions"]]} | {res["seconds"]:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
