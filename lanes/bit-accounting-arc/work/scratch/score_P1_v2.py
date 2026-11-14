"""Score PREREG Part P1 with the Amendment A4 scoring rules (review r1 #2-#6, #8). The registered score_P1.py is run
as well; both are reported.
- point rate = the trained prior's held-out rate (no selection among priors; refits are the C4 diagnostic);
- point nMSE = plain decoder (local); unrestricted/output: on points with refinement, the better of the plain and the
  refined decoder on the same 8192-input subset, otherwise the plain decoder on all 32768 inputs;
- R(eps): monotone lower envelope, LINEAR interpolation in nMSE between evaluated points (time-sharing, achievable);
  the log-linear value is kept as R_loglin (descriptive);
- base = restarts 0 and 1; restart 2 is the certificate restart (C3 'r2'); local cells also get the 'h1' envelope;
- every expected cell is listed with status pass / fail / missing / unreached.
usage: score_P1_v2.py <runs base dir, e.g. runs> <out json>
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402

BASE, OUT = sys.argv[1], sys.argv[2]
EPSC = [0.1, 0.03, 0.01, 0.003, 0.001]
EPS = vra.EPS
LAYERS = {'arc': [0, 2, 4, 8, 12, 16, 20, 24, 28, 31], 'nd': [0, 8, 16, 32, 64, 128, 192, 255]}
LOUT = {'arc': 32, 'nd': 256}
SEEDS = {'arc': [4000, 4001, 4002, 4003], 'nd': [203, 216, 217, 220, 221, 223]}
CERT_NET = {'arc': [4000], 'nd': SEEDS['nd']}
CAP_LAYERS = {'arc': [0, 8, 16, 24, 31, 32], 'nd': [0, 64, 255, 256]}


def point_curve(d):
    out = []
    unr = d['cls'] in ('unres', 'out')
    for c in d['curve']:
        nm = c['nmse']
        if unr and c.get('nmse_refined') is not None and c.get('nmse_plain_on_refset') is not None:
            nm = min(c['nmse_plain_on_refset'], c['nmse_refined'])
        out.append(dict(t=c['t'], rate=c['rate'], nmse=nm))
    return out


def R_lin(curve, eps):
    env = vra.envelope(curve)
    for i, (r, dd) in enumerate(env):
        if dd <= eps:
            if i == 0:
                return r
            r0, d0 = env[i - 1]
            return r0 + (d0 - eps) / (d0 - dd) * (r - r0)
    return None


runs, refs = vra.load_p1(BASE)
for d in runs:
    d['pc'] = point_curve(d)
idx = {}
for d in runs:
    idx.setdefault((vra.fam_tag(d), d['seed'], d['layer'], d['cls'], d['variant']), []).append(d)


def get(fam, seed, l, cls, variant='base', restarts=(0, 1)):
    rs = idx.get((fam, seed, l, cls, variant), [])
    if variant == 'base':
        rs = [r for r in rs if r.get('restart') in restarts]
    return rs


def stat(rs, eps, f=R_lin):
    if not rs:
        return dict(status='missing')
    v = [f(r['pc'], eps) for r in rs]
    if any(x is None for x in v):
        return dict(status='unreached', n=len(v), reached=[x for x in v if x is not None])
    return dict(status='ok', mean=float(np.mean(v)), min=min(v), max=max(v), spread=max(v) - min(v), n=len(v))


res = dict(cells={}, flags=[], pred={}, inventory={})
tol = lambda s: max(s['spread'], 0.03 * s['mean'], 0.5)  # noqa: E731
for fam in ('arc', 'nd'):
    for seed in SEEDS[fam]:
        outb = get(fam, seed, LOUT[fam], 'out')
        for l in LAYERS[fam] + [LOUT[fam]]:
            for cls in (('local', 'unres') if l < LOUT[fam] else ('out',)):
                key = f'{fam}_s{seed}_l{l}_{cls}'
                base = get(fam, seed, l, cls)
                res['inventory'][key] = dict(base_restarts=sorted(r['restart'] for r in base),
                                             variants=sorted({v for (f_, s_, l_, c_, v) in idx
                                                              if (f_, s_, l_, c_) == (fam, seed, l, cls)}))
                cell = dict(eps={})
                ref = refs.get((fam, seed, l))
                for eps in EPS:
                    s = stat(base, eps)
                    s['loglin'] = stat(base, eps, vra.R_at).get('mean')
                    flags = {}
                    if s['status'] == 'ok':
                        if cls == 'unres':
                            so = stat(outb, eps)
                            if so['status'] == 'ok':
                                dl = s['mean'] - so['mean']
                                s['C1_shortfall'] = dl
                                flags['C1'] = 'fail' if dl > max(0.05 * so['mean'], 1.0) + s['spread'] else 'pass'
                            else:
                                flags['C1'] = so['status']
                        if cls == 'out':
                            RG = vra.gauss_bound(base[0]['out_evals'], base[0]['V'], eps)
                            s['R_G'] = RG
                            flags['C2'] = 'fail' if s['mean'] > RG + max(0.02 * RG, 0.5) else 'pass'
                        if ref is not None:
                            rr = [R_lin(rf['curve'], eps) for rf in ref['refs'].values()]
                            rr = [x for x in rr if x is not None]
                            if rr:
                                s['R_ref'] = min(rr)
                                flags['C6'] = 'fail' if s['mean'] > min(rr) + max(0.02 * min(rr), 0.5) else 'pass'
                            else:
                                flags['C6'] = 'ref_unreached'
                        elif fam == 'arc' or fam == 'nd':
                            flags['C6'] = 'ref_missing'
                        # C3: restart 2, steps2, cap2 (and the h1 / refu inits reported)
                        for v in ('r2', 'steps2', 'cap2'):
                            if v == 'r2':
                                vr_ = get(fam, seed, l, cls, 'base', restarts=(2,))
                            else:
                                vr_ = get(fam, seed, l, cls, v)
                            if not vr_:
                                if seed in CERT_NET[fam] and (v == 'r2' or l in CAP_LAYERS[fam]):
                                    flags['C3_' + v] = 'missing'
                                continue
                            sv = stat(vr_, eps)
                            if sv['status'] != 'ok':
                                flags['C3_' + v] = 'unreached'
                                continue
                            s['R_' + v] = sv['min']
                            flags['C3_' + v] = 'fail' if sv['min'] < s['min'] - tol(s) else 'pass'
                        if cls == 'local':
                            h1 = get(fam, seed, l, cls, 'h1')
                            if h1:
                                sh = stat(h1, eps)
                                if sh['status'] == 'ok':
                                    s['R_h1'] = sh['min']
                                    flags['h1'] = 'h1_better' if sh['min'] < s['min'] - tol(s) else 'pass'
                                    s['R_class'] = min(s['mean'], sh['min'])
                                else:
                                    flags['h1'] = 'h1_' + sh['status']
                        if cls == 'unres':
                            rf_ = get(fam, seed, l, cls, 'refu')
                            if rf_:
                                su = stat(rf_, eps)
                                if su['status'] == 'ok':
                                    s['R_refu'] = su['min']
                    s['flags'] = flags
                    for k_, v_ in flags.items():
                        if v_ not in ('pass',):
                            res['flags'].append((k_, v_, f'{key}_e{eps}'))
                    cell['eps'][str(eps)] = s
                # C4 / C8 diagnostics and C7
                c4, c8 = [], []
                for r in base:
                    for c in r['curve']:
                        refits = [c.get(k) for k in ('rate_refit_tri', 'rate_refit_fact', 'rate_refit_gauss')]
                        refits = [x for x in refits if x is not None]
                        if refits and c['rate'] >= 5:
                            c4.append(min(refits) / c['rate'])
                        if c.get('nmse_head') is not None:
                            best = c['nmse']
                            if c.get('nmse_refined') is not None:
                                best = min(c['nmse_plain_on_refset'], c['nmse_refined'])
                            c8.append(c['nmse_head'] / max(best, 1e-30))
                cell['C4'] = dict(n=len(c4), frac_below_097=(float(np.mean([x < 0.97 for x in c4])) if c4 else None),
                                  min_ratio=(min(c4) if c4 else None))
                cell['C8'] = dict(n=len(c8), frac_head_below_08=(float(np.mean([x < 0.8 for x in c8])) if c8 else None))
                fx = idx.get((fam, seed, l, cls, 'fixlam'), [])
                c7 = []
                for r in fx:
                    pt = min(r['pc'], key=lambda c: abs(c['t'] - r['fixed_t']))
                    vals = [R_lin(b['pc'], pt['nmse']) for b in base]
                    vals = [x for x in vals if x is not None]
                    if not vals:
                        c7.append(dict(t=r['fixed_t'], status='vr_unreached', R_fixed=pt['rate'], D_fixed=pt['nmse']))
                        continue
                    sp = max(vals) - min(vals)
                    fl = pt['rate'] < min(vals) - max(sp, 0.03 * np.mean(vals), 0.5)
                    c7.append(dict(t=r['fixed_t'], status='fail' if fl else 'pass', R_fixed=pt['rate'],
                                   D_fixed=pt['nmse'], R_vr_min=min(vals)))
                    if fl:
                        res['flags'].append(('C7', 'fail', f'{key}_t{r["fixed_t"]}'))
                cell['C7'] = c7
                res['cells'][key] = cell
# toy C5
for k in (4, 16, 64):
    for cls in ('local', 'unres'):
        rs = idx.get((f'toy{k}', 1, 0, cls, 'base'), [])
        for eps in (0.1, 0.01, 0.001):
            key = f'toy{k}_{cls}_e{eps}'
            if not rs:
                res['cells'][key] = dict(status='missing')
                res['flags'].append(('C5', 'missing', key))
                continue
            s = stat(rs, eps)
            Rk = vra.gauss_bound(rs[0]['out_evals'], rs[0]['V'], eps)
            s['R_known'] = Rk
            if s['status'] == 'ok':
                s['C5'] = 'fail' if abs(s['mean'] - Rk) > max(0.05 * Rk, 1.0) else 'pass'
            else:
                s['C5'] = s['status']
            if s['C5'] != 'pass':
                res['flags'].append(('C5', s['C5'], key))
            res['cells'][key] = s
json.dump(res, open(OUT, 'w'), indent=1)
from collections import Counter  # noqa: E402
print('cells', len(res['cells']), 'flags', Counter((a, b) for a, b, _ in res['flags']))


# ---------------------------------------------------------------- predictions (registered P1.1-P1.12, A4 rules)
def Rm(fam, seed, l, cls, eps, key='mean'):
    c = res['cells'].get(f'{fam}_s{seed}_l{l}_{cls}', {}).get('eps', {}).get(str(eps), {})
    return c.get(key) if c.get('status') == 'ok' else (float('inf') if c.get('status') == 'unreached' else None)


def P(name, hits, n, need, desc, extra=None):
    res['pred'][name] = dict(hits=hits, n=n, need=need, hit=bool(n > 0 and hits >= need), desc=desc, **(extra or {}))


h = n = 0
for fam in ('arc', 'nd'):
    for seed in SEEDS[fam]:
        for l in LAYERS[fam]:
            if LOUT[fam] - l > 8:
                continue
            for eps in EPSC:
                c = res['cells'].get(f'{fam}_s{seed}_l{l}_unres', {}).get('eps', {}).get(str(eps), {})
                st_ = c.get('flags', {}).get('C1')
                if st_ in ('pass', 'fail'):
                    n += 1
                    h += st_ == 'pass'
P('P1.1', h, n, math.ceil(0.75 * n) if n else 1, 'C1 passes at L - l <= 8 (both curves reached)')
hits = nets = 0
for seed in SEEDS['arc']:
    ro = Rm('arc', seed, 32, 'out', 0.1)
    vals = [Rm('arc', seed, l, 'local', 0.1) for l in (0, 2, 4)]
    if ro is None or ro == float('inf') or any(v is None for v in vals):
        continue
    nets += 1
    hits += all(v >= 4 * ro for v in vals)
P('P1.2', hits, nets, 4, 'ARC local R(0.1) at l <= 4 >= 4 R_out(0.1) or unreached, 4 of 4 nets')
hits = nets = 0
for seed in SEEDS['arc']:
    pairs = [(Rm('arc', seed, 31, 'local', e), Rm('arc', seed, 32, 'out', e)) for e in (0.1, 0.01)]
    if any(a is None or b is None or not math.isfinite(a) or not math.isfinite(b) for a, b in pairs):
        continue
    nets += 1
    hits += all(abs(a - b) <= 0.15 * b for a, b in pairs)
P('P1.3', hits, nets, 3, 'ARC local l = 31 within 15% of R_out at 0.1, 0.01')


def prof(fam, seed):
    vals = [Rm(fam, seed, l, 'local', 0.1) for l in LAYERS[fam]]
    if any(v is None for v in vals):
        return None
    for a, b in zip(vals, vals[1:]):
        if not math.isfinite(a) and math.isfinite(b):
            continue
        if not math.isfinite(b) and math.isfinite(a):
            return False                       # finite -> unreached is a rise
        if math.isfinite(a) and b > 1.1 * a + 1:
            return False
    return True


pa = [prof('arc', s) for s in SEEDS['arc']]
pn = [prof('nd', s) for s in SEEDS['nd']]
res['pred']['P1.4'] = dict(arc=pa, nd=pn, hit=bool(sum(x is True for x in pa) >= 3 and sum(x is True for x in pn) >= 5),
                           desc='local R(0.1) non-increasing up to 10% + 1 bit')


def slope(fam, seed, l, cls, e_hi, e_lo):
    a, b = Rm(fam, seed, l, cls, e_hi), Rm(fam, seed, l, cls, e_lo)
    if a is None or b is None or not math.isfinite(a) or not math.isfinite(b):
        return None
    return 2 * (b - a) / math.log2(e_hi / e_lo)


ha = na = 0
for seed in SEEDS['arc']:
    s0, s31 = slope('arc', seed, 0, 'local', 0.02, 0.005), slope('arc', seed, 31, 'local', 0.02, 0.005)
    if s0 is None or s31 is None:
        continue
    na += 1
    ha += s0 > s31
hn = nn = 0
for seed in SEEDS['nd']:
    ss = [slope('nd', seed, l, c, 0.01, 0.001) for l in LAYERS['nd'] if l >= 32 for c in ('local', 'unres')]
    if any(x is None for x in ss):
        continue
    nn += 1
    hn += all(0.8 <= x <= 1.6 for x in ss)
res['pred']['P1.5'] = dict(arc_hits=ha, arc_n=na, nd_hits=hn, nd_n=nn, hit=bool(ha >= 4 and hn >= 5), desc='slopes')
rel = json.load(open('results/relevance_compare.json')) if os.path.exists('results/relevance_compare.json') else {}
h = n = 0
t6 = []
for seed in SEEDS['arc']:
    for l in (16, 24, 28, 31):
        sl = slope('arc', seed, l, 'local', 0.02, 0.005)
        N = rel.get(f'arc_s{seed}_l{l}', {}).get('N_0.01')
        if sl is None or N is None:
            continue
        n += 1
        h += 0.5 * N <= sl <= 2 * N
        t6.append(dict(seed=seed, l=l, slope=sl, N=N))
P('P1.6', h, n, math.ceil(0.75 * n) if n else 1, 'ARC local slope near 0.01 within [0.5, 2] N(l, 0.01)', dict(table=t6))
bbp = '/home/agent/workspaces/mats/work/bits-bounds/results/compare_bitacc.json'
t7 = []
h = n = 0
if os.path.exists(bbp):
    for cut in json.load(open(bbp))['cuts']:
        if cut['l'] not in (4, 8, 16):
            continue
        f_pr = max(0.0, cut['PR'] * math.log2(cut['D_R']['1'] / 0.1))
        rl = Rm('arc', 4000, cut['l'], 'local', 0.1)
        t7.append(dict(l=cut['l'], formula_dPR=f_pr, R_local=rl))
        if rl is not None and math.isfinite(rl):
            n += 1
            h += 0.5 * f_pr <= rl <= 2 * f_pr
P('P1.7', h, n, 3, 'ARC 4000 local R(0.1) within 2x of the bits-bounds formula (d = PR) at l = 4, 8, 16', dict(table=t7))
c6 = [s['flags'].get('C6') for k_, c in res['cells'].items() if 'eps' in c for e_, s in c['eps'].items()
      if float(e_) in EPSC and 'flags' in s and s['flags'].get('C6') in ('pass', 'fail')]
h2 = n2 = 0
for seed in SEEDS['arc']:
    ref = refs.get(('arc', seed, 31))
    pairs = [(Rm('arc', seed, 31, 'local', e), R_lin(ref['refs']['gram']['curve'], e) if ref else None) for e in (0.1, 0.01)]
    if any(a is None or b is None or not math.isfinite(a) for a, b in pairs):
        continue
    n2 += 1
    h2 += all(abs(a - b) <= 0.1 * b for a, b in pairs)
res['pred']['P1.8'] = dict(c6_pass=sum(x == 'pass' for x in c6), c6_n=len(c6), l31_hits=h2, l31_n=n2,
                           hit=bool(c6 and sum(x == 'pass' for x in c6) >= 0.9 * len(c6) and h2 >= 3), desc='reference')
c2 = [s['flags'].get('C2') for k_, c in res['cells'].items() if k_.endswith('_out') for e_, s in c['eps'].items()
      if 'flags' in s and s['flags'].get('C2') in ('pass', 'fail')]
rat = 0
for seed in SEEDS['arc']:
    c = res['cells'].get(f'arc_s{seed}_l32_out', {}).get('eps', {}).get('0.01', {})
    if c.get('status') == 'ok' and c['mean'] <= 0.8 * c['R_G']:
        rat += 1
res['pred']['P1.9'] = dict(c2_pass=sum(x == 'pass' for x in c2), c2_n=len(c2), ratio_hits=rat,
                           hit=bool(c2 and all(x == 'pass' for x in c2) and rat >= 3), desc='non-Gaussian output')
hs = hb = nn = 0
for seed in SEEDS['nd']:
    ro1, ro2 = Rm('nd', seed, 256, 'out', 0.1), Rm('nd', seed, 256, 'out', 0.01)
    if ro1 is None or ro2 is None:
        continue
    nn += 1
    ok = True
    for l in [x for x in LAYERS['nd'] if x >= 32]:
        for cls in ('local', 'unres'):
            for e, ro in ((0.1, ro1), (0.01, ro2)):
                rl = Rm('nd', seed, l, cls, e)
                if rl is None or not math.isfinite(rl) or abs(rl - ro) > max(0.5, 0.1 * ro):
                    ok = False
    hs += ok
    r0 = Rm('nd', seed, 0, 'local', 0.1)
    hb += bool(r0 is not None and r0 >= 3 * ro1)
res['pred']['P1.10'] = dict(sync_hits=hs, input_hits=hb, n=nn, hit=bool(hs >= 5 and hb >= 5), desc='narrow-deep')
pts = ok = 0
for d in runs:
    if d['family'] == 'toy':
        continue
    for c in d['curve']:
        if c['nmse'] <= 0.1 and c.get('mean_err') is not None and c['mean_err'] > 3 * c.get('mean_floor', 0):
            pts += 1
            ok += c['mean_err'] < c['nmse'] / 10
P('P1.11', ok, pts, math.ceil(0.9 * pts) if pts else 1, 'mean error < nMSE / 10 (resolved points, nMSE <= 0.1)')
t12 = [res['cells'].get(f'toy{k}_{c}_e{e}', {}).get('C5') for k in (4, 16) for c in ('local', 'unres') for e in (0.1, 0.01, 0.001)]
res['pred']['P1.12'] = dict(statuses=t12, hit=bool(all(x == 'pass' for x in t12)), desc='toy k = 4, 16 pass C5')
json.dump(res, open(OUT, 'w'), indent=1)
for k_, v in res['pred'].items():
    print(k_, {kk: vv for kk, vv in v.items() if kk != 'table'})
