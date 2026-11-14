"""P2.0 part 5 analysis (amendment P2.0-b; written and hashed before it reads runs/N): do the code maps in the noisy
nets settle to one shared map with depth? For each noisy net (16x16 layers 8-13, 32x32 layers 16-21; seeds 5000-5002),
codes (model r0, lambda = 0.01) at the 6 consecutive layers on 16384 held-out inputs with their own noise; T_l = affine
and MLP maps from the code at l to the code at l+1 (fitted on half A); transfer: T_l applied at l+k after orthogonal
Procrustes alignment (fitted on half A) of the code at l+k onto the code at l and of the code at l+k+1 onto the code at
l+1, scored on half B (R^2). H5: T fitted at l scores R^2 >= 0.8 at l+4 on the noisy 32x32 nets for l >= L/2 (MLP T;
the affine T is reported too). usage: python scratch/p2_noisy_maps.py -> results/P2_noisy_maps.json"""
import json
import math
import os
import sys

import numpy as np
import torch

W = '/home/agent/workspaces/mats/work/bit-accounting'
src = open(f'{W}/gpu_src/scripts/run_vr.py').read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', '/tmp/p2_unused', '--threads', '2']
G = {'__file__': f'{W}/gpu_src/scripts/run_vr.py', '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, DT, VR, tof, inp = G['sn'], G['DEV'], G['DT'], G['VR'], G['tof'], G['inp']
torch.set_num_threads(2)
SIG = 1.0


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


def r2(pred, y):
    return float(1.0 - ((y - pred) ** 2).sum() / ((y - y.mean(0)) ** 2).sum().clamp(min=1e-30))


def affine(X, Y, nA):
    A = torch.cat([X, torch.ones(X.shape[0], 1, dtype=X.dtype)], 1)
    coef = torch.linalg.lstsq(A[:nA], Y[:nA]).solution
    return lambda Z: torch.cat([Z, torch.ones(Z.shape[0], 1, dtype=Z.dtype)], 1) @ coef


def mlp(X, Y, nA, seed=0, steps=1500):
    torch.manual_seed(seed)
    mx, sx = X[:nA].mean(0), X[:nA].std(0).clamp(min=1e-6)
    my, sy = Y[:nA].mean(0), Y[:nA].std(0).clamp(min=1e-6)
    net = torch.nn.Sequential(torch.nn.Linear(X.shape[1], 128), torch.nn.GELU(), torch.nn.Linear(128, 128), torch.nn.GELU(),
                              torch.nn.Linear(128, Y.shape[1]))
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    g = torch.Generator().manual_seed(seed)
    Xn, Yn = ((X - mx) / sx).float(), ((Y - my) / sy).float()
    for _ in range(steps):
        idx = torch.randint(0, nA, (1024,), generator=g)
        loss = ((net(Xn[idx]) - Yn[idx]) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return lambda Z: (net(((Z - mx) / sx).float()).double() * sy + my)


def procrustes(Xsrc, Xdst, nA):
    """Orthogonal R minimising |(Xsrc - mean) R - (Xdst - mean)| on half A; returns a function on new data."""
    ms, md = Xsrc[:nA].mean(0), Xdst[:nA].mean(0)
    Uu, _, Vh = torch.linalg.svd((Xsrc[:nA] - ms).T @ (Xdst[:nA] - md))
    R = Uu @ Vh
    return lambda Z: (Z - ms) @ R + md


out = {}
for n, L, lays in ((16, 16, list(range(8, 14))), (32, 32, list(range(16, 22)))):
    for seed in (5000, 5001, 5002):
        files = [f'{W}/runs/N/N_n{n}_L{L}_s{seed}_l{l}_local_sig1' for l in lays]
        if not all(os.path.exists(f + '.pt') for f in files):
            continue
        net = NNet(seed, n, L)
        gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
        Hp, Ap, xip = net.sample_noisy(65536, set(lays), gp)
        V = float(Ap.double().var(0).sum())
        ge = torch.Generator(device=DEV).manual_seed(70_000 + seed)
        He, Ae, xie = net.sample_noisy(16384, set(lays), ge)
        nA = 8192
        Y = {}
        for l, f in zip(lays, files):
            fr = sn.frame(Hp[l])
            K = max(16, n)
            anchor = (torch.eye(n, dtype=torch.float64), torch.ones(n, dtype=torch.float64), V)
            sd = torch.load(f + '.pt', map_location=DEV)
            sd = {k: (v[0:1] if v.dim() > 0 and v.shape[0] == 3 else v) for k, v in sd.items()}
            m = VR(1, n, 'local', K, 256, 4, anchor, n)
            m.load_state_dict(sd)
            m.V = V
            with torch.no_grad():
                x = inp(He[l], Ae, fr, None, 'local', 1)
                t = torch.full((1, x.shape[1], 1), tof(0.01), device=DEV)
                Y[l] = m.encode(x, t)[0].double()
        res = {}
        for i, l in enumerate(lays[:-1]):
            X0, X1 = Y[l], Y[lays[i + 1]]
            Ta, Tm = affine(X0, X1, nA), mlp(X0, X1, nA, seed=seed + l)
            ent = dict(r2_affine=r2(Ta(X0)[nA:], X1[nA:]), r2_mlp=r2(Tm(X0)[nA:], X1[nA:]), transfer={})
            for k in range(1, len(lays) - 1 - i):
                lk, lk1 = lays[i + k], lays[i + k + 1]
                Pa, Pb = procrustes(Y[lk], X0, nA), procrustes(Y[lk1], X1, nA)
                src_, tgt = Pa(Y[lk]), Pb(Y[lk1])
                ent['transfer'][str(k)] = dict(affine=r2(Ta(src_)[nA:], tgt[nA:]), mlp=r2(Tm(src_)[nA:], tgt[nA:]),
                                               own_affine=r2(affine(Y[lk], Y[lk1], nA)(Y[lk])[nA:], Y[lk1][nA:]))
            res[str(l)] = ent
        out[f'n{n}_L{L}_s{seed}'] = res
        print(f'n{n}_L{L}_s{seed}', {l: (round(e['r2_affine'], 3), {k: round(v['mlp'], 3) for k, v in e['transfer'].items()})
                                     for l, e in res.items()}, flush=True)
        json.dump(out, open(f'{W}/results/P2_noisy_maps.json', 'w'), indent=1)
h5 = [e['transfer']['4']['mlp'] >= 0.8 for key, r in out.items() if key.startswith('n32') for l, e in r.items()
      if int(l) >= 16 and '4' in e['transfer']]
print('H5:', f'{sum(h5)}/{len(h5)}', 'hit' if h5 and all(h5) else 'missed')
json.dump(dict(H5=dict(count=f'{sum(h5)}/{len(h5)}', hit=bool(h5) and all(h5))), open(f'{W}/results/P2_noisy_scores.json', 'w'))
