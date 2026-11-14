"""Theory references for the small nets (S1): reverse water-filling over eig Cov(a) (layer-free; attained in output
space by the linear analog code), over the active-subspace spectrum at each layer (local high-resolution price) and the
participation ratios; the cloud's rank. -> results/theory_small.json"""
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import bitlib as bl  # noqa: E402
import rwf  # noqa: E402

torch.set_num_threads(1)
CFG = [(16, 4), (16, 16), (32, 8), (32, 32)]
SEEDS = [9100, 5000, 5001, 5002]
EPS = [0.1, 0.01, 0.001]
RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
out = {}
for n, L in CFG:
    for s in SEEDS:
        net = bl.FixedNet([bl.st.W_layer(s, n, k) for k in range(1, L + 1)], f'S_n{n}_L{L}_s{s}')
        layers = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
        H, A = rwf.sample_layers(net, layers, 65536, seed=55_000 + s)
        V = float(A.var(0, ddof=1).sum())
        ev = np.linalg.eigvalsh(np.cov(A, rowvar=False))[::-1]
        # distortion-rate of the linear analog code at the grid rates (nMSE), from the output spectrum
        D_of_R = []
        for R in RATES:
            lo, hi = 1e-300, float(ev[0])
            for _ in range(300):
                mid = np.sqrt(lo * hi)
                Rm = np.maximum(0, 0.5 * np.log2(np.maximum(ev, 1e-300) / mid)).sum()
                lo, hi = (mid, hi) if Rm > R else (lo, mid)
            D_of_R.append(float(np.minimum(ev, hi).sum() / V))
        ent = dict(V=V, out_evals=ev.tolist(), PR_out=float(ev.sum() ** 2 / (ev ** 2).sum()),
                   rwf_out={str(e): rwf.rwf_rate(ev, e * V) for e in EPS}, lin_analog_nmse=D_of_R, layers={})
        for l in layers:
            evas, tr = rwf.as_spectrum(net, l, H[l][:8192], q=4, seed=l)
            c = np.linalg.eigvalsh(np.cov(H[l], rowvar=False))[::-1]
            ent['layers'][str(l)] = dict(rwf_as={str(e): rwf.rwf_rate(evas, e * V) for e in EPS}, D_mean_degree=tr / V,
                                         cloud_rank=int((c > 1e-10 * c[0]).sum()),
                                         cloud_PR=float(c.sum() ** 2 / (c ** 2).sum()))
        out[f'n{n}_L{L}_s{s}'] = ent
        print(n, L, s, 'V', round(V, 4), 'PR_out', round(ent['PR_out'], 2), 'rwf_out', {k: round(v, 2) for k, v in ent['rwf_out'].items()},
              'rwf_as(0.1) by layer', {k: round(v['rwf_as']['0.1'], 1) for k, v in ent['layers'].items()}, flush=True)
os.makedirs('results', exist_ok=True)
json.dump(out, open('results/theory_small.json', 'w'))
