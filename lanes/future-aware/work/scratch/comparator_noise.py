"""POST HOC: how noisy is the RQMC comparator? arc-update's curves are means over 8 scrambles per N. The H1 direct rerun
(runs/hybd_*.json) measured plain RQMC on 8 OTHER scrambles per N on the same nets (seed * 1000 + 17 m + r). This
compares the two independent estimates per point and recomputes the main window gains against the pooled 16-scramble
curve (the average of the two means) where both exist. Side-effect free apart from results/comparator_noise.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402

out = {}
for n, L, seeds in S.CONF:
    ratios = []; G = {'k2': ([], []), 'D1_Cded': ([], []), 'D1_impl': ([], [])}
    for s in seeds:
        p = os.path.join(S.RUNS, f'hybd_n{n}_L{L}_s{s}.json')
        if not os.path.exists(p):
            continue
        D = json.load(open(p))
        Na, ea = S.rqmc_curve(n, L, s)
        own = {int(2 ** int(m)): float(np.mean(v)) for m, v in D['plain'].items()}
        common = [N for N in Na if int(N) in own]
        for N in common:
            ratios.append(float(ea[list(Na).index(N)] / own[int(N)]))
        pooled = (np.array([N for N in Na if int(N) in own], float),
                  np.array([0.5 * (ea[list(Na).index(N)] + own[int(N)]) for N in Na if int(N) in own]))
        d = S.load('k3p', n, L, s)
        if d is None:
            continue
        cur = (Na, ea)
        G['k2'][0].append(S.rqmc_err(cur, d['k2']['passes'])[0] / d['k2']['nmse'])
        G['k2'][1].append(S.rqmc_err(pooled, d['k2']['passes'])[0] / d['k2']['nmse'])
        r = d['variants'].get(f'futmf2_{n // 4}')
        if r is not None and np.isfinite(r['nmse']):
            k = n // 4
            c0 = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + 2.0 * n
            G['D1_Cded'][0].append(S.rqmc_err(cur, c0)[0] / r['nmse'])
            G['D1_Cded'][1].append(S.rqmc_err(pooled, c0)[0] / r['nmse'])
            G['D1_impl'][0].append(S.rqmc_err(cur, r['passes'])[0] / r['nmse'])
            G['D1_impl'][1].append(S.rqmc_err(pooled, r['passes'])[0] / r['nmse'])
    if not ratios:
        continue
    out[n] = dict(arc_over_other=dict(median=S.med(ratios), min=min(ratios), max=max(ratios), points=len(ratios)),
                  gains={k: dict(arc_curve=S.med(v[0]), pooled_curve=S.med(v[1])) for k, v in G.items()})
json.dump(out, open(os.path.join(S.RES, 'comparator_noise.json'), 'w'), indent=1)
for n, v in out.items():
    a = v['arc_over_other']
    print(f'n = {n}: arc-update / other-8-scramble plain RQMC per point: median {a["median"]:.2f}, range {a["min"]:.2f}-'
          f'{a["max"]:.2f} ({a["points"]} points); gains arc curve -> pooled: ' +
          ', '.join(f'{k} {g["arc_curve"]:.3g} -> {g["pooled_curve"]:.3g}' for k, g in v['gains'].items()))
