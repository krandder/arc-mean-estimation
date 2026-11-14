"""Scorer for PREREG Part 1 (P1-P9) plus summary tables. Reads runs/{cut,rec,k3p,hyb}_n{N}_L{L}_s{SEED}.json (eval
files have no tag) and arc-update's RQMC curves. Writes results/score_part1.json and results/tables_part1.md.
RQMC error at cost C (passes): log-log interpolation of the mean-over-scrambles nMSE; outside the measured N range,
slope -1 from the nearest end (labelled 'extrapolated' in the tables)."""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, '..', 'runs'); RES = os.path.join(HERE, '..', 'results')
AU_RUNS = '/home/agent/workspaces/mats/work/arc-update/runs'
CONF = [(64, 8, list(range(300, 308))), (128, 16, list(range(300, 308))), (256, 32, list(range(200, 205)))]


def load(kind, n, L, s):
    p = os.path.join(RUNS, f'{kind}_n{n}_L{L}_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def rqmc_curve(n, L, s):
    d = json.load(open(os.path.join(AU_RUNS, f'rqmc_n{n}_L{L}_s{s}.json')))
    return np.array([r['N'] for r in d['rows']], float), np.array([r['mean_nmse'] for r in d['rows']], float)


def rqmc_err(curve, C):
    N, e = curve
    if C <= N[0]:
        return float(e[0] * N[0] / C), True
    if C >= N[-1]:
        return float(e[-1] * N[-1] / C), True
    return float(np.exp(np.interp(np.log(C), np.log(N), np.log(e)))), False


def rqmc_cost(curve, err):
    N, e = curve
    if err >= e[0]:
        return float(N[0] * e[0] / err)
    if err <= e[-1]:
        return float(N[-1] * e[-1] / err)
    return float(np.exp(np.interp(np.log(err), np.log(e[::-1]), np.log(N[::-1]))))


def med(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.median(x)) if x else float('nan')


score = {}; tab = []

# ---------------- P1 (B1 at n = 256) ----------------
n, L, seeds = 256, 32, list(range(200, 205))
p1 = {}
for l in (4, 8, 16, 24):
    rs = []
    for s in seeds:
        d = load('cut', n, L, s)
        if d is None or str(l) not in d['cuts']:
            continue
        v = d['cuts'][str(l)]['variants']
        a, b = v.get('cond_futnl64', {}).get('b2'), v.get('cond_pca64', {}).get('b2')
        if a is None or b is None or b < 5e-6:
            continue
        rs.append(a / b)
    p1[l] = dict(ratios=rs, median=med(rs), holds=(len(rs) > 0 and med(rs) <= 0.5))
score['P1'] = dict(cuts=p1, holds=sum(1 for c in p1.values() if c['holds']) >= 3)

# ---------------- B2 helpers ----------------


def rec_b2(d, v):
    r = d['variants'].get(v)
    if r is None or 'b2' not in r:
        return None
    return max(r['b2'], r.get('noise', 0.0), 1e-7)


b2tab = {}
for n, L, seeds in CONF:
    vs = ['gauss', 'radg', 'futnl16', f'futnl{n // 4}', f'futnl{n // 2}', f'pca{n // 4}', f'pca{n // 2}', f'rand{n // 4}']
    rows = {}
    for v in dict.fromkeys(vs):
        vals = []
        for s in seeds:
            d = load('rec', n, L, s)
            vals.append(rec_b2(d, v) if d else None)
        rows[v] = vals
    b2tab[n] = rows


def ratio_med(n, num, den):
    rs = []
    for a, b in zip(b2tab[n][num], b2tab[n][den]):
        if a is not None and b is not None:
            rs.append(a / b)
    return med(rs), rs


I16 = {n: ratio_med(n, 'gauss', 'futnl16') for n, _, _ in CONF}
score['P2'] = dict(I16={n: v[0] for n, v in I16.items()}, holds=I16[256][0] < I16[64][0])
p3 = {}
for n, L, _ in CONF:
    a, _ = ratio_med(n, 'gauss', f'futnl{n // 4}'); b, _ = ratio_med(n, 'gauss', f'futnl{n // 2}')
    p3[n] = dict(I_quarter=a, I_half=b, holds=(a >= 2 and b >= 10))
score['P3'] = dict(widths=p3, holds=all(v['holds'] for v in p3.values()))
p4 = {}
for n, L, _ in CONF:
    a = med(b2tab[n][f'futnl{n // 4}']); b = med(b2tab[n][f'pca{n // 4}'])
    p4[n] = dict(futnl=a, pca=b, holds=a < b)
score['P4'] = dict(widths=p4, holds=all(v['holds'] for v in p4.values()))

# ---------------- P5: B2 as an estimator ----------------
p5 = {}
for n, L, seeds in CONF:
    gs = []
    for s in seeds:
        d = load('rec', n, L, s)
        r = d['variants'].get(f'futnl{n // 2}') if d else None
        if r is None or 'passes_per_rep' not in r:
            gs.append(None); continue
        e = float(np.mean(r['nmse_reps']))
        er, _ = rqmc_err(rqmc_curve(n, L, s), r['passes_per_rep'])
        gs.append(er / e)
    p5[n] = dict(G=gs, holds=all(g is not None and g < 0.5 for g in gs))
score['P5'] = dict(widths=p5, holds=all(v['holds'] for v in p5.values()))

# ---------------- D1: P6-P8 ----------------
p6 = {}; d1tab = {}
for n, L, seeds in CONF:
    R = {'futv': [], 'pca': [], 'futmf2': []}
    rows = {}
    for s in seeds:
        d = load('k3p', n, L, s)
        if d is None:
            continue
        e2 = d['k2']['nmse']; e3 = d['variants'].get('none', {}).get('nmse')
        cur = rqmc_curve(n, L, s)
        for v, r in d['variants'].items():
            er, ex = rqmc_err(cur, r['passes'])
            rows.setdefault(v, []).append(dict(nmse=r['nmse'], passes=r['passes'], G=er / r['nmse'], extrap=ex))
        for kind in R:
            for kk in (n // 4, n // 8):
                r = d['variants'].get(f'{kind}{kk}')
                if r is not None and e3 is not None and e2 > e3:
                    R[kind].append((kk, (e2 - r['nmse']) / (e2 - e3)))
    d1tab[n] = rows
    Rk = {kind: {kk: med([v for k2_, v in R[kind] if k2_ == kk]) for kk in (n // 4, n // 8)} for kind in R}
    a = Rk['futv'][n // 4] >= 0.7
    b = Rk['pca'][n // 8] < Rk['futv'][n // 8]
    p6[n] = dict(R=Rk, a=a, b=b, holds=(a and b))
score['P6'] = dict(widths=p6, holds=all(v['holds'] for v in p6.values()))
n, L = 256, 32
gs_all = []
for v, rows in d1tab.get(256, {}).items():
    gs_all += [r['G'] for r in rows]
score['P7'] = dict(G_all=gs_all, holds=(len(gs_all) > 0 and all(g < 0.2 for g in gs_all)))
p8 = {}
for kind in ('futmf2', 'futv'):
    gs = []
    for s in range(200, 205):
        d = load('k3p', n, L, s)
        if d is None or f'{kind}64' not in d['variants']:
            continue
        k = 64
        cback = (1 << 11) * 3 * (L - 1) / 2.0 if kind == 'futv' else 2.0 * n
        cded = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + cback
        e = d['variants'][f'{kind}64']['nmse']
        er, _ = rqmc_err(rqmc_curve(n, L, s), cded)
        gs.append(er / e)
    p8[kind] = dict(G=gs, median=med(gs), holds=(len(gs) > 0 and med(gs) <= 3))
score['P8'] = dict(kinds=p8, holds=all(v['holds'] for v in p8.values()))

# ---------------- H1: P9 ----------------
p9 = {}
eta1, betas, gains = [], {}, []
for s in range(200, 205):
    d = load('hyb', 256, 32, s)
    if d is None:
        continue
    cur = rqmc_curve(256, 32, s)
    lay = d['layers']
    if '1' in lay:
        eta1.append(min(v['eta'] for v in lay['1']['surrogates'].values()))
    best = 0.0
    for l, row in lay.items():
        for name, sv in row['surrogates'].items():
            if int(l) >= 8:
                betas.setdefault((int(l), name), []).append(sv['beta']['eg'])
            C = 6.5e4
            B = row['eg_cost'] + sv['setup_passes']
            if B >= C:
                continue
            Nn = (C - B) / sv['a']
            Ns = np.array([2.0 ** int(m) for m in sv['rqmc']]); es = np.array([sv['rqmc'][m] for m in sv['rqmc']])
            o = np.argsort(Ns); Ns, es = Ns[o], es[o]
            eres = float(es[-1] * Ns[-1] / Nn) if Nn >= Ns[-1] else float(np.exp(np.interp(np.log(Nn), np.log(Ns), np.log(es))))
            tot = sv['beta']['eg'] + eres
            er, _ = rqmc_err(cur, C)
            best = max(best, er / tot)
    gains.append(best)
bmin = min((med(v) for v in betas.values()), default=float('nan'))
p9 = dict(eta_l1=eta1, a=(med(eta1) >= 0.25), beta_min_median_l8plus=bmin, b=(bmin >= 1e-4), best_gain=gains,
          c=(len(gains) > 0 and med(gains) <= 2))
p9['holds'] = p9['a'] and p9['b'] and p9['c']
score['P9'] = p9

json.dump(score, open(os.path.join(RES, 'score_part1.json'), 'w'), indent=1, default=float)
for k, v in score.items():
    print(k, 'HOLDS' if v.get('holds') else 'FAILS', {kk: vv for kk, vv in v.items() if kk != 'holds'})
