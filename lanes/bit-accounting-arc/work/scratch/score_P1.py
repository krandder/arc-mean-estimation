"""Score PREREG Part P1: certificates C1-C8 per curve and predictions P1.1-P1.12.
usage: score_P1.py <runs root> <refs root> <out json>   (run from the work dir)
Point rate = min(trained, refit_tri, refit_fact, refit_gauss); point nMSE = min(plain, refined where present).
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402

RUNS, REFS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
EPSC = [0.1, 0.03, 0.01, 0.003, 0.001]
LAYERS = {'arc': [0, 2, 4, 8, 12, 16, 20, 24, 28, 31], 'nd': [0, 8, 16, 32, 64, 128, 192, 255]}
LOUT = {'arc': 32, 'nd': 256}
SEEDS = {'arc': [4000, 4001, 4002, 4003], 'nd': [203, 216, 217, 220, 221, 223]}


def best_curve(curve):
    out = []
    for c in curve:
        rates = [c[k] for k in ('rate', 'rate_refit_tri', 'rate_refit_fact', 'rate_refit_gauss') if c.get(k) is not None]
        nm = c['nmse']
        if c.get('nmse_refined') is not None and c.get('nmse_plain_on_refset'):
            # refined decoder on the refinement subset; scale the full-set plain nMSE by the subset ratio
            ratio = c['nmse_refined'] / max(c['nmse_plain_on_refset'], 1e-30)
            nm = min(nm, nm * ratio)
        out.append(dict(t=c['t'], rate=min(rates), rate_trained=c['rate'], nmse=nm, nmse_plain=c['nmse'],
                        nmse_head=c.get('nmse_head'), mean_err=c.get('mean_err'), mean_floor=c.get('mean_floor')))
    return out


runs = vra.load_runs(RUNS)
for d in runs:
    d['bcurve'] = best_curve(d['curve'])
idx = vra.index(runs)
refs = vra.load_refs(REFS)


def cell(fam, seed, l, cls, variant='base'):
    rs = idx.get((fam, seed, l, cls, variant), [])
    return [r for r in rs if r.get('restart') is not None]


def Rs(rs, eps):
    v = [vra.R_at(r['bcurve'], eps) for r in rs]
    return [x for x in v if x is not None], len(v)


def stat(rs, eps):
    v, n = Rs(rs, eps)
    if not v or len(v) < n:
        return None
    return dict(mean=float(np.mean(v)), min=min(v), max=max(v), spread=max(v) - min(v), n=n)


res = dict(cert={}, pred={}, tables={})
flags = []
# ---------------------------------------------------------------- per-curve statistics and certificates
for fam in ('arc', 'nd'):
    for seed in SEEDS[fam]:
        out_rs = cell(fam, seed, LOUT[fam], 'out')
        if not out_rs:
            continue
        V = out_rs[0]['V']
        ev = out_rs[0]['out_evals']
        for eps in EPSC:
            so = stat(out_rs, eps)
            RG = vra.gauss_bound(ev, V, eps)
            key = f'{fam}_s{seed}_out_e{eps}'
            rec = dict(R_out=so, R_G=RG)
            if so is not None:
                rec['C2_flag'] = bool(so['mean'] > RG + max(0.02 * RG, 0.5))
                rec['ratio_to_G'] = so['mean'] / RG if RG > 0 else None
                if rec['C2_flag']:
                    flags.append(('C2', key))
            res['cert'][key] = rec
        for l in LAYERS[fam] + [LOUT[fam]]:
            for cls in (('local', 'unres') if l < LOUT[fam] else ('out',)):
                rs = cell(fam, seed, l, cls)
                if not rs:
                    continue
                ref = refs.get((fam, seed, l))
                for eps in EPSC:
                    s = stat(rs, eps)
                    key = f'{fam}_s{seed}_l{l}_{cls}_e{eps}'
                    rec = dict(R=s)
                    if s is not None:
                        if cls == 'unres':
                            so = stat(out_rs, eps)
                            if so is not None:
                                dl = s['mean'] - so['mean']
                                rec['C1_shortfall'] = dl
                                rec['C1_flag'] = bool(dl > max(0.05 * so['mean'], 1.0) + s['spread'])
                                if rec['C1_flag']:
                                    flags.append(('C1', key))
                        if ref is not None:
                            Rref = vra.ref_best_R(ref, eps)
                            rec['R_ref'] = Rref
                            if Rref is not None:
                                rec['C6_flag'] = bool(s['mean'] > Rref + max(0.02 * Rref, 0.5))
                                if rec['C6_flag']:
                                    flags.append(('C6', key))
                        for v in ('r2', 'steps2', 'cap2', 'refu'):
                            vr_ = idx.get((fam, seed, l, cls, v), [])
                            if not vr_:
                                continue
                            vv, nn = Rs(vr_, eps)
                            if not vv:
                                continue
                            Rv = min(vv)
                            rec[f'R_{v}'] = Rv
                            if v in ('r2', 'steps2', 'cap2'):
                                fl = bool(Rv < s['min'] - max(s['spread'], 0.03 * s['mean'], 0.5))
                                rec[f'C3_{v}_flag'] = fl
                                if fl:
                                    flags.append((f'C3_{v}', key))
                    res['cert'][key] = rec
                # C4 prior and C8 decoder per curve
                c4, c8 = [], []
                for r in rs:
                    for c in r['curve']:
                        refits = [c.get(k) for k in ('rate_refit_tri', 'rate_refit_fact', 'rate_refit_gauss')]
                        refits = [x for x in refits if x is not None]
                        if refits and c['rate'] >= 5:
                            c4.append(bool(min(refits) < 0.97 * c['rate']))
                        if c.get('nmse_head') is not None:
                            best_dec = c['nmse']
                            if c.get('nmse_refined') is not None:
                                best_dec = min(best_dec, c['nmse_refined'] / max(c['nmse_plain_on_refset'], 1e-30)
                                               * c['nmse'])
                            c8.append(bool(c['nmse_head'] < 0.8 * best_dec))
                key = f'{fam}_s{seed}_l{l}_{cls}'
                res['cert'][key + '_C4'] = dict(frac_flagged=(float(np.mean(c4)) if c4 else None), n=len(c4))
                res['cert'][key + '_C8'] = dict(frac_decoder_limited=(float(np.mean(c8)) if c8 else None), n=len(c8))
                # C7 fixed lambda
                fx = [r for r in idx.get((fam, seed, l, cls, 'fixlam'), [])]
                if fx:
                    out7 = []
                    for r in fx:
                        pt = min(r['bcurve'], key=lambda c: abs(c['t'] - r['fixed_t']))
                        Rvr = [vra.R_at(b['bcurve'], pt['nmse']) for b in rs]
                        Rvr = [x for x in Rvr if x is not None]
                        if not Rvr:
                            continue
                        spread = max(Rvr) - min(Rvr)
                        fl = bool(pt['rate'] < min(Rvr) - max(spread, 0.03 * np.mean(Rvr), 0.5))
                        out7.append(dict(t=r['fixed_t'], R_fixed=pt['rate'], D_fixed=pt['nmse'], R_vr_min=min(Rvr),
                                         flag=fl))
                        if fl:
                            flags.append(('C7', f'{key}_t{r["fixed_t"]}'))
                    res['cert'][key + '_C7'] = out7

# toy C5
for k in (4, 16, 64):
    for cls in ('local', 'unres'):
        rs = cell(f'toy{k}', 1, 0, cls)
        if not rs:
            continue
        V, ev = rs[0]['V'], rs[0]['out_evals']
        for eps in (0.1, 0.01, 0.001):
            s = stat(rs, eps)
            Rk = vra.gauss_bound(ev, V, eps)
            key = f'toy{k}_{cls}_e{eps}'
            rec = dict(R=s, R_known=Rk)
            if s is not None:
                rec['C5_flag'] = bool(abs(s['mean'] - Rk) > max(0.05 * Rk, 1.0))
                if rec['C5_flag']:
                    flags.append(('C5', key))
            else:
                rec['C5_flag'] = True
                flags.append(('C5', key + '_unreached'))
            res['cert'][key] = rec
res['flags'] = flags


# ---------------------------------------------------------------- predictions
def pred(name, hits, n, need, desc):
    res['pred'][name] = dict(hits=hits, n=n, need=need, hit=bool(n > 0 and hits >= need), desc=desc)


# P1.1
h = n = 0
for fam in ('arc', 'nd'):
    for seed in SEEDS[fam]:
        for l in LAYERS[fam]:
            if LOUT[fam] - l > 8:
                continue
            for eps in EPSC:
                r = res['cert'].get(f'{fam}_s{seed}_l{l}_unres_e{eps}', {})
                if 'C1_flag' in r:
                    n += 1
                    h += (not r['C1_flag'])
pred('P1.1', h, n, math.ceil(0.75 * n) if n else 1, 'C1 passes at L - l <= 8')


def Rcell(fam, seed, l, cls, eps):
    s = res['cert'].get(f'{fam}_s{seed}_l{l}_{cls}_e{eps}', {}).get('R')
    return None if s is None else s['mean']


def Rout(fam, seed, eps):
    s = res['cert'].get(f'{fam}_s{seed}_out_e{eps}', {}).get('R_out')
    return None if s is None else s['mean']


# P1.2
hits = 0
nets = 0
for seed in SEEDS['arc']:
    ro = Rout('arc', seed, 0.1)
    if ro is None:
        continue
    nets += 1
    ok = True
    for l in (0, 2, 4):
        rl = Rcell('arc', seed, l, 'local', 0.1)
        if rl is not None and rl < 4 * ro:
            ok = False
    hits += ok
pred('P1.2', hits, nets, 4, 'ARC local R(0.1) at l <= 4 >= 4 x R_out(0.1) or unreached, 4 of 4 nets')
# P1.3
hits = nets = 0
for seed in SEEDS['arc']:
    ok, have = True, False
    for eps in (0.1, 0.01):
        rl, ro = Rcell('arc', seed, 31, 'local', eps), Rout('arc', seed, eps)
        if rl is None or ro is None:
            ok = False
            continue
        have = True
        ok = ok and abs(rl - ro) <= 0.15 * ro
    if have:
        nets += 1
        hits += ok
pred('P1.3', hits, nets, 3, 'ARC local l = 31 within 15% of R_out at 0.1, 0.01 on >= 3 of 4')


# P1.4
def profile_ok(fam, seed):
    vals = []
    for l in LAYERS[fam]:
        r = Rcell(fam, seed, l, 'local', 0.1)
        vals.append(float('inf') if r is None else r)
    for a, b in zip(vals, vals[1:]):
        if math.isfinite(b) and b > 1.1 * a + 1:
            return False
    return True


h_arc = sum(profile_ok('arc', s) for s in SEEDS['arc'] if Rout('arc', s, 0.1) is not None)
h_nd = sum(profile_ok('nd', s) for s in SEEDS['nd'] if Rout('nd', s, 0.1) is not None)
res['pred']['P1.4'] = dict(arc_hits=h_arc, nd_hits=h_nd, hit=bool(h_arc >= 3 and h_nd >= 5),
                           desc='local R(0.1) non-increasing in l up to 10% + 1 bit')


# P1.5
def slope_near(rs, e_hi=0.02, e_lo=0.005):
    vals = []
    for r in rs:
        a, b = vra.R_at(r['bcurve'], e_hi), vra.R_at(r['bcurve'], e_lo)
        if a is not None and b is not None:
            vals.append(2 * (b - a) / math.log2(e_hi / e_lo))
    return float(np.mean(vals)) if vals else None


hits = nets = 0
for seed in SEEDS['arc']:
    s0, s31 = slope_near(cell('arc', seed, 0, 'local')), slope_near(cell('arc', seed, 31, 'local'))
    if s31 is None:
        continue
    nets += 1
    hits += bool(s0 is None or s0 > s31)
hits_nd = nets_nd = 0
for seed in SEEDS['nd']:
    ok, have = True, False
    for l in [x for x in LAYERS['nd'] if x >= 32]:
        for cls in ('local', 'unres'):
            sl = slope_near(cell('nd', seed, l, cls), 0.01, 0.001)
            if sl is None:
                continue
            have = True
            ok = ok and (0.8 <= sl <= 1.6)
    if have:
        nets_nd += 1
        hits_nd += ok
res['pred']['P1.5'] = dict(arc_hits=hits, arc_n=nets, nd_hits=hits_nd, nd_n=nets_nd,
                           hit=bool(hits >= 4 and hits_nd >= 5), desc='slopes')
# P1.6 relevance lane N(l, 0.01)
rel = {}
for seed in SEEDS['arc']:
    p = f'/home/agent/workspaces/mats/work/relevance/runs/eval_arc_n256_L32_seed{seed}.json'
    if os.path.exists(p):
        for c in json.load(open(p)):
            rel[(seed, c['l'])] = c
hits = n = 0
tab6 = []
for seed in SEEDS['arc']:
    for l in (16, 24, 28, 31):
        c = rel.get((seed, l))
        sl = slope_near(cell('arc', seed, l, 'local'))
        if c is None or sl is None:
            continue
        # the relevance lane's measured N(l, 0.01): best of three bases (active subspace, cloud axes, degree-1), Gaussian
        # convention, smallest tested k with residual / V <= 0.01 (reproduces its table for net 4000)
        N = None
        Vg = c['V_gauss'][0]
        for key in ('res_AS_gauss', 'res_PCA_gauss', 'res_R1_gauss'):
            for k in sorted(int(x) for x in c[key]):
                if c[key][str(k)][0] / Vg <= 0.01:
                    N = k if N is None else min(N, k)
                    break
        if N is None:
            continue
        n += 1
        ok = 0.5 * N <= sl <= 2 * N
        hits += ok
        tab6.append(dict(seed=seed, l=l, slope=sl, N=N, ratio=sl / N))
pred('P1.6', hits, n, math.ceil(0.75 * n) if n else 1, 'ARC local slope near 0.01 within [0.5, 2] x N(l, 0.01)')
res['tables']['P1.6'] = tab6
# P1.7 bits-bounds formula (seed 4000)
bb = '/home/agent/workspaces/mats/work/bits-bounds/results/compare_bitacc.json'
tab7 = []
hits = n = 0
if os.path.exists(bb):
    cb = json.load(open(bb))
    for cut in cb['cuts']:
        l = cut['l']
        if l not in (4, 8, 16):
            continue
        D1 = cut['D_R']['1']
        f_pr = max(0.0, cut['PR'] * math.log2(D1 / 0.1))
        rl = Rcell('arc', 4000, l, 'local', 0.1)
        tab7.append(dict(l=l, formula_dPR=f_pr, formula_rough=cut.get('formula_bits_rough'), R_local=rl))
        if rl is not None:
            n += 1
            hits += (0.5 * f_pr <= rl <= 2 * f_pr)
pred('P1.7', hits, n, 3, 'ARC 4000 local R(0.1) within 2x of the bits-bounds formula (d = PR) at l = 4, 8, 16')
res['tables']['P1.7'] = tab7
# P1.8
h = n = 0
for k_, r in res['cert'].items():
    if 'C6_flag' in r:
        n += 1
        h += (not r['C6_flag'])
hits2 = nets2 = 0
for seed in SEEDS['arc']:
    ref = refs.get(('arc', seed, 31))
    if ref is None:
        continue
    ok, have = True, False
    for eps in (0.1, 0.01):
        rl = Rcell('arc', seed, 31, 'local', eps)
        rg = vra.R_at(ref['refs']['gram']['curve'], eps)
        if rl is None or rg is None:
            continue
        have = True
        ok = ok and abs(rl - rg) <= 0.1 * rg
    if have:
        nets2 += 1
        hits2 += ok
res['pred']['P1.8'] = dict(c6_pass=h, c6_n=n, l31_hits=hits2, l31_n=nets2,
                           hit=bool(n > 0 and h >= 0.9 * n and hits2 >= 3), desc='reference')
# P1.9
c2 = [r for k_, r in res['cert'].items() if 'C2_flag' in r]
c2_all = bool(c2) and not any(r['C2_flag'] for r in c2)
hits = 0
for seed in SEEDS['arc']:
    r = res['cert'].get(f'arc_s{seed}_out_e0.01', {})
    if r.get('ratio_to_G') is not None and r['ratio_to_G'] <= 0.8:
        hits += 1
res['pred']['P1.9'] = dict(c2_all_pass=c2_all, ratio_hits=hits, hit=bool(c2_all and hits >= 3), desc='non-Gaussian')
# P1.10
hits = nets = 0
hits_b = 0
for seed in SEEDS['nd']:
    ro1, ro2 = Rout('nd', seed, 0.1), Rout('nd', seed, 0.01)
    if ro1 is None:
        continue
    nets += 1
    ok = True
    for l in [x for x in LAYERS['nd'] if x >= 32]:
        for cls in ('local', 'unres'):
            for eps, ro in ((0.1, ro1), (0.01, ro2)):
                rl = Rcell('nd', seed, l, cls, eps)
                if rl is None or ro is None or abs(rl - ro) > max(0.5, 0.1 * ro):
                    ok = False
    hits += ok
    r0 = Rcell('nd', seed, 0, 'local', 0.1)
    hits_b += bool(r0 is None or r0 >= 3 * ro1)
res['pred']['P1.10'] = dict(sync_hits=hits, input_hits=hits_b, n=nets, hit=bool(hits >= 5 and hits_b >= 5),
                            desc='narrow-deep synchronisation')
# P1.11
pts = ok = 0
for d in runs:
    if d['family'] == 'toy':
        continue
    for c in d['curve']:
        if c['nmse'] <= 0.1 and c.get('mean_err') is not None and c['mean_err'] > 3 * c.get('mean_floor', 0):
            pts += 1
            ok += c['mean_err'] < c['nmse'] / 10
pred('P1.11', ok, pts, math.ceil(0.9 * pts) if pts else 1, 'mean error < nMSE/10 where nMSE <= 0.1 (resolved)')
# P1.12
ok = True
have = False
for k in (4, 16):
    for cls in ('local', 'unres'):
        for eps in (0.1, 0.01, 0.001):
            r = res['cert'].get(f'toy{k}_{cls}_e{eps}')
            if r is None:
                continue
            have = True
            ok = ok and not r['C5_flag']
res['pred']['P1.12'] = dict(hit=bool(have and ok), desc='toy k = 4, 16 pass C5')
json.dump(res, open(OUT, 'w'), indent=1)
print('flags:', len(flags))
for k_, v in res['pred'].items():
    print(k_, v)
