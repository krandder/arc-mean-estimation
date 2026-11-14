"""PREREG Part 1 scorer: predictions from lib/theory_v1.py (frozen) against measurements in runs/eval_*.json.
Writes results/part1_scores.json and results/part1_tables.md. Rules: PREREG.md Part 1."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import accounting as acc  # noqa: E402
import theory_v1 as th  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
GRID = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160, 192, 224, 256]


def n_meas(curve, V, eps):
    """(N_lo, N) from a residual curve: N = smallest grid k with residual <= eps V; N_lo = previous grid k."""
    ks = sorted(int(k) for k in curve)
    prev = None
    for k in ks:
        if curve[str(k)][0] <= eps * V:
            return (prev if prev is not None else k), k
        prev = k
    return ks[-1], ks[-1]


def within2(pred, lo, hi):
    """Interval rule: [pred/2, 2 pred] intersects (lo, hi], or pred within 2 of hi (small counts)."""
    if abs(pred - hi) <= 2:
        return True
    a, b = pred / 2.0, 2.0 * pred
    return b > lo and a <= hi


def resolved(o):
    V, se = o['V_gauss']
    if not (V > 3 * se):
        return False
    if o['mode'] == 'stat':
        M = o['V_true'][0] / o['totvar_true'][0]
        return M >= 0.02
    return True


def n1_meas(o, eps):
    V1 = o['V1_gauss'][0]
    r1 = np.maximum(np.array(o['R1_evals']), 0)
    cap = np.concatenate([[0], np.cumsum(r1) / V1])
    for k, c in enumerate(cap):
        if 1 - c <= eps:
            return k
    return len(cap) - 1


def cell_record(o):
    rec = dict(mode=o['mode'], n=o['n'], t=o['t'], seed=o['seed'], l=o.get('l'), s=o.get('s'))
    V = o['V_gauss'][0]
    rec['resolved'] = resolved(o)
    rec['V_gauss'], rec['V_true'] = o['V_gauss'], o['V_true']
    if o['mode'] == 'stat':
        rec['M'] = o['V_true'][0] / o['totvar_true'][0]
    rec['s1'] = o['V1_gauss'][0] / V
    rec['s1r'] = o['V1r_gauss'][0] / o['Vr_gauss'][0]
    rec['D'] = o['J1_gauss'][0] / V
    rec['frozen_ratio'] = o['parts_true']['V_lin'] / o['parts_true']['V_da'] if 'parts_true' in o else None
    rec['radial_gauss'] = o['res_radial_gauss'][0] / V
    rec['radial_true'] = o['res_radial_true'][0] / o['V_true'][0] if 'res_radial_true' in o else None
    for e in (0.1, 0.01, 0.001):
        rec[f'Nvec_{e}'] = n_meas(o['res_AS_gauss'], V, e)
        rec[f'Nsc_{e}'] = n_meas(o['res_ASr_gauss'], o['Vr_gauss'][0], e)
        if 'res_ASt_true' in o:
            rec[f'Ntrue_{e}'] = n_meas(o['res_ASt_true'], o['V_true'][0], e)
    for e in (0.1, 0.01):
        rec[f'N1_{e}'] = n1_meas(o, e)
    rec['pca_res'] = {k: o['res_PCA_gauss'][str(k)][0] / V for k in (1, 4, 16) if str(k) in o['res_PCA_gauss']}
    # predictions (theory v1)
    ok_c0 = o.get('mean_cos') is not None and np.isfinite(o['mean_cos'])
    if ok_c0:
        p = th.predict_N(o)
        rec['pred_s1'] = p['pred']['s1']
        rec['pred_D'] = p['pred']['D']
        rec['pred_split'] = p['pred']['s1_split']
        for e in (0.1, 0.01, 0.001):
            rec[f'pred_Nvec_{e}'] = p['N_vec'][str(e)]
            rec[f'pred_Nsc_{e}'] = p['N_sc'][str(e)]
        f1 = th.N1_free_product(o)
        for e in (0.1, 0.01):
            rec[f'pred_N1_{e}'] = f1[str(e)]['fp']
            rec[f'pca_N1_{e}'] = f1[str(e)]['pca']
        lam = np.maximum(np.array(o['cloud_evals'], float), 1e-300)
        kk = [k for k in (1, 4, 16) if k <= o['n']]
        gen = acc.generic_capture(lam, p['pred']['s'], kk)
        rec['pred_pca_res'] = {k: 1 - gen[k] for k in kk}
    return rec


def frac(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs) if xs else float('nan')), len(xs)


def main():
    cells = []
    for fn in sorted(glob.glob(BASE + 'runs/eval_*.json')):
        for o in json.load(open(fn)):
            if o['seed'] >= 9000:
                continue
            cells.append(cell_record(o))
    arc = [c for c in cells if c['mode'] == 'arc']
    nd = [c for c in cells if c['mode'] == 'nd']
    st = [c for c in cells if c['mode'] == 'stat']
    res = [c for c in arc + st if c['resolved'] and 'pred_s1' in c]
    S = {}
    # P1
    for e in (0.1, 0.01):
        S[f'P1_fp_{e}'] = frac([abs(math.log(max(c[f'pred_N1_{e}'], 1) / max(c[f'N1_{e}'], 1))) <= math.log(2)
                                or abs(c[f'pred_N1_{e}'] - c[f'N1_{e}']) <= 1 for c in res])
    S['P1_pca_3x'] = frac([c['pca_N1_0.01'] >= 3 * c['N1_0.01'] for c in res if c['t'] >= 4])
    # P2
    S['P2_arc'] = frac([abs(c['s1'] - c['pred_s1']) <= 0.12 for c in arc if c['resolved'] and 'pred_s1' in c])
    S['P2_stat'] = frac([abs(c['s1'] - c['pred_s1']) <= 0.12 for c in st if c['resolved'] and 'pred_s1' in c])
    S['P2_nd_report'] = frac([abs(c['s1'] - c['pred_s1']) <= 0.12 for c in nd if 'pred_s1' in c])
    # P3
    S['P3_arc'] = frac([2 / 3 <= c['pred_D'] / c['D'] <= 1.5 for c in arc if c['resolved'] and 'pred_D' in c])
    # P4
    S['P4_stat_s1_ge_0.85'] = frac([c['s1'] >= 0.85 for c in st if c['resolved']])
    # P5
    S['P5_band'] = frac([c['D'] / 2 <= c['frozen_ratio'] <= 2 * c['D'] for c in arc if c['resolved'] and c['D'] >= 2])
    S['P5_ge_1.5'] = frac([c['frozen_ratio'] >= 1.5 for c in arc if c['resolved'] and c['D'] >= 2])
    # P6
    sel = [c for c in arc if c['resolved'] and c['l'] >= 4 and 'pred_pca_res' in c] + \
          [c for c in st if c['resolved'] and 'pred_pca_res' in c]
    S['P6_generic'] = frac([all(abs(c['pca_res'][k] - c['pred_pca_res'][k]) <= 0.10 for k in (1, 4, 16)
                                if k in c['pca_res'] and k in c['pred_pca_res']) for c in sel])
    # P7, P8
    for e in (0.1, 0.01, 0.001):
        S[f'P7_vec_{e}'] = frac([within2(c[f'pred_Nvec_{e}'], *c[f'Nvec_{e}']) for c in res])
        S[f'P8_sc_{e}'] = frac([within2(c[f'pred_Nsc_{e}'], *c[f'Nsc_{e}']) for c in res])
    # P9
    seeds_arc = sorted(set(c['seed'] for c in arc))
    S['P9a'] = all(c['Nvec_0.01'][1] >= 64 for c in arc if c['l'] <= 8) if arc else None
    S['P9b'] = sum(all(c['Nvec_0.01'][1] >= 16 for c in arc if c['seed'] == s) for s in seeds_arc)
    S['P9c'] = sum(any(c['l'] == 31 and c['Nsc_0.01'][1] <= 4 for c in arc if c['seed'] == s) for s in seeds_arc)
    seeds_nd = sorted(set(c['seed'] for c in nd))
    S['P9d'] = sum(all(c['radial_true'] is not None and c['radial_true'] <= 0.01 for c in nd
                       if c['seed'] == s and c['l'] >= 16) for s in seeds_nd)
    sel = [c for c in st if c['resolved'] and c['n'] >= 64 and c['t'] in (16, 32)]
    S['P9e'] = frac([c['Nvec_0.1'][1] <= 2 for c in sel])
    # P10
    S['P10a'] = frac([0.8 <= c['V_true'][0] / c['V_gauss'][0] <= 1.25 for c in st if c['n'] >= 64 and c['t'] <= 8])
    S['P10b'] = sum(any(abs(c['V_gauss'][0] / c['V_true'][0] - 1) > 0.2 for c in nd if c['seed'] == s and c['l'] >= 32)
                    for s in seeds_nd)
    # P11
    incr = []
    rates = {}
    for n in sorted(set(c['n'] for c in st)):
        for s in sorted(set(c['seed'] for c in st if c['n'] == n)):
            cs = sorted([c for c in st if c['n'] == n and c['seed'] == s], key=lambda c: c['t'])
            for a, b in zip(cs, cs[1:]):
                se = math.hypot(a['V_true'][1], b['V_true'][1])
                incr.append(b['V_true'][0] <= a['V_true'][0] + 3 * se)
            fit = [c for c in cs if c['resolved'] and n / 4 <= c['t'] <= n and c['V_true'][0] > 0]
            if len(fit) >= 2:
                tt = np.array([c['t'] for c in fit])
                lv = np.log([c['V_true'][0] for c in fit])
                rates.setdefault(n, []).append(-np.polyfit(tt, lv, 1)[0])
    S['P11a'] = frac(incr)
    S['P11b'] = {str(n): dict(median_rate=float(np.median(r)), pred=5.0 / n,
                              ok=bool(1 / 1.6 <= np.median(r) / (5.0 / n) <= 1.6)) for n, r in rates.items()}
    json.dump(dict(scores=S, cells=cells), open(BASE + 'results/part1_scores.json', 'w'), default=float, indent=1)
    for k, v in S.items():
        print(k, v)


if __name__ == '__main__':
    main()
