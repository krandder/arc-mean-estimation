"""Part S10 (Kelvin 02:25Z): a compressed simulator with simple code dynamics. Input code c_0 = A x + b + eps (linear
input encoder, eps ~ N(0, I) fixed, so c_0 is exactly Gaussian), then c_{i+1} = T_i(c_i) + eps along the layer grid
{0, L/4, L/2, 3L/4, L-1}, a decoder D_i at every grid layer (MLP -> state -> real future). Loss = sum_i nMSE(D_i(c_i))
+ lambda * rate(c_0) (information estimate of the input code with a learned prior; later codes add no information about
x). Each layer's own decode forces the code to describe that layer; the linear input encoder cannot compute the
output, so the identity shortcut is not available.
Transition classes (one model per class, lambdas side by side): mlp (reference), linear, shared (one linear T for all
steps), sparse<s> (linear, each output reads at most s inputs: fixed random mask), id<w> (T(c) = c + d(c), penalty
w |d|^2 on the change: "codes very similar"), deg2 (quadratic features, linear readout).
Report: per class, the per-layer and final nMSE and the input-code rate: what forcing simple dynamics costs.
Estimation (linear and shared classes): the code law stays Gaussian, propagated in closed form (mean, covariance);
E a = E over c_last ~ N(mu, Sigma) of g(D_last(c)), computed by RQMC over K dims (scrambled Sobol, N points), against
the truth (2^20 MC) and plain MC / RQMC on the net with the same N.
usage: run_sim.py --configs 16x16 --seed 5000 --out /root/runs/S_sim
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
ap.add_argument('--seed', type=int, default=5000)
ap.add_argument('--classes', default='mlp,linear,shared,sparse2,id10,deg2')
ap.add_argument('--lambdas', default='0.01,0.001')
ap.add_argument('--K', type=int, default=8)
ap.add_argument('--steps', type=int, default=2500)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--netkind', default='relu')
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
LAMS = [float(v) for v in args.lambdas.split(',')]
M, K = len(LAMS), args.K
LOG2 = math.log(2.0)
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


class Trans(nn.Module):
    def __init__(self, kind, g):
        super().__init__()
        self.kind = kind
        if kind == 'mlp':
            self.f = sn.BMLP(M, K, K, 256, 2)
        elif kind in ('linear', 'shared') or kind.startswith('sparse'):
            self.A = nn.Parameter(torch.eye(K, device=DEV).repeat(M, 1, 1) + 0.01 * torch.randn(M, K, K, device=DEV))
            self.b = nn.Parameter(torch.zeros(M, 1, K, device=DEV))
            mask = torch.ones(K, K, device=DEV)
            if kind.startswith('sparse'):
                s = int(kind[6:])
                mask = torch.zeros(K, K, device=DEV)
                for j in range(K):
                    idx = torch.randperm(K, generator=g, device=DEV)[:s]
                    mask[idx, j] = 1.0
                    mask[j, j] = 1.0                                 # each output reads itself and s-1 others
            self.register_buffer('mask', mask)
        elif kind.startswith('id'):
            self.f = sn.BMLP(M, K, K, 256, 2, last_scale=0.0)
        elif kind == 'deg2':
            self.W = nn.Parameter(torch.zeros(M, K + K * (K + 1) // 2, K, device=DEV))
            with torch.no_grad():
                self.W[:, :K, :] = torch.eye(K, device=DEV)
            iu = torch.triu_indices(K, K)
            self.register_buffer('iu0', iu[0])
            self.register_buffer('iu1', iu[1])

    def forward(self, c):
        if self.kind == 'mlp':
            return self.f(c), 0.0
        if self.kind in ('linear', 'shared') or self.kind.startswith('sparse'):
            return torch.baddbmm(self.b, c, self.A * self.mask), 0.0
        if self.kind.startswith('id'):
            d = self.f(c)
            return c + d, (d ** 2).sum(-1).mean(-1)
        q = c[..., self.iu0] * c[..., self.iu1]
        return torch.bmm(torch.cat([c, q], -1), self.W), 0.0


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    m_ = len(layers)
    net = sn.Net(args.seed, n, L, kind=args.netkind)
    gp = torch.Generator(device=DEV).manual_seed(10_000 + args.seed * 7 + n * 13 + L)
    Hp, Ap = net.sample(65536, set(layers), gp)
    V = float(Ap.double().var(0).sum())
    frames = [sn.frame(Hp[l]) for l in layers]
    i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
    starts = [(Hp[l][i_star] - frames[i]['m']) @ frames[i]['Sm12'] for i, l in enumerate(layers)]
    gtr = torch.Generator(device=DEV).manual_seed(4242)
    _, At = net.sample(1 << 20, set(), gtr)
    Ea_true = At.double().mean(0)
    for kind in args.classes.split(','):
        tag = f'Q_n{n}_L{L}_s{args.seed}_{kind}'
        path = os.path.join(args.out, tag + '.json')
        if os.path.exists(path):
            continue
        t1 = time.time()
        gk = torch.Generator(device=DEV).manual_seed(7)
        enc0 = sn.BMLP(M, n, K, n, 0)
        decs = nn.ModuleList([sn.BMLP(M, K, n, 256, 3, last_scale=0.0) for _ in layers])
        with torch.no_grad():
            for i in range(m_):
                decs[i].bs[-1].copy_(starts[i].view(1, 1, n).expand(M, 1, n))
        if kind == 'shared':
            T1 = Trans('shared', gk)
            Ts = nn.ModuleList([T1])
            getT = lambda i: Ts[0]  # noqa: E731
        else:
            Ts = nn.ModuleList([Trans(kind, gk) for _ in range(m_ - 1)])
            getT = lambda i: Ts[i]  # noqa: E731
        prior = GPrior()
        mods = nn.ModuleList([enc0, decs, Ts, prior])
        lam = torch.tensor(LAMS, device=DEV)
        w_id = float(kind[2:]) if kind.startswith('id') else 0.0
        opt = torch.optim.Adam(mods.parameters(), lr=1e-3)
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 50) * (
            0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
        gt = torch.Generator(device=DEV).manual_seed(123_000 + args.seed + n)

        def run_chain(x, g):
            xw = (x - frames[0]['m']) @ frames[0]['Sm12']
            mu0 = enc0(xw.unsqueeze(0).expand(M, *xw.shape))
            c = mu0 + torch.randn(mu0.shape, generator=g, device=DEV)
            logq = (-0.5 * (c - mu0) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
            rate = (logq - prior.log2p(c)).sum(-1).mean(-1)
            cs, pen = [c], 0.0
            for i in range(m_ - 1):
                c, p = getT(i)(c)
                pen = pen + p
                c = c + torch.randn(c.shape, generator=g, device=DEV)
                cs.append(c)
            return cs, rate, pen

        for step in range(args.steps):
            H, A = net.sample(args.batch, set(layers), gt)
            cs, rate, pen = run_chain(H[0], gt)
            loss = (lam * rate).sum() + (w_id * pen).sum() if w_id else (lam * rate).sum()
            for i, l in enumerate(layers):
                hh = frames[i]['m'] + decs[i](cs[i]) @ frames[i]['S12']
                loss = loss + (((net.run(hh, l) - A) ** 2).sum(-1).mean(-1) / V).sum()
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(mods.parameters(), 10.0)
            opt.step()
            sched.step()
        res = dict(n=n, L=L, seed=args.seed, kind=kind, lambdas=LAMS, K=K, layers=layers, V=V)
        with torch.no_grad():
            ge = torch.Generator(device=DEV).manual_seed(321)
            He, Ae = net.sample(32768, set(layers), ge)
            cs, rate, _ = run_chain(He[0], ge)
            res['rate_c0'] = rate.tolist()
            res['nmse'] = [(((net.run(frames[i]['m'] + decs[i](cs[i]) @ frames[i]['S12'], l) - Ae) ** 2).sum(-1).mean(-1)
                            / V).tolist() for i, l in enumerate(layers)]
            if kind in ('linear', 'shared') or kind.startswith('sparse'):
                # closed-form Gaussian propagation of the code law, then RQMC over K dims for the last decoder
                W0, b0 = enc0.Ws[0], enc0.bs[0]                    # (M, n, K), (M, 1, K)
                S0 = frames[0]['Sm12']
                Aeff = torch.einsum('ij,mjk->mik', S0, W0)        # x -> mu0 = (x - m0) S0 W0 + b0
                mu = b0.squeeze(1) - torch.einsum('j,mjk->mk', frames[0]['m'], Aeff)
                Sig = torch.einsum('mik,mil->mkl', Aeff, Aeff) + torch.eye(K, device=DEV)
                for i in range(m_ - 1):
                    T = getT(i)
                    Am = T.A * T.mask
                    mu = torch.einsum('mk,mkl->ml', mu, Am) + T.b.squeeze(1)
                    Sig = torch.einsum('mkl,mkp,mlq->mpq', Sig, Am, Am) + torch.eye(K, device=DEV)
                est_err = {}
                for N in [256, 4096, 65536]:
                    sob = torch.quasirandom.SobolEngine(K, scramble=True, seed=17)
                    u = sob.draw(N).to(DEV).clamp(1e-7, 1 - 1e-7)
                    z = torch.special.ndtri(u)
                    errs = []
                    for mi in range(M):
                        Lc = torch.linalg.cholesky(Sig[mi] + 1e-6 * torch.eye(K, device=DEV))
                        c = mu[mi] + z @ Lc.T
                        hh = frames[-1]['m'] + decs[-1](c.unsqueeze(0).expand(M, N, K))[mi] @ frames[-1]['S12']
                        est = net.run(hh, layers[-1]).double().mean(0)
                        errs.append(float(((est - Ea_true) ** 2).sum() / V))
                    est_err[str(N)] = errs
                res['deductive_err'] = est_err
            # MC and RQMC on the net with the same N (cost reference)
            ref = {}
            for N in [256, 4096, 65536]:
                gm = torch.Generator(device=DEV).manual_seed(555 + N)
                _, Am_ = net.sample(N, set(), gm)
                sob = torch.quasirandom.SobolEngine(n, scramble=True, seed=19)
                x = torch.special.ndtri(sob.draw(N).to(DEV).clamp(1e-7, 1 - 1e-7))
                ref[str(N)] = dict(mc=float(((Am_.double().mean(0) - Ea_true) ** 2).sum() / V),
                                   rqmc=float(((net.run(x, 0).double().mean(0) - Ea_true) ** 2).sum() / V))
            res['mc_rqmc'] = ref
        res['seconds'] = time.time() - t1
        json.dump(res, open(path, 'w'))
        print(f'{tag}: rate {[round(r, 1) for r in res["rate_c0"]]} | nMSE by layer ' +
              str([[round(v, 3) for v in x] for x in res['nmse']]) +
              (f' | deductive {res.get("deductive_err")}' if 'deductive_err' in res else '') + f' | {res["seconds"]:.0f}s',
              flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
