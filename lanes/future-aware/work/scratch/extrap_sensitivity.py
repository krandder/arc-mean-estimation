"""POST HOC (GPT-6 review rounds 1-2, finding 13): sensitivity of the extrapolated RQMC comparisons in section 4.4.
The registered rule extrapolates RQMC's error outside the measured range with slope -1 from the nearest end. Here each
extrapolated cell is recomputed with (a) slope -1 (registered), (b) the net's local slope between its two measured
points nearest that end, (c) a bounding slope against the stated conclusion: -0.5 beyond the top end (RQMC flattening,
against "the method loses"), -0.8 below the bottom end (RQMC flatter at small N, against "the method wins").
Gain G = RQMC error at the method's cost / the method's error; median over nets. Side-effect free apart from writing
results/extrap_sensitivity.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402


def err_at(curve, C, mode):
    N, e = curve
    if N[0] <= C <= N[-1]:
        return float(np.exp(np.interp(np.log(C), np.log(N), np.log(e)))), False
    top = C > N[-1]
    if top:
        local = np.log(e[-1] / e[-2]) / np.log(N[-1] / N[-2]); N0, e0 = N[-1], e[-1]
    else:
        local = np.log(e[1] / e[0]) / np.log(N[1] / N[0]); N0, e0 = N[0], e[0]
    slope = {'reg': -1.0, 'local': local, 'bound': (-0.5 if top else -0.8)}[mode]
    return float(e0 * (C / N0) ** slope), True


cells = {}
for n, L, seeds in S.CONF:
    rows = {'k2 simple': [], 'D1 mean-field n/4 as implemented': [], 'D1 PCA n/8 at C_ded': [],
            'B2 future n/2 particles': []}
    for s in seeds:
        cur = S.rqmc_curve(n, L, s)
        d = S.load('k3p', n, L, s)
        if d is not None:
            rows['k2 simple'].append((d['k2']['passes'], d['k2']['nmse'], cur))
            r = d['variants'].get(f'futmf2_{n // 4}')
            if r is not None and np.isfinite(r['nmse']):
                rows['D1 mean-field n/4 as implemented'].append((r['passes'], r['nmse'], cur))
            r = d['variants'].get(f'pca{n // 8}')
            if r is not None and np.isfinite(r['nmse']):
                k = n // 8
                rows['D1 PCA n/8 at C_ded'].append((d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2, r['nmse'], cur))
        d = S.load('rec', n, L, s)
        if d is not None:
            r = d['variants'].get(f'futnl{n // 2}')
            if r is not None and 'passes_per_rep' in r:
                rows['B2 future n/2 particles'].append((r['passes_per_rep'], float(np.mean(r['nmse_reps'])), cur))
    for name, lst in rows.items():
        if not lst:
            continue
        out = {}
        for mode in ('reg', 'local', 'bound'):
            G = []; ex = 0
            for C, e, cur in lst:
                er, x = err_at(cur, C, mode); G.append(er / e); ex += int(x)
            out[mode] = S.med(G)
        out['extrapolated_nets'] = ex; out['nets'] = len(lst)
        out['median_cost'] = S.med([c for c, _, _ in lst])
        out['max_extrapolation_factor'] = max(max(C / cur[0][-1], cur[0][0] / C) for C, _, cur in lst)
        cells[f'{n}: {name}'] = out
json.dump(cells, open(os.path.join(S.RES, 'extrap_sensitivity.json'), 'w'), indent=1)
for k, v in cells.items():
    print(f'{k:45s} cost {v["median_cost"]:.3g} (extrap. {v["extrapolated_nets"]}/{v["nets"]} nets, up to '
          f'{v["max_extrapolation_factor"]:.3g}x): G slope -1 {v["reg"]:.3g}, local {v["local"]:.3g}, bound {v["bound"]:.3g}')
