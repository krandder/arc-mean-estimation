"""Train and evaluate lambda-conditioned variable-rate codes for one (family, layer, class, variant), batched over
seeds x restarts (or seeds x fixed lambdas for the dedicated spot-check models). One JSON per model.
usage: run_vr.py --family arc --seeds 4000,4001 --layer 16 --cls local --restarts 3 --out /root/runs/VR
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
import vrlib as vr  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--family', default='arc')
ap.add_argument('--seeds', default='9100')
ap.add_argument('--layer', type=int, required=True)
ap.add_argument('--cls', default='local')                       # local | unres | out (out requires layer = L)
ap.add_argument('--restarts', type=int, default=1)
ap.add_argument('--restart0', type=int, default=0)              # index of the first restart (for split jobs)
ap.add_argument('--variant', default='base')                     # label only; sizes from the flags below
ap.add_argument('--steps', type=int, default=20000)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--G', type=int, default=32)
ap.add_argument('--K', type=int, default=0)                      # 0: family default
ap.add_argument('--width', type=int, default=0)
ap.add_argument('--depth', type=int, default=3)
ap.add_argument('--tmin', type=float, default=-6.0)
ap.add_argument('--tmax', type=float, default=0.0)
ap.add_argument('--lr', type=float, default=1e-3)
ap.add_argument('--lr_lin', type=float, default=3e-5)
ap.add_argument('--lr_enc', type=float, default=3e-5)
ap.add_argument('--init', default='')                            # '' = default for the class; identity | h1 | outpca
ap.add_argument('--anneal', type=float, default=0.3)
ap.add_argument('--no_tri', action='store_true')
ap.add_argument('--refine_every', type=int, default=2)
ap.add_argument('--P_ref', type=int, default=8192)
ap.add_argument('--graphs', action='store_true')
ap.add_argument('--fixlam', default='')                          # e.g. -1,-2,-3: dedicated models at these t
ap.add_argument('--toy_k', type=int, default=0)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--t_step', type=float, default=0.25)
ap.add_argument('--no_tf32', action='store_true')
ap.add_argument('--save_pt', action='store_true')
ap.add_argument('--bwd_pt', default='')                          # A18 backward curriculum: saved code of a later layer
ap.add_argument('--bwd_index', type=int, default=0)               # which model of that file
ap.add_argument('--bwd_steps', type=int, default=3000)            # distillation steps of the backward start
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
T0 = time.time()
fam = args.family
seeds = [int(s) for s in args.seeds.split(',')]
K = args.K or {'arc': 256, 'nd': 16, 'toy': 256}[fam]
W = args.width or {'arc': 1024, 'nd': 256, 'toy': 1024}[fam]
l = args.layer
fix = [float(v) for v in args.fixlam.split(',')] if args.fixlam else None
R = len(fix) if fix else args.restarts
tag_fam = fam if fam != 'toy' else f'toy{args.toy_k}'


def name(seed, r):
    rr = f'fix{fix[r]:+.2f}' if fix else f'r{args.restart0 + r}'
    return f'VR_{tag_fam}_s{seed}_l{l}_{args.cls}_{args.variant}_{rr}'


todo = [(s, r) for s in seeds for r in range(R) if not os.path.exists(os.path.join(args.out, name(s, r) + '.json'))]
if not todo:
    print('all done', flush=True)
    sys.exit(0)
Ws_list, act = [], None
for s in seeds:
    Ws, act = vr.family_weights(fam, s, args.toy_k)
    Ws_list.append(Ws)
L = len(Ws_list[0])
if args.cls == 'out':
    assert l == L
bnet = vr.BNet(Ws_list, act)
stats = [vr.pilot_stats(Ws, act, l, P=65536, seed=10_000 + s) for s, Ws in zip(seeds, Ws_list)]
TJ = time.time()
for s, Ws, st_ in zip(seeds, Ws_list, stats):
    if l < len(Ws):
        st_['G'], st_['Bm'] = vr.jac_stats(Ws, act, l, st_['h'], P=8192, seed=s)
    else:
        st_['G'] = st_['a']['S12'] @ st_['a']['S12']
    if args.init in ('h1', 'bwd'):            # G of the future from layer l+1, in whitened h_{l+1} coordinates
        if l + 1 < len(Ws):
            st_['G1'], _ = vr.jac_stats(Ws, act, l + 1, st_['h1'], P=8192, seed=s + 1)
        else:
            st_['G1'] = st_['h1']['S12'] @ st_['h1']['S12']
t_jac = time.time() - TJ
t_range = (args.tmin, args.tmax)
M = len(seeds) * R
torch.manual_seed(1000 * seeds[0] + 17 * l + args.restart0 + 7 * len(args.variant) + (0 if args.cls == 'local' else 1))
init = vr.build_init(stats, Ws_list, l, args.cls, K, R, toy=(fam == 'toy'), seed=seeds[0] + args.restart0,
                     mode=('h1' if args.init == 'bwd' else (args.init or None)))
model = vr.VRCode(M, args.cls, bnet.n, K, W, args.depth, t_range, init,
                  lin_src=('y' if init['mode'] == 'refu' else 'xa'), tri=not args.no_tri)
fr = vr.Frames(stats, l, L, R)


@torch.no_grad()
def bwd_init(model, src_path, src_index, P=16384):
    """Kelvin's backward curriculum (PREREG A18): start layer l's local code from a later layer's saved code composed
    with the layer map, inside the local class. The hidden layer computes h_{l+1} exactly (the look-ahead start); for
    each encoder anchor t_j the affine map is the least-squares fit, over fresh pilot inputs, of the source code's
    latents nu_src(h_l'; t_j) on h_{l+1}; then the whole encoder (both layers, every anchor) is distilled for
    bwd_steps Adam steps onto the source's signal g * nu_src (the composed code projected onto the class); the gains
    (anchor spectrum ev and correction c) and the prior are the source's; the decoder's linear path is the
    least-squares map from the new latents at the highest-budget anchor to whitened h_l, the decoder bias its intercept,
    and the zero-rate offset is set relative to it. Returns the gain-weighted R^2 of the distilled fit per anchor
    (model 0)."""
    src = torch.load(src_path, map_location=vr.DEV)
    sa, sst = src['args'], src['state']
    ls = sa['layer']
    assert sa['cls'] == 'local' and sa['family'] == fam and ls > l, (sa['cls'], sa['family'], ls, l)
    Ms = sst['c'].shape[0]
    n = bnet.n
    Ksrc = sst['c'].shape[2]
    assert Ksrc == K
    z = lambda *sh: torch.zeros(*sh, dtype=vr.DT, device=vr.DEV)  # noqa: E731
    dummy = dict(B=z(Ms, K, n), dec_bias=z(Ms, n), Plin=z(Ms, n, K), ev=z(Ms, K), V=torch.ones(Ms, dtype=vr.DT,
                 device=vr.DEV), mode='h1', Bhead=z(Ms, K, n), ystar=z(Ms, n), A1=z(Ms, n, n), b1=z(Ms, n),
                 A2=z(Ms, n, K), b2=z(Ms, K), nh=n)
    Wsrc = sa['width'] or {'arc': 1024, 'nd': 256, 'toy': 1024}[fam]
    srcm = vr.VRCode(Ms, 'local', n, K, Wsrc, sa['depth'], (sa['tmin'], sa['tmax']), dummy, tri=not sa['no_tri'])
    srcm.load_state_dict(sst)
    i = src_index
    r2s = []
    for m in range(model.M):
        s = seeds[m // R]
        Ws = Ws_list[m // R]
        rng = np.random.default_rng([55_000 + s, l, ls])
        h = rng.standard_normal((P, n))
        for k in range(l):
            h = h @ Ws[k].T
            if act == 'relu':
                h = np.maximum(h, 0.0)
        hl = h.copy()
        for k in range(l, ls):
            h = h @ Ws[k].T
            if act == 'relu':
                h = np.maximum(h, 0.0)
        hls = h
        fs = vr.pilot_stats(Ws, act, ls, P=65536, seed=10_000 + s)['h']          # the source run's frames at l'
        ysrc = torch.tensor((hls - fs['m']) @ fs['Sm12'], dtype=vr.DT, device=vr.DEV)
        fl = stats[m // R]['h']
        yl = (hl - fl['m']) @ fl['Sm12']                                          # encoder-side whitening at l
        A1 = model.enc.A1[m, 0].double().cpu().numpy()
        b1 = model.enc.b1[m, 0].double().cpu().numpy()
        u = np.maximum(yl @ A1 + b1, 0.0)                                         # = h_{l+1}
        U1 = np.concatenate([u, np.ones((P, 1))], 1)
        G = U1.T @ U1 + 1e-6 * np.trace(U1.T @ U1) / U1.shape[1] * np.eye(U1.shape[1])
        NU, GS = [], []
        for j, tj in enumerate(model.anch_e):
            tt = torch.full((Ms, 1), float(tj), dtype=vr.DT, device=vr.DEV)
            nu = srcm.encode(ysrc.view(1, 1, P, n).expand(Ms, 1, P, n).contiguous(), None, tt)[i, 0]
            gs = srcm.gains(tt, vr.hat(tt, srcm.anch_t))[i, 0]                      # the source's gains at t_j
            NU.append(nu)
            GS.append(gs)
            Y = nu.double().cpu().numpy()
            X = np.linalg.solve(G, U1.T @ Y)                                       # least-squares readout start
            model.enc.A2[m, j].copy_(torch.tensor(X[:-1], dtype=vr.DT))
            model.enc.b2[m, j].copy_(torch.tensor(X[-1], dtype=vr.DT))
        # distillation inside the class: fit the whole one-ReLU-layer encoder (every anchor) to the source code's
        # signal g * nu_src(f(h_l)), weighted by the source's gains (what the channel carries), from the start above
        yt = torch.tensor(yl, dtype=vr.DT, device=vr.DEV)
        par = [model.enc.A1[m].detach().clone().requires_grad_(True), model.enc.b1[m].detach().clone().requires_grad_(True),
               model.enc.A2[m].detach().clone().requires_grad_(True), model.enc.b2[m].detach().clone().requires_grad_(True)]
        gw = [g_ / g_.pow(2).mean().sqrt().clamp(min=1e-6) for g_ in GS]
        gen = torch.Generator(device=vr.DEV).manual_seed(4242 + s + 31 * l)
        with torch.enable_grad():
            opt = torch.optim.Adam([dict(params=par[:2], lr=1e-4), dict(params=par[2:], lr=1e-3)])
            for step in range(args.bwd_steps):
                bi = torch.randint(0, P, (2048,), generator=gen, device=vr.DEV)
                loss = 0.0
                for j in range(len(model.anch_e)):
                    u_ = torch.relu(yt[bi] @ par[0][j] + par[1][j])
                    loss = loss + (((u_ @ par[2][j] + par[3][j] - NU[j][bi]) * gw[j]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()
        for k_, nm in enumerate(('A1', 'b1', 'A2', 'b2')):
            getattr(model.enc, nm)[m].copy_(par[k_].detach())
        if m == 0:
            for j in range(len(model.anch_e)):
                u_ = torch.relu(yt @ par[0][j] + par[1][j])
                res = ((u_ @ par[2][j] + par[3][j] - NU[j]) * gw[j]) ** 2
                tot = ((NU[j] - NU[j].mean(0)) * gw[j]) ** 2
                r2s.append(float(1 - res.sum() / tot.sum().clamp(min=1e-30)))
        A1h = model.enc.A1[m, 0].double().cpu().numpy()
        b1h = model.enc.b1[m, 0].double().cpu().numpy()
        u = np.maximum(yl @ A1h + b1h, 0.0)
        model.ev[m].copy_(srcm.ev[i])
        for nm in ('c', 'p_logit', 'p_mean', 'p_lsd') + (('Ltri',) if model.tri and srcm.tri else ()):
            getattr(model, nm)[m].copy_(getattr(srcm, nm)[i])
        A2h = model.enc.A2[m, 0].double().cpu().numpy()
        b2h = model.enc.b2[m, 0].double().cpu().numpy()
        nuh = u @ A2h + b2h
        Z1 = np.concatenate([nuh, np.ones((P, 1))], 1)
        GZ = Z1.T @ Z1 + 1e-6 * np.trace(Z1.T @ Z1) / Z1.shape[1] * np.eye(Z1.shape[1])
        XB = np.linalg.solve(GZ, Z1.T @ yl)
        model.Blin[m].copy_(torch.tensor(XB[:-1], dtype=vr.DT))
        model.dec.out.b[m].copy_(torch.tensor(XB[-1], dtype=vr.DT).view(1, n))
        ys = (stats[m // R]['h_star'] - fl['m']) @ fl['Tinv']
        model.ystar[m].copy_(torch.tensor(ys - XB[-1], dtype=vr.DT))
    return r2s


bwd_r2 = None
if args.init == 'bwd':
    assert args.cls == 'local' and args.bwd_pt
    bwd_r2 = bwd_init(model, args.bwd_pt, args.bwd_index)
nparam = sum(p.numel() for p in model.parameters()) // M
logf = open(os.path.join(args.out, f'log_{tag_fam}_l{l}_{args.cls}_{args.variant}_r{args.restart0}_s{seeds[0]}.txt'), 'a')
print(f'{fam} seeds {seeds} l={l} cls={args.cls} variant={args.variant} M={M} K={K} W={W} params/model={nparam} '
      f'dev={vr.DEV}', file=logf, flush=True)
fixed_t = None
if fix:
    fixed_t = torch.tensor([fix[m % R] for m in range(M)], device=vr.DEV, dtype=vr.DT)
seed_train = 77_000 + 131 * seeds[0] + 17 * l + 1009 * args.restart0 + (0 if args.cls == 'local' else 5)
log = vr.train(model, bnet, fr, l, args.steps, args.batch, args.G, t_range, seed_train, lr=args.lr,
               lr_lin=args.lr_lin, lr_enc=args.lr_enc, fixed_t=fixed_t, tf32=not args.no_tf32, logf=logf,
               anneal=args.anneal, graphs=args.graphs)
t_train = time.time() - T0
t_grid = list(np.round(np.arange(args.tmin, args.tmax + 1e-9, args.t_step), 4))
ev = vr.evaluate(model, bnet, fr, l, t_grid, args.P_eval, seeds, refine_every=args.refine_every, P_ref=args.P_ref)
for m in range(M):
    s, r = seeds[m // R], m % R
    st_ = stats[m // R]
    res = dict(family=fam, toy_k=args.toy_k, seed=s, layer=l, L=L, n=bnet.n, cls=args.cls, variant=args.variant,
               restart=(None if fix else args.restart0 + r), fixed_t=(fix[r] if fix else None), K=K, width=W,
               depth=args.depth, steps=args.steps, batch=args.batch, G=args.G, t_range=t_range, lr=args.lr,
               lr_lin=args.lr_lin, lr_enc=args.lr_enc, anneal=args.anneal,
               init=('bwd' if args.init == 'bwd' else init['mode']), bwd_pt=os.path.basename(args.bwd_pt) or None,
               bwd_fit_r2=bwd_r2,
               params_per_model=nparam, V=st_['V'], Ea2=st_['Ea2'], EJ=st_['EJ'],
               out_evals=[float(v) for v in st_['a']['evals']],
               G_evals=[float(v) for v in vr.eig_desc(st_['G'])[0]], seconds_jac=t_jac, tri=not args.no_tri,
               curve=ev[m], train_log=[dict(step=x['step'], sec=x['sec']) for x in log],
               train_log_last=(log[-1] if log else None), seconds_train=t_train, seconds_total=time.time() - T0, M=M)
    json.dump(res, open(os.path.join(args.out, name(s, r) + '.json'), 'w'))
if args.save_pt:
    torch.save(dict(state=model.state_dict(), args=vars(args)), os.path.join(
        args.out, f'VR_{tag_fam}_l{l}_{args.cls}_{args.variant}_r{args.restart0}_s{seeds[0]}.pt'))
print(f'done {fam} {seeds} l={l} {args.cls} {args.variant} train {t_train:.0f}s total {time.time() - T0:.0f}s',
      file=logf, flush=True)
print(f'done {fam} {seeds} l={l} {args.cls} {args.variant} train {t_train:.0f}s total {time.time() - T0:.0f}s',
      flush=True)
