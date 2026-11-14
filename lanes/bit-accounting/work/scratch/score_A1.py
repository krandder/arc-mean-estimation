"""Score PREREG Part A1 (ARC 256 x 32). Writes results/A1_scores.json and results/A1_tables.md.
Rules exactly as registered; "unreached" (no crossing within 256) is None, counted as 257 where a rule says so."""
import json
import os

import numpy as np

SEEDS = [4000, 4001, 4002, 4003]
LAYERS = [0, 2, 4, 8, 16, 24, 31]
EPS = [0.1, 0.01]
REL = '/home/agent/workspaces/mats/work/relevance/results/part1_scores.json'


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def learned(seed, l, kind, eps):
    d = load(f'runs/A1_arc{seed}_l{l}_{kind}.json')
    if d is None:
        return 'missing'
    v = d.get(f'b_{eps}')
    return None if (v is None or v[1] is None) else float(v[1])


def linear(seed, l, kind, eps):
    d = load(f'runs/lin_arc_{seed}.json')
    if d is None or str(l) not in d['layers']:
        return 'missing'
    ent = d['layers'][str(l)]
    vals = []
    for b in ['as', 'lin']:
        k = f'{b}_{kind}'
        if k in ent:
            c = ent[k]['cross'][str(eps)]
            if c[1] is not None:
                vals.append(float(c[1]))
    return min(vals) if vals else None


def theory(seed):
    return load(f'results/theory_arc_{seed}.json')


def rel_N(seed, l, eps):
    d = load(REL)
    for c in d['cells']:
        if c['mode'] == 'arc' and c['seed'] == seed and c['l'] == l:
            v = c.get(f'Nvec_{eps}')
            return None if v is None else v[1]
    return 'missing'


def ok(x):
    return x is not None and x != 'missing'


def big(x):
    return 257.0 if x is None else x


S = {}
cells = {}
for s in SEEDS:
    for l in LAYERS + [32]:
        for e in [0.1, 0.01, 0.001]:
            for kind in ['gauss', 'fsq', 'bin']:
                cells[(s, l, kind, e)] = learned(s, l, kind, e)
            # linear codes: 'gauss' = analog water-filled, 'fsq' = Lloyd-Max transform code ('bin' in lin_codes.py)
            cells[('lin', s, l, 'gauss', e)] = linear(s, l, 'gauss', e)
            cells[('lin', s, l, 'fsq', e)] = linear(s, l, 'bin', e)

# A1.1
rows = []
for s in SEEDS:
    th = theory(s)
    for e in EPS:
        C = cells[(s, 32, 'gauss', e)]
        R = th['rwf_out'][str(e)] if th else None
        if ok(C) and R is not None:
            rows.append(dict(seed=s, eps=e, C_out=C, R_out=R, hit=C <= 1.05 * R + 1))
        else:
            rows.append(dict(seed=s, eps=e, C_out=C, R_out=R, hit=None))
nets_ok = [all(r['hit'] for r in rows if r['seed'] == s and r['hit'] is not None) and
           any(r['hit'] is not None for r in rows if r['seed'] == s) for s in SEEDS]
S['A1.1'] = dict(rows=rows, hit=all(nets_ok) and all(r['hit'] is not None for r in rows))

# A1.2
viol, checked = [], 0
for s in SEEDS:
    for l in LAYERS:
        for e in EPS:
            Co = cells[(s, 32, 'gauss', e)]
            Cl = [x for x in [cells[(s, l, 'gauss', e)], cells[('lin', s, l, 'gauss', e)]] if ok(x)]
            if ok(Co) and Cl:
                checked += 1
                if min(Cl) < 0.9 * Co - 2:
                    viol.append(dict(seed=s, l=l, eps=e, C_local_min=min(Cl), C_out=Co))
S['A1.2'] = dict(checked=checked, violations=viol, hit=(checked > 0 and not viol))

# A1.3
per = []
for s in SEEDS:
    vals = [cells[(s, 0, k, 0.1)] for k in ['gauss', 'fsq']] + [cells[('lin', s, 0, k, 0.1)] for k in ['gauss', 'fsq']]
    if any(v == 'missing' for v in vals):
        per.append(None)
    else:
        per.append(all(v is None for v in vals))
S['A1.3'] = dict(per_net=per, hit=sum(1 for p in per if p) >= 3)

# A1.4
per = []
for s in SEEDS:
    good = []
    for e in EPS:
        for k in ['gauss', 'fsq']:
            a, b = cells[(s, 31, k, e)], cells[(s, 32, k, e)]
            if a == 'missing' or b == 'missing':
                good.append(None)
            elif b is None:
                good.append(None)
            else:
                good.append(a is not None and a <= 1.25 * b)
    per.append(None if any(g is None for g in good) else all(good))
S['A1.4'] = dict(per_net=per, hit=sum(1 for p in per if p) >= 3)

# A1.5
per = []
for s in SEEDS:
    seq = [(l, cells[(s, l, 'gauss', 0.1)]) for l in LAYERS if cells[(s, l, 'gauss', 0.1)] != 'missing']
    okk = True
    for (l1, a), (l2, b) in zip(seq[:-1], seq[1:]):
        if big(b) > 1.1 * big(a) + 2:
            okk = False
    per.append(dict(layers=[x[0] for x in seq], vals=[x[1] for x in seq], hit=okk))
S['A1.5'] = dict(per_net=per, hit=sum(1 for p in per if p['hit'] and len(p['layers']) >= 2) >= 3)

# A1.6
rat = []
for s in SEEDS:
    for l in LAYERS + [32]:
        for e in EPS:
            b, C = cells[(s, l, 'fsq', e)], cells[(s, l, 'gauss', e)]
            if ok(b) and ok(C):
                rat.append(dict(seed=s, l=l, eps=e, ratio=b / C, hit=1.0 <= b / C <= 1.7))
S['A1.6'] = dict(cells=rat, frac=(np.mean([r['hit'] for r in rat]) if rat else None),
                 hit=(bool(rat) and np.mean([r['hit'] for r in rat]) >= 0.75))

# A1.7
rr = []
for s in SEEDS:
    for l in [16, 31, 32]:
        bs, bf = cells[(s, l, 'bin', 0.1)], cells[(s, l, 'fsq', 0.1)]
        if bs != 'missing' and ok(bf):
            rr.append(dict(seed=s, l=l, sign=bs, fsq=bf, hit=(bs is None or bs >= 1.5 * bf)))
S['A1.7'] = dict(cells=rr, hit=(bool(rr) and np.mean([r['hit'] for r in rr]) >= 0.75))

# A1.8
per = []
for s in SEEDS:
    a, b = cells[(s, 31, 'gauss', 0.01)], cells[('lin', s, 31, 'gauss', 0.01)]
    per.append(None if not (ok(a) and ok(b)) else a >= 0.85 * b)
S['A1.8'] = dict(per_net=per, hit=sum(1 for p in per if p) >= 3)

# A1.9
rr = []
for s in SEEDS:
    th = theory(s)
    for l in [0, 2, 4, 8]:
        C = cells[(s, l, 'gauss', 0.1)]
        if ok(C) and th:
            ra = th['layers'][str(l)]['rwf_as']['0.1']
            rr.append(dict(seed=s, l=l, C=C, rwf_as=ra, hit=ra >= C))
out_cmp = []
for s in SEEDS:
    th = theory(s)
    for e in EPS:
        C = cells[(s, 32, 'gauss', e)]
        if ok(C) and th:
            out_cmp.append(dict(seed=s, eps=e, C_out=C, R_out=th['rwf_out'][str(e)], ratio=C / th['rwf_out'][str(e)]))
S['A1.9'] = dict(cells=rr, out_vs_theory=out_cmp,
                 hit=(None if not rr else np.mean([r['hit'] for r in rr]) >= 0.75))

# A1.10
rr = []
for s in SEEDS:
    for l in [16, 24, 31]:
        b, N = cells[(s, l, 'fsq', 0.1)], rel_N(s, l, 0.1)
        if ok(b) and ok(N):
            rr.append(dict(seed=s, l=l, b=b, N=N, ratio=b / N, hit=1.5 <= b / N <= 8))
S['A1.10'] = dict(cells=rr, hit=(bool(rr) and np.mean([r['hit'] for r in rr]) >= 0.75))

# A1.11
pts = []
for s in SEEDS:
    for l in LAYERS + [32]:
        for k in ['gauss', 'fsq', 'bin']:
            d = load(f'runs/A1_arc{s}_l{l}_{k}.json')
            if d is None:
                continue
            for c in d['curve']:
                if c['nmse'] <= 0.1 and c['mean_err'] > 3 * c['mean_floor']:
                    pts.append(c['mean_err'] < c['nmse'] / 10)
S['A1.11'] = dict(points=len(pts), frac=(float(np.mean(pts)) if pts else None),
                  hit=(None if not pts else float(np.mean(pts)) >= 0.8))


def tojson(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    raise TypeError(type(o))


os.makedirs('results', exist_ok=True)
json.dump(dict(scores=S, cells={str(k): v for k, v in cells.items()}), open('results/A1_scores.json', 'w'),
          default=tojson, indent=1)
for k, v in S.items():
    print(k, 'HIT' if v['hit'] else ('MISS' if v['hit'] is False else 'n/a'))
