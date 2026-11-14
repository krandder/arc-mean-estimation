"""Corrected Part 1 scoring (post hoc, after gpt-6-astra's round-2 audit T3; the registered scorer score_part1.py is
kept and both are reported). Changes: registered-net whitelist; P9/P10 use only nets with every registered layer present;
N_1 from the stored 96 eigenvalues is censored (None) when the target is not reached; P1 also scored with the
split-free U-statistic count along the AS basis (degree-1 captured, cap1_AS); P11b only for registered widths
{64, 128, 256}; the unresolved-cell rule applied to P10a and P11a. Writes results/part1_scores_v2.json."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
import score_part1 as sp  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
WL = {('arc', 256): {4000, 4001, 4002, 4003}, ('nd', 8): {203, 216, 217, 220, 221, 223},
      ('stat', 32): {1000, 1001, 1002, 1003}, ('stat', 64): {1000, 1001, 1002, 1003},
      ('stat', 128): {1000, 1001, 1002, 1003}, ('stat', 256): {1000, 1001}}
LAYERS = {'arc': [0, 4, 8, 16, 24, 28, 31], 'nd': [0, 2, 4, 8, 16, 32, 64, 128, 192, 255]}


def n1_censored(o, eps):
    V1 = o['V1_gauss'][0]
    r1 = np.maximum(np.array(o['R1_evals']), 0)
    cap = np.concatenate([[0], np.cumsum(r1) / V1])
    for k, c in enumerate(cap):
        if 1 - c <= eps:
            return k
    return None


def n1_cap1(o, eps):
    V1 = o['V1_gauss'][0]
    c = o['cap1_AS']
    for k in sorted(c, key=int):
        if V1 - c[k] <= eps * V1:
            return int(k)
    return None


def main():
    raw = []
    for fn in sorted(glob.glob(BASE + 'runs/eval_*.json')):
        for o in json.load(open(fn)):
            if o['seed'] in WL.get((o['mode'], o['n']), set()):
                raw.append(o)
    cells = [(o, sp.cell_record(o)) for o in raw]
    S = {}
    res = [(o, c) for o, c in cells if c['mode'] in ('arc', 'stat') and c['resolved'] and 'pred_N1_0.1' in c]
    for e in (0.1, 0.01):
        ok_reg, ok_cap = [], []
        for o, c in res:
            m1 = n1_censored(o, e)
            if m1 is not None:
                ok_reg.append(abs(math.log(max(c[f'pred_N1_{e}'], 1) / max(m1, 1))) <= math.log(2)
                              or abs(c[f'pred_N1_{e}'] - m1) <= 1)
            m2 = n1_cap1(o, e)
            if m2 is not None:
                ok_cap.append(abs(math.log(max(c[f'pred_N1_{e}'], 1) / max(m2, 1))) <= math.log(2)
                              or abs(c[f'pred_N1_{e}'] - m2) <= 1)
        S[f'P1_fp_{e}_eigen_censored'] = sp.frac(ok_reg)
        S[f'P1_fp_{e}_cap1_AS'] = sp.frac(ok_cap)
    # P9 with completeness
    def complete(mode, n, seed):
        ls = sorted(c['l'] for o, c in cells if c['mode'] == mode and c['n'] == n and c['seed'] == seed)
        return ls == LAYERS[mode]
    arc_seeds = [s for s in sorted(WL[('arc', 256)]) if complete('arc', 256, s)]
    nd_seeds = [s for s in sorted(WL[('nd', 8)]) if complete('nd', 8, s)]
    arc = [c for o, c in cells if c['mode'] == 'arc' and c['seed'] in arc_seeds]
    nd = [c for o, c in cells if c['mode'] == 'nd' and c['seed'] in nd_seeds]
    S['complete_arc_nets'] = arc_seeds
    S['P9a'] = all(c['Nvec_0.01'][1] >= 64 for c in arc if c['l'] <= 8) if arc else None
    S['P9b'] = (sum(all(c['Nvec_0.01'][1] >= 16 for c in arc if c['seed'] == s) for s in arc_seeds), len(arc_seeds))
    S['P9c'] = (sum(any(c['l'] == 31 and c['Nsc_0.01'][1] <= 4 for c in arc if c['seed'] == s) for s in arc_seeds),
                len(arc_seeds))
    S['P9d'] = (sum(all(c['radial_true'] is not None and c['radial_true'] <= 0.01 for c in nd
                        if c['seed'] == s and c['l'] >= 16) for s in nd_seeds), len(nd_seeds))
    st = [c for o, c in cells if c['mode'] == 'stat']
    S['P10a'] = sp.frac([0.8 <= c['V_true'][0] / c['V_gauss'][0] <= 1.25 for c in st
                         if c['n'] >= 64 and c['t'] <= 8 and c['resolved']])
    S['P10b'] = (sum(any(abs(c['V_gauss'][0] / c['V_true'][0] - 1) > 0.2 for c in nd if c['seed'] == s and c['l'] >= 32)
                     for s in nd_seeds), len(nd_seeds))
    incr = []
    rates = {}
    for n in (32, 64, 128, 256):
        for s in sorted(WL.get(('stat', n), set())):
            cs = sorted([c for c in st if c['n'] == n and c['seed'] == s and c['resolved']], key=lambda c: c['t'])
            for a, b in zip(cs, cs[1:]):
                se = math.hypot(a['V_true'][1], b['V_true'][1])
                incr.append(b['V_true'][0] <= a['V_true'][0] + 3 * se)
            fit = [c for c in cs if n / 4 <= c['t'] <= n and c['V_true'][0] > 0]
            if n in (64, 128, 256) and len(fit) >= 2:
                tt = np.array([c['t'] for c in fit])
                lv = np.log([c['V_true'][0] for c in fit])
                rates.setdefault(n, []).append(float(-np.polyfit(tt, lv, 1)[0]))
    S['P11a_resolved_only'] = sp.frac(incr)
    S['P11b_registered_widths'] = {str(n): dict(rates=r, median_rate=float(np.median(r)), pred=5.0 / n,
                                                ok=bool(1 / 1.6 <= np.median(r) / (5.0 / n) <= 1.6))
                                   for n, r in rates.items()}
    json.dump(S, open(BASE + 'results/part1_scores_v2.json', 'w'), default=float, indent=1)
    for k, v in S.items():
        print(k, v)


if __name__ == '__main__':
    main()
