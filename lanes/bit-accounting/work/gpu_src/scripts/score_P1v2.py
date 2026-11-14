"""Score PREREG Part P1 with amendment P1-A (score_P1.py v2). Run from the work dir:
python gpu_src/scripts/score_P1v2.py [runs/P1] [runs/P1X] -> results/P1_scores.json, results/P1_table.md.
Crossing (primary, conservative): the rate at which the monotone envelope of a curve's achieved points reaches D, with
time-sharing (linear in nMSE) between adjacent points; secondary: the registered log-linear interpolation.
Counts per cell: R_r0 (the registered single model) and R* (minimum over the class's codes: r0-r2, long, r0_refit,
explorer x0-x2, wdec; wide for unres only; plus the fixed points if the C6 fallback applies)."""
import glob
import json
import math
import os
import sys

import numpy as np

DGRID = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
RUNS = sys.argv[1] if len(sys.argv) > 1 else 'runs/P1'
XRUNS = sys.argv[2] if len(sys.argv) > 2 else 'runs/P1X'
YRUNS = sys.argv[3] if len(sys.argv) > 3 else 'runs/P1Y'


def envelope(rates, nmse):
    pts = sorted((r, e) for r, e in zip(rates, nmse) if r is not None and e is not None and np.isfinite(r) and np.isfinite(e))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((max(r, 0.0), e))
            best = e
    return env


def cross(rates, nmse, D, mode='ts'):
    env = envelope(rates, nmse)
    for i, (r, e) in enumerate(env):
        if e <= D:
            if i == 0:
                return float(r)
            r0, e0 = env[i - 1]
            if mode == 'ts':
                f = (e0 - D) / (e0 - e)
            else:
                f = (math.log(e0) - math.log(D)) / (math.log(e0) - math.log(max(e, 1e-30)))
            return float(r0 + f * (r - r0))
    return None


def nmse_at(rates, nmse, R):
    env = envelope(rates, nmse)
    if not env or R < env[0][0]:
        return None
    for (r0, e0), (r1, e1) in zip(env[:-1], env[1:]):
        if r0 <= R <= r1:
            return e0 + ((R - r0) / (r1 - r0) if r1 > r0 else 0.0) * (e1 - e0)
    return env[-1][1]


def tol(r):
    return max(0.5, 0.1 * r)


def close(ca, cb, D):
    ra, rb = cross(ca['rate'], ca['nmse'], D), cross(cb['rate'], cb['nmse'], D)
    if ra is None and rb is None:
        return None
    if rb is None:
        return True
    if ra is not None and ra - rb <= tol(ra):
        return True
    e, eb = nmse_at(ca['rate'], ca['nmse'], rb), nmse_at(cb['rate'], cb['nmse'], rb)
    return e is not None and eb is not None and e <= 1.1 * eb


cells, xcells = {}, {}
for p in sorted(glob.glob(f'{RUNS}/P_*.json')):
    d = json.load(open(p))
    cells[(d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls'])] = d
for p in sorted(glob.glob(f'{XRUNS}/X_*.json')):
    x = json.load(open(p))
    xcells[(x['netkind'], x['n'], x['L'], x['seed'], x['l'], x['cls'])] = x
ycells = {}
for p in sorted(glob.glob(f'{YRUNS}/Y_*.json')):
    y = json.load(open(p))
    ycells[(y['netkind'], y['n'], y['L'], y['seed'], y['l'], y['cls'])] = y


def manifest():
    m = []
    for kind, n, L, seeds in [('relu', 16, 4, (5000, 5001, 5002)), ('relu', 32, 8, (5000, 5001, 5002)),
                              ('relu', 16, 16, (5000, 5001, 5002)), ('relu', 32, 32, (5000, 5001, 5002)),
                              ('tanh4', 16, 16, (5000,)), ('feistel', 16, 16, (5000,)), ('linear', 16, 16, (5000,))]:
        for s in seeds:
            for l in sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])):
                m += [(kind, n, L, s, l, 'local'), (kind, n, L, s, l, 'unres')]
            m.append((kind, n, L, s, L, 'unres'))
    return m


MAN = manifest()
complete = all(k in cells for k in MAN)
xcomplete = all(k in xcells for k in MAN)


def curves_of(d, x):
    c = {}
    for g in d['groups'].values():
        c.update(g['curves'])
    if 'refit' in d:
        rb = [min(q['rate_trained_B'], q['rate_refit_mix8'], q['rate_refit_fullgauss']) for q in d['refit']]
        c['r0_refit'] = dict(rate=rb, nmse=d['groups']['G1']['curves']['r0']['nmse'])
    if x is not None:
        for k, v in x.get('explorer', {}).items():
            c[k] = v
        if 'wdec' in x:
            c['wdec'] = x['wdec']
    return c


C = {k: [] for k in ('C1', 'C2', 'C3', 'C3_local', 'C4', 'C5', 'C5v2', 'C6_r0', 'C6_long', 'C7')}
NC = {k: 0 for k in C}
info = {}
for key, d in cells.items():
    x = xcells.get(key)
    c = curves_of(d, x)
    yv = ycells.get(key)
    if yv is not None:
        for k2, cv in yv['curves'].items():
            c['y' + k2] = cv
    names = [k for k in ('r0', 'r1', 'r2', 'long', 'r0_refit', 'x0', 'x1', 'x2', 'wdec') if k in c] + \
        sorted(k for k in c if k.startswith('y'))
    if d['cls'] == 'unres' and 'wide' in c:
        names.append('wide')
    flags = []
    for D in DGRID:
        s = str(D)
        rr = [cross(c[k]['rate'], c[k]['nmse'], D) for k in ('r0', 'r1', 'r2')]
        if all(v is None for v in rr):
            NC['C1'] += 1
        else:
            vv = [v for v in rr if v is not None]
            ok = len(vv) == 3 and max(vv) - min(vv) <= tol(float(np.median(vv)))
            if not ok and len(vv) == 3:
                es = [nmse_at(c[k]['rate'], c[k]['nmse'], float(np.median(vv))) for k in ('r0', 'r1', 'r2')]
                ok = all(e is not None for e in es) and max(es) <= 1.1 * min(es)
            C['C1'].append(ok)
            if not ok:
                flags.append(f'C1@{D}')
        for nm, cname in (('long', 'C2'), ('wide', 'C3' if d['cls'] == 'unres' else 'C3_local')):
            if nm in c:
                ok = close(c['r0'], c[nm], D)
                if ok is None:
                    NC[cname] += 1
                    continue
                C[cname].append(ok)
                if not ok:
                    flags.append(f'{cname}@{D}')
    for q in d.get('refit', []):
        if q['rate_trained_B'] > 1.0:
            ok = min(q['rate_refit_mix8'], q['rate_refit_fullgauss']) >= 0.95 * q['rate_trained_B']
            C['C4'].append(ok)
            if not ok and 'C4' not in flags:
                flags.append('C4')
    for q in d.get('centroid', []):
        C['C5'].append(q['nmse_model'] <= 1.1 * q['nmse_centroid'] + 0.002)
    if x is not None:
        for q in x.get('centroid2', []):
            conv = abs(q['train_loss_q4'] - q['train_loss_q3']) <= 0.02 * max(q['train_loss_q3'], 1e-12)
            ok = q['nmse_model'] <= 1.05 * q['nmse_corrected'] + 0.002
            if not conv:                                  # unconverged comparator: neither pass nor fail
                NC['C5v2'] += 1
                flags.append(f'C5v2conv@{q["lam"]}')
                continue
            C['C5v2'].append(ok)
            if not ok:
                flags.append(f'C5v2@{q["lam"]}')
    fixed = d['groups'].get('G1', {}).get('fixed', [])
    for q in fixed:
        lam = q['lam']
        Lf = q['nmse'] + lam * q['rate']
        ok = q['vr_nmse'] + lam * q['vr_rate'] <= 1.03 * Lf
        C['C6_r0'].append(ok)
        if not ok:
            flags.append(f'C6@{lam}')
        if 'long' in c:
            gi = min(range(len(d['grid'])), key=lambda i: abs(math.log10(d['grid'][i]) - math.log10(lam)))
            C['C6_long'].append(c['long']['nmse'][gi] + lam * c['long']['rate'][gi] <= 1.03 * Lf)
    lr = (dict(rate=x['linref']['rate_heldout_power'], nmse=x['linref']['nmse']) if x is not None
          else dict(rate=d['linref']['rate'], nmse=d['linref']['nmse']))
    info[key] = dict(d=d, x=x, c=c, names=names, flags=flags, linref=lr, fixed=fixed)

S = {k: dict(frac=(float(np.mean(v)) if v else None), n=len(v), not_covered=NC[k]) for k, v in C.items()}
fallback = S['C6_r0']['frac'] is not None and S['C6_r0']['frac'] < 0.9
S['C6_fallback_triggered'] = fallback
for key, v in info.items():
    c, names = v['c'], v['names']
    pts = [(r, e) for nm in names for r, e in zip(c[nm]['rate'], c[nm]['nmse'])]
    fx = [(q['rate'], q['nmse']) for q in v['fixed']] if fallback else []
    R, R_ll, Rr0, src = {}, {}, {}, {}
    for D in DGRID:
        s = str(D)
        per = {nm: cross(c[nm]['rate'], c[nm]['nmse'], D) for nm in names}
        best = min((r for r in per.values() if r is not None), default=None)
        pooled_vr = cross([p[0] for p in pts], [p[1] for p in pts], D)
        pooled = cross([p[0] for p in pts + fx], [p[1] for p in pts + fx], D)
        cands = [r for r in (best, pooled_vr, pooled) if r is not None]
        R[s] = min(cands) if cands else None
        if R[s] is None:
            src[s] = None
        elif fallback and pooled is not None and pooled < min(r for r in (best, pooled_vr) if r is not None) - 1e-9 \
                if any(r is not None for r in (best, pooled_vr)) else (pooled is not None):
            src[s] = 'fixed'
        elif pooled_vr is not None and (best is None or pooled_vr < best - 1e-9):
            src[s] = 'pooled'
        else:
            src[s] = min((k for k in per if per[k] is not None), key=lambda k: per[k])
        per_ll = [cross(c[nm]['rate'], c[nm]['nmse'], D, 'll') for nm in names]
        per_ll += [cross([p[0] for p in pts], [p[1] for p in pts], D, 'll'),
                   cross([p[0] for p in pts + fx], [p[1] for p in pts + fx], D, 'll')]
        R_ll[s] = min((r for r in per_ll if r is not None), default=None)
        Rr0[s] = cross(c['r0']['rate'], c['r0']['nmse'], D)
        rl = cross(v['linref']['rate'], v['linref']['nmse'], D)
        if R[s] is None and rl is None:
            NC['C7'] += 1
        elif R[s] is None:                    # learned curves do not reach D within the price range: not covered
            NC['C7'] += 1
            v['flags'].append(f'C7@{D}(not covered)')
        elif rl is not None:
            ok = R[s] - rl <= max(0.3, 0.05 * rl)
            C['C7'].append(ok)
            if not ok:
                v['flags'].append(f'C7@{D}')
    v.update(R=R, R_ll=R_ll, Rr0=Rr0, src=src, Rlin={str(D): cross(v['linref']['rate'], v['linref']['nmse'], D) for D in DGRID})
S['C7'] = dict(frac=(float(np.mean(C['C7'])) if C['C7'] else None), n=len(C['C7']), not_covered=NC['C7'])
S['coverage'] = dict(main=f'{sum(k in cells for k in MAN)}/{len(MAN)}', certificates=f'{sum(k in xcells for k in MAN)}/{len(MAN)}')


def slope(R, D1, D2):
    a, b = R[str(D1)], R[str(D2)]
    return None if (a is None or b is None) else (b - a) / math.log2(D1 / D2)


def get(kind, n, L, s, l, cls):
    return info.get((kind, n, L, s, l, cls))


def pending(cond):
    return 'pending' if not complete else cond


ka1 = []
for (kind, n, L, s, l, cls) in MAN:
    if kind == 'relu' and l == L and get(kind, n, L, s, l, cls):
        o = get(kind, n, L, s, l, cls)
        for D in (0.1, 0.03, 0.01):
            r = o['R'][str(D)]
            ka1.append(r is not None and r <= o['d']['RG'][str(D)] + 0.3)
S['KA1'] = dict(n=len(ka1), frac=(float(np.mean(ka1)) if ka1 else None), hit=pending(bool(ka1) and all(ka1)))
ka2 = []
for (kind, n, L, s, l, cls) in MAN:
    if kind == 'relu' and cls == 'unres' and l < L and get(kind, n, L, s, l, cls) and get(kind, n, L, s, L, 'unres'):
        a, o = get(kind, n, L, s, l, cls), get(kind, n, L, s, L, 'unres')
        for D in (0.1, 0.01):
            ra, ro = a['R'][str(D)], o['R'][str(D)]
            if ra is None and ro is None:
                continue
            ka2.append(ra is not None and ro is not None and abs(ra - ro) <= max(0.5, 0.15 * ro))
S['KA2 (empirical comparison)'] = dict(n=len(ka2), frac=(float(np.mean(ka2)) if ka2 else None),
                                       hit=pending(bool(ka2) and float(np.mean(ka2)) >= 0.9))
ka3 = []
for k, v in info.items():
    if k[0] == 'linear':
        for D in (0.1, 0.03, 0.01):
            r, g = v['R'][str(D)], v['d']['RG'][str(D)]
            ka3.append(r is not None and abs(r - g) <= max(0.3, 0.1 * g))
S['KA3'] = dict(n=len(ka3), frac=(float(np.mean(ka3)) if ka3 else None), hit=pending(bool(ka3) and all(ka3)))
S['P1.1'] = dict(note='C1, C2, C3 (unres), C4, C5 (v2), C7 >= 90% each; C6 has its own rule (fallback)',
                 hit=('pending' if not (complete and xcomplete) else
                      (all(S[k]['frac'] is not None and S[k]['frac'] >= 0.9 for k in ('C1', 'C2', 'C3', 'C4', 'C7'))
                       and (S['C5v2']['frac'] or 0) >= 0.9)))
p12 = []
for s in (5000, 5001, 5002):
    for n in (16, 32):
        a, o = get('relu', n, n, s, 0, 'local'), get('relu', n, n, s, n, 'unres')
        if a and o and o['R']['0.1'] is not None:
            p12.append(a['R']['0.1'] is None or a['R']['0.1'] >= 2 * o['R']['0.1'])
S['P1.2'] = dict(n=len(p12), hits=int(sum(p12)), hit=pending(len(p12) == 6 and sum(p12) >= 5))
p13 = []
for (n, L) in ((16, 4), (32, 8), (16, 16), (32, 32)):
    for s in (5000, 5001, 5002):
        ls = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
        vv = [get('relu', n, L, s, l, 'local') for l in ls]
        if all(vv):
            r = [math.inf if q['R']['0.1'] is None else q['R']['0.1'] for q in vv]
            p13.append(all(r[i + 1] <= r[i] + 0.5 for i in range(len(r) - 1)))
S['P1.3'] = dict(n=len(p13), frac=(float(np.mean(p13)) if p13 else None), hit=pending(len(p13) == 12 and float(np.mean(p13)) >= 0.8))
p14 = []
for s in (5000, 5001, 5002):
    for deep, shallow in (((16, 16), (16, 4)), ((32, 32), (32, 8))):
        a, b = get('relu', *deep, s, deep[1], 'unres'), get('relu', *shallow, s, shallow[1], 'unres')
        if a and b:
            sa, sb = slope(a['R'], 0.1, 0.01), slope(b['R'], 0.1, 0.01)
            if sa is not None and sb is not None:
                p14.append(sa < sb)
S['P1.4'] = dict(n=len(p14), hits=int(sum(p14)), hit=pending(len(p14) == 6 and all(p14)))
p15 = {}
o = get('tanh4', 16, 16, 5000, 16, 'unres')
if o and o['R']['0.1'] is not None:
    t = [get('tanh4', 16, 16, 5000, l, 'local') for l in (0, 4, 8)]
    if all(t):
        p15['tanh4'] = all(q['R']['0.1'] is None or q['R']['0.1'] >= o['R']['0.1'] + 4 for q in t)
o, a = get('feistel', 16, 16, 5000, 16, 'unres'), get('feistel', 16, 16, 5000, 0, 'local')
if o and a and o['R']['0.1'] is not None:
    p15['feistel'] = a['R']['0.1'] is None or a['R']['0.1'] >= o['R']['0.1'] + 2
p15['linear'] = S['KA3']['hit']
S['P1.5'] = dict(parts=p15, hit=pending(len(p15) == 3 and all(v is True for v in p15.values())))
b1, b2 = [], []
for key, v in info.items():
    yv = ycells.get(key)
    if yv is None:
        continue
    c = v['c']
    xa = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in ('x0', 'x1', 'x2') if k in c]
    xa = [q for q in xa if q is not None]
    yb = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in c if k.startswith('yx') and not k.startswith('yxl')]
    yb = [q for q in yb if q is not None]
    yl = [cross(c[k]['rate'], c[k]['nmse'], 0.1) for k in c if k.startswith('yxl')]
    yl = [q for q in yl if q is not None]
    if key[0] == 'relu' and key[4] in (0, key[2] // 4, key[2] // 2) and xa and (yb or yl):
        b1.append(min(yb + yl) >= 0.95 * min(xa))          # registered: the best P1-B code (incl. 12000-step explorers)
    if yb and yl:
        b2.append(min(yl) >= min(yb) - max(0.5, 0.05 * min(yb)))
S['B1'] = dict(n=len(b1), hits=int(sum(b1)), hit=(bool(b1) and float(np.mean(b1)) >= 0.75) if b1 else 'pending')
S['B2'] = dict(n=len(b2), hits=int(sum(b2)), hit=(bool(b2) and float(np.mean(b2)) >= 0.75) if b2 else 'pending')
os.makedirs('results', exist_ok=True)
json.dump(dict(scores=S, cells={'_'.join(map(str, k)): dict(R=v['R'], R_loglinear=v['R_ll'], R_r0=v['Rr0'], source=v['src'],
                                                            R_linref=v['Rlin'], flags=v['flags'], RG=v['d']['RG'],
                                                            gates_r0=(v['x'] or {}).get('gates_r0'),
                                                            gates_explorer=(v['x'] or {}).get('gates_explorer'))
                                for k, v in info.items()}),
          open('results/P1_scores.json', 'w'), indent=1)
fm = lambda q: '-' if q is None else f'{q:.1f}'  # noqa: E731
fs = lambda q: '-' if q is None else f'{q:.2f}'  # noqa: E731
lines = ['# Phase 1: bits needed per layer for each output error (R* in bits; "-" = not reached in the lambda range)', '',
         f'Coverage: main cells {S["coverage"]["main"]}, extra certificates {S["coverage"]["certificates"]}. R* = smallest '
         'rate among the class\'s codes (variable-rate restarts r0-r2, 2x steps, refitted prior, explorer restarts, '
         'width-n encoder with wide decoder; unres also 2x width) reaching held-out output nMSE D, conservative '
         '(time-sharing between achieved points). R_r0 = the single registered model. slope = bits per halving of the '
         'error. lin = the linear analytic reference. Flags: failed certificates (C1 restarts, C2 2x steps, C3 2x width, '
         'C4 prior refit, C5v2 centroid, C6 fixed-lambda spot check, C7 linear reference).', '',
         '| net | seed | l | class | R*(0.3) | R*(0.1) | R*(0.03) | R*(0.01) | R*(0.003) | R*(0.001) | R_r0(0.1) / (0.01) | '
         'lin(0.1) / (0.01) | slope .1->.03 | .03->.01 | .01->.003 | R_G(0.1) / (0.01) | source of R*(0.1) / (0.01) | flags |',
         '|' + '---|' * 18]
for k in sorted(info, key=lambda k: (k[0] != 'relu', k[0], k[1], k[2], k[3], k[4], k[5])):
    v = info[k]
    R = v['R']
    lines.append(f'| {k[0]} {k[1]}x{k[2]} | {k[3]} | {k[4] if k[4] < k[2] else "out"} | {k[5]} | ' +
                 ' | '.join(fm(R[str(D)]) for D in DGRID) +
                 f' | {fm(v["Rr0"]["0.1"])} / {fm(v["Rr0"]["0.01"])} | {fm(v["Rlin"]["0.1"])} / {fm(v["Rlin"]["0.01"])} | ' +
                 ' | '.join(fs(slope(R, a, b)) for a, b in ((0.1, 0.03), (0.03, 0.01), (0.01, 0.003))) +
                 f' | {v["d"]["RG"]["0.1"]:.1f} / {v["d"]["RG"]["0.01"]:.1f} | {v["src"]["0.1"]} / {v["src"]["0.01"]} | '
                 f'{" ".join(sorted(set(v["flags"]))) or "ok"} |')
lines += ['', '## Scores', ''] + [f'- {k}: ' + json.dumps(val) for k, val in S.items()]
open('results/P1_table.md', 'w').write('\n'.join(lines) + '\n')
for k, val in S.items():
    print(k, val)
