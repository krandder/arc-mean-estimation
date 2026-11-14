"""Post-hoc analyses of the registered runs (labelled POST HOC in the report):
1. the cloud-dimension law: PR against n/l (least squares PR = a n/l + b over all (net, l));
2. decay exponents gamma of D_best(M) (forward-only, M = 4..256) against 3/PR and 1/PR;
3. N_cell(l, eps) = log2 of the least grid M with D_best(M) <= eps^2 (interpolated log-linearly between grid points;
   "> 8" if none) for eps^2 = 0.1, 0.03, 0.01, medians per configuration;
4. ratio bias_best/(D_best/M), split by regime (rho = theta x L'/2 < 1 smooth, > 1 rough).
Output: results/posthoc.md"""
import os
import json
import glob
import math
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def ncell(e, eps2):
    Ms = [1, 4, 16, 64, 256]
    D = [e['fwd'][str(M)]['D_best'] if M > 1 else min(e['fwd']['1']['D_R'], e['fwd']['1']['D_F']) for M in Ms]
    for i, M in enumerate(Ms):
        if D[i] <= eps2:
            if i == 0:
                return 0.0
            # log-linear interpolation of log D in log M between grid points i-1 and i
            x0, x1 = math.log2(Ms[i - 1]), math.log2(M)
            y0, y1 = math.log(max(D[i - 1], 1e-300)), math.log(max(D[i], 1e-300))
            t = (math.log(eps2) - y0) / (y1 - y0) if y1 != y0 else 1.0
            return x0 + t * (x1 - x0)
    return float('inf')


def main():
    nets = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json')))]
    nets = [r for r in nets if not r.get('dead')]
    cfgs = sorted(set((r['n'], r['L']) for r in nets), key=lambda c: (c[1] / c[0], c[0]))
    L1 = ['# Post-hoc analyses (bits-bounds)', '']
    # 1. PR law
    X, Y = [], []
    for r in nets:
        for e in r['E1']:
            X.append(r['n'] / e['l'])
            Y.append(e['PR'])
    X, Y = np.array(X), np.array(Y)
    a, b = np.polyfit(X, Y, 1)
    resid = Y - (a * X + b)
    L1.append(f'## 1. Cloud dimension: PR = {a:.3f} (n/l) + {b:.2f}; R^2 = '
              f'{1 - resid.var() / Y.var():.3f}; {len(X)} (net, layer) points; median |relative residual| '
              f'{np.median(np.abs(resid) / Y):.2f}')
    L1.append('')
    # 2. gamma vs PR
    L1.append('## 2. Decay exponent gamma of D_best(M) (M = 4..256) and the implied dimension 3/gamma, 1/gamma')
    L1.append('')
    L1.append('| n x L | l | rho = theta L\'/2 | median PR | median gamma | 3/gamma | 1/gamma |')
    L1.append('|---|---|---|---|---|---|---|')
    for c in cfgs:
        rs = [r for r in nets if (r['n'], r['L']) == c]
        for li in range(len(rs[0]['E1'])):
            gs, prs, rhos = [], [], []
            for r in rs:
                e = r['E1'][li]
                Ms = [4, 16, 64, 256]
                D = [e['fwd'][str(M)]['D_best'] for M in Ms]
                gs.append(-np.polyfit(np.log(Ms), np.log(np.maximum(D, 1e-300)), 1)[0])
                prs.append(e['PR'])
                rhos.append(e['theta_median'] * e['Lp'] / 2)
            g = float(np.median(gs))
            L1.append(f'| {c[0]}x{c[1]} | {rs[0]["E1"][li]["l"]} | {np.median(rhos):.2f} | {np.median(prs):.2f} | '
                      f'{g:.3f} | {3 / g if g > 0 else float("inf"):.1f} | {1 / g if g > 0 else float("inf"):.1f} |')
    L1.append('')
    # 3. N_cell
    L1.append('## 3. N_cell(l, eps) in bits (forward-only references; medians over nets; inf = beyond 256 cells)')
    L1.append('')
    L1.append('| n x L | l | eps^2 = 0.1 | 0.03 | 0.01 |')
    L1.append('|---|---|---|---|---|')
    for c in cfgs:
        rs = [r for r in nets if (r['n'], r['L']) == c]
        for li in range(len(rs[0]['E1'])):
            row = [f'{c[0]}x{c[1]}', str(rs[0]['E1'][li]['l'])]
            for eps2 in [0.1, 0.03, 0.01]:
                v = float(np.median([ncell(r['E1'][li], eps2) for r in rs]))
                row.append('inf' if not np.isfinite(v) else f'{v:.1f}')
            L1.append('| ' + ' | '.join(row) + ' |')
    L1.append('')
    # 4. bias ratio by regime
    sm, ro = [], []
    for r in nets:
        for e in r['E1']:
            rho = e['theta_median'] * e['Lp'] / 2
            for M in [16, 64, 256]:
                d = e['fwd'][str(M)]
                q = d['bias_best'] / max(d['D_best'] / M, 1e-300)
                (sm if rho < 1 else ro).append(q)
    L1.append('## 4. bias_best / (D_best/M), M in {16, 64, 256}: median [10%, 90%]')
    L1.append('')
    for name, v in [('smooth (rho < 1)', sm), ('rough (rho >= 1)', ro)]:
        if v:
            L1.append(f'- {name}: {np.median(v):.2f} [{np.percentile(v, 10):.2f}, {np.percentile(v, 90):.2f}], '
                      f'{len(v)} cells')
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    open(os.path.join(ROOT, 'results', 'posthoc.md'), 'w').write('\n'.join(L1) + '\n')
    print('\n'.join(L1))


if __name__ == '__main__':
    main()
