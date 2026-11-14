"""POST HOC companion to the hashed Amendment 1 scorer (scratch/score_amend1.py): the n = 512 rows for the report's
window table and the k = n/8 substitutes for P11/P12, whose registered k = n/4 = 128 runs fail numerically at n = 512
(NaN; with the rank guard of lib/fa_kprop_guard.py they diverge). Side-effect free apart from
results/amend1_posthoc.json. RQMC at n = 512: this lane's curves (8 scrambles, N = 2^8..2^14), the scorer's rule
(log-log interpolation, slope -1 outside, labelled)."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402


def curve(n, L, s):
    p = os.path.join(S.RUNS, f'rqmc_n{n}_L{L}_s{s}.json')
    if os.path.exists(p):
        d = json.load(open(p))
        return np.array([r['N'] for r in d['rows']], float), np.array([r['mean_nmse'] for r in d['rows']], float)
    return S.rqmc_curve(n, L, s)


def width(n, L, seeds, k8):
    out = dict(nets=[], k2=[], k3=[], q3=[], k2G=[], k3G=[], ret={}, Gimpl={}, Gded=[], Gded_pilot=[], C_ded=[],
               Gded_pilot_dense=[], rqmc=[])
    for s in seeds:
        d = S.load('k3p', n, L, s)
        if d is None or 'none' not in d['variants']:
            continue
        cur = curve(n, L, s)
        out['nets'].append(s)
        out['rqmc'].append(dict(zip([int(x) for x in cur[0]], cur[1].tolist())))
        e2, c2 = d['k2']['nmse'], d['k2']['passes']; e3 = d['variants']['none']['nmse']
        out['k2'].append(e2); out['k3'].append(e3); out['q3'].append(e2 / e3)
        out['k2G'].append(S.rqmc_err(cur, c2)[0] / e2)
        out['k3G'].append(S.rqmc_err(cur, d['variants']['none']['passes'])[0] / e3)
        for v, r in d['variants'].items():
            if v == 'none':
                continue
            gp = os.path.join(S.RUNS, f'k3p_n{n}_L{L}_s{s}_guard.json')
            e = r['nmse']
            if not np.isfinite(e) and os.path.exists(gp):
                g = json.load(open(gp))['variants'].get(v)
                e = g['nmse'] if g is not None else e
                v = v + ' (guarded)'
            out['ret'].setdefault(v, []).append(e3 / e if np.isfinite(e) else float('nan'))
            out['Gimpl'].setdefault(v, []).append(S.rqmc_err(cur, r['passes'])[0] / e if np.isfinite(e) else float('nan'))
        r = d['variants'].get(f'futmf2_{k8}')
        if r is not None and np.isfinite(r['nmse']):
            cd = c2 + k8 + 1.5 * k8 ** 4 / n ** 2 + 2.0 * n
            dense = 26.0 * n ** 3 * (L - 1) / (2.0 * n * n * L)
            out['C_ded'].append(cd)
            out['Gded'].append(S.rqmc_err(cur, cd)[0] / r['nmse'])
            out['Gded_pilot'].append(S.rqmc_err(cur, cd + c2)[0] / r['nmse'])
            out['Gded_pilot_dense'].append(S.rqmc_err(cur, cd + c2 + dense)[0] / r['nmse'])
    med = {k: S.med(v) for k, v in out.items() if isinstance(v, list) and v and not isinstance(v[0], dict)
           and k != 'nets'}
    med['ret'] = {v: S.med(x) for v, x in out['ret'].items()}
    med['Gimpl'] = {v: S.med(x) for v, x in out['Gimpl'].items()}
    return out, med


res = {}
for n, L, seeds, k8 in ((256, 32, list(range(200, 205)), 32), (512, 64, [500, 501, 502], 64)):
    raw, med = width(n, L, seeds, k8)
    res[n] = dict(raw=raw, median=med)
json.dump(res, open(os.path.join(S.RES, 'amend1_posthoc.json'), 'w'), indent=1, default=float)
for n, r in res.items():
    m = r['median']
    print(f'n = {n} ({len(r["raw"]["nets"])} nets): k2 {m["k2"]:.2e} (G {m["k2G"]:.2f}), k3 {m["k3"]:.2e} (G at its cost '
          f'{m["k3G"]:.3f}), q3 = e2/e3 {m["q3"]:.2f}; D1 futmf2 n/8: G at C_ded {m.get("Gded", float("nan")):.2f}, + pilot '
          f'{m.get("Gded_pilot", float("nan")):.2f}, + pilot + dense extraction {m.get("Gded_pilot_dense", float("nan")):.2f} '
          f'(C_ded {m.get("C_ded", float("nan")):.0f})')
    print('   retained e3/e:', {v: round(x, 3) for v, x in m['ret'].items()})
    print('   G at implemented cost:', {v: round(x, 4) for v, x in m['Gimpl'].items()})
