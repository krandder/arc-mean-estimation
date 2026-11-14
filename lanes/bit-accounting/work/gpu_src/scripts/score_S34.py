"""Score PREREG amendment S3-S4 and Part A2 (run from the lane's work dir). Writes results/S34_scores.json.
S3 counts use the monotone envelope over b (a b-bit nested code can ignore its last bits), as S1 (DEVIATIONS.md)."""
import json
import math
import os

import numpy as np

KD, ND_, CD = 'runs/S_kelvin', 'runs/S_noisy', 'runs/S_curves'
CFG = [(16, 4), (16, 16), (32, 8), (32, 32)]
EVAL = [5000, 5001, 5002]
RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]


def crossing(rates, y, eps):
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def env(y):
    return np.minimum.accumulate(np.asarray(y, float)).tolist()


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def grid(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


S = {}
# ---------------- S3
c1a, c1b, c2, c3, c5 = [], [], [], [], []
deep = []
for n, L in CFG:
    for s in EVAL:
        k = load(f'{KD}/K_n{n}_L{L}_s{s}.json')
        if k is None:
            continue
        lay = k['layers']
        out = load(f'{CD}/S_n{n}_L{L}_s{s}_l{L}_unres.json')
        b_out = None if out is None else crossing(RATES, env(out['curves']['bin']['nmse']), 0.1)
        for i, l in enumerate(lay):
            A = k['phases']['A']['nmse'][str(i)]
            C = k['phases']['C']['nmse'][str(i)]
            rA = [A['recon'][-1][j] for j in range(2)]
            rC = [C['recon'][-1][j] for j in range(2)]
            if L - l <= 8:
                c1a.append(rC[0] >= 2 * rA[0])
                c1b.append(rC[1] / max(rA[1], 1e-12) < rC[0] / max(rA[0], 1e-12))
            fwd0 = crossing(RATES, env([v[0] for v in C['fwd']]), 0.1)
            if L - l <= 4 and b_out is not None:
                c2.append(fwd0 is not None and abs(fwd0 - b_out) <= max(0.25 * b_out, 2.0))
            elif b_out is not None:
                deep.append(dict(n=n, L=L, seed=s, l=l, fwd=fwd0, b_out=b_out))
            o0 = crossing(RATES, env([v[0] for v in C['out']]), 0.1)
            if o0 is not None and fwd0 is not None:
                c3.append(o0 <= fwd0 + 1)
        if (n, L) in [(16, 16), (32, 32)]:
            loc = load(f'{CD}/S_n{n}_L{L}_s{s}_l0_local.json')
            if loc is not None:
                bl = crossing(RATES, env(loc['curves']['bin']['nmse']), 0.1)
                C0 = k['phases']['C']['nmse']['0']
                f05 = crossing(RATES, env([v[1] for v in C0['fwd']]), 0.1)
                c5.append((bl is None and f05 is not None) or (bl is not None and f05 is not None and f05 <= 0.8 * bl))
f = lambda x: (float(np.mean(x)) if x else None)  # noqa: E731
S['S3.1'] = dict(frac_shortcut=f(c1a), frac_floor_smaller=f(c1b), n=len(c1a),
                 hit=(bool(c1a) and f(c1a) >= 0.75 and f(c1b) >= 0.75))
S['S3.2'] = dict(frac=f(c2), n=len(c2), deep=deep, hit=(bool(c2) and f(c2) >= 0.75))
S['S3.3'] = dict(frac=f(c3), n=len(c3), hit=(bool(c3) and f(c3) >= 0.75))
# S3.4: S3 transitions against S2 jointly trained local chains (same net, b, transition)
c4 = []
for n, L in CFG:
    for s in EVAL:
        k = load(f'{KD}/K_n{n}_L{L}_s{s}.json')
        ch = load(f'runs/S_chain/C_n{n}_L{L}_s{s}_local.json')
        if k is None or ch is None:
            continue
        for b, lst in k['transitions'].items():
            if b not in ch['per_b']:
                continue
            for i, models in enumerate(lst):
                a3 = models[0]['majority_ptf_acc']['1']
                a2 = ch['per_b'][b]['transitions'][i]['majority_ptf_acc']['1']
                c4.append(a3 < a2)
S['S3.4'] = dict(frac=f(c4), n=len(c4), hit=(bool(c4) and f(c4) >= 0.6))
S['S3.5'] = dict(n=len(c5), hits=sum(c5), hit=(len(c5) > 0 and sum(c5) >= 4))
# ---------------- S4
viol, pts = [], 0
c2n, c3n = [], []
for n, L in [(16, 16), (32, 32)]:
    for s in EVAL:
        per = {}
        for l in grid(L) + [L]:
            for cls in ['local', 'unres']:
                r = load(f'{ND_}/N_n{n}_L{L}_s{s}_l{l}_{cls}.json')
                if r is None:
                    continue
                for kind, cu in r['curves'].items():
                    for j in range(len(cu['rate'])):
                        pts += 1
                        tol = 0.01 * cu['crn'][j] + 3 * cu['crn_se'][j]
                        if cu['mean_err'][j] > cu['dist'][j] + tol or cu['dist'][j] > cu['crn'][j] + tol or \
                                cu['avg'][j] > cu['crn'][j] + tol:
                            viol.append(dict(n=n, L=L, seed=s, l=l, cls=cls, kind=kind, rate=cu['rate'][j]))
                if l < L:
                    per[(l, cls)] = crossing(r['rates'], env(r['curves']['gauss']['crn']), 0.1)
        un = [per.get((l, 'unres')) for l in grid(L) if (l, 'unres') in per]
        if len(un) >= 2:
            reached = [v for v in un if v is not None]
            if reached and len(reached) < len(un):
                c2n.append(True)
            elif reached:
                c2n.append(max(reached) / max(min(reached), 1e-9) >= 1.5)
        for l in grid(L):
            if (l, 'local') in per and (l, 'unres') in per:
                lo, un_ = per[(l, 'local')], per[(l, 'unres')]
                c3n.append(lo is None or (un_ is not None and lo >= un_ - 1))
S['S4.1'] = dict(points=pts, violations=viol[:20], n_viol=len(viol), hit=(pts > 0 and not viol))
S['S4.2'] = dict(n=len(c2n), hits=sum(c2n), hit=(len(c2n) > 0 and sum(c2n) >= 4))
S['S4.3'] = dict(frac=f(c3n), n=len(c3n), hit=(bool(c3n) and f(c3n) >= 0.75))
# ---------------- A2 (narrow-deep linear codes)
a21, a22 = [], []
for s in [203, 216, 217, 220, 221, 223]:
    d = load(f'runs/lin_nd_{s}.json')
    if d is None:
        continue

    def best(l, e):
        ent = d['layers'][str(l)]
        v = [ent[k]['cross'][e][1] for k in ['as_gauss', 'lin_gauss'] if k in ent and ent[k]['cross'][e][1] is not None]
        return min(v) if v else None
    ok = True
    for l in [32, 64, 128, 192, 255]:
        for e in ['0.1', '0.01', '0.001']:
            v = best(l, e)
            if v is None or abs(v - 0.5 * math.log2(1 / float(e))) > 0.6:
                ok = False
    a21.append(ok)
    c0, c32 = best(0, '0.1'), best(32, '0.1')
    a22.append(c0 is None or (c32 is not None and c0 >= 3 * c32))
S['A2.1'] = dict(per_net=a21, hit=sum(a21) >= 5)
S['A2.2'] = dict(per_net=a22, hit=sum(a22) >= 5)
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/S34_scores.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
for k, v in S.items():
    print(k, 'HIT' if v['hit'] else ('MISS' if v['hit'] is False else 'n/a'),
          {kk: vv for kk, vv in v.items() if kk not in ('deep', 'violations', 'per_net')})
