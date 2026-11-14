"""Descriptive ladder table from the structure runs (medians over nets per width; [min, max] where useful)."""
import json, glob, numpy as np, sys
W = {32: (4, range(300, 308)), 64: (8, range(300, 308)), 128: (16, range(300, 308)), 256: (32, range(200, 205))}
def sh(r):
    V, Vrb = r['V'], r['V_rb']; d = r['designs']; rel = lambda k: d[k]['inv_gain_mc'] / (Vrb / V)
    o = dict(odd=r['V_odd'] / Vrb, even=r['V_even'] / Vrb, le2=1 - rel('simplex'), E2=1 - rel('onb'), ev4=rel('cross') / 2)
    o['E1'] = o['le2'] - o['E2']
    if 'kerdock' in d: o['ev6'] = rel('kerdock') / 2; o['g_kerdock'] = 1 / d['kerdock']['inv_gain_mc']
    o['g_simplex'] = 1 / d['simplex']['inv_gain_mc']; o['g_cross'] = 1 / d['cross']['inv_gain_mc']; o['g_onb'] = 1 / d['onb']['inv_gain_mc']
    for fr in ('std', 'polar', 'svd'):
        for m in (10, 12, 14):
            o[f'rq_{fr}_{m}'] = 1 / r['rqmc'][f'rqmc_rb_{fr}_m{m}']['inv_gain_mc']
    for fr in ('std', 'polar'):
        for m in (12, 14):
            o[f'anti_{fr}_{m}'] = 1 / r['rqmc_anti'][f'rqmc_anti_rb_{fr}_m{m}']['inv_gain_mc']
    o['ml'] = max(v['gain_vs_rb'] for v in r['multilevel'].values())
    o['rho_rb'] = Vrb / V; o['mu2V'] = r['mean_norm2_over_V']
    return o
out = {}
keys = None
for n, (L, seeds) in W.items():
    rows = []
    for s in seeds:
        p = f'runs/struct_n{n}_L{L}_s{s}.json'
        try: rows.append(sh(json.load(open(p))))
        except FileNotFoundError: pass
    if not rows: continue
    keys = sorted(set().union(*[r.keys() for r in rows]))
    out[n] = {k: (float(np.median([r[k] for r in rows if k in r])), float(min(r[k] for r in rows if k in r)), float(max(r[k] for r in rows if k in r)), sum(k in r for r in rows)) for k in keys}
show = ['rho_rb', 'E1', 'E2', 'odd', 'even', 'ev4', 'ev6', 'g_onb', 'g_simplex', 'g_cross', 'g_kerdock', 'rq_std_10', 'rq_std_12', 'rq_std_14', 'rq_polar_10', 'rq_polar_12', 'rq_polar_14', 'rq_svd_14', 'anti_std_14', 'anti_polar_14', 'ml']
print('quantity | ' + ' | '.join(f'n={n} (nets)' for n in out))
for k in show:
    print(k + ' | ' + ' | '.join((f'{out[n][k][0]:.3f} [{out[n][k][1]:.2f},{out[n][k][2]:.2f}] ({out[n][k][3]})' if k in out[n] else '-') for n in out))
json.dump(out, open('results/ladder_table.json', 'w'), indent=1)
