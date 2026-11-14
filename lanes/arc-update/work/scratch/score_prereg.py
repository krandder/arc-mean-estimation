"""Scores PREREG Part 1 predictions P1-P5, P10-P12 (P6-P9 are scored by score_attr.py) from the hashed scorer
score_lad.py's per-net rows. Written 05:56Z after the n = 32 ladder results existed (which I had looked at) and
before any other evaluation result had been scored; hashed before the remaining results were read.
usage: score_prereg.py [OUT_JSON]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
SEEDS = {32: list(range(300, 308)), 64: list(range(300, 308)), 128: list(range(300, 308)), 256: list(range(200, 205))}
ORD = {2: ('k2', 'k2a'), 3: ('k3', 'k3f', 'k3fa'), 4: ('k4', 'k4f')}
rows = SL.score(SEEDS)


def med(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.median(xs)) if xs else float('nan')


def table(n, v, key):
    return med([r[key] for (nn, s, vv), r in rows.items() if nn == n and vv == v and key in r])


def best_gain(n, K, key='gain_mc'):
    vals = [table(n, v, key) for v in ORD[K]]
    vals = [x for x in vals if np.isfinite(x)]
    return max(vals) if vals else float('nan')


def best_err(n, K):
    vals = [table(n, v, 'nmse') for v in ORD[K]]
    vals = [x for x in vals if np.isfinite(x)]
    return min(vals) if vals else float('nan')


S = {}
L = SL.CFG
G = {(n, K): best_gain(n, K) for n in SL.CFG for K in (2, 3, 4)}
GR = {(n, K): best_gain(n, K, 'gain_rqmc') for n in SL.CFG for K in (2, 3, 4)}
E = {(n, K): best_err(n, K) for n in SL.CFG for K in (2, 3, 4)}
S['G_MC'] = {f'{n}_K{K}': G[(n, K)] for (n, K) in G}
S['G_RQMC'] = {f'{n}_K{K}': GR[(n, K)] for (n, K) in GR}
S['e_best'] = {f'{n}_K{K}': E[(n, K)] for (n, K) in E}
# P1
p1a = {n: G[(n, 3)] / G[(n, 2)] for n in (32, 64, 128, 256)}
p1b = {n: G[(n, 4)] / G[(n, 3)] for n in (64, 128)}
S['P1a'] = dict(ratios=p1a, bound={n: 2.0 / L[n] for n in p1a}, hit=bool(all(p1a[n] <= 2.0 / L[n] for n in p1a)))
S['P1b'] = dict(ratios=p1b, bound={n: 2.0 / L[n] for n in p1b}, hit=bool(all(p1b[n] <= 2.0 / L[n] for n in p1b)))
# P2
c1 = G[(128, 3)] < 1 and G[(256, 3)] < 1 and G[(128, 4)] < 1
best_hi_rqmc = {n: max([x for x in (GR[(n, 3)], GR[(n, 4)]) if np.isfinite(x)]) for n in (64, 128, 256)}
c2 = all(v < 0.5 for v in best_hi_rqmc.values())
S['P2'] = dict(G3_128=G[(128, 3)], G3_256=G[(256, 3)], G4_128=G[(128, 4)], best_order_ge3_G_RQMC=best_hi_rqmc,
               hit=bool(c1 and c2))
# P3: per net at 256, the best K = 2 variant (by that net's nMSE) has G_RQMC <= 4
p3 = []
for s in SEEDS[256]:
    rr = [rows[(256, s, v)] for v in ORD[2] if (256, s, v) in rows]
    if not rr:
        continue
    b = min(rr, key=lambda r: r['nmse'])
    p3.append(b.get('gain_rqmc', float('nan')))
S['P3'] = dict(per_net=p3, hit=bool(sum(x <= 4 for x in p3) >= 4))
# P4: at 6.5e4 passes, RQMC nMSE <= best affordable ARC variant / 10, on 5/5 nets
p4 = []
for s in SEEDS[256]:
    cur = SL.rqmc_curve(256, 32, s)
    if cur is None:
        continue
    rq = SL.rqmc_at(cur, 6.5e4)
    aff = [r['nmse'] for (nn, ss, v), r in rows.items() if nn == 256 and ss == s and r['passes'] <= 6.5e4]
    if aff:
        p4.append(min(aff) / rq)
S['P4'] = dict(ratio_best_affordable_over_rqmc=p4, hit=bool(len(p4) == 5 and all(x >= 10 for x in p4)))
# P5
g3 = [G[(n, 3)] for n in (32, 64, 128, 256)]
S['P5a'] = dict(G3=g3, hit=bool(all(g3[i] > g3[i + 1] for i in range(3))))
S['P5b'] = dict(G2_32=G[(32, 2)], G2_256=G[(256, 2)], hit=bool(G[(256, 2)] < G[(32, 2)]))
# P11, P12
estar = {n: min([table(n, v, 'nmse') for v in SL.VARIANTS if np.isfinite(table(n, v, 'nmse'))]) for n in SL.CFG}
S['P11'] = dict(e_star=estar, hit=bool(estar[256] >= 3 * estar[32] and estar[128] >= estar[64]))
p12 = {n: E[(n, 3)] / E[(n, 2)] for n in (64, 128, 256)}
S['P12'] = dict(e3_over_e2=p12, hit=bool(all(v >= 0.2 for v in p12.values())))
# P10 from the attribution runs (exact Gaussian recursion): median nMSE in [2e-4, 2e-3], median G_RQMC <= 1.5
ex, gr = [], []
for s in SEEDS[256]:
    p = os.path.join(RUNS, f'attr_s{s}.json')
    if not os.path.exists(p):
        continue
    A = json.load(open(p))
    m = A['models']['exact_gauss']
    passes = m['cost'] / (2.0 * 256 * 256 * 32)
    ex.append(m['total'])
    cur = SL.rqmc_curve(256, 32, s)
    if cur is not None:
        gr.append(SL.rqmc_at(cur, passes) / m['total'])
S['P10'] = dict(nmse=ex, G_RQMC=gr, hit=bool(ex and 2e-4 <= med(ex) <= 2e-3 and med(gr) <= 1.5))
print(json.dumps(S, indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(S, open(sys.argv[1], 'w'), indent=1, default=float)
