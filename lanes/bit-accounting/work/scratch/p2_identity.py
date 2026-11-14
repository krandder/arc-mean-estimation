"""Phase 2, P2.0 measurement (1) (registered 04:01Z; approved by main 15:5xZ to run on the CPU): how far the
identity-anchored P1 codes are from a linear function of the layer, rotation-invariant. For each finished P1 cell
(model r0 of the saved G1 group) and lambda in {0.1, 0.01, 0.001}, on 16384 held-out states:
  lin_share = R^2 of the best linear map from the whitened h_l to the code mean y (variance-weighted over latents);
  k         = latents with Var(y_i) > 1 (signal above the unit noise);
  cos2_G    = mean cos^2 of the principal angles between the top-k right singular vectors of that linear map and the
              top-k eigenvectors of G = E[J^T J] (the future-weighted Jacobian spectrum: the linearisation from the
              output back to layer l).
Descriptive (not registered): G_capture = tr(Qa' G Qa) / (sum of the top-k eigenvalues of G): the share of the
future-weighted Jacobian energy that the code's k directions capture, relative to the best k directions (robust to
near-degenerate eigenvalues); gate_active = share of the local encoder's ReLU units whose gate switches inside the
data cloud (active on 5-95% of inputs); 0 means the encoder is affine on the data.
usage (CPU): python scratch/p2_identity.py runs/P1 <part i> <parts k> <out.json>"""
import json
import os
import sys

import numpy as np
import torch

W = '/home/agent/workspaces/mats/work/bit-accounting'
RUNS = sys.argv[1] if len(sys.argv) > 1 else f'{W}/runs/P1'
PART, NPART = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
OUT = sys.argv[4] if len(sys.argv) > 4 else f'{W}/results/P2_identity.json'
src = open(f'{W}/gpu_src/scripts/run_vr.py').read()
src = src[:src.index("for cfg in args.configs.split(','):")]
sys.argv = ['run_vr.py', '--out', '/tmp/p2_unused', '--threads', '2']
G = {'__file__': f'{W}/gpu_src/scripts/run_vr.py', '__name__': 'run_vr_defs'}
exec(compile(src, 'run_vr.py', 'exec'), G)
sn, DEV, VR, linref, tof = G['sn'], G['DEV'], G['VR'], G['linref'], G['tof']
out = json.load(open(OUT)) if os.path.exists(OUT) else {}
names = sorted(f for f in os.listdir(RUNS) if f.startswith('P_') and f.endswith('.json')
               and os.path.exists(f'{RUNS}/{f[:-5]}.pt'))
names = [f for i, f in enumerate(names) if i % NPART == PART]
for f in names:
    if f[:-5] in out:
        continue
    d = json.load(open(f'{RUNS}/{f}'))
    kind, n, L, seed, l, cls = d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls']
    G['SQUASH'] = (kind == 'feistel')
    net = sn.Net(seed, n, L, kind=kind)
    layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    gp = torch.Generator(device=DEV).manual_seed(10_000 + seed * 7 + n * 13 + L)
    Hp, Ap = net.sample(65536, set(layers), gp)
    Hp[L] = Ap
    V = float(Ap.double().var(0).sum())
    fr_a = sn.frame(Ap)
    fr = sn.frame(Hp[l]) if l < L else fr_a
    ge = torch.Generator(device=DEV).manual_seed(20_000 + seed * 7 + n * 13 + L)
    He, Ae = net.sample(16384, set(layers), ge)
    He[L] = Ae
    _, anchor = linref(net, l, L, V, fr, He, Ae, 99_000 + seed, P=8192, NT=2)
    U, ev, _ = anchor
    K = max(16, n)
    sd = torch.load(f'{RUNS}/{f[:-5]}.pt', map_location=DEV)
    sd = {k: (v[0:1] if v.dim() > 0 and v.shape[0] == 6 else v) for k, v in sd.items()}   # model r0 only
    m = VR(1, n, cls, K, 256, 4, anchor, n)
    m.load_state_dict(sd)
    m.V = V
    x = G['inp'](He[l], Ae, fr, fr_a, cls, 1)
    xw = x[0, :, :n].double()
    res = {}
    with torch.no_grad():
        for lam in (0.1, 0.01, 0.001):
            t = torch.full((1, x.shape[1], 1), tof(lam), device=DEV)
            y = m.encode(x, t)[0].double()
            var = y.var(0)
            A = torch.cat([xw, torch.ones(xw.shape[0], 1, dtype=torch.float64)], 1)
            coef = torch.linalg.lstsq(A, y).solution
            resid = y - A @ coef
            share = float(1.0 - resid.var(0).sum() / var.sum().clamp(min=1e-12))
            k = int((var > 1.0).sum())
            cos2, gcap = None, None
            if k > 0:
                Wl = coef[:-1].T                                   # (K, n): y ~ Wl x
                Vh = torch.linalg.svd(Wl, full_matrices=False)[2]
                Qa = Vh[:k].T                                      # the code's active input directions
                Ud = U.double().cpu()
                Qg = Ud[:, :k]
                sv = torch.linalg.svdvals(Qa.T @ Qg)
                cos2 = float((sv ** 2).mean())
                evd = ev.double().cpu()
                gcap = float(((Ud.T @ Qa) ** 2).sum(1) @ evd / evd[:k].sum().clamp(min=1e-30))   # tr(Qa' G Qa) / best
            gate = None
            if cls == 'local':
                f_ = m.enc.film(t)
                w = m.enc.width
                pre = (1.0 + f_[..., :w]) * torch.baddbmm(m.enc.bs[0], x, m.enc.Ws[0]) + f_[..., w:2 * w]
                act = (pre[0] > 0).double().mean(0)
                gate = float(((act > 0.05) & (act < 0.95)).double().mean())
            res[str(lam)] = dict(lin_share=share, k=k, cos2_G=cos2, G_capture=gcap, gate_active=gate)
    out[f[:-5]] = dict(kind=kind, n=n, L=L, seed=seed, l=l, cls=cls, **res)
    print(f[:-5], {q: (round(r['lin_share'], 3), r['k'], None if r['cos2_G'] is None else round(r['cos2_G'], 3),
                       None if r['G_capture'] is None else round(r['G_capture'], 3), r['gate_active'])
                   for q, r in res.items()}, flush=True)
    json.dump(out, open(OUT, 'w'), indent=1)
print('ALL DONE', flush=True)
