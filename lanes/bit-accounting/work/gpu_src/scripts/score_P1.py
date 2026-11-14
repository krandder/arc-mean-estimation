"""Score PREREG Part P1 (phase 1) from the lane's work dir: runs/P1/P_*.json -> results/P1_scores.json and
results/P1_table.md (counts R*(D), slopes, certificate flags per cell). Written and hashed before any P1 result.
usage: python gpu_src/scripts/score_P1.py [runs dir, default runs/P1]"""
import glob
import json
import math
import os
import sys

import numpy as np

DGRID = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
DC = [0.1, 0.01]
RUNS = sys.argv[1] if len(sys.argv) > 1 else 'runs/P1'


def rate_at(rates, nmse, eps):
    pts = sorted(zip(rates, nmse))
    env, best = [], float('inf')
    for r, e in pts:
        if e is None or not np.isfinite(e) or r is None or not np.isfinite(r):
            continue
        if e < best:
            env.append((r, e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= eps:
            if i == 0:
                return float(r)
            r0, e0 = env[i - 1]
            f = (math.log(e0) - math.log(eps)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return float(r0 + f * (r - r0))
    return None


def tol(r):
    return max(0.5, 0.1 * r)


def nmse_at(rates, nmse, R):
    """nMSE of the monotone envelope of a curve at rate R (log-nMSE linear in rate); None outside its range."""
    pts = sorted((r, e) for r, e in zip(rates, nmse) if r is not None and e is not None and np.isfinite(r) and np.isfinite(e))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((r, e))
            best = e
    if not env or R < env[0][0]:
        return None
    for (r0, e0), (r1, e1) in zip(env[:-1], env[1:]):
        if r0 <= R <= r1:
            f = (R - r0) / (r1 - r0) if r1 > r0 else 0.0
            return float(math.exp(math.log(e0) + f * (math.log(e1) - math.log(e0))))
    return float(env[-1][1])


def close(ca, cb, D, ra, rb):
    """Curves a (reference) and b agree at distortion D: rates within max(0.5, 10%), or at b's rate the reference's
    nMSE is within 10% of b's (flat curves: a small error difference is a large rate difference)."""
    if ra is not None and rb is not None and ra - rb <= tol(ra):
        return True
    if rb is None:
        return True
    e = nmse_at(ca['rate'], ca['nmse'], rb)
    eb = nmse_at(cb['rate'], cb['nmse'], rb)
    return e is not None and eb is not None and e <= 1.1 * eb


cells = {}
for p in sorted(glob.glob(f'{RUNS}/P_*.json')):
    d = json.load(open(p))
    cells[(d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls'])] = d


def raw(d):
    out = {}
    for g in d['groups'].values():
        out.update(g['curves'])
    if 'linref' in d:
        out['linref'] = dict(rate=d['linref']['rate'], nmse=d['linref']['nmse'])
    return out


def curves(d):
    c = {}
    for g in d['groups'].values():
        for name, cv in g['curves'].items():
            c[name] = {str(D): rate_at(cv['rate'], cv['nmse'], D) for D in DGRID}
    if 'linref' in d:
        c['linref'] = {str(D): rate_at(d['linref']['rate'], d['linref']['nmse'], D) for D in DGRID}
    if 'refit' in d and 'r0' in d['groups'].get('G1', {}).get('curves', {}):
        rb = [min(x['rate_trained_B'], x['rate_refit_mix8'], x['rate_refit_fullgauss']) for x in d['refit']]
        nm = d['groups']['G1']['curves']['r0']['nmse']
        c['r0_refit'] = {str(D): rate_at(rb, nm, D) for D in DGRID}
    return c


def rstar(d, c):
    names = ['r0', 'r1', 'r2', 'long', 'r0_refit'] + (['wide'] if d['cls'] == 'unres' else [])
    out = {}
    for D in DGRID:
        v = [c[nm][str(D)] for nm in names if nm in c and c[nm][str(D)] is not None]
        out[str(D)] = min(v) if v else None
    return out


def slopes(R):
    s = {}
    for D1, D2 in zip(DGRID[:-1], DGRID[1:]):
        a, b = R[str(D1)], R[str(D2)]
        s[f'{D1}->{D2}'] = None if (a is None or b is None) else (b - a) / math.log2(D1 / D2)
    return s


C = {k: [] for k in ('C1', 'C2', 'C3', 'C3_local', 'C4', 'C5', 'C6', 'C7')}
info = {}
for key, d in cells.items():
    c = curves(d)
    R = rstar(d, c)
    flags = []
    for D in DC:
        s = str(D)
        rw = raw(d)
        if all(x in c for x in ('r0', 'r1', 'r2')):
            v = [c[x][s] for x in ('r0', 'r1', 'r2')]
            if any(x is not None for x in v):
                vv = [x for x in v if x is not None]
                ok = len(vv) == 3 and (max(vv) - min(vv) <= tol(float(np.median(vv))))
                if not ok:
                    Rm = float(np.median(vv))
                    es = [nmse_at(rw[x]['rate'], rw[x]['nmse'], Rm) for x in ('r0', 'r1', 'r2')]
                    ok = all(e is not None for e in es) and max(es) <= 1.1 * min(es)
                C['C1'].append(ok)
                if not ok:
                    flags.append(f'C1@{D}')
        for nm, cname in (('long', 'C2'), ('wide', 'C3' if d['cls'] == 'unres' else 'C3_local'), ('linref', 'C7')):
            if nm in c and 'r0' in c:
                a, b = (rstar(d, c)[s] if nm == 'linref' else c['r0'][s]), c[nm][s]
                if a is None and b is None:
                    continue
                if nm == 'linref':
                    ok = (b is None) or (a is not None and a - b <= max(0.3, 0.05 * b))
                    if not ok and a is None:
                        ok = False
                else:
                    ok = close(rw['r0'], rw[nm], D, a, b)
                C[cname].append(ok)
                if not ok:
                    flags.append(f'{cname}@{D}')
    for x in d.get('refit', []):
        if x['rate_trained_B'] > 1.0:
            ok = min(x['rate_refit_mix8'], x['rate_refit_fullgauss']) >= 0.95 * x['rate_trained_B']
            C['C4'].append(ok)
            if not ok and 'C4' not in flags:
                flags.append('C4')
    for x in d.get('centroid', []):
        ok = x['nmse_model'] <= 1.1 * x['nmse_centroid'] + 0.002
        C['C5'].append(ok)
        if not ok:
            flags.append(f'C5@{x["lam"]}')
    for x in d.get('groups', {}).get('G1', {}).get('fixed', []):
        lam = x['lam']
        ok = x['vr_nmse'] + lam * x['vr_rate'] <= 1.03 * (x['nmse'] + lam * x['rate'])
        C['C6'].append(ok)
        if not ok:
            flags.append(f'C6@{lam}')
    info[key] = dict(R=R, slope=slopes(R), flags=flags, RG=d['RG'], curves=c, d=d)

S = {}
for k, v in C.items():
    S[k] = dict(frac=(float(np.mean(v)) if v else None), n=len(v))
S['P1.1'] = dict(hit=(all(S[k]['frac'] is not None and S[k]['frac'] >= 0.9 for k in ('C1', 'C2', 'C3', 'C4', 'C5', 'C7'))
                      and S['C6']['frac'] is not None and S['C6']['frac'] >= 0.9))
S['C6_fallback_triggered'] = (S['C6']['frac'] is not None and S['C6']['frac'] < 0.9)
if S['C6_fallback_triggered']:
    # registered fallback: R* = lower envelope of the variable-rate curves (class's codes) and the fixed-lambda points
    for key, v in info.items():
        d = v['d']
        pts = []
        for g in d['groups'].values():
            for name, cv in g['curves'].items():
                if name == 'wide' and d['cls'] == 'local':
                    continue
                pts += list(zip(cv['rate'], cv['nmse']))
        pts += [(x['rate'], x['nmse']) for x in d['groups'].get('G1', {}).get('fixed', [])]
        R2 = {str(D): rate_at([p[0] for p in pts], [p[1] for p in pts], D) for D in DGRID}
        v['R'] = {k: (min(x for x in (v['R'][k], R2[k]) if x is not None) if (v['R'][k] is not None or R2[k] is not None)
                      else None) for k in v['R']}
        v['slope'] = slopes(v['R'])


def get(kind, n, L, s, l, cls):
    return info.get((kind, n, L, s, l, cls))


def nets(kind):
    return sorted({(k[1], k[2], k[3]) for k in info if k[0] == kind})


# KA1
ka1 = []
for (n, L, s) in nets('relu'):
    o = get('relu', n, L, s, L, 'unres')
    if o is None:
        continue
    for D in (0.1, 0.03, 0.01):
        r = o['R'][str(D)]
        ka1.append(dict(net=f'{n}x{L}_s{s}', D=D, R=r, RG=o['RG'][str(D)], ok=(r is not None and r <= o['RG'][str(D)] + 0.3)))
S['KA1'] = dict(n=len(ka1), frac=(float(np.mean([x['ok'] for x in ka1])) if ka1 else None),
                hit=(bool(ka1) and all(x['ok'] for x in ka1)), cells=ka1)
# KA2
ka2 = []
for (n, L, s) in nets('relu'):
    o = get('relu', n, L, s, L, 'unres')
    if o is None:
        continue
    for k, v in info.items():
        if k[0] == 'relu' and k[1:4] == (n, L, s) and k[5] == 'unres' and k[4] < L:
            for D in DC:
                a, b = v['R'][str(D)], o['R'][str(D)]
                if a is None and b is None:
                    continue
                ok = a is not None and b is not None and abs(a - b) <= max(0.5, 0.15 * b)
                ka2.append(ok)
S['KA2'] = dict(n=len(ka2), frac=(float(np.mean(ka2)) if ka2 else None), hit=(bool(ka2) and float(np.mean(ka2)) >= 0.9))
# KA3
ka3 = []
for k, v in info.items():
    if k[0] == 'linear':
        for D in (0.1, 0.03, 0.01):
            r, g = v['R'][str(D)], v['RG'][str(D)]
            ka3.append(dict(cell=f'l{k[4]}_{k[5]}', D=D, R=r, RG=g, ok=(r is not None and abs(r - g) <= max(0.3, 0.1 * g))))
S['KA3'] = dict(n=len(ka3), frac=(float(np.mean([x['ok'] for x in ka3])) if ka3 else None),
                hit=(bool(ka3) and all(x['ok'] for x in ka3)), cells=ka3)
# P1.2
p12 = []
for (n, L, s) in nets('relu'):
    if n != L:
        continue
    a, o = get('relu', n, L, s, 0, 'local'), get('relu', n, L, s, L, 'unres')
    if a is None or o is None or o['R']['0.1'] is None:
        continue
    r = a['R']['0.1']
    p12.append(r is None or r >= 2 * o['R']['0.1'])
S['P1.2'] = dict(n=len(p12), hits=int(sum(p12)), hit=(len(p12) == 6 and sum(p12) >= 5) if len(p12) == 6 else None)
# P1.3
p13 = []
for (n, L, s) in nets('relu'):
    ls = sorted(k[4] for k in info if k[0] == 'relu' and k[1:4] == (n, L, s) and k[5] == 'local')
    v = [info[('relu', n, L, s, l, 'local')]['R']['0.1'] for l in ls]
    v = [math.inf if x is None else x for x in v]
    if len(v) >= 2:
        p13.append(all(v[i + 1] <= v[i] + 0.5 for i in range(len(v) - 1)))
S['P1.3'] = dict(n=len(p13), frac=(float(np.mean(p13)) if p13 else None), hit=(len(p13) == 12 and float(np.mean(p13)) >= 0.8) if len(p13) == 12 else None)
# P1.4


def oslope(n, L, s):
    o = get('relu', n, L, s, L, 'unres')
    if o is None or o['R']['0.1'] is None or o['R']['0.01'] is None:
        return None
    return (o['R']['0.01'] - o['R']['0.1']) / math.log2(10.0)


p14 = []
for s in (5000, 5001, 5002):
    for (deep, shallow) in (((16, 16), (16, 4)), ((32, 32), (32, 8))):
        a, b = oslope(*deep, s), oslope(*shallow, s)
        if a is not None and b is not None:
            p14.append(dict(seed=s, deep=f'{deep[0]}x{deep[1]}', slope_deep=a, slope_shallow=b, ok=a < b))
S['P1.4'] = dict(n=len(p14), hit=(all(x['ok'] for x in p14) if len(p14) == 6 else None), cells=p14)
# P1.5
p15 = {}
o = get('tanh4', 16, 16, 5000, 16, 'unres')
if o is not None and o['R']['0.1'] is not None:
    t = []
    for l in (0, 4, 8):
        a = get('tanh4', 16, 16, 5000, l, 'local')
        if a is not None:
            t.append(a['R']['0.1'] is None or a['R']['0.1'] >= o['R']['0.1'] + 4)
    p15['tanh4'] = (all(t) if len(t) == 3 else None)
o = get('feistel', 16, 16, 5000, 16, 'unres')
a = get('feistel', 16, 16, 5000, 0, 'local')
if o is not None and a is not None and o['R']['0.1'] is not None:
    p15['feistel'] = a['R']['0.1'] is None or a['R']['0.1'] >= o['R']['0.1'] + 2
p15['linear'] = S['KA3']['hit'] if S['KA3']['n'] else None
S['P1.5'] = dict(parts=p15, hit=(all(v for v in p15.values()) if len(p15) == 3 and None not in p15.values() else None))
os.makedirs('results', exist_ok=True)
json.dump(dict(scores=S, cells={'_'.join(map(str, k)): dict(R=v['R'], slope=v['slope'], flags=v['flags'], RG=v['RG'])
                                for k, v in info.items()}), open('results/P1_scores.json', 'w'), indent=1)
fm = lambda x: '-' if x is None else f'{x:.1f}'  # noqa: E731
fs = lambda x: '-' if x is None else f'{x:.2f}'  # noqa: E731
lines = ['# Phase 1: bits needed for each output error, per layer (R*(D) in bits; "-" = not reached)', '',
         'R*(D) = smallest rate among the codes of the class (variable-rate restarts r0-r2, 2x steps, refitted prior; '
         'unres also 2x width) at which the held-out output nMSE reaches D. Slope = bits per halving of the error. '
         'R_G = Gaussian bound on the output (reverse water-filling). Flags: failed certificates (C1 restarts, C2 2x '
         'steps, C3 2x width, C4 prior refit, C5 centroid, C6 fixed-lambda spot check, C7 linear analytic reference).', '',
         '| net | seed | l | class | R*(0.3) | R*(0.1) | R*(0.03) | R*(0.01) | R*(0.003) | R*(0.001) | slope 0.1->0.03 | '
         'slope 0.03->0.01 | slope 0.01->0.003 | R_G(0.1) / R_G(0.01) | flags |', '|' + '---|' * 15]
for k in sorted(info, key=lambda k: (k[0] != 'relu', k[0], k[1], k[2], k[3], k[4], k[5])):
    v = info[k]
    R, sl = v['R'], v['slope']
    lines.append(f'| {k[0]} {k[1]}x{k[2]} | {k[3]} | {k[4] if k[4] < k[2] else "out"} | {k[5]} | ' +
                 ' | '.join(fm(R[str(D)]) for D in DGRID) + ' | ' +
                 ' | '.join(fs(sl[x]) for x in ('0.1->0.03', '0.03->0.01', '0.01->0.003')) +
                 f' | {v["RG"]["0.1"]:.1f} / {v["RG"]["0.01"]:.1f} | {" ".join(v["flags"]) or "ok"} |')
lines += ['', '## Scores', '']
for k, v in S.items():
    if isinstance(v, dict):
        lines.append(f'- {k}: ' + json.dumps({kk: vv for kk, vv in v.items() if kk != 'cells'}))
    else:
        lines.append(f'- {k}: {v}')
open('results/P1_table.md', 'w').write('\n'.join(lines) + '\n')
for k, v in S.items():
    if isinstance(v, dict):
        h = v.get('hit')
        print(k, 'HIT' if h is True else ('MISS' if h is False else '-'), {kk: vv for kk, vv in v.items() if kk not in ('cells', 'hit')})
    else:
        print(k, v)
