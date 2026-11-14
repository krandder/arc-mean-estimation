"""Per-layer analytic reference curves (Kelvin 03:20Z): a linear code on a future-weighted spectrum with reverse
water-filled power, decoded by linear MMSE, evaluated through the real net.

At layer l, in whitened coordinates y (h = m + y T, unit covariance on the data's span), J = d a / d y:
  'gram'  G = E_true[J^T J] (cloud-averaged Jacobian Gram; the bit-accounting lane's linref; the anchor of the codes)
  'mean'  R_1 = E_true[J]^T E_true[J] (cloud-averaged Jacobian, true law)
  'gauss' R_1 with E[J] under the relevance lane's Gaussian convention h ~ N(m, S)
For each spectrum (eigenpairs lam_k, v_k): at lambda = 10^t, theta = lambda V / (2 ln 2), SNR_k = max(0, lam_k/theta - 1),
z_k = g_k v_k.y + eps_k; y_hat = sum_k v_k g_k / (1 + g_k^2) z_k; h_hat = m + y_hat T; a_hat = real future(h_hat)
(the output cell clips to a >= 0 like the learned output decoders). Reported per t: capacity rate
sum (1/2) log2(1 + SNR_k); information rate with fresh priors on held-out codes (same estimator as the learned codes:
vrlib.refit_rates, the triangular family); nMSE; the linear-Gaussian prediction (V - tr R + sum min(lam_k, theta)) / V;
error of the output mean. In the linear-Gaussian approximation this is the optimal code (uncoded transmission of the
water-filled components). Held-out inputs = those of the learned codes (vrlib.heldout_x).
usage: ref_curve.py --family arc --seeds 4000 --layers 0,2,4 --out /root/runs/REF
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
ap.add_argument('--layers', default='0')
ap.add_argument('--toy_k', type=int, default=0)
ap.add_argument('--P_jac', type=int, default=8192)
ap.add_argument('--P_eval', type=int, default=32768)
ap.add_argument('--tmin', type=float, default=-6.0)
ap.add_argument('--tmax', type=float, default=0.0)
ap.add_argument('--t_step', type=float, default=0.5)                 # A5: 13 points (refits are costly)
ap.add_argument('--out', required=True)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
torch.backends.cuda.matmul.allow_tf32 = False
DEV, DT = vr.DEV, torch.float32
tag_fam = args.family if args.family != 'toy' else f'toy{args.toy_k}'


def run_layers(WT, act, h, l0, l1):
    for k in range(l0, l1):
        h = h @ WT[k]
        if act == 'relu':
            h = torch.relu(h)
    return h


for seed in [int(s) for s in args.seeds.split(',')]:
    Ws, act = vr.family_weights(args.family, seed, args.toy_k)
    L = len(Ws)
    n = Ws[0].shape[1]
    WT = [torch.tensor(np.ascontiguousarray(W.T), dtype=DT, device=DEV) for W in Ws]
    for l in [int(v) for v in args.layers.split(',')]:
        path = os.path.join(args.out, f'REF_{tag_fam}_s{seed}_l{l}.json')
        if os.path.exists(path):
            continue
        T0 = time.time()
        st = vr.pilot_stats(Ws, act, l, P=65536, seed=10_000 + seed)
        V = st['V']
        fh = st['h'] if l < L else st['a']
        m = torch.tensor(fh['m'], dtype=DT, device=DEV)
        T = torch.tensor(fh['T'], dtype=DT, device=DEV)
        Sm12 = torch.tensor(fh['Sm12'], dtype=DT, device=DEV)
        if l < L:
            Gt, Bt = vr.jac_stats(Ws, act, l, fh, P=args.P_jac, seed=seed)
            _, Bg = vr.jac_stats(Ws, act, l, fh, P=args.P_jac, seed=seed + 1, cloud='gauss')
            spectra = dict(gram=Gt, mean=Bt.T @ Bt, gauss=Bg.T @ Bg)
        else:
            C = fh['S12'] @ fh['S12']
            spectra = dict(gram=C, mean=C, gauss=C)
        x_ev = vr.heldout_x(seed, args.P_eval, n)
        h_ev = run_layers(WT, act, x_ev, 0, l)
        a_ev = run_layers(WT, act, h_ev, l, L)
        y_ev = (h_ev - m) @ Sm12
        res = dict(family=args.family, toy_k=args.toy_k, seed=seed, layer=l, L=L, n=n, V=V,
                   out_evals=[float(v) for v in st['a']['evals']], refs={})
        t_grid = list(np.round(np.arange(args.tmin, args.tmax + 1e-9, args.t_step), 4))
        for name, Sp in spectra.items():
            lam, Vv = vr.eig_desc(Sp)
            lam_t = torch.tensor(lam, device=DEV, dtype=torch.float64)
            Vf = torch.tensor(Vv, device=DEV, dtype=DT)
            nu = y_ev @ Vf                                              # (P, n) unit-variance components
            curve = []
            for ti, tv in enumerate(t_grid):
                th = (10.0 ** tv) * V / (2 * math.log(2))
                snr = (lam_t / th - 1.0).clamp(min=0.0)
                g = snr.sqrt().float()
                ng = torch.Generator(device=DEV).manual_seed(seed + 1000 + ti)
                z = g * nu + torch.randn(nu.shape, generator=ng, device=DEV, dtype=DT)
                yhat = (z * (g / (1.0 + g * g))) @ Vf.T
                hh = m + yhat @ T
                ah = run_layers(WT, act, hh, l, L) if l < L else (torch.relu(hh) if act == 'relu' else hh)
                d = (ah - a_ev).double()
                D = (d * d).sum(1) / V
                md = d.mean(0)
                act_k = snr > 0
                rec = dict(t=float(tv), rate_cap=float(0.5 * torch.log2(1.0 + snr).sum()), nmse=float(D.mean()),
                           nmse_se=float(D.std() / math.sqrt(len(D))), mean_err=float((md * md).sum() / V),
                           n_sent=int(act_k.sum()),
                           D_lin=(V - float(lam_t.sum()) + float(torch.clamp(lam_t, max=th).sum())) / V)
                if bool(act_k.any()):
                    rr = vr.refit_rates(z[:, act_k], g[act_k], torch.ones(int(act_k.sum()), device=DEV), tc=False,
                                        kinds=('fact',))
                    rec['rate'] = min(rr['rate_refit_fact'], rec['rate_cap'])     # A5: both upper-bound the information
                    rec.update(rr)
                else:
                    rec['rate'] = 0.0
                curve.append(rec)
            res['refs'][name] = dict(lam=[float(v) for v in lam], trace=float(lam.sum()), s=float(lam.sum()) / V,
                                     curve=curve)
        res['seconds'] = time.time() - T0
        json.dump(res, open(path, 'w'))
        print(f'REF {tag_fam} s{seed} l{l}: V {V:.3f} tr/V gram {res["refs"]["gram"]["s"]:.3f} mean '
              f'{res["refs"]["mean"]["s"]:.3f} gauss {res["refs"]["gauss"]["s"]:.3f} ({res["seconds"]:.0f}s)', flush=True)
