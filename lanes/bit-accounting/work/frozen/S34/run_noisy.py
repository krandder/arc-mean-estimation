"""Part S4, the noisy regime with common random numbers (Kelvin, relayed 23:4xZ): Model S nets h_0 = x ~ N(0, I_n),
h_k = relu(W_k h_{k-1}) + sigma xi_k (k < L), a = relu(W_L h_{L-1}). The decoded state h_hat_l is propagated through
the real future with the SAME future noise as h_l (common random numbers), so the encoding error is separated from the
future's own noise.
Scores (strongest to weakest; each relative to V = tr Var(a)):
  crn    E|F_l(h_hat, Xi) - F_l(h_l, Xi)|^2 (per-sample output match under the shared noise; the training loss);
  dist   Gaussian 2-Wasserstein (Gelbrich) distance^2 between the law of F_l(h_hat, Xi) and the law of a;
  mean   |E F_l(h_hat, Xi) - E a|^2.
  avg    E[(F(h_hat, Xi) - F(h, Xi)) . (F(h_hat, Xi') - F(h, Xi'))] with independent Xi, Xi': |g(h_hat) - g(h)|^2, the
         noise-averaged distortion (where the compute-the-answer shortcut works), for comparison.
mean <= dist <= crn (Gelbrich bound and coupling) and avg <= crn (Jensen) hold exactly; they are checked.
Encoders: 'local' (one ReLU layer of width n) and 'unres' (MLP on h_l and an R = 8 noise-draw average of the future
output, i.e. it can compute E[a | h_l] but cannot see the future noise). Decoder, bottlenecks, rates as run_curves.py.
usage: run_noisy.py --configs 16x16 --seeds 5000 --sigma 1 --out /root/runs/S_noisy
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import smallnets as sn  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--configs', default='16x16')
ap.add_argument('--seeds', default='9100')
ap.add_argument('--classes', default='local,unres')
ap.add_argument('--sigma', type=float, default=1.0)
ap.add_argument('--rates', default='1,2,3,4,6,8,12,16,24,32')
ap.add_argument('--steps', type=int, default=1500)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--R', type=int, default=8)
ap.add_argument('--P_pilot', type=int, default=65536)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--threads', type=int, default=2)
ap.add_argument('--out', required=True)
args = ap.parse_args()
torch.set_num_threads(args.threads)
os.makedirs(args.out, exist_ok=True)
DEV, DT = sn.DEV, sn.DT
rates = [float(r) for r in args.rates.split(',')]
EPS = [0.1, 0.01, 0.001]
SIG = args.sigma
T0 = time.time()


class NoisyNet(sn.Net):
    @torch.no_grad()
    def sample_noisy(self, P, layers, gen):
        x = torch.randn(P, self.n, generator=gen, device=DEV, dtype=DT)
        xi = torch.randn(self.L, P, self.n, generator=gen, device=DEV, dtype=DT)    # xi[k-1] used at layer k < L
        H = {}
        h = x
        for k in range(self.L + 1):
            if k in layers:
                H[k] = h
            if k < self.L:
                h = torch.relu(h @ self.WT[k])
                if k + 1 < self.L:
                    h = h + SIG * xi[k]
        return H, h, xi

    def future(self, h, l, xi):
        """Layers l+1..L from state h with the given noise (xi[k-1] at hidden layer k)."""
        for k in range(l, self.L):
            h = torch.relu(h @ self.WT[k])
            if k + 1 < self.L:
                h = h + SIG * xi[k]
        return h

    @torch.no_grad()
    def g_hat(self, h, l, R, gen):
        acc = 0.0
        for _ in range(R):
            xi = torch.randn(self.L, *h.shape, generator=gen, device=DEV, dtype=DT)
            acc = acc + self.future(h, l, xi)
        return acc / R


def gelbrich(X, Y):
    """Gaussian (Gelbrich) W2^2 between the laws of the rows of X and Y (float64)."""
    mx, my = X.mean(0), Y.mean(0)
    Sx = torch.cov(X.T)
    Sy = torch.cov(Y.T)
    w, U = torch.linalg.eigh(Sx)
    Sx12 = (U * w.clamp(min=0).sqrt()) @ U.T
    Mx = Sx12 @ Sy @ Sx12
    w2 = torch.linalg.eigvalsh((Mx + Mx.T) / 2).clamp(min=0).sqrt().sum()
    return float(((mx - my) ** 2).sum() + torch.trace(Sx) + torch.trace(Sy) - 2 * w2)


def layer_grid(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


for cfg in args.configs.split(','):
    n, L = [int(v) for v in cfg.split('x')]
    for seed in [int(s) for s in args.seeds.split(',')]:
        net = NoisyNet(seed, n, L)
        layers = layer_grid(L)
        gp = torch.Generator(device=DEV).manual_seed(11_000 + seed * 7 + n * 13 + L)
        Hp, Ap, _ = net.sample_noisy(args.P_pilot, set(layers), gp)
        Hp[L] = Ap
        V = float(Ap.double().var(0).sum())
        fr_a = sn.frame(Ap)
        ge = torch.Generator(device=DEV).manual_seed(21_000 + seed * 7 + n * 13 + L)
        He, Ae, Xe = net.sample_noisy(args.P_eval, set(layers), ge)
        He[L] = Ae
        Ve = float(Ae.double().var(0).sum())
        i_star = int(((Ap - Ap.mean(0)) ** 2).sum(1).argmin())
        # memory share M_l = tr Var E[a | h_l] / V by pick-freeze (two independent future noises)
        gm = torch.Generator(device=DEV).manual_seed(31_000 + seed)
        mem = {}
        for l in layers:
            hh = He[l][:16384]
            a1 = net.future(hh, l, torch.randn(L, *hh.shape, generator=gm, device=DEV, dtype=DT)).double()
            a2 = net.future(hh, l, torch.randn(L, *hh.shape, generator=gm, device=DEV, dtype=DT)).double()
            mu = 0.5 * (a1.mean(0) + a2.mean(0))
            mem[str(l)] = float(((a1 - mu) * (a2 - mu)).sum(1).mean() / Ve)
        for l in layers + [L]:
            fr = sn.frame(Hp[l]) if l < L else fr_a
            h_star_w = (Hp[l][i_star] - fr['m']) @ fr['Sm12']
            classes = args.classes.split(',') if l < L else ['unres']
            for cls in classes:
                tag = f'N_n{n}_L{L}_s{seed}_l{l}_{cls}'
                path = os.path.join(args.out, tag + '.json')
                if os.path.exists(path):
                    continue
                t1 = time.time()
                gg = torch.Generator(device=DEV).manual_seed(41_000 + seed + l)
                if cls == 'unres' and l < L:
                    # frame for the encoder's extra input (the R-draw average of the future output)
                    gfr = sn.frame(net.g_hat(Hp[l][:16384], l, args.R, gg))
                else:
                    gfr = fr_a
                models = [sn.Bottlenecks(n, kind, cls, rates, fr, gfr, h_star_w) for kind in ('bin', 'gauss')]
                params = [p for m in models for p in m.parameters()]
                opt = torch.optim.Adam(params, lr=args.lr)
                warm = max(1, args.steps // 50)
                sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warm) * (
                    0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps))))
                gt = torch.Generator(device=DEV).manual_seed(51_000 + seed * 7 + n * 13 + L * 101 + l * 3
                                                               + (0 if cls == 'local' else 1))
                for step in range(args.steps):
                    Hb, Ab, Xb = net.sample_noisy(args.batch, {l}, gt)
                    hb = Ab if l == L else Hb[l]
                    side = (net.g_hat(hb, l, args.R, gt) if (cls == 'unres' and l < L) else Ab)
                    loss = 0.0
                    for m in models:
                        ah = net.future(m(hb, side, gt), l, Xb)              # the same future noise as a
                        loss = loss + (((ah - Ab) ** 2).sum(-1).mean(-1) / V).sum()
                    opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(params, 10.0)
                    opt.step()
                    sched.step()
                res = dict(n=n, L=L, seed=seed, l=l, cls=cls, sigma=SIG, V=V, V_eval=Ve, memory_share=mem,
                           rates=rates, curves={})
                gev = torch.Generator(device=DEV).manual_seed(61_000 + seed)
                for m in models:
                    m.eval()
                    with torch.no_grad():
                        crn, avg, D, OUT = [], [], [], []
                        for c0 in range(0, args.P_eval, 8192):
                            hb = He[l][c0:c0 + 8192]
                            ab = Ae[c0:c0 + 8192]
                            xb = Xe[:, c0:c0 + 8192]
                            side = net.g_hat(hb, l, args.R, gev) if (cls == 'unres' and l < L) else ab
                            hh = m(hb, side, gev)                             # (M, B, n)
                            o1 = net.future(hh, l, xb).double()
                            d = o1 - ab.double()
                            crn.append((d * d).sum(-1))
                            D.append(d)
                            OUT.append(o1)
                            if l < L:
                                xi2 = torch.randn(L, *hb.shape, generator=gev, device=DEV, dtype=DT)
                                d2 = net.future(hh, l, xi2).double() - net.future(hb, l, xi2).double()
                                avg.append((d * d2).sum(-1))
                        crn = torch.cat(crn, 1) / Ve
                        D = torch.cat(D, 1)
                        OUT = torch.cat(OUT, 1)
                        md = D.mean(1)
                        mean_err = (md * md).sum(-1) / Ve
                        floor = D.var(1).sum(-1) / args.P_eval / Ve
                        dist = [gelbrich(OUT[i], Ae.double()) / Ve for i in range(m.M)]
                        avgv = (torch.cat(avg, 1).mean(1) / Ve).tolist() if avg else crn.mean(1).tolist()
                    cur = dict(rate=rates, crn=crn.mean(1).tolist(), crn_se=(crn.std(1) / math.sqrt(args.P_eval)).tolist(),
                               dist=dist, mean_err=mean_err.tolist(), mean_floor=floor.tolist(), avg=avgv)
                    cur['cross_crn'] = {str(e): sn.crossing(rates, cur['crn'], e) for e in EPS}
                    cur['cross_dist'] = {str(e): sn.crossing(rates, cur['dist'], e) for e in EPS}
                    cur['cross_avg'] = {str(e): sn.crossing(rates, [max(v, 1e-12) for v in cur['avg']], e) for e in EPS}
                    res['curves'][m.kind] = cur
                res['seconds'] = time.time() - t1
                with open(path, 'w') as f:
                    json.dump(res, f)
                cg = res['curves']['gauss']
                print(f'{tag}: {res["seconds"]:.0f}s | M_l {mem.get(str(l), 1.0):.3f} | gauss crn ' +
                      ' '.join(f'{v:.3g}' for v in cg['crn']) + ' | avg ' + ' '.join(f'{v:.3g}' for v in cg['avg']) +
                      f' | C_crn {cg["cross_crn"]} C_avg {cg["cross_avg"]} | total {time.time() - T0:.0f}s', flush=True)
print('ALL DONE', f'{time.time() - T0:.0f}s', flush=True)
