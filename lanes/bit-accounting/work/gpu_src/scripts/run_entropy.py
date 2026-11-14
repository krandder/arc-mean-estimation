"""Part S7 (primary from 2 Nov 02:00Z, Kelvin's decision): the encoder decides how many bits to use. Loss =
forward-propagated distortion + lambda * rate; the average number of bits actually used is the count.
Per (net, layer, class) cell, models for lambda in LAMBDAS trained side by side (M = len(LAMBDAS)):
  ent   (Balle et al. 2017) latents y in R^K; training: y + U(-1/2, 1/2); test: round(y) (integer codes). Rate =
        -log2 P(round(y)) under a learned factorised prior (per latent a mixture of 3 logistics, the probability of the
        unit bin). Count = mean bits per sample on held-out inputs; the per-sample distribution of bits is kept.
  vib   Gaussian noise: z = mu(h) + sigma(h) eps; rate = KL(N(mu, sigma^2) || N(0, I)) in bits (an upper bound on
        I(h; z)); distortion with a sampled z.
Checks: a fresh factorised prior refitted on held-out integer codes (half A) and evaluated on half B (the rate should
barely drop); the plug-in entropy of the joint integer code where the code space is small; the centroid decoder
(per-code mean output) on integer codes.
usage: run_entropy.py --configs 16x16 --seeds 5000 --out /root/runs/S_ent
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
ap.add_argument('--lambdas', default='1,0.3,0.1,0.03,0.01,0.003,0.001')
ap.add_argument('--K', type=int, default=16)
ap.add_argument('--steps', type=int, default=2000)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--width', type=int, default=256)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--tag', default='')
ap.add_argument('--kinds', default='gfix,bern,ent,vib')
ap.add_argument('--netkind', default='relu')
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
LAMS = [float(v) for v in args.lambdas.split(',')]
KINDS = args.kinds.split(',')
M, K = len(LAMS), args.K
LOG2 = math.log(2.0)
T0 = time.time()


class Prior(nn.Module):
    """Factorised prior: per (model, latent) a mixture of 3 logistics; probability of the unit bin around x."""

    def __init__(self):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(M, 1, K, 3, device=DEV) * 0.5)
        self.ls = nn.Parameter(torch.zeros(M, 1, K, 3, device=DEV))
        self.lw = nn.Parameter(torch.zeros(M, 1, K, 3, device=DEV))

    def bits(self, x):
        """x (M, B, K) -> -log2 P(bin of x), (M, B, K)."""
        s = torch.exp(self.ls).clamp(min=1e-3)
        xe = x.unsqueeze(-1)
        up = torch.sigmoid((xe + 0.5 - self.mu) / s)
        lo = torch.sigmoid((xe - 0.5 - self.mu) / s)
        w = torch.softmax(self.lw, -1)
        p = (w * (up - lo)).sum(-1).clamp(min=1e-9)
        return -torch.log2(p)


class GPrior(nn.Module):
    """Per (model, latent) mixture of 3 Gaussians; log2 density."""

    def __init__(self):
        super().__init__()
        self.mu = nn.Parameter(torch.randn(M, 1, K, 3, device=DEV))
        self.ls = nn.Parameter(torch.full((M, 1, K, 3), 0.7, device=DEV))
        self.lw = nn.Parameter(torch.zeros(M, 1, K, 3, device=DEV))

    def log2p(self, z):
        ze = z.unsqueeze(-1)
        s = torch.exp(self.ls).clamp(min=1e-2)
        lp = -0.5 * ((ze - self.mu) / s) ** 2 - torch.log(s) - 0.5 * math.log(2 * math.pi)
        lw = torch.log_softmax(self.lw, -1)
        return torch.logsumexp(lp + lw, -1) / LOG2


def hbits(p):
    p = p.clamp(1e-6, 1 - 1e-6)
    return -(p * torch.log2(p) + (1 - p) * torch.log2(1 - p))


class Arm(nn.Module):
    def __init__(self, n, cls, fr, fr_a, h_star_w, kind):
        super().__init__()
        self.cls, self.fr, self.fr_a, self.kind = cls, fr, fr_a, kind
        d_in = n if cls == 'local' else 2 * n
        d_out = 2 * K if kind == 'vib' else K
        self.enc = (sn.BMLP(M, d_in, d_out, n, 1, act='relu') if cls == 'local' else sn.BMLP(M, d_in, d_out, args.width, 3))
        self.dec = sn.BMLP(M, K, n, args.width, 3, last_scale=0.0)
        with torch.no_grad():
            self.dec.bs[-1].copy_(h_star_w.view(1, 1, n).expand(M, 1, n))
        self.prior = Prior() if kind == 'ent' else (GPrior() if kind == 'gfix' else None)

    def inp(self, h, a):
        x = (h - self.fr['m']) @ self.fr['Sm12']
        if self.cls == 'unres':
            x = torch.cat([x, (a - self.fr_a['m']) @ self.fr_a['Sm12']], -1)
        return x.unsqueeze(0).expand(M, *x.shape)

    def forward(self, h, a, g, train=True):
        y = self.enc(self.inp(h, a))
        if self.kind == 'ent':
            yq = y + (torch.rand(y.shape, generator=g, device=DEV) - 0.5) if train else torch.round(y)
            rate = self.prior.bits(yq).sum(-1)                                  # (M, B) bits
            return self.dec(yq), rate, yq
        if self.kind == 'gfix':
            z = y + torch.randn(y.shape, generator=g, device=DEV)            # fixed unit noise, encoder-chosen scale
            logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
            rate = (logq - self.prior.log2p(z)).sum(-1)                     # MC estimate of KL(q || p), bits
            return self.dec(z), rate, z
        if self.kind == 'bern':
            pr = torch.sigmoid(y)
            if train:
                u = torch.rand(y.shape, generator=g, device=DEV).clamp(1e-6, 1 - 1e-6)
                soft = torch.sigmoid((y + torch.log(u) - torch.log1p(-u)) / 0.5)
                hard = (soft > 0.5).to(DT)
                b = hard + soft - soft.detach()
            else:
                b = (torch.rand(y.shape, generator=g, device=DEV) < pr).to(DT)
            pbar = pr.mean(1, keepdim=True)
            info = (hbits(pbar) - hbits(pr).mean(1, keepdim=True)).sum(-1)  # (M, 1): sum_j I(h; b_j) estimate
            return self.dec(2 * b - 1), info.expand(-1, y.shape[1]), pr
        mu, ls = y[..., :K], y[..., K:].clamp(-8, 4)
        sig = torch.exp(ls)
        z = mu + sig * torch.randn(mu.shape, generator=g, device=DEV)
        kl = 0.5 * (mu ** 2 + sig ** 2 - 1.0 - 2.0 * ls).sum(-1) / LOG2   # bits
        return self.dec(z), kl, z


def refit_prior(codes_A, codes_B, steps=600):
    """Fresh factorised prior fitted on integer codes A (M, NA, K), mean bits per sample on B."""
    pr = Prior()
    opt = torch.optim.Adam(pr.parameters(), lr=0.05)
    for _ in range(steps):
        loss = pr.bits(codes_A).sum(-1).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        return pr.bits(codes_B).sum(-1).mean(1).tolist()


def joint_plugin(codes, maxk=1 << 18):
    """Plug-in entropy (bits) of the joint integer code per model, fitted on half A, cross-entropy on half B with
    unseen codes counted at log2 of the code count + 1 (an upper estimate); None if too many distinct codes."""
    out = []
    for mi in range(codes.shape[0]):
        c = codes[mi].long()
        h = c.shape[0] // 2
        keyA = [tuple(r) for r in c[:h].tolist()]
        keyB = [tuple(r) for r in c[h:].tolist()]
        from collections import Counter
        cnt = Counter(keyA)
        if len(cnt) > maxk:
            out.append(None)
            continue
        tot = sum(cnt.values())
        unseen_bits = math.log2(tot + 1) + 8.0
        bits = [(-math.log2(cnt[k] / tot) if k in cnt else unseen_bits) for k in keyB]
        out.append(float(np.mean(bits)))
    return out


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = sn.Net(seed, n, L, kind=args.netkind)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap = net.sample(65536, set(layers), gp)
        Hp[L] = Ap
        V = float(Ap.double().var(0).sum())
        fr_a = sn.frame(Ap)
        ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
        He, Ae = net.sample(args.P_eval, set(layers), ge)
        He[L] = Ae
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        for l in layers + [L]:
            fr = sn.frame(Hp[l]) if l < L else fr_a
            h_star_w = (Hp[l][i_star] - fr['m']) @ fr['Sm12']
            for cls in (args.classes.split(',') if l < L else ['unres']):
                tag = f'E_n{n}_L{L}_s{seed}_l{l}_{cls}{args.tag}'
                path = os.path.join(args.out, tag + '.json')
                if os.path.exists(path):
                    continue
                t1 = time.time()
                arms = [Arm(n, cls, fr, fr_a, h_star_w, kind) for kind in KINDS]
                lam = torch.tensor(LAMS, device=DEV)
                params = [p for a in arms for p in a.parameters()]
                opt = torch.optim.Adam(params, lr=1e-3)
                warm = max(1, args.steps // 50)
                sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
                    0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
                gt = torch.Generator(device=DEV).manual_seed(77_000 + seed * 7 + n * 13 + L * 101 + l * 3 +
                                                               (0 if cls == "local" else 1) + sum(map(ord, args.tag)))
                for step in range(args.steps):
                    Hb, Ab = net.sample(args.batch, {l}, gt)
                    hb = Ab if l == L else Hb[l]
                    loss = 0.0
                    for arm in arms:
                        zh, rate, _ = arm(hb, Ab, gt, train=True)
                        ah = net.run(fr['m'] + zh @ fr['S12'], l)
                        dist = ((ah - Ab) ** 2).sum(-1).mean(-1) / V
                        loss = loss + (dist + lam * rate.mean(-1)).sum()
                    opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(params, 10.0)
                    opt.step()
                    sched.step()
                res = dict(n=n, L=L, seed=seed, l=l, cls=cls, V=V, lambdas=LAMS, K=K, steps=args.steps, curves={})
                gev = torch.Generator(device=DEV).manual_seed(88_000 + seed)
                for arm in arms:
                    arm.eval()
                    with torch.no_grad():
                        zh, rate, codes = arm(He[l], Ae, gev, train=False)
                        ah = net.run(fr['m'] + zh @ fr['S12'], l)
                        d = (ah - Ae).double()
                        nm = ((d * d).sum(-1).mean(-1) / V).tolist()
                        md = d.mean(1)
                        mean_err = ((md * md).sum(-1) / V).tolist()
                        rb = rate.double()
                        cur = dict(nmse=nm, rate=rb.mean(1).tolist(), mean_err=mean_err,
                                   rate_q=[torch.quantile(rb[mi].float(), torch.tensor([0.1, 0.5, 0.9], device=DEV)).tolist()
                                           for mi in range(M)])
                    half = args.P_eval // 2
                    if arm.kind == 'gfix':
                        zA, zB = codes[:, :half].detach(), codes[:, half:].detach()
                        mu_e = arm.enc(arm.inp(He[l], Ae)).detach()
                        gp2 = GPrior()
                        o2 = torch.optim.Adam(gp2.parameters(), lr=0.05)
                        for _ in range(600):
                            lo = -gp2.log2p(zA).sum(-1).mean()
                            o2.zero_grad()
                            lo.backward()
                            o2.step()
                        with torch.no_grad():
                            logqB = (-0.5 * (zB - mu_e[:, half:]) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
                            cur['rate_refit'] = (logqB - gp2.log2p(zB)).sum(-1).mean(1).tolist()
                            cur['scale'] = mu_e.std(1).mean(-1).tolist()
                    if arm.kind == 'bern':
                        pr = codes.detach()
                        pbar = pr.mean(1)
                        info_j = (hbits(pbar) - hbits(pr).mean(1))                  # (M, K)
                        cur['bit_info'] = info_j.tolist()
                        cur['bits_half'] = ((pr - 0.5).abs() < 0.05).float().mean(1).tolist()  # per bit: share of samples with p ~ 0.5
                        cur['bits_det'] = ((pr < 0.05) | (pr > 0.95)).float().mean(1).tolist()
                    if arm.kind == 'ent':
                        cur['rate_refit'] = refit_prior(codes[:, :half].detach(), codes[:, half:].detach())
                        cur['joint_plugin'] = joint_plugin(codes.detach().cpu())
                        cur['active_latents'] = [int((codes[mi].abs().amax(0) > 0).sum()) for mi in range(M)]
                        # centroid decoder on integer codes (per distinct code mean output, fitted on half A)
                        cent = []
                        for mi in range(M):
                            c = codes[mi].long()
                            keys = torch.unique(c, dim=0, return_inverse=True)[1]
                            nk = int(keys.max()) + 1
                            kA, kB = keys[:half], keys[half:]
                            s = torch.zeros(nk, n, device=DEV, dtype=torch.float64).index_add_(0, kA, Ae[:half].double())
                            cn = torch.bincount(kA, minlength=nk).double()
                            seen = cn[kB] > 0
                            pred = torch.where(seen[:, None], s[kB] / cn[kB].clamp(min=1)[:, None], ah[mi][half:].double())
                            cent.append(float(((pred - Ae[half:].double()) ** 2).sum(-1).mean() / V))
                        cur['centroid_nmse_halfB'] = cent
                        cur['model_nmse_halfB'] = (((ah[:, half:] - Ae[half:]).double() ** 2).sum(-1).mean(-1) / V).tolist()
                    res['curves'][arm.kind] = cur
                res['seconds'] = time.time() - t1
                json.dump(res, open(path, 'w'))
                torch.save({kk: a.state_dict() for kk, a in zip(KINDS, arms)}, path.replace('.json', '.pt'))
                print(f'{tag}: {res["seconds"]:.0f}s | ' + ' | '.join(
                    f'{kd} (rate, nMSE) ' + ' '.join(f'({r:.1f},{e:.3f})' for r, e in zip(res['curves'][kd]['rate'],
                                                                                    res['curves'][kd]['nmse']))
                    for kd in KINDS[:2]) + f' | total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
