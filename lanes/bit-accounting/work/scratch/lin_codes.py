"""Linear transform codes at every layer of one net (no training), both kinds, bases 'as' and 'lin'.

usage: lin_codes.py arc 4000 [P_fit P_eval]  -> runs/lin_arc_4000.json (dev seeds go to runs_dev/)
Layer L (output space) is included: there both bases are the output PCA.
"""
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bitlib as bl  # noqa: E402
import lincodes as lc  # noqa: E402

torch.set_num_threads(2)
kind, seed = sys.argv[1], int(sys.argv[2])
P_fit = int(sys.argv[3]) if len(sys.argv) > 3 else 16384
P_eval = int(sys.argv[4]) if len(sys.argv) > 4 else 8192
net = bl.make_net(kind, seed)
if kind == 'arc':
    layers = [0, 2, 4, 8, 16, 24, 31]
elif kind == 'nd':
    layers = [0, 8, 32, 64, 128, 192, 255]
else:
    layers = sorted(set([0, net.L // 4, net.L // 2, (3 * net.L) // 4, net.L - 1]))
layers = layers + [net.L]
# processing order (optional 5th argument, comma-separated); results are saved after every layer
order = [int(v) for v in sys.argv[5].split(',')] if len(sys.argv) > 5 else layers
t0 = time.time()


def sample(P, s):
    rng = np.random.default_rng(s)
    H = {}
    h = rng.standard_normal((P, net.n))
    for k in range(net.L + 1):
        if k in layers:
            H[k] = h.copy()
        if k < net.L:
            h = np.maximum(h @ net.WT64[k], 0.0)
    return H, h


Hf, Af = sample(P_fit, 91_000 + seed)
He, Ae = sample(P_eval, 92_000 + seed)
V = float(Ae.var(0, ddof=1).sum())
Vf = float(Af.var(0, ddof=1).sum())
rates_b = [1, 2, 3, 4, 6, 8, 11, 16, 23, 32, 45, 64, 91, 128, 181, 256]
rates_c = bl.gauss_grid(256)
if kind.startswith('small'):
    rates_b = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
    rates_c = [1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0]
rng = np.random.default_rng(93_000 + seed)
res = dict(net=kind, seed=seed, P_fit=P_fit, P_eval=P_eval, V=V, V_fit=Vf, layers={})
outdir = 'runs' if seed < 9000 else 'runs_dev'
for l in order:
    fr = lc.frame(Hf[l])
    ent = {}
    bases = {'lin': lc.basis_lin(Hf[l], Af, fr)}
    if l < net.L:
        bases['as'] = lc.basis_as(net, l, Hf[l][:4096], fr, q=4, seed=l)
    for bname, (lam, Q) in bases.items():
        for ck in ['bin', 'gauss']:
            curve = lc.eval_linear(net, l, fr, lam, Q, He[l], Ae, V, rates_b if ck == 'bin' else rates_c, ck, rng)
            cr = {str(e): bl.crossing(curve, e) for e in [0.1, 0.01, 0.001]}
            ent[f'{bname}_{ck}'] = dict(curve=curve, cross=cr)
        ent[f'{bname}_evals'] = lam[:256].tolist()
    res['layers'][str(l)] = ent
    print(l, {k: v['cross'] for k, v in ent.items() if isinstance(v, dict) and 'cross' in v}, f'{time.time() - t0:.0f}s',
          flush=True)
    with open(f'{outdir}/lin_{kind}_{seed}.json', 'w') as f:
        json.dump(res, f)
print('done', f'{time.time() - t0:.0f}s')
