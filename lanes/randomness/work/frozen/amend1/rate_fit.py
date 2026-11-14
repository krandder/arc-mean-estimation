"""Amendment 1 scorer: error-vs-compute exponents p (risk ~ N^-p; plain MC has p = 1) at 256 x 32 with confidence
intervals, for every series measured over a range of N, and the registered checks PA1-PA3.
Randomised series (replicate variance, unbiased designs): rqmc_std, rqmc_polar at N = 2^8 (E5), 2^10, 2^12, 2^14 (E1),
2^16 (E2), 2^18 (E5). Per net: weighted least squares of log(var) on log N, weights from the delta-method variance of
log(var) (2/(R - 1) for a chi-square-like replicate variance), slope SE from the fit. Deterministic series (E4):
sobol_rb, sobol_rb_polar, sobol_plain, lattice_rb, lattice_baker_rb: least squares of log nMSE on log N over
N = 2^8..2^16, points with nMSE >= 3 x truth floor (no weights; residual-based SE). Across nets: median and a 95%
bootstrap interval of the median (2,000 resamples of the nets).
Writes results/rates.json and results/rates.md.
"""
import json
import math
import os
import sys
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RUNS = os.environ.get('RND_SCORE_RUNS', os.path.join(ROOT, 'runs'))
OUTD = os.environ.get('RND_SCORE_OUT', os.path.join(ROOT, 'results'))
S256 = [int(x) for x in os.environ.get('RND_SCORE_S256', '200,201,202,203,204').split(',')]


def load(kind, s, n=256, L=32):
    p = os.path.join(RUNS, f'{kind}_n{n}_L{L}_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def wls(x, y, w):
    x, y, w = map(np.asarray, (x, y, w))
    W = np.sum(w); xm = np.sum(w * x) / W; ym = np.sum(w * y) / W
    sxx = np.sum(w * (x - xm) ** 2)
    b = np.sum(w * (x - xm) * (y - ym)) / sxx
    return b, math.sqrt(1.0 / sxx)


def ols(x, y):
    x, y = np.asarray(x), np.asarray(y)
    if len(x) < 3:
        return float('nan'), float('nan')
    A = np.stack([np.ones_like(x), x], 1)
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef
    s2 = float(r @ r) / (len(x) - 2)
    cov = s2 * np.linalg.inv(A.T @ A)
    return float(coef[1]), math.sqrt(cov[1, 1])


rng = np.random.default_rng(2026)


def boot_median(v, B=2000):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)])
    if len(v) == 0:
        return float('nan'), (float('nan'), float('nan'))
    meds = [np.median(rng.choice(v, size=len(v), replace=True)) for _ in range(B)]
    return float(np.median(v)), (float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5)))


per = {}
for s in S256:
    st, co, ra, dt = load('struct', s), load('combo', s), load('rates', s), load('det', s)
    for frame in ('std', 'polar'):
        pts = []                          # (N, var x N / V, R)
        if ra:
            for x in ra['series'][f'rqmc_{frame}']:
                pts.append((x['N'], x['var_x_N_over_V'], x['R']))
        if st:
            for mlog in (10, 12, 14):
                x = st['rqmc'][f'rqmc_rb_{frame}_m{mlog}']
                pts.append((x['m'], x['inv_gain_mc'], x['R']))
        if co:
            x = co['methods'][f'rqmc_{frame}']
            pts.append((co['N'], x['rep_var_x_N_over_V'], x['reps']))
        if len(pts) >= 3:
            pts.sort()
            lx = [math.log(p[0]) for p in pts]
            ly = [math.log(p[1] / p[0]) for p in pts]          # log of the risk relative to V
            w = [(p[2] - 1) / 2.0 for p in pts]
            b, se = wls(lx, ly, w)
            per.setdefault(f'rqmc_{frame}', {})[s] = dict(p=-b, se=se, N=[p[0] for p in pts],
                                                         gain=[1 / p[1] for p in pts])
    if dt:
        fl = dt['truth_floor']
        for name in ('sobol_rb', 'sobol_rb_polar', 'sobol_plain', 'lattice_rb', 'lattice_baker_rb'):
            ser = [x for x in dt['series'].get(name, []) if x['N'] >= 256 and x['nmse'] >= 3 * fl]
            if len(ser) >= 3:
                b, se = ols([math.log(x['N']) for x in ser], [math.log(x['nmse']) for x in ser])
                per.setdefault(name, {})[s] = dict(p=-b, se=se, N=[x['N'] for x in ser],
                                                   gain=[1 / x['nmse_x_N'] for x in ser])

summary = {}
for name, d in per.items():
    ps = [v['p'] for v in d.values()]
    m, ci = boot_median(ps)
    summary[name] = dict(nets=len(ps), p_median=m, p_ci95=ci, p_per_net=[round(v, 3) for v in ps],
                         se_per_net=[round(v['se'], 3) for v in d.values()])
rows = []
if 'rqmc_std' in summary:
    s_ = summary['rqmc_std']
    rows.append(('PA1', 'rqmc_std median p over 2^8..2^18 in [0.85, 1.25]', s_['p_median'],
                 0.85 <= s_['p_median'] <= 1.25, s_['nets']))
if 'rqmc_polar' in summary:
    s_ = summary['rqmc_polar']
    rows.append(('PA2', 'rqmc_polar median p in [0.85, 1.35]', s_['p_median'], 0.85 <= s_['p_median'] <= 1.35,
                 s_['nets']))
mx = max((v['p_median'] for v in summary.values() if np.isfinite(v['p_median'])), default=float('nan'))
rows.append(('PA3', 'no series has median p > 1.5 at 256 x 32', mx, mx <= 1.5, min((v['nets'] for v in summary.values()),
                                                                                    default=0)))
if 'rqmc_std' in per and 'rqmc_polar' in per:
    common = sorted(set(per['rqmc_std']) & set(per['rqmc_polar']))
    diff = [per['rqmc_polar'][s]['p'] - per['rqmc_std'][s]['p'] for s in common]
    m, ci = boot_median(diff)
    summary['polar_minus_std'] = dict(nets=len(diff), p_median=m, p_ci95=ci, p_per_net=[round(v, 3) for v in diff])
os.makedirs(OUTD, exist_ok=True)
json.dump(dict(per=per, summary=summary, rows=rows), open(os.path.join(OUTD, 'rates.json'), 'w'), indent=1,
          default=float)
with open(os.path.join(OUTD, 'rates.md'), 'w') as fh:
    fh.write('| series | nets | median p | 95% CI (bootstrap over nets) | p per net |\n|---|---|---|---|---|\n')
    for name, v in summary.items():
        fh.write(f"| {name} | {v['nets']} | {v['p_median']:.3f} | [{v['p_ci95'][0]:.3f}, {v['p_ci95'][1]:.3f}] | "
                 f"{v['p_per_net']} |\n")
    fh.write('\n| id | prediction | measured | result |\n|---|---|---|---|\n')
    for pid, text, val, ok, k in rows:
        res = ('HOLDS' if ok else 'FAILS') if k == 5 else f'PARTIAL ({k} of 5 nets)'
        fh.write(f'| {pid} | {text} | {val:.3f} | {res} |\n')
print(open(os.path.join(OUTD, 'rates.md')).read())
