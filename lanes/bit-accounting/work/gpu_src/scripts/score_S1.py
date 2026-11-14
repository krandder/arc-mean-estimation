"""Score PREREG Part S1 from runs/S_curves (run from the lane's work dir). Writes results/S1_scores.json."""
import json
import os
import sys

import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else 'runs/S_curves'
CFG = [(16, 4), (16, 16), (32, 8), (32, 32)]
EVAL = [5000, 5001, 5002]
EPS = ['0.1', '0.01']


def grid(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


def get(n, L, s, l, cls):
    p = os.path.join(D, f'S_n{n}_L{L}_s{s}_l{l}_{cls}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def cross(r, kind, e):
    return None if r is None else r['curves'][kind]['cross'][e]


S = {}
# S1.1
rows = []
for n, L in CFG:
    for s in EVAL:
        out = get(n, L, s, L, 'unres')
        for l in grid(L):
            r = get(n, L, s, l, 'unres')
            for e in EPS:
                for kind in ['bin', 'gauss']:
                    co = cross(out, kind, e)
                    if co is None or r is None:
                        continue
                    cl = cross(r, kind, e)
                    hit = cl is not None and abs(cl - co) <= max(0.15 * co, 1.5)
                    rows.append(dict(n=n, L=L, seed=s, l=l, t=L - l, eps=e, kind=kind, c_layer=cl, c_out=co, hit=hit))
sh = [r for r in rows if r['t'] <= 8]
S['S1.1'] = dict(frac_shallow=(np.mean([r['hit'] for r in sh]) if sh else None), n_shallow=len(sh),
                 deep=[r for r in rows if r['t'] >= 12], hit=(bool(sh) and np.mean([r['hit'] for r in sh]) >= 0.75),
                 rows=rows)
# S1.2
per = []
for n, L in [(16, 16), (32, 32)]:
    for s in EVAL:
        r0, out = get(n, L, s, 0, 'local'), get(n, L, s, L, 'unres')
        if r0 is None or out is None:
            per.append(None)
            continue
        c0, co = cross(r0, 'gauss', '0.1'), cross(out, 'gauss', '0.1')
        per.append(dict(n=n, L=L, seed=s, c_local0=c0, c_out=co,
                        hit=(c0 is None) or (co is not None and c0 >= 1.5 * co)))
S['S1.2'] = dict(per_net=per, hit=sum(1 for p in per if p and p['hit']) >= 5)
# S1.3
per = []
for n, L in CFG:
    for s in EVAL:
        r, out = get(n, L, s, L - 1, 'local'), get(n, L, s, L, 'unres')
        if r is None or out is None:
            continue
        ok = []
        for e in EPS:
            co = cross(out, 'gauss', e)
            if co is None:
                continue
            c = cross(r, 'gauss', e)
            ok.append(c is not None and c <= 1.25 * co + 1)
        if ok:
            per.append(dict(n=n, L=L, seed=s, hit=all(ok)))
S['S1.3'] = dict(per_net=per, hit=(bool(per) and np.mean([p['hit'] for p in per]) >= 0.75))
# S1.4
per = []
for n, L in CFG:
    for s in EVAL:
        vals = []
        for l in grid(L):
            r = get(n, L, s, l, 'local')
            if r is not None:
                c = cross(r, 'gauss', '0.1')
                vals.append(33.0 if c is None else c)
        if len(vals) >= 2:
            hit = all(b <= 1.1 * a + 1 for a, b in zip(vals[:-1], vals[1:]))
            per.append(dict(n=n, L=L, seed=s, vals=vals, hit=hit))
S['S1.4'] = dict(per_net=per, hit=(bool(per) and np.mean([p['hit'] for p in per]) >= 0.75))
# S1.5
rows = []
for n, L in CFG:
    for s in EVAL:
        for l in grid(L):
            rl, rn = get(n, L, s, l, 'local'), get(n, L, s, l, 'linear')
            if rl is None or rn is None:
                continue
            for e in EPS:
                cn = cross(rn, 'gauss', e)
                if cn is None:
                    continue
                cl = cross(rl, 'gauss', e)
                rows.append(dict(n=n, L=L, seed=s, l=l, eps=e, c_local=cl, c_linear=cn,
                                 hit=cl is not None and cl <= 1.1 * cn + 1))
S['S1.5'] = dict(rows=rows, hit=(bool(rows) and np.mean([r['hit'] for r in rows]) >= 0.75))
# S1.6
rows = []
for n, L in CFG:
    for s in EVAL:
        for l in grid(L) + [L]:
            for cls in (['local', 'linear', 'unres'] if l < L else ['unres']):
                r = get(n, L, s, l, cls)
                if r is None:
                    continue
                b, c = cross(r, 'bin', '0.1'), cross(r, 'gauss', '0.1')
                if b is not None and c is not None:
                    rows.append(dict(n=n, L=L, seed=s, l=l, cls=cls, ratio=b / c, hit=1.0 <= b / c <= 2.5))
S['S1.6'] = dict(rows=rows, frac=(np.mean([r['hit'] for r in rows]) if rows else None),
                 hit=(bool(rows) and np.mean([r['hit'] for r in rows]) >= 0.75))
# S1.7
pts = []
for n, L in CFG:
    for s in EVAL:
        for l in grid(L) + [L]:
            for cls in ['local', 'linear', 'unres']:
                r = get(n, L, s, l, cls)
                if r is None:
                    continue
                for kind in ['bin', 'gauss']:
                    cu = r['curves'][kind]
                    for nm, me, fl in zip(cu['nmse'], cu['mean_err'], cu['mean_floor']):
                        if nm <= 0.1 and me > 3 * fl:
                            pts.append(me < nm / 10)
S['S1.7'] = dict(points=len(pts), frac=(float(np.mean(pts)) if pts else None),
                 hit=(None if not pts else float(np.mean(pts)) >= 0.8))
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/S1_scores.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
for k, v in S.items():
    print(k, 'HIT' if v['hit'] else ('MISS' if v['hit'] is False else 'n/a'),
          {kk: vv for kk, vv in v.items() if kk in ('frac', 'frac_shallow', 'n_shallow', 'points')})
