"""P2.0 part 5 (registered): phase-1 codes in the noisy nets (Model S of S4: h_k = relu(W_k h_{k-1}) + sigma xi_k for
hidden layers, a = relu(W_L h_{L-1})), scored with common random numbers: the decoded state runs through the real
future with the SAME future noise as the original (distortion E|F_l(h_hat, xi) - F_l(h, xi)|^2 / tr Var(a)). Local
class, the P1 method (lambda-conditioned code, analytic anchor from G = E[J^T J] of the noisy future, upward anneal,
per-lambda normalisation), 3 variable-rate restarts, at consecutive layers (16x16: 8-12; 32x32: 16-20). Saves the
models for the code-map analysis. usage: run_vr_noisy.py --configs 16x16 --seeds 5000 --layers 8,9 --out /root/runs/N
"""
import argparse
import json
import math
import os
import sys
import time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ap2 = argparse.ArgumentParser()
ap2.add_argument('--configs', default='16x16')
ap2.add_argument('--seeds', default='5000')
ap2.add_argument('--layers', required=True)
ap2.add_argument('--sigma', type=float, default=1.0)
ap2.add_argument('--steps', type=int, default=6000)
ap2.add_argument('--out', required=True)
a2 = ap2.parse_args()
os.makedirs(a2.out, exist_ok=True)
src = open(os.path.join(HERE, 'run_vr.py')).read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', a2.out, '--steps', str(a2.steps)]
G = {'__file__': os.path.join(HERE, 'run_vr.py'), '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, DT, VR, tof, inp, state, LOG2, GRID, summarise, args = (G['sn'], G['DEV'], G['DT'], G['VR'], G['tof'], G['inp'],
                                                               G['state'], G['LOG2'], G['GRID'], G['summarise'], G['args'])
SIG = a2.sigma
CH = 8192


class NNet(sn.Net):
    @torch.no_grad()
    def sample_noisy(self, P, layers, gen):
        h = torch.randn(P, self.n, generator=gen, device=DEV, dtype=DT)
        xi = torch.randn(self.L, P, self.n, generator=gen, device=DEV, dtype=DT)
        H = {}
        for k in range(self.L + 1):
            if k in layers:
                H[k] = h
            if k < self.L:
                h = torch.relu(h @ self.WT[k])
                if k + 1 < self.L:
                    h = h + SIG * xi[k]
        return H, h, xi

    def future(self, h, l, xi):
        for k in range(l, self.L):
            h = torch.relu(h @ self.WT[k])
            if k + 1 < self.L:
                h = h + SIG * xi[k]
        return h


def anchor_noisy(net, l, V, fr, H, xi, P=8192):
    xw = ((H[:P] - fr['m']) @ fr['Sm12']).detach().requires_grad_(True)
    a = net.future(fr['m'] + xw @ fr['S12'], l, xi[:, :P])
    Gm = torch.zeros(xw.shape[1], xw.shape[1], device=DEV, dtype=torch.float64)
    for j in range(a.shape[1]):
        gr, = torch.autograd.grad(a[:, j].sum(), xw, retain_graph=(j < a.shape[1] - 1))
        Gm += (gr.double().T @ gr.double()) / P
    ev, U = torch.linalg.eigh(Gm)
    return U.flip(1).detach(), ev.clamp(min=0).flip(0).detach(), V


for cfg in a2.configs.split(','):
    n, L = map(int, cfg.split('x'))
    for seed in map(int, a2.seeds.split(',')):
        net = NNet(seed, n, L)
        lays = [int(v) for v in a2.layers.split(',')]
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap, xip = net.sample_noisy(65536, set(lays), gp)
        V = float(Ap.double().var(0).sum())
        ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
        He, Ae, xie = net.sample_noisy(16384, set(lays), ge)
        for l in lays:
            tag = f'N_n{n}_L{L}_s{seed}_l{l}_local_sig{SIG:g}'
            path = os.path.join(a2.out, tag + '.json')
            if os.path.exists(path):
                continue
            t1 = time.time()
            fr = sn.frame(Hp[l])
            anchor = anchor_noisy(net, l, V, fr, Hp[l], xip)
            torch.manual_seed(77_000 + seed + l)
            M = 3
            m = VR(M, n, 'local', max(16, n), 256, 4, anchor, n)
            opt = torch.optim.Adam(m.parameters(), lr=1e-3, betas=(0.9, 0.99))
            S = a2.steps
            sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, S // 50)) * (
                0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * min(s, S) / S))))
            gt = torch.Generator(device=DEV).manual_seed(77_000 + seed * 7 + l)
            NB = 16
            ema = torch.zeros(M, NB, device=DEV)
            for step in range(S):
                Hb, Ab, xib = net.sample_noisy(2048, {l}, gt)
                x = inp(Hb[l], Ab, fr, None, 'local', M)
                ramp = min(1.0, step / max(1.0, 0.25 * S))
                t = -1.0 + ramp * 2.0 * torch.rand(M, 2048, 1, generator=gt, device=DEV)
                lam = 10.0 ** (2.0 * t - 2.0)
                zh, rate, _, _ = m(x, t, gt)
                ah = torch.stack([net.future(state(fr, zh[i]), l, xib) for i in range(M)])     # the same future noise
                d = ((ah - Ab) ** 2).sum(-1) / V
                lag = d + lam.squeeze(-1) * rate
                with torch.no_grad():
                    bi = ((t.squeeze(-1) + 1.0) * 0.5 * NB).long().clamp(0, NB - 1)
                    tot = torch.zeros(M, NB, device=DEV).scatter_add_(1, bi, lag)
                    cnt = torch.zeros(M, NB, device=DEV).scatter_add_(1, bi, torch.ones_like(lag))
                    mb = tot / cnt.clamp(min=1)
                    upd = cnt > 0
                    ema = torch.where(upd & (ema == 0), mb, torch.where(upd, 0.95 * ema + 0.05 * mb, ema))
                    wgt = 1.0 / ema.gather(1, bi).clamp(min=1e-6)
                loss = (lag * wgt).mean(-1).sum()
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(m.parameters(), 100.0)
                opt.step()
                sched.step()
            out = dict(rate=[], nmse=[])
            with torch.no_grad():
                xe = inp(He[l], Ae, fr, None, 'local', M)
                for lamv in GRID:
                    g = torch.Generator(device=DEV).manual_seed(88_000 + seed)
                    tt = torch.full((M, xe.shape[1], 1), tof(lamv), device=DEV)
                    zh, rate, _, _ = m(xe, tt, g)
                    ah = torch.stack([net.future(state(fr, zh[i]), l, xie) for i in range(M)])
                    out['nmse'].append((((ah - Ae) ** 2).sum(-1).mean(-1) / V).tolist())
                    out['rate'].append(rate.mean(1).tolist())
            curves = {f'r{i}': dict(rate=[q[i] for q in out['rate']], nmse=[q[i] for q in out['nmse']]) for i in range(M)}
            res = dict(n=n, L=L, seed=seed, l=l, cls='local', sigma=SIG, V=V, grid=GRID, curves=curves,
                       summary={k: dict(zip(('cross', 'slope'), summarise(c['rate'], c['nmse']))) for k, c in curves.items()},
                       seconds=time.time() - t1)
            json.dump(res, open(path, 'w'))
            torch.save(m.state_dict(), path.replace('.json', '.pt'))
            print(tag, f'{res["seconds"]:.0f}s', {k: (v['cross']['0.1'], v['cross']['0.01']) for k, v in res['summary'].items()},
                  flush=True)
print('ALL DONE', flush=True)
