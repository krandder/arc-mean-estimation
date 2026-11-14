"""Phase 1, amendment P1-A (responses to review r2a): extra certificates on finished P1 cells.
For each cell P_<kind>_n<n>_L<L>_s<seed>_l<l>_<cls>.json in --runs with its saved G1 model (.pt):
  explorer (local cells, finding 1): 3 local encoders whose ReLU gates start INSIDE the input cloud: hidden layer =
      the net's own next-layer pre-activations relu(W_{l+1} h_l) (relu/tanh4/linear nets; random unit-variance gates
      for feistel), jittered per restart; output layer fitted by least squares to the anchor's unit-scale code U^T x;
      analytic gains, decoder and prior as in P1; S steps, lambda-conditioned. Still the class L^1(n).
  wdec (local cells, finding 7): width-n local encoder with the wide decoder (512) and prior (8 components): separates
      the encoder-width effect from the decoder/prior effect in G2.
  centroid2 (all cells, finding 2): on r0's held-out codes at lambda = 0.1, 0.01, 0.001: an output-space residual
      correction a_hat + MLP(b~ z) (MLP 3 x 512, last layer zero at start) trained on output MSE (normalised by V) for
      4000 steps on 98304 fresh samples; held-out nMSE of the model and of the corrected output; the improvement in the
      last quarter of training (convergence).
  linref_rate2 (all cells, finding 9): the linear reference's rate with the directional powers measured on the
      held-out states (0.5 sum log2(1 + p_i v_i), v_i = held-out variance of u_i^T x) instead of v_i = 1.
  gates (local cells, finding 1): fraction of hidden units active on 5-95% of held-out inputs, for r0 and the explorers.
Output: <out>/X_<cell>.json. usage: run_vr_cert2.py --runs /root/runs/P1 --cells <list file or 'all'> --out /root/runs/P1X
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

HERE = os.path.dirname(os.path.abspath(__file__))
ap2 = argparse.ArgumentParser()
ap2.add_argument('--runs', required=True)
ap2.add_argument('--cells', default='all')
ap2.add_argument('--out', required=True)
ap2.add_argument('--steps', type=int, default=6000)
ap2.add_argument('--cent_steps', type=int, default=4000)
a2 = ap2.parse_args()
os.makedirs(a2.out, exist_ok=True)

# load the registered P1 definitions (classes and functions) from run_vr.py without running its main loop
src = open(os.path.join(HERE, 'run_vr.py')).read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', a2.out, '--steps', str(a2.steps)]
G = {'__file__': os.path.join(HERE, 'run_vr.py'), '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, args, VR, train, inp, evaluate, linref, summarise = (G['sn'], G['DEV'], G['args'], G['VR'], G['train'], G['inp'],
                                                              G['evaluate'], G['linref'], G['summarise'])
GRID, FIXED, tof, state, CH, LOG2 = G['GRID'], G['FIXED'], G['tof'], G['state'], G['CH'], G['LOG2']

if a2.cells == 'all':
    names = sorted(f[:-5] for f in os.listdir(a2.runs) if f.startswith('P_') and f.endswith('.json')
                   and os.path.exists(os.path.join(a2.runs, f[:-5] + '.pt')))
else:
    names = [ln.strip() for ln in open(a2.cells) if ln.strip()]


def gate_activity(model, mi, x, lam):
    """Fraction of hidden units of a local encoder active on 5-95% of the inputs x (B, n), at lambda."""
    M = model.enc.Ws[0].shape[0]
    with torch.no_grad():
        t = torch.full((M, x.shape[0], 1), tof(lam), device=DEV)
        f = model.enc.film(t)
        w = model.enc.width
        pre = (1.0 + f[..., :w]) * torch.baddbmm(model.enc.bs[0], x.unsqueeze(0).expand(M, -1, -1), model.enc.Ws[0]) + f[..., w:2 * w]
        act = (pre[mi] > 0).float().mean(0)
    return float(((act > 0.05) & (act < 0.95)).float().mean())


def explorer_init(model, net, l, fr, x, U, kind, n, seed):
    """Gates inside the cloud: hidden = the next layer's pre-activations (jittered), output fitted by least squares to
    U^T x. In place on model.enc (M restarts)."""
    M = model.enc.Ws[0].shape[0]
    g = torch.Generator(device=DEV).manual_seed(555 + seed + 7 * l)
    with torch.no_grad():
        S12, m = fr['S12'], fr['m']
        if kind in ('relu', 'tanh4', 'linear') and l < net.L:
            Wn = net.WT[l]                                   # h_{l+1}^pre = h_l @ WT[l]
            W1 = S12 @ Wn                                    # whitened x -> pre-activation: (m + x S12) WT
            b1 = m @ Wn
            sc = W1.std() + 1e-8
        else:
            W1 = torch.randn(n, n, generator=g, device=DEV) / math.sqrt(n)
            b1 = torch.zeros(n, device=DEV)
            sc = W1.std()
        target = (x @ U.float())                             # unit-scale anchor code U^T x, (B, K)
        for mi in range(M):
            Wj = W1 + (0.0 if mi == 0 else 0.1) * sc * torch.randn(W1.shape, generator=g, device=DEV)
            u = torch.relu(x @ Wj + b1)
            A = torch.cat([u, torch.ones(u.shape[0], 1, device=DEV)], 1)
            sol = torch.linalg.lstsq(A.double().cpu(), target.double().cpu()).solution.float().to(DEV)
            model.enc.Ws[0][mi].copy_(Wj)
            model.enc.bs[0][mi].copy_(b1.view(1, -1))
            model.enc.Ws[1][mi].copy_(sol[:-1])
            model.enc.bs[1][mi].copy_(sol[-1:].view(1, -1))


def centroid2(model, mi, net, l, L, V, fr, fr_a, cls, n, lam, gseed):
    g = torch.Generator(device=DEV).manual_seed(gseed)
    H, A = net.sample(131072, {l}, g)
    h = A if l == L else H[l]
    x = inp(h, A, fr, fr_a, cls, 1)[0]
    nA = 98304
    M = model.enc.Ws[0].shape[0]
    K = model.dec.Ws[0].shape[1]
    reg = sn.BMLP(1, K, n, 512, 3, last_scale=0.0)
    opt = torch.optim.Adam(reg.parameters(), lr=3e-4)
    steps = a2.cent_steps
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * s / steps)))

    def codes(xb):
        with torch.no_grad():
            t = torch.full((M, xb.shape[0], 1), tof(lam), device=DEV)
            y = model.encode(xb.unsqueeze(0).expand(M, -1, -1), t)[mi]
            z = y + torch.randn(y.shape, generator=g, device=DEV)
            at = model.gain(t)[mi]
            zn = z * (at / (at * at + 1.0))
            ah = net.run(state(fr, model.decode(z.unsqueeze(0).expand(M, -1, -1), t)[mi]), l)
        return zn, ah

    hist = []
    for s in range(steps):
        idx = torch.randint(0, nA, (4096,), generator=g, device=DEV)
        zn, ah = codes(x[idx])
        loss = ((ah + reg(zn.unsqueeze(0))[0] - A[idx]) ** 2).sum(-1).mean() / V
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        hist.append(float(loss.detach()))
    with torch.no_grad():
        se_m, se_c = 0.0, 0.0
        for c0 in range(nA, x.shape[0], CH):
            zn, ah = codes(x[c0:c0 + CH])
            se_m += float(((ah - A[c0:c0 + CH]) ** 2).sum())
            se_c += float(((ah + reg(zn.unsqueeze(0))[0] - A[c0:c0 + CH]) ** 2).sum())
    nB = x.shape[0] - nA
    q = steps // 4
    return dict(lam=lam, nmse_model=se_m / nB / V, nmse_corrected=se_c / nB / V,
                train_loss_q3=float(np.mean(hist[2 * q:3 * q])), train_loss_q4=float(np.mean(hist[3 * q:])))


for name in names:
    outp = os.path.join(a2.out, 'X_' + name[2:] + '.json')
    if os.path.exists(outp):
        continue
    d = json.load(open(os.path.join(a2.runs, name + '.json')))
    kind, n, L, seed, l, cls = d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls']
    t1 = time.time()
    G['SQUASH'] = (kind == 'feistel')                       # state() reads the module global
    torch.manual_seed(1)
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
    fr = sn.frame(Hp[l]) if l < L else fr_a
    K = max(16, n)
    lr0, anchor = linref(net, l, L, V, fr, He, Ae, 99_000 + seed)
    U, ev, _ = anchor
    res = dict(cell=name, n=n, L=L, seed=seed, l=l, cls=cls, netkind=kind, V=V, V_cell=d['V'])
    # linear reference with held-out directional powers
    xe = (He[l] - fr['m']) @ fr['Sm12'] if l < L else (Ae - fr['m']) @ fr['Sm12']
    v = (xe.double() @ U).var(0)
    r2 = []
    for th in lr0['theta']:
        p = (ev / th - 1.0).clamp(min=0.0)
        r2.append(float((0.5 * torch.log2(1.0 + p * v)).sum()))
    res['linref'] = dict(rate=lr0['rate'], rate_heldout_power=r2, nmse=lr0['nmse'], v_min=float(v.min()), v_max=float(v.max()))
    # saved r0 model
    m1 = VR(6, n, cls, K, args.width, args.C, anchor, n)
    m1.load_state_dict(torch.load(os.path.join(a2.runs, name + '.pt'), map_location=DEV))
    m1.V = V
    res['centroid2'] = [centroid2(m1, 0, net, l, L, V, fr, fr_a, cls, n, lam, 88_000 + seed + 2) for lam in FIXED]
    xs = xe[:16384]
    gev = 88_000 + seed
    if cls == 'local':
        res['gates_r0'] = {str(lam): gate_activity(m1, 0, xs, lam) for lam in FIXED}
        torch.manual_seed(4242 + seed + l)
        mx = VR(3, n, cls, K, args.width, args.C, anchor, n)
        xp = ((Hp[l] if l < L else Ap)[:16384] - fr['m']) @ fr['Sm12']    # pilot samples (not the evaluation set)
        explorer_init(mx, net, l, fr, xp, U, kind, n, seed)
        res['gates_explorer_init'] = {str(lam): gate_activity(mx, 0, xs, lam) for lam in FIXED}
        res['explorer_init_data'] = 'pilot'
        base = 66_000 + seed * 7 + n * 13 + L * 101 + l * 3
        train(mx, 3, n, net, l, L, V, fr, fr_a, cls, a2.steps, [None, None, None], base)
        xe3 = inp(He[l], Ae, fr, fr_a, cls, 3)
        ev3 = evaluate(mx, 3, xe3, Ae, net, l, V, fr, GRID, gev)
        res['explorer'] = {f'x{i}': {k: ev3[k][i] for k in ev3} for i in range(3)}
        res['gates_explorer'] = {str(lam): [gate_activity(mx, i, xs, lam) for i in range(3)] for lam in FIXED}
        del mx
        torch.manual_seed(5353 + seed + l)
        mw = VR(1, n, cls, K, 2 * args.width, 2 * args.C, anchor, n)
        train(mw, 1, n, net, l, L, V, fr, fr_a, cls, a2.steps, [None], base + 9)
        ev1 = evaluate(mw, 1, xe3[:1], Ae, net, l, V, fr, GRID, gev)
        res['wdec'] = {k: ev1[k][0] for k in ev1}
        del mw
    summ = {}
    for nm, c in list(res.get('explorer', {}).items()) + ([('wdec', res['wdec'])] if 'wdec' in res else []):
        cr, sl = summarise(c['rate'], c['nmse'])
        summ[nm] = dict(cross=cr, slope=sl)
    cr, sl = summarise(r2, lr0['nmse'])
    summ['linref_heldout_power'] = dict(cross=cr, slope=sl)
    res['summary'] = summ
    res['seconds'] = time.time() - t1
    json.dump(res, open(outp, 'w'))
    fm = lambda v: '-' if v is None else f'{v:.2f}'  # noqa: E731
    print(name, f'{res["seconds"]:.0f}s', ' | '.join(f'{k}: R(0.1)={fm(s["cross"]["0.1"])} R(0.01)={fm(s["cross"]["0.01"])}'
                                                       for k, s in summ.items()),
          '| centroid2', [(round(c['nmse_model'], 4), round(c['nmse_corrected'], 4)) for c in res['centroid2']],
          '| gates r0', res.get('gates_r0'), flush=True)
print('ALL DONE', flush=True)
