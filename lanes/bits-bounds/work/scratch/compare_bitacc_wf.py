"""POST HOC companion to scratch/compare_bitacc.py: Gaussian reverse water-filling counts of the layer-l angular cloud
of the bit-accounting lane's ARC net (st.W_layer seed 4000), for the precision eps^2 = 0.1 of V.
The radial-merge residual is D_R(1) at the cloud's RMS spread phi_1 (results/compare_bitacc.json, times 0.972 for the
Gaussian-input normalisation). If the distortion scales like angle^pw (pw = 1 rough, pw = 2 smooth), reaching eps^2
needs an RMS angular error phi_1 (eps^2/D_R(1))^{1/pw}; the Gaussian rate for that squared error on the measured
angular covariance spectrum lambda_k is sum_k max(0, (1/2) log2(lambda_k/theta)), sum_k min(lambda_k, theta) = target.
Writes results/compare_bitacc_wf.json."""
import os
import sys
import json
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
sys.path.insert(0, '/home/agent/workspaces/mats/work/stationary/lib')
import bb
import st


def waterfill_bits(ev, target):
    lo, hi = 0.0, float(ev.max())
    for _ in range(200):
        th = 0.5 * (lo + hi)
        if np.minimum(ev, th).sum() > target:
            hi = th
        else:
            lo = th
    th = 0.5 * (lo + hi)
    return float(np.sum(np.maximum(0.0, 0.5 * np.log2(np.maximum(ev, 1e-300) / th))))


def main():
    seed, n, L = 4000, 256, 32
    W = [st.W_layer(seed, n, l) for l in range(1, L + 1)]
    rng = np.random.default_rng([seed, n, L, 11])
    U = bb.sphere(rng, 4096, n)
    cuts = [1, 2, 4, 8, 16, 24, 28, 31]
    H = bb.forward_keep(W, U, set(cuts))
    d = json.load(open(os.path.join(HERE, '..', 'results', 'compare_bitacc.json')))
    out = []
    for c in d['cuts']:
        l = c['l']
        ev = bb.cloud_angular_spectrum(H[l])
        D1 = c['D_R']['1'] * 0.972
        row = {'l': l, 'PR': c['PR'], 'D_R1_gauss_norm': D1,
               'formula_d_PR': max(0.0, c['PR'] * math.log2(D1 / 0.1)),
               'formula_d_1.4PR': max(0.0, c['PR'] / 0.72 * math.log2(D1 / 0.1))}
        for pw in (1, 2):
            row[f'waterfill_pw{pw}'] = 0.0 if D1 <= 0.1 else waterfill_bits(ev, float(ev.sum()) * (0.1 / D1) ** (2 / pw))
        out.append(row)
        print(json.dumps({k: (round(v, 1) if isinstance(v, float) else v) for k, v in row.items()}), flush=True)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'compare_bitacc_wf.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
