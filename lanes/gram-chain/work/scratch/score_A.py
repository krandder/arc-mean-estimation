"""Score PREREG Part A (+ Amendment A1). Bootstrap over chains (B = 200). Writes results/partA_scores.json and prints a table."""
import sys, json, math, os
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/gram-chain/lib')
import gc2

RUNS = '/home/agent/workspaces/mats/work/gram-chain/runs/'
rng = np.random.default_rng(1234)
NS = [8, 16, 32, 64, 128, 256, 512, 1024]
SDE = [2.74, 3.30, 3.73, 4.14, 4.49, 4.75, 5.13]
BINS = [0, 0.3, 0.6, 1.2, 2.5, 5, 10, 1e9]
out = dict(r2={}, share={}, r3={}, r4={}, r6={})


def chain_boot(chain, vals_fn, B=200):
    """vals_fn(mask_weights) over resampled chains: resample chain ids with replacement, weight samples by counts."""
    ids = np.unique(chain)
    res = []
    for _ in range(B):
        pick = rng.choice(ids, ids.size, replace=True)
        w = np.bincount(pick, minlength=ids.max() + 1)[chain].astype(float)
        res.append(vals_fn(w))
    return float(np.std(res))


def wmean(x, w):
    return float(np.sum(w * x) / np.sum(w))


def wmedian(x, w):
    o = np.argsort(x)
    c = np.cumsum(w[o])
    return float(x[o][np.searchsorted(c, 0.5 * c[-1])])


for n in NS:
    f = RUNS + 'A_r2_n%d.npz' % n
    if not os.path.exists(f):
        continue
    z = np.load(f)
    q, d, ell, ch, ds = z['q'], z['delta'], z['ell'], z['chain'].astype(int), z['dstar']
    r = d / ds
    one = np.ones_like(r)
    rec = dict(n=n, samples=int(r.size),
               median_ratio=wmedian(r, one), median_ratio_se=chain_boot(ch, lambda w: wmedian(r, w)),
               mean_ratio=wmean(r, one), mean_ratio_se=chain_boot(ch, lambda w: wmean(r, w)),
               sd_ratio_n13=float(np.std(r) * n ** (1 / 3)),
               sd_ratio_n13_se=chain_boot(ch, lambda w: math.sqrt(wmean(r ** 2, w) - wmean(r, w) ** 2) * n ** (1 / 3)),
               sd_ell_n13=float(math.sqrt(np.mean(ell ** 2)) * n ** (1 / 3)),
               sd_ell_n13_se=chain_boot(ch, lambda w: math.sqrt(wmean(ell ** 2, w)) * n ** (1 / 3)),
               E_delta=float(d.mean()))
    rec['mean_ratio_minus1_n23'] = (rec['mean_ratio'] - 1) * n ** (2 / 3)
    bins = []
    for (lo, hi), sde in zip(zip(BINS[:-1], BINS[1:]), SDE):
        m = (q >= lo) & (q < hi)
        bins.append(dict(lo=lo, hi=hi, count=int(m.sum()), E_ell2_n23=float(np.mean(ell[m] ** 2) * n ** (2 / 3)) if m.sum() else None,
                         sde=sde, E_ratio=float(np.mean(r[m])) if m.sum() else None))
    rec['bins'] = bins
    # autocorrelations from the contiguous traces
    ac = {}
    for key, tr in (('logq', np.log(z['tr_q'])), ('ell', z['tr_ell']), ('ratio', z['tr_delta'] / gc2.mf_fixed_point(z['tr_q'].ravel() * n).reshape(z['tr_q'].shape))):
        x = tr - tr.mean()
        v = np.mean(x * x)
        T = x.shape[0]
        lagc = None
        for k in range(1, T // 2):
            c = np.mean(x[:-k] * x[k:]) / v
            if c < 1 / math.e:
                lagc = k
                break
        ac[key] = lagc
    rec['ac_lag_1e'] = ac
    rec['ac_pred'] = dict(logq=1.6 * n, ell=0.577 * n + 1, ratio=1.49 * (0.577 * n) ** (1 / 3))
    out['r2'][n] = rec

# share curves
for n in [16, 64, 256, 1024]:
    f = RUNS + 'A_share_n%d.json' % n
    if not os.path.exists(f):
        continue
    js = json.load(open(f))
    d0_own = [c for c in js['cfgs'] if c['kind'] == 'indep'][0]['E_delta']
    # registered baseline (PREREG Part A): E delta_0 from the A-r2 run at the same n (review r1 finding 5)
    d0 = out['r2'][n]['E_delta'] if n in out['r2'] else d0_own
    rows = []
    for c in js['cfgs']:
        rows.append(dict(kind=c['kind'], t=c['t'], E_delta=c['E_delta'], C=1 - c['E_delta'] / d0, se=c['se'] / d0,
                         C_own_baseline=1 - c['E_delta'] / d0_own,
                         G_over_eps=(c['E_delta'] / d0) / (1 - c['t']) if c['t'] > 0 and c['t'] < 1 else None))
    out['share'][n] = rows
    out.setdefault('share_baselines', {})[n] = dict(registered_A_r2=d0, own_run=d0_own)

for n in NS:
    f = RUNS + 'A_r4_n%d.npz' % n
    if os.path.exists(f):
        z = np.load(f)
        ch = z['chain'].astype(int)
        trC, trC2, x22 = 0.5 * z['x11'], 0.25 * z['x12'] ** 2, z['x22']
        num = 0.25 * z['x11'] * x22
        pr4 = lambda w: wmean(num, w) / wmean(trC2, w)
        out['r4'][n] = dict(PR_4rep=pr4(np.ones_like(trC)), PR_4rep_se=chain_boot(ch, pr4),
                            PR_rom=float(trC.mean() ** 2 / trC2.mean()),
                            PR_norm=float((trC / z['dstar']).mean() ** 2 / (trC2 / z['dstar'] ** 2).mean()),
                            E_trC=float(trC.mean()), cv_chain=float(math.sqrt(max(num.mean() / trC.mean() ** 2 - 1, 0))))
    f = RUNS + 'A_r3_n%d.json' % n
    if os.path.exists(f):
        out['r3'][n] = json.load(open(f))
    f = RUNS + 'A_r6_n%d.json' % n
    if os.path.exists(f):
        out['r6'][n] = json.load(open(f))

# ---- scoring ----
S = {}
r2 = out['r2']
big = [n for n in (64, 128, 256, 512, 1024) if n in r2]
if 1024 in r2:
    v = [r2[n]['sd_ell_n13'] for n in big]
    se = [r2[n]['sd_ell_n13_se'] for n in big]
    mono = all(v[i + 1] >= v[i] - 2 * math.hypot(se[i], se[i + 1]) for i in range(len(v) - 1))
    S['PA1'] = dict(hit=bool(1.70 <= r2[1024]['sd_ell_n13'] <= 2.05 and mono), value_1024=r2[1024]['sd_ell_n13'], series=v)
    ok = []
    for b in r2[1024]['bins']:
        if b['count'] >= 500:
            ok.append(abs(b['E_ell2_n23'] / b['sde'] - 1) <= 0.25)
    S['PA2'] = dict(hit=bool(all(ok)), bins=[(b['lo'], b['count'], b['E_ell2_n23'], b['sde']) for b in r2[1024]['bins']])
    med_ok = all(0.97 <= r2[n]['median_ratio'] <= 1.03 for n in big)
    pos = all(r2[n]['mean_ratio'] > 1 for n in big)
    m23 = [r2[n]['mean_ratio_minus1_n23'] for n in big]
    fac = (max(m23) / min(m23)) if min(m23) > 0 else float('inf')
    S['PA3'] = dict(hit=bool(med_ok and pos and fac <= 2), medians=[r2[n]['median_ratio'] for n in big],
                    mean_ratios=[r2[n]['mean_ratio'] for n in big], n23=m23)
    sds = [r2[n]['sd_ratio_n13'] for n in big]
    S['PA4'] = dict(hit=bool(all(1.5 <= s <= 2.4 for s in sds) and max(sds) / min(sds) <= 1.4), values=sds)
    lags = {n: r2[n]['ac_lag_1e'] for n in big}
    preds = {n: r2[n]['ac_pred'] for n in big}
    ok6 = []
    for n in big:
        L = lags[n]
        ok6.append(L['logq'] is not None and 0.8 * n <= L['logq'] <= 3.2 * n if L['logq'] is not None else False)
        ok6.append(L['ell'] is not None and 0.5 <= L['ell'] / preds[n]['ell'] <= 2)
        ok6.append(L['ratio'] is not None and 0.5 <= L['ratio'] / preds[n]['ratio'] <= 2)
    S['PA6'] = dict(hit=bool(all(ok6)), lags={n: lags[n] for n in big}, preds=preds)
sh = out['share']
if all(n in sh for n in (64, 256, 1024)):
    ok = []
    for n in (64, 256, 1024):
        rows = sh[n]
        get = lambda k, t: [x for x in rows if x['kind'] == k and abs(x['t'] - t) < 1e-9]
        for t, tgt in ((0.25, 0.175), (0.5, 0.370), (0.75, 0.603)):
            cc = get('coord', t)[0]['C']
            ok.append(abs(cc - tgt) <= 0.03)
            ok.append(abs(get('corr', t)[0]['C'] - cc) <= 0.02)
            ok.append(abs(get('block', t)[0]['C'] - cc) <= 0.05)
        if n >= 256:
            anti = get('corr', -1.0)[0]
            ok.append(abs((1 - anti['C']) / 1.587 - 1) <= 0.10)
    S['PA5'] = dict(hit=bool(all(ok)), clauses=ok)
ok7 = []
for n in (16, 32, 64, 128, 256, 512, 1024):
    if n in out['r3'] and n in out['r4']:
        pred = 1.46 * math.sqrt(2 / out['r4'][n]['PR_rom'])
        ok7.append((n, out['r3'][n]['range_over_mean'], pred, abs(out['r3'][n]['range_over_mean'] / pred - 1) <= 0.25))
S['PA7'] = dict(hit=bool(len(ok7) == 7 and all(x[3] for x in ok7)), rows=ok7,
                status=('scored' if len(ok7) == 7 else ('incomplete: %d of 7 registered widths run' % len(ok7))))
PRk = {16: 9.7, 32: 15.2, 64: 22.3, 128: 30.8, 256: 41.0, 512: 52.6, 1024: 65.8}
R3k = {16: 1.40, 32: 1.64, 64: 1.91, 128: 2.21, 256: 2.52}
ok8 = []
for n, v in R3k.items():
    if n in out['r6']:
        ok8.append(('r3', n, out['r6'][n]['r3_norm'], v, abs(out['r6'][n]['r3_norm'] / v - 1) <= 0.25))
for n, v in PRk.items():
    if n in out['r4']:
        ok8.append(('PR', n, out['r4'][n]['PR_norm'], v, abs(out['r4'][n]['PR_norm'] / v - 1) <= 0.25))
S['PA8'] = dict(hit=bool(len(ok8) == 12 and all(x[4] for x in ok8)), rows=ok8,
                status=('miss' if any(not x[4] for x in ok8) else ('incomplete: %d of 12 clauses' % len(ok8))))
if 256 in out['r4'] and 1024 in out['r4']:
    z1, z2 = np.load(RUNS + 'A_r4_n256.npz'), np.load(RUNS + 'A_r4_n1024.npz')
    def prb(z, w=None):
        num, den = 0.25 * z['x11'] * z['x22'], 0.25 * z['x12'] ** 2
        if w is None:
            return num.mean() / den.mean()
        return np.sum(w * num) / np.sum(w * den)
    sl = math.log(prb(z2) / prb(z1)) / math.log(4)
    bs = []
    c1, c2 = z1['chain'].astype(int), z2['chain'].astype(int)
    for _ in range(200):
        w1 = np.bincount(rng.integers(0, c1.max() + 1, c1.max() + 1), minlength=c1.max() + 1)[c1]
        w2 = np.bincount(rng.integers(0, c2.max() + 1, c2.max() + 1), minlength=c2.max() + 1)[c2]
        bs.append(math.log(prb(z2, w2) / prb(z1, w1)) / math.log(4))
    lo, hi = np.quantile(bs, [0.05, 0.95])
    verdict = 'n^{2/3} favoured' if (sl > 0.5 and lo > 0.42) else ('1/k favoured' if (sl < 0.5 and hi < 0.58) else 'unresolved')
    S['PA9'] = dict(slope=sl, ci90=[float(lo), float(hi)], verdict=verdict)
out['scores'] = S
json.dump(out, open('/home/agent/workspaces/mats/work/gram-chain/results/partA_scores.json', 'w'), indent=1, default=float)
print('n   median   mean    n23(mean-1)  SDratio n^1/3  SDell n^1/3   lags(logq, ell, ratio)')
for n, r in r2.items():
    print('%4d %.4f(%.4f) %.4f(%.4f) %+.3f  %.3f(%.3f)  %.3f(%.3f)  %s' % (n, r['median_ratio'], r['median_ratio_se'], r['mean_ratio'],
          r['mean_ratio_se'], r['mean_ratio_minus1_n23'], r['sd_ratio_n13'], r['sd_ratio_n13_se'], r['sd_ell_n13'], r['sd_ell_n13_se'],
          r['ac_lag_1e']))
for n, r in out['r4'].items():
    print('r4 n=%d PR_4rep=%.2f(%.2f) PR_rom=%.2f PR_norm=%.2f cv_chain=%.3f' % (n, r['PR_4rep'], r['PR_4rep_se'], r['PR_rom'], r['PR_norm'], r['cv_chain']))
for k, v in S.items():
    print(k, {kk: vv for kk, vv in v.items() if kk not in ('rows', 'bins', 'preds', 'lags', 'clauses')})
