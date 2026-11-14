"""PREREG Part 3 scorer: prospective test of theory v2 on E-ARC seeds 4002-4003 and E-ST n >= 128.
Writes results/part3A_scores.json."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import score_part1 as sp  # noqa: E402
import theory_v2 as t2  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def main():
    arc, st = [], []
    for fn in sorted(glob.glob(BASE + 'runs/eval_arc_n256_L32_seed400[45].json')):
        arc += json.load(open(fn))
    for fn in sorted(glob.glob(BASE + 'runs/eval_stat_n128_seed*.json')) + \
            sorted(glob.glob(BASE + 'runs/eval_stat_n256_seed*.json')):
        st += json.load(open(fn))
    S, cells = {}, []
    q1 = q2 = q3 = 0
    q4 = {0.1: 0, 0.01: 0}
    q4lo = True
    for o in arc:
        c = sp.cell_record(o)
        pl = t2.predict_layer(o)
        pN = t2.predict_N(o)
        lo = t2.first_chaos_lower_bound(o, 4096)
        Vrel = o['V_gauss'][0] / o['Ea2_true']
        r = dict(seed=o['seed'], l=o['l'], Vrel=Vrel, Vrel_v2=pl['V_rel'], s1=c['s1'], s1_v2=pl['s1'], D=c['D'],
                 D_v2=pl['D'])
        q1 += abs(pl['V_rel'] / Vrel - 1) <= 0.2
        q2 += abs(c['s1'] - pl['s1']) <= 0.08
        q3 += 0.75 <= pl['D'] / c['D'] <= 1.33
        for e in (0.1, 0.01):
            lo_e, hi_e = c[f'Nvec_{e}']
            ok = sp.within2(pN['N_vec'][str(e)], lo_e, hi_e)
            q4[e] += ok
            r[f'N_{e}'] = (lo_e, hi_e)
            r[f'N_v2_{e}'] = pN['N_vec'][str(e)]
            r[f'lo_{e}'] = lo[str(e)]
        for e in (0.1, 0.01, 0.001):
            if lo[str(e)] > c[f'Nvec_{e}'][1]:
                q4lo = False
        cells.append(r)
    S['Q1'] = (q1, len(arc))
    S['Q2_arc'] = (q2, len(arc))
    S['Q3'] = (q3, len(arc))
    S['Q4'] = {str(e): (q4[e], len(arc)) for e in q4}
    S['Q4_lower_bound_consistent'] = q4lo
    # stationary
    q2s, q5, q6a, q6b = [], [], [], []
    rates = {}
    for o in st:
        c = sp.cell_record(o)
        if not c['resolved']:
            continue
        pl = t2.predict_layer(o)
        pN = t2.predict_N(o)
        q2s.append(abs(c['s1'] - pl['s1']) <= 0.12)
        lo_e, hi_e = c['Nvec_0.1']
        q5.append(sp.within2(pN['N_vec']['0.1'], lo_e, hi_e))
        Q = o['meanQ']
        n = o['n']
        delta = 0.672 * Q ** (-1 / 3) + 1 / Q - 5 / n
        t1 = math.log(9) / delta if delta > 0 else float('inf')
        V = o['V_gauss'][0]
        if o['t'] >= t1:
            q6a.append(o['res_AS_gauss']['1'][0] <= 0.1 * V)
            q6b.append(o['res_radial_gauss'][0] > 0.1 * V)
        cells.append(dict(n=n, seed=o['seed'], t=o['t'], s1=c['s1'], s1_v2=pl['s1'], N01=(lo_e, hi_e),
                          N01_v2=pN['N_vec']['0.1'], t1=t1, res1=o['res_AS_gauss']['1'][0] / V,
                          res_rad=o['res_radial_gauss'][0] / V, M=c['M']))
    S['Q2_stat'] = (sum(q2s), len(q2s))
    S['Q5'] = (sum(q5), len(q5))
    S['Q6_one_direction'] = (sum(q6a), len(q6a))
    S['Q6_radius_not_enough'] = (sum(q6b), len(q6b))
    for n in (128, 256):
        for seed in sorted(set(o['seed'] for o in st if o['n'] == n)):
            cs = sorted([o for o in st if o['n'] == n and o['seed'] == seed], key=lambda o: o['t'])
            fit = [o for o in cs if sp.cell_record(o)['resolved'] and n / 8 <= o['t'] <= n and o['V_true'][0] > 0]
            if len(fit) >= 2:
                tt = np.array([o['t'] for o in fit])
                lv = np.log([o['V_true'][0] for o in fit])
                Q = np.median([o['meanQ'] for o in fit])
                rates[f'{n}|{seed}'] = dict(rate=float(-np.polyfit(tt, lv, 1)[0]), v1=5.0 / n,
                                            astra=5.0 / (2 * n) + 1.0 / Q)
    S['Q7'] = rates
    json.dump(dict(scores=S, cells=cells), open(BASE + 'results/part3A_scores.json', 'w'), default=float, indent=1)
    for k, v in S.items():
        print(k, v)


if __name__ == '__main__':
    main()
