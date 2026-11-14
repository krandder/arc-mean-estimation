"""PREREG Part 2 scorer (gate counts PG1-PG3, gram-chain stationary prediction PS1, synchronisation PS2).
Inputs: runs/p2_*.json (Part 2 runner) and runs/eval_*.json (Part 1 measurements for N and PS1).
Writes results/part2_scores.json."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
import score_part1 as sp  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def G_need(curve, V, eps):
    """Amendment 2A: smallest grid G whose nonlinear residual + 2 SE <= eps V (a tested count, not a bracket)."""
    for G in sorted(curve, key=int):
        v = curve[G]
        se = v[3] if len(v) > 3 else 0.0
        if v[0] + 2 * se <= eps * V:
            return int(G)
    return None


def G1_need(imp_tail, imp_total, eps):
    for G in sorted(imp_tail, key=int):
        if imp_tail[G] <= eps * imp_total:
            return int(G)
    return None


def frac(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs) if xs else float('nan')), len(xs)


def main():
    S = {}
    cells = []
    p1 = {}
    for fn in glob.glob(BASE + 'runs/eval_*.json'):
        for o in json.load(open(fn)):
            p1[(o['mode'], o['n'], o['seed'], o.get('l'), o.get('s'))] = o
    for fn in sorted(glob.glob(BASE + 'runs/p2_arc_*.json')) + sorted(glob.glob(BASE + 'runs/p2_stat_*.json')):
        for o in json.load(open(fn)):
            V = o['V_gauss'][0]
            g = o['gates']
            rec = dict(mode=o['mode'], n=o['n'], t=o['t'], seed=o['seed'], l=o.get('l'), s=o.get('s'),
                       total=g['total_gates'], flips=g['mean_flips_vs_m'], tau_lt=g['n_gates_tau_lt'])
            for e in (0.1, 0.01):
                rec[f'G_imp_{e}'] = G_need(g['importance'], V, e)
                rec[f'G_mar_{e}'] = G_need(g['margin'], V, e)
                rec[f'G1_{e}'] = G1_need(g['imp_tail'], g['imp_total'], e)
            rec['Vnl_frozen_rel'] = g['importance']['0'][0] / V
            # N_>=2 along the nonlinear AS basis, resolved only with residual + 2 SE (SE not stored: use point values)
            nl = o['nl']['nlAS']
            for e in (0.1, 0.01):
                rec[f'Nge2_{e}'] = next((int(k) for k in sorted(nl, key=int)
                                         if nl[k][2] + 2 * (nl[k][3] if len(nl[k]) > 3 else 0.0) <= e * V), None)
            n1 = o['n1']
            for e in (0.1, 0.01):
                rec[f'N1split_{e}'] = next((int(k) for k in sorted(n1['res1'], key=int)
                                            if n1['res1'][k] <= e * n1['V1'][0]), None)
            key = (o['mode'], o['n'], o['seed'], o.get('l'), o.get('s'))
            if key in p1:
                c1 = sp.cell_record(p1[key])
                rec['N_0.1'] = c1['Nvec_0.1'][1]
                rec['N_0.01'] = c1['Nvec_0.01'][1]
            cells.append(rec)
    arc = [c for c in cells if c['mode'] == 'arc']
    seeds = sorted(set(c['seed'] for c in arc))
    complete = [s for s in seeds if sorted(c['l'] for c in arc if c['seed'] == s) == [8, 16, 24, 31]]
    S['PG_complete_nets'] = complete
    S['PG1a'] = sum(all(c['G_imp_0.01'] is not None and c['G_imp_0.01'] >= c['n'] for c in arc
                        if c['seed'] == s and c['t'] >= 8) for s in complete), len(complete)
    S['PG1b'] = sum(all(c['G_imp_0.01'] is not None and c['G_imp_0.01'] >= 0.25 * c['total'] for c in arc
                        if c['seed'] == s and c['l'] <= 16) for s in complete), len(complete)
    S['PG2'] = frac([None if (c['G1_0.1'] is None or c['G_imp_0.1'] is None) else
                     (abs(c['G1_0.1'] - c['G_imp_0.1']) <= 2 or
                      (c['G_imp_0.1'] > 0 and 0.5 <= c['G1_0.1'] / c['G_imp_0.1'] <= 2)) for c in cells])
    S['PG2_zero_G_cells'] = sum(1 for c in cells if c['G_imp_0.1'] == 0)
    S['PG3'] = frac([None if (c['G_imp_0.1'] is None or 'N_0.1' not in c) else c['G_imp_0.1'] >= 3 * c['N_0.1']
                     for c in arc])
    # PS1: stationary cells from Part 1
    ps = {e: dict(a=[], b=[], a_pro=[], b_pro=[]) for e in (0.1, 0.01)}
    for key, o in p1.items():
        if o['mode'] != 'stat':
            continue
        c = sp.cell_record(o)
        if not c['resolved']:
            continue
        n, t = o['n'], o['t']
        V = o['V_gauss'][0]
        for e in (0.1, 0.01):
            tx = 2 * n ** (1 / 3) * math.log(1 / e)
            if t >= tx:
                tag = '_pro' if n >= 128 else ''
                ps[e]['a' + tag].append(o['res_AS_gauss']['1'][0] <= e * V)
                ps[e]['b' + tag].append(o['res_radial_gauss'][0] <= e * V)
    for e in (0.1, 0.01):
        S[f'PS1a_{e}_seen'] = frac(ps[e]['a'])
        S[f'PS1b_{e}_seen'] = frac(ps[e]['b'])
        S[f'PS1a_{e}_prospective'] = frac(ps[e]['a_pro'])
        S[f'PS1b_{e}_prospective'] = frac(ps[e]['b_pro'])
    # PS2: synchronisation
    sync = {}
    for fn in sorted(glob.glob(BASE + 'runs/p2_sync_*.json')):
        d = json.load(open(fn))
        if not d:
            continue
        n = d[0]['n']
        res = [(o['l'], o['res_radial_true'][0] / max(o['V_true'][0], 1e-300)) for o in d]
        after = [r for l, r in res if l >= 4 * n]
        ok1 = bool(after) and all(r <= 0.05 for r in after)
        seg = []
        for l, r in res:
            if l < 4 * n:
                continue
            if r <= 1e-3:
                break
            seg.append((l, r))
        rate = None
        if len(seg) >= 2:
            ll = np.array([l for l, _ in seg])
            lr = np.log([max(r, 1e-300) for _, r in seg])
            rate = float(-np.polyfit(ll, lr, 1)[0])
        ok2 = None if rate is None else bool(0.5 <= rate / (2.0 / n) <= 2.0)
        sync[fn.split('/')[-1]] = dict(n=n, le_0p05_after_4n=ok1, rate=rate, pred=2.0 / n, rate_ok=ok2, curve=res)
    S['PS2'] = sync
    json.dump(dict(scores=S, cells=cells), open(BASE + 'results/part2_scores.json', 'w'), default=float, indent=1)
    for k, v in S.items():
        if k != 'PS2':
            print(k, v)
    for k, v in sync.items():
        print(k, {kk: vv for kk, vv in v.items() if kk != 'curve'})


if __name__ == '__main__':
    main()
