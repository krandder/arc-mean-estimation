"""Score the registered predictions S5.1-S10.2 (run from the lane's work dir). Writes results/S5to10_scores.json.
Written before the S5-S10 results were complete (hashed in prereg_hashes.txt before its first run)."""
import glob
import json
import math
import os

import numpy as np

GRID8 = [1, 2, 3, 4, 6, 8, 12, 16]
GRID10 = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def crossing(rates, y, eps):
    y = np.minimum.accumulate(np.asarray(y, float))
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def rate_at(rates, nmse, eps):
    pts = sorted(zip(rates, nmse))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return r
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return r0 + f * (r - r0)
    return None


f = lambda x: (float(np.mean(x)) if x else None)  # noqa: E731
S = {}
# ---------------- S5
toy = load('runs/S_cert/toy.json') or {}
t1 = []
for k in [2, 4, 8]:
    for cls in ['local', 'unres']:
        r = toy.get(f'toy_k{k}_{cls}')
        if r is None:
            continue
        need = min(g for g in GRID8 if g >= k)
        got = next((g for g, v in zip(GRID8, np.minimum.accumulate(r['nmse'])) if v <= 1e-3), None)
        t1.append(dict(k=k, cls=cls, measured=got, expected=need, hit=(got == need)))
S['S5.1'] = dict(cells=t1, hit=(bool(t1) and all(c['hit'] for c in t1)))
c2, c3, c5 = [], [], []
by_cell = {}
for p in glob.glob('runs/S_cert/Z_*.json'):
    d = load(p)
    for c in d['cert']:
        if c['rate'] <= 8:
            c2.append(c['centroid'] >= 0.8 * c['model'])
        if c['rate'] >= 4:
            c3.append(c['nn'] < 0.8 * c['centroid'])
        if d['cls'] == 'local' and d['l'] <= d['L'] // 4 and c['rate'] >= 4 and c.get('within') is not None:
            gain_u = c['centroid'] - c['nn']
            if gain_u > 1e-6:
                c5.append((c['centroid'] - c['within']) < 0.5 * gain_u)
    by_cell.setdefault((d['n'], d['L'], d['l'], d['cls']), {})[d['variant']] = crossing(GRID8, [c['model'] for c in d['cert']], 0.1)
S['S5.2'] = dict(frac=f(c2), n=len(c2), hit=(bool(c2) and f(c2) >= 0.75))
S['S5.3'] = dict(frac=f(c3), n=len(c3), hit=(bool(c3) and f(c3) >= 0.5))
c4 = []
for key, v in by_cell.items():
    rs = [v.get(x) for x in ('base', 'r1', 'r2') if x in v]
    if len(rs) == 3:
        vals = [33.0 if x is None else x for x in rs]
        ok = max(vals) - min(vals) <= 1.5
        if 'big' in v:
            bb = 33.0 if v['big'] is None else v['big']
            ok = ok and (bb <= vals[0] + 1.5)
        c4.append(ok)
S['S5.4'] = dict(frac=f(c4), n=len(c4), hit=(bool(c4) and f(c4) >= 0.75))
S['S5.5'] = dict(frac=f(c5), n=len(c5), hit=(bool(c5) and f(c5) >= 0.75))
# ---------------- S6
vq = {}
for p in ['runs/S_vq/vq.json', 'runs/S_vq/vq_b.json']:
    vq.update(load(p) or {})
bounds = load('results/bounds_small.json') or {}
c61, c62, c63 = [], [], []
for key, e in vq.items():
    n, L, s = key.split('_')
    n, L, s = int(n[1:]), int(L[1:]), int(s[1:])
    bvq = e['cross_free']['0.1']
    cand = [bounds.get(key, {}).get('rwf', {}).get('0.1')]
    out = load(f'runs/S_curves/S_n{n}_L{L}_s{s}_l{L}_unres.json')
    if out is not None:
        cand.append(crossing(GRID10, out['curves']['gauss']['nmse'], 0.1))
    lin = load(f'runs/lin_small{n}x{L}_{s}.json')
    if lin is not None:
        ent = lin['layers'][str(L)]
        cand += [ent[k]['cross']['0.1'][1] for k in ('lin_gauss',) if k in ent]
    cand = [c for c in cand if c is not None]
    if bvq is None or not cand:
        continue
    cb = min(cand)
    c61.append(bvq <= 1.3 * cb)
    c62.append(bvq >= cb)
    bm = e['cross_medoid']['0.1']
    c63.append(bm is not None and abs(bm - bvq) <= 0.5)
S['S6.1'] = dict(frac=f(c61), n=len(c61), hit=(bool(c61) and f(c61) >= 0.75))
S['S6.2'] = dict(frac=f(c62), n=len(c62), hit=(bool(c62) and f(c62) >= 0.75))
S['S6.3'] = dict(frac=f(c63), n=len(c63), hit=(bool(c63) and f(c63) >= 0.75))
# ---------------- S7 / S8
E = {}
for p in glob.glob('runs/S_ent/E_*.json'):
    d = load(p)
    E[(d['n'], d['L'], d['seed'], d['l'], d['cls'])] = d
c71, c72, c73, c74a, c74b, c81, c82 = [], [], [], [], [], [], []
for (n, L, s, l, cls), d in E.items():
    g = d['curves']['gfix']
    R = rate_at(g['rate'], g['nmse'], 0.1)
    out = E.get((n, L, s, L, 'unres'))
    Ro = rate_at(out['curves']['gfix']['rate'], out['curves']['gfix']['nmse'], 0.1) if out else None
    if cls == 'unres' and l < L and L - l <= 8 and Ro is not None:
        c71.append(R is not None and abs(R - Ro) <= max(0.25 * Ro, 1.0))
    if cls == 'local' and l == 0 and n == L and Ro is not None:
        c72.append(R is None or R >= 2 * Ro)
    if not all(k in d['curves'] for k in ('vib', 'ent', 'bern')):   # gfix-only cell (compute deviation 02:48Z)
        for rt, rf in zip(g['rate'], g.get('rate_refit', [])):
            if rt > 0.5:
                c74a.append(rf >= 0.95 * rt)
        continue
    s1 = load(f'runs/S_curves/S_n{n}_L{L}_s{s}_l{l}_{cls}.json')
    Cs1 = crossing(GRID10, s1['curves']['gauss']['nmse'], 0.1) if s1 else None
    Rv = rate_at(d['curves']['vib']['rate'], d['curves']['vib']['nmse'], 0.1)
    Re = rate_at(d['curves']['ent']['rate'], d['curves']['ent']['nmse'], 0.1)
    ref = [x for x in (Cs1, Rv) if x is not None]
    if Re is not None and ref:
        c73.append(Re <= 1.2 * min(ref) + 1)
    for rt, rf in zip(g['rate'], g.get('rate_refit', [])):
        if rt > 0.5:
            c74a.append(rf >= 0.95 * rt)
    ent = d['curves']['ent']
    for rt, jp in zip(ent['rate'], ent.get('joint_plugin', [])):
        if jp is not None:
            c74b.append(jp <= rt + 0.5)
    b = d['curves']['bern']
    half0 = np.array(b['bits_half'][0])
    info0 = np.array(b['bit_info'][0])
    infoL = np.array(b['bit_info'][-1])
    c81.append(float(np.mean((half0 > 0.5) & (info0 < 0.1))) >= 0.75 and float(np.mean(infoL > 0.3)) >= 0.5)
    Rb = rate_at(b['rate'], b['nmse'], 0.1)
    if Rb is not None and R is not None:
        c82.append(Rb <= 1.5 * R + 1)
S['S7.1'] = dict(frac=f(c71), n=len(c71), hit=(bool(c71) and f(c71) >= 0.75))
S['S7.2'] = dict(n=len(c72), hits=int(sum(c72)), hit=(len(c72) >= 1 and sum(c72) >= min(5, len(c72))))
S['S7.3'] = dict(frac=f(c73), n=len(c73), hit=(bool(c73) and f(c73) >= 0.75))
S['S7.4'] = dict(frac_refit=f(c74a), n_refit=len(c74a), frac_plugin=f(c74b), n_plugin=len(c74b),
                 hit=(bool(c74a) and f(c74a) >= 0.9 and (not c74b or f(c74b) >= 0.9)))
S['S8.1'] = dict(frac=f(c81), n=len(c81), hit=(bool(c81) and f(c81) >= 0.75))
S['S8.2'] = dict(frac=f(c82), n=len(c82), hit=(bool(c82) and f(c82) >= 0.75))
# ---------------- S9
c91, c91s, c92 = [], [], []
for p in glob.glob('runs/S_real/R_*.json'):
    d = load(p)
    for pm in d['per_model']:
        for t in pm['transitions']:
            c91.append(t['learned']['W1_exact'] >= 0.7)
            c91s.append(t['base_highdeg']['W1_exact'] <= 0.1)
            c92.append(t['learned']['n_inputs_1pct'] >= 3)
S['S9.1'] = dict(frac=f(c91), sanity=f(c91s), n=len(c91), hit=(bool(c91) and f(c91) >= 0.75))
S['S9.2'] = dict(frac=f(c92), n=len(c92), hit=(bool(c92) and f(c92) >= 0.5))
# ---------------- S10
Q = {}
for p in glob.glob('runs/S_sim/Q_*.json'):
    d = load(p)
    Q[(d['n'], d['L'], d['kind'])] = d
c101, c102 = [], []
for (n, L) in [(16, 16), (32, 32)]:
    mlp = Q.get((n, L, 'mlp'))
    for kind in ('linear', 'shared'):
        d = Q.get((n, L, kind))
        if d is None or mlp is None:
            continue
        for mi in range(len(d['lambdas'])):
            c101.append(d['nmse'][-1][mi] <= mlp['nmse'][-1][mi] + 0.05)
        if 'deductive_err' in d:
            for mi in range(len(d['lambdas'])):
                e4, e65 = d['deductive_err']['4096'][mi], d['deductive_err']['65536'][mi]
                c102.append(e65 >= 0.5 * e4 and e65 > d['mc_rqmc']['65536']['mc'])
S['S10.1'] = dict(frac=f(c101), n=len(c101), hit=(bool(c101) and all(c101)))
S['S10.2'] = dict(frac=f(c102), n=len(c102), hit=(bool(c102) and all(c102)))
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/S5to10_scores.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
for k, v in S.items():
    h = v['hit']
    print(k, 'HIT' if h is True else ('MISS' if h is False else 'n/a'), {kk: vv for kk, vv in v.items() if kk not in ('cells',)})
