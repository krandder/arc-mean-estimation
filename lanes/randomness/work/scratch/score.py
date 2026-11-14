"""Scorer for PREREG.md (registered predictions). Reads runs/{struct,combo,noise,det}_*.json of the evaluation nets and
writes results/score.json and results/scorecard.md. Rules exactly as PREREG.md states them; nets without a run are
reported as missing (a prediction over k of K nets is scored only when all K runs exist, otherwise PARTIAL).
"""
import glob
import json
import math
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'lib'))
import rnd  # noqa: E402

S256 = [int(x) for x in os.environ.get('RND_SCORE_S256', '200,201,202,203,204').split(',')]
LAD = {32: 4, 64: 8, 128: 16}
LSEEDS = [int(x) for x in os.environ.get('RND_SCORE_LSEEDS', ','.join(str(v) for v in range(300, 308))).split(',')]
RUNS = os.environ.get('RND_SCORE_RUNS', os.path.join(ROOT, 'runs'))
OUTD = os.environ.get('RND_SCORE_OUT', os.path.join(ROOT, 'results'))


def load(kind, n, L, s):
    p = os.path.join(RUNS, f'{kind}_n{n}_L{L}_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def med(x):
    x = [v for v in x if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return float(np.median(x)) if x else float('nan')


rows = []


def gsa_pool(r):
    """Per-layer GSA pooled over delta = 1e-6, 1e-5, 1e-4: sum of flips / sum of 2 sqrt(delta/pi)."""
    ds = ('1e-06', '1e-05', '0.0001')
    fl = sum(np.array(r['gauss'][d]['flips']) for d in ds)
    return fl / sum(2 * math.sqrt(float(d) / math.pi) for d in ds)


def row(pid, text, measured, ok, n_have, n_need):
    status = ('HOLDS' if ok else 'FAILS') if n_have == n_need else f'PARTIAL ({n_have} of {n_need} nets): ' + \
        ('holds so far' if ok else 'fails so far')
    rows.append(dict(id=pid, prediction=text, measured=measured, result=status))


def shares(r):
    V, Vrb = r['V'], r['V_rb']
    d = r['designs']
    rel = lambda k: d[k]['inv_gain_mc'] / (Vrb / V)
    out = dict(odd=r['V_odd'] / Vrb, even=r['V_even'] / Vrb, le2=1 - rel('simplex'), E2=1 - rel('onb'))
    out['E1'] = out['le2'] - out['E2']
    if 'kerdock' in d:
        out['even6'] = rel('kerdock') / 2
    out['simplex_gain'] = 1 / d['simplex']['inv_gain_mc']
    return out


# ---------------------------------------------------------------- structure runs
st = {s: load('struct', 256, 32, s) for s in S256}
have = [s for s in S256 if st[s] is not None]
if have:
    sh = {s: shares(st[s]) for s in have}
    odd = [sh[s]['odd'] for s in have]
    row('PS1', 'median odd share in [0.45, 0.70], every net in [0.40, 0.75] (256 x 32)', [round(v, 3) for v in odd],
        0.45 <= med(odd) <= 0.70 and all(0.40 <= v <= 0.75 for v in odd), len(have), 5)
    le2 = [sh[s]['le2'] for s in have]
    row('PS2', 'median share of degrees <= 2 in [0.30, 0.65] (256 x 32)', [round(v, 3) for v in le2],
        0.30 <= med(le2) <= 0.65, len(have), 5)
    e6 = [sh[s].get('even6') for s in have]
    row('PS3', 'median even >= 6 share in [0.08, 0.30] (256 x 32)', [round(v, 3) for v in e6],
        0.08 <= med(e6) <= 0.30, len(have), 5)
    kg = [1 / st[s]['designs']['kerdock']['inv_gain_mc'] for s in have]
    row('PB1', 'Kerdock (Haar) gain over MC: median in [2.0, 5.0], >= 1.5 on 5 of 5', [round(v, 2) for v in kg],
        2.0 <= med(kg) <= 5.0 and sum(v >= 1.5 for v in kg) == len(have), len(have), 5)
    allg = []
    for s in have:
        for k, v in st[s]['designs'].items():
            if k != 'kerdock_polar_sp':
                allg.append(1 / v['inv_gain_mc'])
    row('PB2', 'no Haar-randomised design gains more than 6 over MC (256 x 32)', round(max(allg), 2),
        max(allg) <= 6.0, len(have), 5)
    ratio = [(1 / st[s]['rqmc']['rqmc_rb_polar_m14']['inv_gain_mc']) / (1 / st[s]['rqmc']['rqmc_rb_std_m14']['inv_gain_mc'])
             for s in have]
    row('PW1', 'polar RQMC beats standard RQMC at 2^14 on >= 4 of 5 nets, median ratio >= 1.2 (256 x 32)',
        [round(v, 2) for v in ratio], sum(v > 1 for v in ratio) >= 4 and med(ratio) >= 1.2, len(have), 5)
    kb = [st[s]['designs']['kerdock_polar_sp'].get('nmse_mean_x_m') for s in have]
    row('PW3', 'polar-aligned Kerdock (signed permutations) biased: nMSE x m >= 5 on >= 4 of 5', [round(v, 1) for v in kb],
        sum(v >= 5 for v in kb) >= 4, len(have), 5)
    ml = [max(v['gain_vs_rb'] for v in st[s]['multilevel'].values()) for s in have]
    row('PW4', 'multilevel two-level best gain over RB-MC <= 1.1 on 5 of 5 (256 x 32)', [round(v, 3) for v in ml],
        all(v <= 1.1 for v in ml), len(have), 5)
# ladder trends and white-box ratios
lad = {n: [load('struct', n, L, s) for s in LSEEDS] for n, L in LAD.items()}
nl = {n: [r for r in v if r is not None] for n, v in lad.items()}
if all(len(v) == 8 for v in nl.values()) and len(have) == 5:
    sg = {n: med([shares(r)['simplex_gain'] for r in nl[n]]) for n in LAD}
    sg[256] = med([sh[s]['simplex_gain'] for s in have])
    e1 = {n: med([shares(r)['E1'] for r in nl[n]]) for n in LAD}
    e1[256] = med([sh[s]['E1'] for s in have])
    row('PS4', 'simplex gain and E_1 share fall from n = 32 to 256 (medians)',
        dict(simplex_gain={k: round(v, 2) for k, v in sg.items()}, E1={k: round(v, 3) for k, v in e1.items()}),
        sg[32] > sg[256] and e1[32] > e1[256], 4, 4)
    pr = {n: med([(1 / r['rqmc']['rqmc_rb_polar_m14']['inv_gain_mc']) / (1 / r['rqmc']['rqmc_rb_std_m14']['inv_gain_mc'])
                  for r in nl[n]]) for n in LAD}
    row('PW2', 'polar/standard RQMC ratio at 2^14, median per width in [0.8, 1.3] for n = 32, 64, 128',
        {k: round(v, 2) for k, v in pr.items()}, all(0.8 <= v <= 1.3 for v in pr.values()), 3, 3)
else:
    row('PS4/PW2', 'ladder predictions', 'ladder runs incomplete', False, sum(len(v) for v in nl.values()), 24)

# ---------------------------------------------------------------- registered combination
co = {s: load('combo', 256, 32, s) for s in S256}
hc = [s for s in S256 if co[s] is not None]
if hc:
    g = lambda s, k: co[s]['methods'][k]['gain_mc']
    gp = [g(s, 'rqmc_polar') for s in hc]; gs = [g(s, 'rqmc_std') for s in hc]
    row('PC1', 'rqmc_polar gain >= 2.0 on >= 4 of 5 and >= 1.2 x rqmc_std on >= 4 of 5 (N = 2^16)',
        dict(polar=[round(v, 2) for v in gp], std=[round(v, 2) for v in gs]),
        sum(v >= 2.0 for v in gp) >= 4 and sum(p >= 1.2 * q for p, q in zip(gp, gs)) >= 4, len(hc), 5)
    gk = [g(s, 'kerdock') for s in hc]
    row('PC2', 'Kerdock gain >= 1.8 on >= 4 of 5 (66,048 points, vs truth)', [round(v, 2) for v in gk],
        sum(v >= 1.8 for v in gk) >= 4, len(hc), 5)
    best = [max(g(s, 'rqmc_polar'), g(s, 'rqmc_std'), g(s, 'kerdock')) for s in hc]
    row('PC3', 'best structured sampler gains in [2, 8] over MC on every net (none reaches 10x)',
        [round(v, 2) for v in best], all(2 <= v <= 8 for v in best), len(hc), 5)
    pw = [co[s]['methods']['mc_pairwise']['nmse_mean'] * co[s]['N'] for s in hc]
    rb = [st[s]['rho_rb'] if st.get(s) else None for s in hc]
    rel = [p / r for p, r in zip(pw, rb) if r]
    row('PC4', 'pairwise-independent MC: median nMSE x N / (V_rb/V) in [0.6, 1.5]', [round(v, 2) for v in rel],
        0.6 <= med(rel) <= 1.5, len(rel), 5)
    dp = [co[s]['methods']['det_polar']['nmse_mean'] * co[s]['N'] for s in hc]
    row('PC5', 'zero-bit polar Sobol: median nMSE x N <= 1', [round(v, 2) for v in dp], med(dp) <= 1.0, len(hc), 5)

# ---------------------------------------------------------------- noise sensitivity and GSA
nz = {s: load('noise', 256, 32, s) for s in S256}
hn = [s for s in S256 if nz[s] is not None]
c = 256 / math.sqrt(2 * math.pi)
if hn:
    l1all = []
    for (n, L) in [(256, 32)] + list(LAD.items()):
        for s in (S256 if n == 256 else LSEEDS):
            r = load('noise', n, L, s)
            if r is not None:
                l1all.append(gsa_pool(r)[0] / (n / math.sqrt(2 * math.pi)))
    row('PN1', 'layer-1 GSA (pooled delta = 1e-6..1e-4) within +-10% of n/sqrt(2 pi), every net, all widths',
        [round(min(l1all), 3), round(max(l1all), 3), len(l1all)], all(0.9 <= v <= 1.1 for v in l1all), len(l1all), 29)
    per = [gsa_pool(nz[s])[1:] / c for s in hn]
    row('PN2', 'per-layer GSA (l >= 2) in [0.5, 1.3] x n/sqrt(2 pi), every layer, every 256 net',
        [round(float(min(p.min() for p in per)), 3), round(float(max(p.max() for p in per)), 3)],
        all(p.min() >= 0.5 and p.max() <= 1.3 for p in per), len(hn), 5)
    tot = [float(np.sum(gsa_pool(nz[s]))) / (c * 32) for s in hn]
    row('PN3', 'total partition GSA in [0.6, 1.2] x n L / sqrt(2 pi) (256 x 32)', [round(v, 3) for v in tot],
        all(0.6 <= v <= 1.2 for v in tot), len(hn), 5)
    nsr = []
    for s in hn:
        V = rnd.load_truth(s, 256, 32)['V']
        nsr.append(nz[s]['gauss']['1e-05']['ns'][-1] / 1e-5 / (256 / V))
    row('PN4', 'NS_out(1e-5)/1e-5 in [0.4, 1.5] x n/V on every 256 net', [round(v, 3) for v in nsr],
        all(0.4 <= v <= 1.5 for v in nsr), len(hn), 5)
    pa = [nz[s]['gauss']['1e-06']['p_any'][-1] for s in hn]
    row('PN5', 'P(gate pattern changes) at delta = 1e-6 >= 0.8 on every 256 net', [round(v, 3) for v in pa],
        all(v >= 0.8 for v in pa), len(hn), 5)
    chk = []
    for s in hn:
        if st.get(s) is None:
            continue
        tau2 = 1 - shares(st[s])['le2']
        lbs = []
        for dl in ('0.03', '0.1', '0.3'):
            rho = 1 - float(dl)
            ns = nz[s]['sph'][dl]['ns_sph']
            a = [1 - float(rnd.gegen_P(d, 256, np.array([rho]))[0]) for d in range(1, 400)]
            alo = max(a[:2]); ahi = max(a[2:])
            lbs.append((ns - alo) / (ahi - alo))
        chk.append((round(tau2, 3), round(max(lbs), 3), tau2 >= max(lbs) - 0.05))
    row('PN6', 'validity: design tail tau_2 >= the T6 lower bound from NS_sph (tolerance 0.05), every net', chk,
        all(c_[2] for c_ in chk), len(chk), 5)

# ---------------------------------------------------------------- deterministic QMC and k-wise
dt = {s: load('det', 256, 32, s) for s in S256}
hd = [s for s in S256 if dt[s] is not None]
if hd:
    ps = [dt[s].get('rate_p', {}).get('sobol_rb') for s in hd]
    row('PQ1', 'centred Sobol (rb) fitted rate p over N = 2^8..2^16: median in [0.6, 1.4] (256 x 32)',
        [round(v, 2) if v else None for v in ps], 0.6 <= med(ps) <= 1.4, len(hd), 5)
    lat = [next(x['nmse_x_N'] for x in dt[s]['series']['lattice_rb'] if x['N'] == 1 << 14) for s in hd]
    row('PQ4', 'Korobov lattice (rb) median nMSE x N at 2^14 >= 0.5 (256 x 32)', [round(v, 2) for v in lat],
        med(lat) >= 0.5, len(hd), 5)
    s14 = {256: med([next(x['nmse_x_N'] for x in dt[s]['series']['sobol_rb'] if x['N'] == 1 << 14) for s in hd])}
    for n, L in LAD.items():
        rr = [load('det', n, L, s) for s in LSEEDS]
        rr = [r for r in rr if r is not None]
        if rr:
            s14[n] = med([next(x['nmse_x_N'] for x in r['series']['sobol_rb'] if x['N'] == 1 << 14) for r in rr])
    if 32 in s14:
        row('PQ2', 'centred Sobol (rb) median nMSE x N at 2^14 higher at n = 256 than at n = 32',
            {k: round(v, 3) for k, v in sorted(s14.items())}, s14[256] > s14[32], len(s14), 4)
    kw = []
    for (n, L) in [(256, 32)] + list(LAD.items()):
        for s in (S256 if n == 256 else LSEEDS):
            r = load('det', n, L, s)
            if r is None:
                continue
            fl = r['truth_floor']
            for name, ser in r['series'].items():
                if name.startswith('kwise'):
                    for x in ser:
                        if x['nmse'] >= 3 * fl:
                            kw.append((n, name, round(x['nmse_x_N'], 3)))
    row('PQ3', 'k-wise designs, every resolved (net, k): nMSE x N in [0.05, 5]',
        dict(count=len(kw), min=min(v[2] for v in kw) if kw else None, max=max(v[2] for v in kw) if kw else None),
        all(0.05 <= v[2] <= 5 for v in kw), len(kw), len(kw))

os.makedirs(OUTD, exist_ok=True)
json.dump(rows, open(os.path.join(OUTD, 'score.json'), 'w'), indent=1)
with open(os.path.join(OUTD, 'scorecard.md'), 'w') as fh:
    fh.write('| id | prediction | measured | result |\n|---|---|---|---|\n')
    for r in rows:
        fh.write(f"| {r['id']} | {r['prediction']} | {r['measured']} | {r['result']} |\n")
print(open(os.path.join(OUTD, 'scorecard.md')).read())
