"""Theory side of part A: spectra and reverse water-filling rates per layer for one net.

usage: theory_spectra.py arc 4000 [P]   -> results/theory_arc_4000.json
"""
import json
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bitlib as bl  # noqa: E402
import rwf  # noqa: E402

torch.set_num_threads(2)
kind, seed = sys.argv[1], int(sys.argv[2])
P = int(sys.argv[3]) if len(sys.argv) > 3 else 32768
layers = [0, 2, 4, 8, 16, 24, 31] if kind == 'arc' else [0, 8, 32, 64, 128, 192, 255]
net = bl.make_net(kind, seed)
t0 = time.time()
H, A = rwf.sample_layers(net, layers, P, seed=55_000 + seed)
V = float(A.var(0, ddof=1).sum())
ev_out = np.linalg.eigvalsh(np.cov(A, rowvar=False))[::-1]
eps_fine = list(np.exp(np.linspace(np.log(1e-4), np.log(0.9), 60)))
eps_rep = [0.1, 0.01, 0.001]
res = dict(net=kind, seed=seed, P=P, V=V, Ea2=float((A * A).sum(1).mean()), out_evals=ev_out.tolist(),
           rwf_out={str(e): rwf.rwf_rate(ev_out, e * V) for e in eps_rep},
           rwf_out_curve=[[float(e), rwf.rwf_rate(ev_out, e * V)] for e in eps_fine], layers={})
print('V', V, 'rwf_out', res['rwf_out'], f'{time.time() - t0:.0f}s', flush=True)
for l in layers:
    ev1 = rwf.lin_spectrum(H[l], A)
    V1 = float(ev1.sum())
    ev1p = np.maximum(ev1, 0.0)
    nas = min(P, 8192)
    evas, tras = rwf.as_spectrum(net, l, H[l][:nas], q=4, seed=l)
    ent = dict(V1=V1, s1=V1 / V, lin_evals=ev1.tolist(), as_evals=evas.tolist(), as_trace=tras, D_mean_degree=tras / V)
    # linear part to relative precision eps of V_1, and the linear code's best total error (needs eps V > V - V1)
    ent['rwf_lin_rel'] = {str(e): rwf.rwf_rate(ev1p, e * V1) for e in eps_rep}
    ent['rwf_lin_total'] = {str(e): (rwf.rwf_rate(ev1p, e * V - (V - V1)) if e * V > V - V1 else None)
                            for e in eps_rep}
    ent['rwf_as'] = {str(e): rwf.rwf_rate(evas, e * V) for e in eps_rep}
    ent['rwf_lin_curve'] = [[float(e), rwf.rwf_rate(ev1p, e * V1)] for e in eps_fine]
    ent['rwf_as_curve'] = [[float(e), rwf.rwf_rate(evas, e * V)] for e in eps_fine]
    # participation ratios
    ent['PR_out'] = float(ev_out.sum() ** 2 / (ev_out ** 2).sum())
    ent['PR_lin'] = float(ev1p.sum() ** 2 / (ev1p ** 2).sum())
    ent['PR_as'] = float(evas.sum() ** 2 / (evas ** 2).sum())
    res['layers'][str(l)] = ent
    print(l, 's1', round(V1 / V, 3), 'D', round(tras / V, 2), 'rwf_lin_rel', ent['rwf_lin_rel'], 'rwf_lin_total',
          ent['rwf_lin_total'], 'rwf_as', ent['rwf_as'], f'{time.time() - t0:.0f}s', flush=True)
os.makedirs('results', exist_ok=True)
with open(f'results/theory_{kind}_{seed}.json', 'w') as f:
    json.dump(res, f)
print('done', f'{time.time() - t0:.0f}s')
