"""Phase 2 (b): the unscrambling loss at (nearly) fixed rate. For a pair of consecutive layers (l, l+1) of one net and
class, start from the phase-1 codes (model r0 of P1 at l and of P2a at l+1, lambda fixed) and fine-tune both codes
jointly with
    loss = sum_{j = l, l+1} (d_j + lambda * rate_j) / Lag0_j  +  mu * |y_{l+1} - S(y_l)|^2 / tr Var(y_{l+1})
where y_j is the code mean (encoder output), S a map from code l to code l+1 trained jointly, restricted to a simple
class ('linear': any affine map; 'diag': coordinate-wise affine, i.e. identity up to scaling), Lag0_j the starting
Lagrangian of layer j (so each layer's rate-distortion term starts at 1). M = len(MUS) copies trained side by side,
mu = 0 is the control (fine-tuning without the penalty). Evaluation on held-out samples: per layer rate, nMSE and
Lagrangian; predictability of y_{l+1} from y_l: R^2 of the best affine map, of the best coordinate-wise affine map,
and of an MLP (the limit of what is predictable at all, fitted on half A, scored on half B).
usage: run_unscr.py --pair <kind>_<n>x<L>_s<seed>_l<l>_<cls> --p1 /root/runs/P1 --p2a /root/runs/P2a --out /root/runs/U
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
ap2.add_argument('--pair', required=True)
ap2.add_argument('--p1', required=True)
ap2.add_argument('--p2a', required=True)
ap2.add_argument('--out', required=True)
ap2.add_argument('--lam', type=float, default=0.01)
ap2.add_argument('--smap', default='linear')
ap2.add_argument('--mus', default='0,0.1,0.3,1,3')
ap2.add_argument('--steps', type=int, default=3000)
ap2.add_argument('--batch', type=int, default=2048)
a2 = ap2.parse_args()
os.makedirs(a2.out, exist_ok=True)
src = open(os.path.join(HERE, 'run_vr.py')).read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', a2.out]
G = {'__file__': os.path.join(HERE, 'run_vr.py'), '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, VR, linref, tof, inp, state, LOG2 = (G['sn'], G['DEV'], G['VR'], G['linref'], G['tof'], G['inp'], G['state'],
                                              G['LOG2'])
MUS = [float(v) for v in a2.mus.split(',')]
M = len(MUS)
kind, nl, seedp, lp, cls = a2.pair.split('_')
n, L = map(int, nl.split('x'))
seed, l = int(seedp[1:]), int(lp[1:])
l1 = l + 1
tag = f'Uc_{a2.pair}_lam{a2.lam}_{a2.smap}'   # corrected version (review r3)
path = os.path.join(a2.out, tag + '.json')
if os.path.exists(path):
    sys.exit(0)
G['SQUASH'] = (kind == 'feistel')
t0 = time.time()
net = sn.Net(seed, n, L, kind=kind)
gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
Hp, Ap = net.sample(65536, {l, l1}, gp)
V = float(Ap.double().var(0).sum())
fr_a = sn.frame(Ap)
frs = [sn.frame(Hp[l]), sn.frame(Hp[l1])]
ge = torch.Generator(device=DEV).manual_seed(40_000 + seed)
He, Ae = net.sample(32768, {l, l1}, ge)
K = max(16, n)
models = []
for j, (lj, root) in enumerate(((l, a2.p1), (l1, a2.p2a))):
    _, anchor = linref(net, lj, L, V, frs[j], He, Ae, 99_000 + seed, P=8192, NT=2)
    sd = torch.load(os.path.join(root, f'P_{kind}_n{n}_L{L}_s{seed}_l{lj}_{cls}.pt'), map_location=DEV)
    sd = {k: (v[0:1].expand(M, *v.shape[1:]).clone() if v.dim() > 0 and v.shape[0] == 6 else v) for k, v in sd.items()}
    m = VR(M, n, cls, K, 256, 4, anchor, n)
    m.load_state_dict(sd)
    m.V = V
    models.append(m)
if a2.smap == 'linear':
    S_W = torch.nn.Parameter(torch.zeros(M, K, K, device=DEV))
else:
    S_W = torch.nn.Parameter(torch.zeros(M, 1, K, device=DEV))
S_b = torch.nn.Parameter(torch.zeros(M, 1, K, device=DEV))
mu = torch.tensor(MUS, device=DEV)


def S(y):
    return (torch.bmm(y, S_W) if a2.smap == 'linear' else y * S_W) + S_b


def step_terms(hs, A, g, lam_t):
    """Per model: d_j, rate_j (j = 0, 1) and code means y_j. hs = [h_l, h_{l+1}] (B, n)."""
    out = []
    for j, (m, lj) in enumerate(zip(models, (l, l1))):
        x = inp(hs[j], A, frs[j], fr_a, cls, M)
        y = m.encode(x, lam_t)
        z = y + torch.randn(y.shape, generator=g, device=DEV)
        logq = (-0.5 * (z - y) ** 2 - 0.5 * math.log(2 * math.pi)) / LOG2
        rate = (logq - m.log2p(z, lam_t)).sum(-1)
        ah = net.run(state(frs[j], m.decode(z, lam_t)), lj)
        d = ((ah - A) ** 2).sum(-1) / V
        out.append((d, rate, y))
    return out


@torch.no_grad()
def evaluate(nB=16384):
    g = torch.Generator(device=DEV).manual_seed(50_000 + seed)
    lam_t = torch.full((M, nB, 1), tof(a2.lam), device=DEV)
    terms = step_terms([He[l][:nB], He[l1][:nB]], Ae[:nB], g, lam_t)
    res = {}
    for j in range(2):
        d, r, _ = terms[j]
        res[f'nmse_{j}'] = d.mean(1).tolist()
        res[f'rate_{j}'] = r.mean(1).tolist()
    y0, y1 = terms[0][2].double(), terms[1][2].double()
    h = nB // 2
    pred = dict(lin=[], diag=[], mlp=[], penalty_map=[])
    for mi in range(M):
        X, Y = y0[mi], y1[mi]
        Yc = Y[h:] - Y[h:].mean(0)
        den = (Yc ** 2).sum()
        A1 = torch.cat([X, torch.ones(X.shape[0], 1, dtype=X.dtype, device=X.device)], 1)
        coef = torch.linalg.lstsq(A1[:h], Y[:h]).solution
        pred['lin'].append(float(1 - ((Y[h:] - A1[h:] @ coef) ** 2).sum() / den))
        Xm, Ym = X[:h].mean(0), Y[:h].mean(0)
        sl = ((X[:h] - Xm) * (Y[:h] - Ym)).sum(0) / ((X[:h] - Xm) ** 2).sum(0).clamp(min=1e-12)
        pred['diag'].append(float(1 - ((Y[h:] - (Ym + sl * (X[h:] - Xm))) ** 2).sum() / den))
        Sy = S(y0.float())[mi].double()
        pred['penalty_map'].append(float(1 - ((Y[h:] - Sy[h:]) ** 2).sum() / den))
        torch.manual_seed(mi)
        mlp = torch.nn.Sequential(torch.nn.Linear(K, 128), torch.nn.GELU(), torch.nn.Linear(128, 128), torch.nn.GELU(),
                                  torch.nn.Linear(128, K)).to(DEV)
        mx, sx = X[:h].mean(0), X[:h].std(0).clamp(min=1e-6)
        my, sy = Y[:h].mean(0), Y[:h].std(0).clamp(min=1e-6)
        Xn, Yn = ((X - mx) / sx).float(), ((Y - my) / sy).float()
        with torch.enable_grad():
            opt = torch.optim.Adam(mlp.parameters(), lr=2e-3)
            gg = torch.Generator(device=DEV).manual_seed(mi)
            for _ in range(1500):
                idx = torch.randint(0, h, (1024,), generator=gg, device=DEV)
                loss = ((mlp(Xn[idx]) - Yn[idx]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()
        P_ = mlp(Xn).double() * sy + my
        pred['mlp'].append(float(1 - ((Y[h:] - P_[h:]) ** 2).sum() / den))
    res['predict'] = pred
    res['k'] = [[int((y0[mi].var(0) > 1).sum()), int((y1[mi].var(0) > 1).sum())] for mi in range(M)]
    return res


res = dict(pair=a2.pair, kind=kind, n=n, L=L, seed=seed, l=l, cls=cls, lam=a2.lam, smap=a2.smap, mus=MUS, steps=a2.steps)
res['start'] = evaluate()
lag0 = [sum(res['start'][f'nmse_{j}'][0] + a2.lam * res['start'][f'rate_{j}'][0] for _ in [0]) for j in range(2)]
params = [p for m in models for p in m.parameters()] + [S_W, S_b]
opt = torch.optim.Adam(params, lr=3e-4, betas=(0.9, 0.99))
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 60) * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * s / a2.steps))))
gt = torch.Generator(device=DEV).manual_seed(60_000 + seed)
lam_t = torch.full((M, a2.batch, 1), tof(a2.lam), device=DEV)
for step in range(a2.steps):
    Hb, Ab = net.sample(a2.batch, {l, l1}, gt)
    terms = step_terms([Hb[l], Hb[l1]], Ab, gt, lam_t)
    loss_rd = sum((terms[j][0] + a2.lam * terms[j][1]).mean(1) / lag0[j] for j in range(2))
    y0, y1 = terms[0][2], terms[1][2]
    var1 = y1.var(1).sum(-1).clamp(min=1e-6)                 # NOT detached: scale-invariant, shrinking does not help
    pen = ((y1 - S(y0)) ** 2).sum(-1).mean(1) / var1
    if step == 0:
        var1_0 = var1.detach().clone()
    pen = pen + 10.0 * torch.relu(0.5 - var1 / var1_0) ** 2  # guard: the next code may not shrink below half its variance
    loss = (loss_rd + mu * pen).sum()
    opt.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(params, 100.0)
    opt.step()
    sched.step()
res['end'] = evaluate()
res['lag0'] = lag0
res['seconds'] = time.time() - t0
json.dump(res, open(path, 'w'))
e, s0 = res['end'], res['start']
print(tag, f'{res["seconds"]:.0f}s', 'mu', MUS, '| R2 lin', [round(x, 3) for x in e['predict']['lin']], '| mlp',
      [round(x, 3) for x in e['predict']['mlp']], '| rate0', [round(x, 2) for x in e['rate_0']], '| nmse0',
      [round(x, 4) for x in e['nmse_0']], '| start lin/mlp', round(s0['predict']['lin'][0], 3), round(s0['predict']['mlp'][0], 3),
      flush=True)
