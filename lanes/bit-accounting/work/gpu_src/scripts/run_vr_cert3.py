"""Phase 2 (c), amendment P1-B: more exploration of the local class at the early layers and on the controls. For each
listed P1 local cell: 6 explorer restarts (local encoders whose ReLU gates start inside the data cloud): x0 = the net's
own next-layer gates, x1-x2 jitter 0.1, x3-x4 jitter 0.3, x5 random unit-variance gates (relu/tanh4/linear nets; all
random for feistel); output layers fitted by least squares on pilot samples to the anchor's unit-scale code; analytic
gains, decoder and prior as in P1; 6000 steps. Plus 2 explorer restarts (exact gates, jitter 0.1) trained 12000 steps
(xl0, xl1). Evaluation on the P1 lambda grid; gate activity. Output <out>/Y_<cell>.json.
usage: run_vr_cert3.py --runs /root/runs/P1 --cells <list file> --out /root/runs/P1Y"""
import argparse
import json
import math
import os
import sys
import time

import torch

HERE = os.path.dirname(os.path.abspath(__file__))
ap2 = argparse.ArgumentParser()
ap2.add_argument('--runs', required=True)
ap2.add_argument('--cells', required=True)
ap2.add_argument('--out', required=True)
ap2.add_argument('--steps', type=int, default=6000)
a2 = ap2.parse_args()
os.makedirs(a2.out, exist_ok=True)
src = open(os.path.join(HERE, 'run_vr.py')).read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', a2.out, '--steps', str(a2.steps)]
G = {'__file__': os.path.join(HERE, 'run_vr.py'), '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, args, VR, train, inp, evaluate, linref, summarise, GRID, tof = (G['sn'], G['DEV'], G['args'], G['VR'], G['train'],
                                                                         G['inp'], G['evaluate'], G['linref'], G['summarise'],
                                                                         G['GRID'], G['tof'])


def gate_activity(model, mi, x, lam):
    M = model.enc.Ws[0].shape[0]
    with torch.no_grad():
        t = torch.full((M, x.shape[0], 1), tof(lam), device=DEV)
        f = model.enc.film(t)
        w = model.enc.width
        pre = (1.0 + f[..., :w]) * torch.baddbmm(model.enc.bs[0], x.unsqueeze(0).expand(M, -1, -1), model.enc.Ws[0]) + f[..., w:2 * w]
        act = (pre[mi] > 0).float().mean(0)
    return float(((act > 0.05) & (act < 0.95)).float().mean())


def init_gates(model, net, l, fr, xp, U, kind, n, seed, specs):
    """specs: list of (mode, jitter) per restart; mode 'next' = next-layer gates, 'random' = random gates."""
    g = torch.Generator(device=DEV).manual_seed(777 + seed + 7 * l)
    with torch.no_grad():
        S12, m = fr['S12'], fr['m']
        target = xp @ U.float()
        for mi, (mode, jit) in enumerate(specs):
            if mode == 'next' and kind in ('relu', 'tanh4', 'linear'):
                W1 = S12 @ net.WT[l]
                b1 = m @ net.WT[l]
            else:
                W1 = torch.randn(n, n, generator=g, device=DEV) / math.sqrt(n)
                b1 = torch.zeros(n, device=DEV)
            sc = W1.std() + 1e-8
            Wj = W1 + jit * sc * torch.randn(W1.shape, generator=g, device=DEV)
            u = torch.relu(xp @ Wj + b1)
            A = torch.cat([u, torch.ones(u.shape[0], 1, device=DEV)], 1)
            sol = torch.linalg.lstsq(A.double().cpu(), target.double().cpu()).solution.float().to(DEV)
            model.enc.Ws[0][mi].copy_(Wj)
            model.enc.bs[0][mi].copy_(b1.view(1, -1))
            model.enc.Ws[1][mi].copy_(sol[:-1])
            model.enc.bs[1][mi].copy_(sol[-1:].view(1, -1))


for name in [ln.strip() for ln in open(a2.cells) if ln.strip()]:
    outp = os.path.join(a2.out, 'Y_' + name[2:] + '.json')
    if os.path.exists(outp):
        continue
    d = json.load(open(os.path.join(a2.runs, name + '.json')))
    kind, n, L, seed, l, cls = d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls']
    G['SQUASH'] = (kind == 'feistel')
    t1 = time.time()
    net = sn.Net(seed, n, L, kind=kind)
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
    Hp, Ap = net.sample(65536, set(layers), gp)
    Hp[L] = Ap
    V = float(Ap.double().var(0).sum())
    fr_a = sn.frame(Ap)
    ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
    He, Ae = net.sample(args.P_eval, set(layers), ge)
    He[L] = Ae
    fr = sn.frame(Hp[l])
    K = max(16, n)
    _, anchor = linref(net, l, L, V, fr, He, Ae, 99_000 + seed)
    U = anchor[0]
    xp = (Hp[l][:16384] - fr['m']) @ fr['Sm12']
    xs = (He[l][:16384] - fr['m']) @ fr['Sm12']
    res = dict(cell=name, n=n, L=L, seed=seed, l=l, cls=cls, netkind=kind, curves={}, gates={})
    base = 55_000 + seed * 7 + n * 13 + L * 101 + l * 3
    for gname, specs, steps in (('x', [('next', 0.0), ('next', 0.1), ('next', 0.1), ('next', 0.3), ('next', 0.3), ('random', 1.0)], a2.steps),
                                ('xl', [('next', 0.0), ('next', 0.1)], 2 * a2.steps)):
        Mg = len(specs)
        torch.manual_seed(base + Mg)
        mx = VR(Mg, n, cls, K, args.width, args.C, anchor, n)
        init_gates(mx, net, l, fr, xp, U, kind, n, seed, specs)
        train(mx, Mg, n, net, l, L, V, fr, fr_a, cls, steps, [None] * Mg, base + Mg)
        xe = inp(He[l], Ae, fr, fr_a, cls, Mg)
        ev = evaluate(mx, Mg, xe, Ae, net, l, V, fr, GRID, 88_000 + seed)
        for i in range(Mg):
            res['curves'][f'{gname}{i}'] = {k: ev[k][i] for k in ev}
            res['gates'][f'{gname}{i}'] = {str(lam): gate_activity(mx, i, xs, lam) for lam in (0.1, 0.01, 0.001)}
        del mx
    res['summary'] = {k: dict(zip(('cross', 'slope'), summarise(c['rate'], c['nmse']))) for k, c in res['curves'].items()}
    res['seconds'] = time.time() - t1
    json.dump(res, open(outp, 'w'))
    fm = lambda v: '-' if v is None else f'{v:.2f}'  # noqa: E731
    print(name, f'{res["seconds"]:.0f}s', ' '.join(f'{k}:{fm(s["cross"]["0.1"])}/{fm(s["cross"]["0.01"])}' for k, s in res['summary'].items()),
          flush=True)
print('ALL DONE', flush=True)
