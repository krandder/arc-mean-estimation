"""POST HOC recomputations requested by the GPT-6 review (review/review_gpt6.md, findings 5-7, 10, 14). Writes
results/review_recompute.json and prints the numbers used in the revised report. Nothing here changes a registered
outcome; the hashed outputs are kept.
(5) literal-wording versions of P1 and P3: raw b2 (no max(b2, noise, 1e-7) floor) and the PREREG truth-floor rule (values
    below 10x the truth's nMSE floor, 6e-8 at n = 64, 128 and 1.5e-8 at 256, are not used in ratios; non-positive
    denominators excluded);
(6) success counts of the D1 variants per width (NaN runs);
(7) medians of PAIRED per-net ratios: PCA/future recursion b2 at k = n/4; D1 retained factor q_proj/q_3 = e_k3/e_proj;
(10) the hypothetical dedicated window with one extra K = 2 pilot (the mean-field gate probabilities come from a separate
     K = 2 run);
(14) the n = 256, l = 24, k = 64 paired single-cut counts and medians."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402  (side-effect free; importing score_part1 would rewrite its output)

out = {}
FLOOR = S.FLOOR
CONF = S.CONF


def raw(d, v):
    r = d['variants'].get(v)
    return None if r is None or 'b2' not in r else r['b2']


# (5) P3 literal and P1 literal
p3 = {}
for n, L, seeds in CONF:
    rq, rh = [], []
    for s in seeds:
        d = S.load('rec', n, L, s)
        if d is None:
            continue
        g = raw(d, 'gauss'); q = raw(d, f'futnl{n // 4}'); h = raw(d, f'futnl{n // 2}')
        lim = 10 * FLOOR[n]
        if g is not None and q is not None and g > lim and q > lim:   # both sides above the truth floor (review r2)
            rq.append(g / q)
        if g is not None and h is not None and g > lim and h > lim:
            rh.append(g / h)
    p3[n] = dict(I_quarter=S.med(rq), I_half=S.med(rh), n_quarter=len(rq), n_half=len(rh))
out['P3_literal'] = p3
p1 = {}
for l in (4, 8, 16, 24):
    rs = []
    for s in range(200, 205):
        d = S.load('cut', 256, 32, s)
        if d is None or str(l) not in d['cuts']:
            continue
        v = d['cuts'][str(l)]['variants']
        a, b = v['cond_futnl64']['b2'], v['cond_pca64']['b2']
        if b < 5e-6 or a < 10 * FLOOR[256]:
            continue
        rs.append(a / b)
    p1[l] = dict(median=S.med(rs), nets=len(rs), holds=(len(rs) > 0 and S.med(rs) <= 0.5))
out['P1_literal'] = dict(cuts=p1, holds=sum(1 for c in p1.values() if c['holds']) >= 3)

# (7) paired PCA/future recursion ratios at k = n/4
pr = {}
for n, L, seeds in CONF:
    rs = []
    for s in seeds:
        d = S.load('rec', n, L, s)
        if d is None:
            continue
        f, p = raw(d, f'futnl{n // 4}'), raw(d, f'pca{n // 4}')
        if f and p and f > 0 and p > 0:
            rs.append(p / f)
    pr[n] = dict(median=S.med(rs), per_net=rs)
out['pca_over_future_recursion_paired'] = pr

# (6, 7, 10) D1: success counts, paired retained factors, window with an extra k2 pilot
d1 = {}
for n, L, seeds in CONF:
    succ = {}; retained = {}; G0 = []; G1 = []
    for s in seeds:
        d = S.load('k3p', n, L, s)
        if d is None:
            continue
        e2 = d['k2']['nmse']; e3 = d['variants']['none']['nmse']
        cur = S.rqmc_curve(n, L, s)
        for v, r in d['variants'].items():
            ok = bool(np.isfinite(r['nmse']))
            succ.setdefault(v, [0, 0]); succ[v][1] += 1; succ[v][0] += int(ok)
            if ok and v != 'none':
                retained.setdefault(v, []).append(e3 / r['nmse'])
        r = d['variants'].get(f'futmf2_{n // 4}')
        if r is not None and np.isfinite(r['nmse']):
            k = n // 4
            c0 = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + 2.0 * n
            c1 = c0 + d['k2']['passes']
            G0.append(S.rqmc_err(cur, c0)[0] / r['nmse']); G1.append(S.rqmc_err(cur, c1)[0] / r['nmse'])
    d1[n] = dict(success=succ, retained_factor_median={v: S.med(x) for v, x in retained.items()},
                 window_G_registered=S.med(G0), window_G_with_extra_k2_pilot=S.med(G1))
out['D1'] = d1

# (14) paired single cut at 256, l = 24, k = 64
fs, ps, better = [], [], 0
for s in range(200, 205):
    d = S.load('cut', 256, 32, s)
    v = d['cuts']['24']['variants']
    fs.append(v['cond_futnl64']['b2']); ps.append(v['cond_pca64']['b2'])
    better += int(v['cond_pca64']['b2'] > v['cond_futnl64']['b2'])
out['cut256_l24_k64'] = dict(futnl_median=S.med(fs), pca_median=S.med(ps), future_better=better, nets=len(fs))
json.dump(out, open(os.path.join(S.RES, 'review_recompute.json'), 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k != 'D1'}, indent=1, default=float)[:3000])
for n, v in d1.items():
    print(n, 'success n/2:', {kk: vv for kk, vv in v['success'].items() if kk.endswith(str(n // 2)) or kk.endswith(f'_{n // 2}')},
          'retained (paired e3/e):', {kk: round(vv, 3) for kk, vv in v['retained_factor_median'].items() if kk in (f'futv{n // 4}', f'futmf2_{n // 4}', f'pca{n // 4}', f'futv{n // 8}', f'pca{n // 8}', f'futv{n // 2}', f'futmf2_{n // 2}', 'futv16', 'pca16')},
          'window G registered %.2f, with extra k2 pilot %.2f' % (v['window_G_registered'], v['window_G_with_extra_k2_pilot']))
