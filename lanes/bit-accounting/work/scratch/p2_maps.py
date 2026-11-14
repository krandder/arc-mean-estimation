"""P2.0 parts 2-4 (amendment P2.0-a): the code map between consecutive layers against the layer map, gates tracked by
the code, rotation of the code's subspace. CPU. Pairs: P1 cell at grid layer l (runs/P1) and P2a cell at l+1
(runs/P2a), same net, seed and class; model r0; lambda in {0.1, 0.01, 0.001}; 16384 held-out inputs split in halves
A (fit) and B (score). usage: python scratch/p2_maps.py <part i> <parts k> <out.json>"""
import json
import math
import os
import sys

import numpy as np
import torch

W = '/home/agent/workspaces/mats/work/bit-accounting'
PART, NPART = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 1)
OUT = sys.argv[3] if len(sys.argv) > 3 else f'{W}/results/P2_maps.json'
src = open(f'{W}/gpu_src/scripts/run_vr.py').read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', '/tmp/p2_unused', '--threads', '2']
G = {'__file__': f'{W}/gpu_src/scripts/run_vr.py', '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, VR, linref, tof, inp = G['sn'], G['DEV'], G['VR'], G['linref'], G['tof'], G['inp']
torch.set_num_threads(2)
LAMS = (0.1, 0.01, 0.001)


def r2(pred, y):
    """Variance-weighted R^2 of pred for y (both (N, K))."""
    return float(1.0 - ((y - pred) ** 2).sum() / ((y - y.mean(0)) ** 2).sum().clamp(min=1e-30))


def linfit(X, Y, nA):
    A = torch.cat([X, torch.ones(X.shape[0], 1, dtype=X.dtype)], 1)
    coef = torch.linalg.lstsq(A[:nA], Y[:nA]).solution
    return A @ coef


def mlpfit(X, Y, nA, steps=1500, seed=0):
    torch.manual_seed(seed)
    mu, sd = X[:nA].mean(0), X[:nA].std(0).clamp(min=1e-6)
    my, sy = Y[:nA].mean(0), Y[:nA].std(0).clamp(min=1e-6)
    Xn, Yn = ((X - mu) / sd).float(), ((Y - my) / sy).float()
    net = torch.nn.Sequential(torch.nn.Linear(X.shape[1], 128), torch.nn.GELU(), torch.nn.Linear(128, 128), torch.nn.GELU(),
                              torch.nn.Linear(128, Y.shape[1]))
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    g = torch.Generator().manual_seed(seed)
    for _ in range(steps):
        idx = torch.randint(0, nA, (1024,), generator=g)
        loss = ((net(Xn[idx]) - Yn[idx]) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        return (net(Xn).double() * sy + my)


def load_model(path_pt, n, cls, anchor, V):
    sd = torch.load(path_pt, map_location=DEV)
    sd = {k: (v[0:1] if v.dim() > 0 and v.shape[0] == 6 else v) for k, v in sd.items()}
    m = VR(1, n, cls, max(16, n), 256, 4, anchor, n)
    m.load_state_dict(sd)
    m.V = V
    return m


def active_dirs(x, y, k):
    A = torch.cat([x, torch.ones(x.shape[0], 1, dtype=x.dtype)], 1)
    coef = torch.linalg.lstsq(A, y).solution
    Vh = torch.linalg.svd(coef[:-1].T, full_matrices=False)[2]
    return Vh[:k].T


def mean_cos2(Q1, Q2):
    k = min(Q1.shape[1], Q2.shape[1])
    if k == 0:
        return None
    Q1o = torch.linalg.qr(Q1)[0]
    Q2o = torch.linalg.qr(Q2)[0]
    sv = torch.linalg.svdvals(Q1o.T @ Q2o)[:k]
    return float((sv ** 2).mean())


pairs = []
for f in sorted(os.listdir(f'{W}/runs/P2a')):
    if f.startswith('P_') and f.endswith('.json') and os.path.exists(f'{W}/runs/P2a/{f[:-5]}.pt'):
        d = json.load(open(f'{W}/runs/P2a/{f}'))
        l1 = d['l']
        prev = f'P_{d["netkind"]}_n{d["n"]}_L{d["L"]}_s{d["seed"]}_l{l1 - 1}_{d["cls"]}'
        if os.path.exists(f'{W}/runs/P1/{prev}.pt'):
            pairs.append((prev, f[:-5], d))
pairs = [p for i, p in enumerate(pairs) if i % NPART == PART]
out = json.load(open(OUT)) if os.path.exists(OUT) else {}
for prev, cur, d in pairs:
    key = cur
    if key in out:
        continue
    kind, n, L, seed, l1, cls = d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls']
    l = l1 - 1
    G['SQUASH'] = (kind == 'feistel')
    net = sn.Net(seed, n, L, kind=kind)
    gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
    Hp, Ap = net.sample(65536, {l, l1}, gp)
    V = float(Ap.double().var(0).sum())
    fr_a = sn.frame(Ap)
    fr0, fr1 = sn.frame(Hp[l]), sn.frame(Hp[l1])
    ge = torch.Generator(device=DEV).manual_seed(30_000 + seed)
    He, Ae = net.sample(16384, {l, l1}, ge)
    nA = 8192
    _, an0 = linref(net, l, L, V, fr0, He, Ae, 99_000 + seed, P=8192, NT=2)
    _, an1 = linref(net, l1, L, V, fr1, He, Ae, 99_000 + seed, P=8192, NT=2)
    m0 = load_model(f'{W}/runs/P1/{prev}.pt', n, cls, an0, V)
    m1 = load_model(f'{W}/runs/P2a/{cur}.pt', n, cls, an1, V)
    x0 = inp(He[l], Ae, fr0, fr_a, cls, 1)
    x1 = inp(He[l1], Ae, fr1, fr_a, cls, 1)
    res = dict(kind=kind, n=n, L=L, seed=seed, l=l, cls=cls)
    # gate energies of layer l+1 units (pre-activations h_l @ WT[l])
    pre = (He[l] @ net.WT[l]).double()
    hl = He[l][:4096].clone().requires_grad_(True)
    prel = hl @ net.WT[l]
    act = torch.relu(prel) if kind == 'relu' else (torch.tanh(prel) if kind == 'tanh4' else prel)
    a_ = net.run(act, l1)
    energy = torch.zeros(n, dtype=torch.float64)
    for j in range(a_.shape[1]):
        gr, = torch.autograd.grad(a_[:, j].sum(), prel, retain_graph=(j < a_.shape[1] - 1))
        energy += (gr.double() ** 2).mean(0)
    dist = (pre.abs().mean(0) / pre.std(0).clamp(min=1e-12))
    gates = (pre > 0).double()
    base = torch.maximum(gates[nA:].mean(0), 1 - gates[nA:].mean(0))
    # cloud-averaged Jacobian of layer l+1 in whitened coordinates
    if kind == 'relu':
        fprime = (pre > 0).double().mean(0)
    elif kind == 'tanh4':
        fprime = (1 - torch.tanh(pre) ** 2).mean(0)
    else:
        fprime = torch.ones(n, dtype=torch.float64)
    Jh = (fprime.view(-1, 1) * net.WT[l].double().T)                 # dh_{l+1}/dh_l averaged: diag(E f') W
    Jw = fr1['Sm12'].double() @ Jh @ fr0['S12'].double()
    for lam in LAMS:
        with torch.no_grad():
            t = torch.full((1, x0.shape[1], 1), tof(lam), device=DEV)
            y0 = m0.encode(x0, t)[0].double()
            y1 = m1.encode(x1, t)[0].double()
            gn = torch.Generator(device=DEV).manual_seed(4_000 + seed)
            z0 = y0 + torch.randn(y0.shape, generator=gn, dtype=torch.float64)
            hh = G['state'](fr0, m0.decode(z0.float().unsqueeze(0), t)[0])
            h1 = net.layer(hh, l)
            yp = m1.encode(inp(h1, net.run(h1, l1), fr1, fr_a, cls, 1), t)[0].double()   # layer path E_{l+1}(f(D_l(z_l)))
        k0, k1 = int((y0.var(0) > 1).sum()), int((y1.var(0) > 1).sum())
        Tl = linfit(y0, y1, nA)
        Tm = mlpfit(y0, y1, nA, seed=seed + l)
        B = slice(nA, None)
        st = dict(k0=k0, k1=k1,
                  r2_Tlin=r2(Tl[B], y1[B]), r2_Tmlp=r2(Tm[B], y1[B]), r2_path=r2(yp[B], y1[B]),
                  agree_Tmlp_path=r2(Tm[B], yp[B]),
                  linshare_Tmlp=r2(linfit(y0, Tm, nA)[B], Tm[B]), linshare_path=r2(linfit(y0, yp, nA)[B], yp[B]))
        # gates of layer l+1 from the code at l (logistic regression per unit, held out)
        Xg = torch.cat([y0, torch.ones(y0.shape[0], 1, dtype=torch.float64)], 1)
        Xn = (Xg - Xg[:nA].mean(0)) / Xg[:nA].std(0).clamp(min=1e-9)
        Xn[:, -1] = 1.0
        Wg = torch.zeros(Xn.shape[1], n, dtype=torch.float64, requires_grad=True)
        opt = torch.optim.Adam([Wg], lr=0.05)
        for _ in range(300):
            lg = Xn[:nA] @ Wg
            loss = torch.nn.functional.binary_cross_entropy_with_logits(lg, gates[:nA])
            opt.zero_grad()
            loss.backward()
            opt.step()
        with torch.no_grad():
            acc = ((Xn[nA:] @ Wg > 0).double() == gates[nA:]).double().mean(0)
        tracked = (acc >= 0.95)
        q = torch.quantile(energy, torch.tensor([0.25, 0.75], dtype=torch.float64))
        st.update(gate_acc_mean=float(acc.mean()), gate_base_mean=float(base.mean()), tracked_frac=float(tracked.double().mean()),
                  tracked_top_energy=float(tracked[energy >= q[1]].double().mean()),
                  tracked_low_energy=float(tracked[energy <= q[0]].double().mean()),
                  spearman_acc_energy=float(np.corrcoef(np.argsort(np.argsort(acc.numpy())), np.argsort(np.argsort(energy.numpy())))[0, 1]),
                  spearman_acc_dist=float(np.corrcoef(np.argsort(np.argsort(acc.numpy())), np.argsort(np.argsort(dist.numpy())))[0, 1]))
        # rotation of the code's active subspace
        if k0 > 0 and k1 > 0:
            Q0 = active_dirs(x0[0, :, :n].double(), y0, k0)
            Q1 = active_dirs(x1[0, :, :n].double(), y1, k1)
            st['rot_cos2'] = mean_cos2(Jw @ Q0, Q1)
            st['rot_cos2_identity'] = mean_cos2(Q0, Q1)
        res[str(lam)] = st
    out[key] = res
    print(key, {q: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[q].items()
                    if k in ('r2_Tlin', 'r2_Tmlp', 'r2_path', 'agree_Tmlp_path', 'tracked_frac', 'rot_cos2')} for q in ('0.01',)},
          flush=True)
    json.dump(out, open(OUT, 'w'), indent=1)
print('ALL DONE', flush=True)
