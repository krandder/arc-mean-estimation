"""Score the registered predictions P1-P11 of PREREG.md from runs/eval_*.json and runs/pairs_*.npz.
Written and hashed before reading any evaluation result. Rules fixed here (in addition to PREREG.md):
- P1/P2 bins are the delta levels; a bin qualifies if L' x median(phi) <= 0.3, it has >= 20 pairs and its mean r_F > 0.
- P2 chain: lib/chain3.run(n, L', median(phi), 4000 chains) per qualifying bin (cached), mean frozen residual; the net's
  pooled value is the pair-average of r_F/(L' phi^3) over the qualifying bins; the chain's is the pair-count-weighted
  average over the same bins of chain_mean/(L' phi_median^3).
- P3: a cell passes if every bin with L' phi_med <= 0.5 has median r_F < median r_R and every bin with L' phi_med >= 5
  has median r_F > median r_R; it qualifies if it has at least one bin of each kind.
- P5: gamma = minus the least-squares slope of log D_best (forward-only) on log M over M = 4, 16, 64, 256.
- P8: decrease = non-increasing over the four layers L/4, L/2, 3L/4, 7L/8.
- P9: ideal ratios are minimised over r for each variant; multi = min over r, M in {16, 64, 256}, merge in {R, rule}.
- P10: PR decrease = PR(L/4) > PR(7L/8).
Output: results/prereg_scores.json and a printed table.
"""
import os
import sys
import json
import glob
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import chain3

ROOT = os.path.join(os.path.dirname(__file__), '..')


def load():
    nets = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json'))):
        r = json.load(open(f))
        if r.get('dead'):
            continue
        pf = f.replace('eval_', 'pairs_').replace('.json', '.npz')
        r['pairs'] = dict(np.load(pf)) if os.path.exists(pf) else {}
        nets.append(r)
    return nets


_chain_cache = {}


def chain_mean(n, Lp, phi):
    key = (n, Lp, round(float(phi), 6))
    if key not in _chain_cache:
        rng = np.random.default_rng([int(n), int(Lp), int(round(phi * 1e6))])
        _chain_cache[key] = float(chain3.run(n, Lp, phi, 4000, rng)['frozen'].mean())
    return _chain_cache[key]


def frac(xs):
    xs = [bool(x) for x in xs]
    return (sum(xs) / len(xs)) if xs else float('nan'), len(xs)


def main():
    nets = load()
    out = {'n_nets': len(nets)}
    cfgs = sorted(set((r['n'], r['L']) for r in nets))
    out['configs'] = [list(c) for c in cfgs]
    # ---------------- P1, P2, P3 from pairs
    p1, p2, p3 = [], [], []
    p1_detail = []
    for r in nets:
        n, L = r['n'], r['L']
        for e in r['E1']:
            l, Lp = e['l'], e['Lp']
            key = f'l{l}'
            if Lp < 8 or key not in r['pairs']:
                continue
            P = r['pairs'][key]
            bins = []
            for d in sorted(set(P[:, 1])):
                sel = P[:, 1] == d
                phi = P[sel, 2]
                rF, rR = P[sel, 3], P[sel, 4]
                bins.append({'phi': float(np.median(phi)), 'meanF': float(rF.mean()), 'count': int(sel.sum()),
                             'medF': float(np.median(rF)), 'medR': float(np.median(rR)),
                             'ratioF': float(np.mean(rF / np.maximum(Lp * phi ** 3, 1e-300)))})
            q = [b for b in bins if Lp * b['phi'] <= 0.3 and b['count'] >= 20 and b['meanF'] > 0]
            if len(q) >= 3:
                x = np.log([b['phi'] for b in q])
                y = np.log([b['meanF'] for b in q])
                slope = float(np.polyfit(x, y, 1)[0])
                p1.append(2.4 <= slope <= 3.6)
                cnt = np.array([b['count'] for b in q], dtype=float)
                net_val = float(np.sum(cnt * np.array([b['ratioF'] for b in q])) / cnt.sum())
                ch = np.array([chain_mean(n, Lp, b['phi']) / (Lp * b['phi'] ** 3) for b in q])
                ch_val = float(np.sum(cnt * ch) / cnt.sum())
                ratio = net_val / ch_val if ch_val > 0 else float('inf')
                p2.append(1 / 3 <= ratio <= 3)
                p1_detail.append({'n': n, 'L': L, 'seed': r['seed'], 'l': l, 'slope': slope,
                                  'net_coef': net_val, 'chain_coef': ch_val, 'ratio': ratio,
                                  'meanfield_coef': 4 / (3 * math.pi)})
            small = [b for b in bins if Lp * b['phi'] <= 0.5]
            large = [b for b in bins if Lp * b['phi'] >= 5]
            if small and large:
                ok = all(b['medF'] < b['medR'] for b in small) and all(b['medF'] > b['medR'] for b in large)
                p3.append(ok)
    out['P1'] = {'frac': frac(p1), 'pass': frac(p1)[0] >= 0.8}
    out['P2'] = {'frac': frac(p2), 'pass': frac(p2)[0] >= 0.75}
    out['P3'] = {'frac': frac(p3), 'pass': frac(p3)[0] >= 0.8}
    out['P1P2_detail'] = p1_detail

    def layer(r, which):
        L = r['L']
        target = {'L/4': max(1, L // 4), 'L/2': L // 2, '3L/4': (3 * L) // 4, '7L/8': (7 * L) // 8}[which]
        for e in r['E1']:
            if e['l'] == target:
                return e
        return None

    # ---------------- P4
    a, b = [], []
    for r in nets:
        e = layer(r, 'L/4')
        a.append(e['fwd']['1']['D_F'] > e['fwd']['1']['D_R'])
        e = layer(r, '7L/8')
        b.append(e['fwd']['16']['D_F'] < e['fwd']['16']['D_R'])
    out['P4'] = {'roughL4': frac(a), 'smooth7L8': frac(b), 'pass': frac(a)[0] >= 0.9 and frac(b)[0] >= 0.8}
    # ---------------- P5
    p5 = {}
    allpass = True
    for c in cfgs:
        for which, lo, hi in [('L/4', 0.05, 0.4), ('L/2', 0.05, 0.4), ('7L/8', 0.3, 1.2)]:
            g = []
            for r in nets:
                if (r['n'], r['L']) != c:
                    continue
                e = layer(r, which)
                Ms = [4, 16, 64, 256]
                D = [e['fwd'][str(M)]['D_best'] for M in Ms]
                gam = -float(np.polyfit(np.log(Ms), np.log(np.maximum(D, 1e-300)), 1)[0])
                g.append((gam, lo <= gam <= hi))
            fr = frac([x[1] for x in g])
            p5[f'{c[0]}x{c[1]} {which}'] = {'gammas': [x[0] for x in g], 'frac': fr, 'pass': fr[0] >= 0.75}
            allpass = allpass and fr[0] >= 0.75
    out['P5'] = {'groups': p5, 'groups_passing': sum(v['pass'] for v in p5.values()), 'groups_total': len(p5),
                 'pass': allpass}
    # ---------------- P6
    p6 = []
    for r in nets:
        for e in r['E1']:
            if '64' in e['two']:
                p6.append(e['two']['64']['D_best'] / max(e['fwd']['64']['D_best'], 1e-300) <= 0.8)
    out['P6'] = {'frac': frac(p6), 'pass': frac(p6)[0] >= 0.6}
    # ---------------- P7
    p7 = []
    for r in nets:
        for e in r['E1']:
            for M in ['16', '64', '256']:
                d = e['fwd'][M]
                if d['bias_best'] > 3 * d['D_best'] / 2048:
                    p7.append(d['bias_best'] <= d['D_best'] / 10)
    out['P7'] = {'frac': frac(p7), 'pass': frac(p7)[0] >= 0.8}
    # ---------------- P8
    a, b = [], []
    for r in nets:
        seq = [layer(r, w)['meanprop_err'] for w in ['L/4', 'L/2', '3L/4', '7L/8']]
        a.append(all(seq[i + 1] <= seq[i] for i in range(3)))
        b.append(seq[-1] <= 0.05)
    out['P8'] = {'monotone': frac(a), 'small7L8': frac(b), 'pass': frac(a)[0] >= 0.8 and frac(b)[0] >= 0.75}
    # ---------------- P9
    a, b1, b2 = [], [], []
    gains = {}
    for r in nets:
        rr = min(e['randref_R']['ideal'] for e in r['E3'])
        multi = min(e[f'M{M}_{m}']['ideal'] for e in r['E3'] for M in [16, 64, 256] for m in ['R', 'rule'])
        if r['L'] <= r['n']:
            a.append(0.5 <= rr <= 1.2)
        b1.append(multi < rr)
        b2.append(multi / rr >= 0.6)
        gains.setdefault((r['n'], r['L']), []).append(rr / multi)
    med = {f'{k[0]}x{k[1]}': float(np.median(v)) for k, v in gains.items()}
    c_ok = None
    if '64x64' in med and '256x256' in med:
        c_ok = med['256x256'] / med['64x64'] <= 1.5
    out['P9'] = {'a': frac(a), 'b_below': frac(b1), 'b_ratio_ge_0.6': frac(b2), 'median_gain_multi_over_randref': med,
                 'c': c_ok, 'pass': frac(a)[0] >= 0.75 and frac(b1)[0] >= 0.7 and frac(b2)[0] >= 0.8 and bool(c_ok)}
    # ---------------- P10
    a, b = [], []
    for r in nets:
        for e in r['E1']:
            a.append(-0.7 <= e['ev_logslope_1_10'] <= -0.15)
        b.append(layer(r, 'L/4')['PR'] > layer(r, '7L/8')['PR'])
    out['P10'] = {'slope': frac(a), 'PRdecr': frac(b), 'pass': frac(a)[0] >= 0.9 and frac(b)[0] >= 0.8}
    # ---------------- P11
    a, b = [], []
    for r in nets:
        if r['L'] != r['n']:
            continue
        e = layer(r, 'L/2')
        a.append(e['fwd']['256']['D_best'] > 0.01)
        e = layer(r, '7L/8')
        b.append(any(e['fwd'][str(M)]['D_best'] <= 0.01 for M in [1, 4, 16, 64]))
    out['P11'] = {'L2_gt8bits': frac(a), '7L8_le6bits': frac(b), 'pass': frac(a)[0] >= 0.75 and frac(b)[0] >= 0.75}
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, 'results', 'prereg_scores.json'), 'w'), indent=1, default=str)
    for k in ['P1', 'P2', 'P3', 'P4', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11']:
        v = {kk: vv for kk, vv in out[k].items()}
        print(k, json.dumps(v, default=str))
    print('P5', out['P5']['groups_passing'], '/', out['P5']['groups_total'], 'groups pass')
    for g, v in out['P5']['groups'].items():
        print('   ', g, 'frac', v['frac'], 'gammas', ['%.2f' % x for x in v['gammas']])


if __name__ == '__main__':
    main()
