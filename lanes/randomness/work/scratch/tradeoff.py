"""Descriptive trade-off table at 256 x 32 (nets 200-204): nMSE x N (plain MC = 1) against N for every sampler, the
random bits each uses, and the median gain over MC; from runs/{struct,combo,rates,det}_*. Writes results/tradeoff.json
and prints a table. Not a scorer (the registered outcomes are in score.py and rate_fit.py)."""
import json
import os
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
S = [200, 201, 202, 203, 204]
n, b = 256, 32
BITS = {'mc': 'N n b', 'mc_pairwise': f'{2 * n * b}', 'rqmc_std': f'{n * b * (b - 1) // 2 + n * b}',
        'rqmc_polar': f'{n * b * (b - 1) // 2 + n * b}', 'kerdock': f'{n * (n - 1) // 2 * b}', 'det_std': '0',
        'det_polar': '0', 'lattice_rb': '0', 'kwise2_rb': '0', 'kerdock_fixed_rb': '0'}


def load(kind, s):
    p = os.path.join(ROOT, 'runs', f'{kind}_n256_L32_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


tab = {}
for s in S:
    st, co, ra, dt = load('struct', s), load('combo', s), load('rates', s), load('det', s)
    if ra:
        for fr in ('std', 'polar'):
            for x in ra['series'][f'rqmc_{fr}']:
                tab.setdefault(f'rqmc_{fr}', {}).setdefault(x['N'], []).append(x['var_x_N_over_V'])
    if st:
        for fr in ('std', 'polar'):
            for m in (10, 12, 14):
                x = st['rqmc'][f'rqmc_rb_{fr}_m{m}']
                tab.setdefault(f'rqmc_{fr}', {}).setdefault(x['m'], []).append(x['inv_gain_mc'])
        x = st['designs']['kerdock']
        tab.setdefault('kerdock', {}).setdefault(x['m'], []).append(x['inv_gain_mc'])
        tab.setdefault('rb_mc', {}).setdefault(1, []).append(st['rho_rb'])
    if co:
        for k in ('rqmc_std', 'rqmc_polar', 'kerdock', 'mc_pairwise'):
            x = co['methods'][k]
            tab.setdefault(k + '_vs_truth', {}).setdefault(x['points'], []).append(x['nmse_mean'] * x['points'])
        for k in ('det_std', 'det_polar'):
            x = co['methods'][k]
            tab.setdefault(k, {}).setdefault(x['points'], []).append(x['nmse_mean'] * x['points'])
    if dt:
        for name in ('sobol_rb', 'sobol_rb_polar', 'lattice_rb', 'lattice_baker_rb', 'kwise2_rb', 'kerdock_fixed_rb',
                     'kerdock_polar_rb'):
            for x in dt['series'].get(name, []):
                tab.setdefault(name, {}).setdefault(x['N'], []).append(x['nmse_x_N'])
out = {}
for k, d in tab.items():
    out[k] = {int(N): dict(median=float(np.median(v)), min=float(min(v)), max=float(max(v)), nets=len(v))
              for N, v in sorted(d.items())}
json.dump(out, open(os.path.join(ROOT, 'results', 'tradeoff.json'), 'w'), indent=1)
for k, d in out.items():
    print(f'{k:22s} bits={BITS.get(k.replace("_vs_truth", ""), "-"):>10s} | ' +
          ' '.join(f'2^{int(np.log2(N)) if N > 1 else 0}:{v["median"]:.3f}({v["nets"]})' for N, v in d.items()))
