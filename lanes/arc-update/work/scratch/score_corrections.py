"""Documented scoring corrections (written 09:57Z after the GPT-6 review; the hashed scorers and their outputs are kept
unchanged). (1) PREREG Part 1 defines G_K as "the median over nets of the best variant of that order"; the hashed
scorer took the best variant's median. Here: the median over nets of each net's best variant (literal reading), and
P1a, P1b, P2, P5a, P5b recomputed with it. (2) P3's wording is a crossover-cost ratio; the hashed scorer used the gain
at own cost. Here: the literal ratio. usage: score_corrections.py [OUT_JSON]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

SEEDS = {32: list(range(300, 308)), 64: list(range(300, 308)), 128: list(range(300, 308)), 256: list(range(200, 205))}
ORD = {2: ('k2', 'k2a'), 3: ('k3', 'k3f', 'k3fa'), 4: ('k4', 'k4f')}
rows = SL.score(SEEDS)


def rqmc_cost(cur, e):
    Ns, es = cur
    if e >= es[0]:
        return Ns[0] * es[0] / e
    if e <= es[-1]:
        return Ns[-1] * es[-1] / e
    return float(np.exp(np.interp(-np.log(e), -np.log(es), np.log(Ns))))


def G_lit(n, K, key='gain_mc'):
    per = []
    for s in SEEDS[n]:
        g = [rows[(n, s, v)][key] for v in ORD[K] if (n, s, v) in rows and rows[(n, s, v)].get(key) is not None]
        if g:
            per.append(max(g))
    return float(np.median(per)) if per else float('nan')


L = SL.CFG
G = {(n, K): G_lit(n, K) for n in SL.CFG for K in (2, 3, 4)}
GR = {(n, K): G_lit(n, K, 'gain_rqmc') for n in SL.CFG for K in (2, 3, 4)}
out = dict(G_literal={f'{n}_K{K}': v for (n, K), v in G.items()})
p1a = {n: G[(n, 3)] / G[(n, 2)] for n in (32, 64, 128, 256)}
p1b = {n: G[(n, 4)] / G[(n, 3)] for n in (64, 128)}
out['P1a'] = dict(ratios=p1a, hit=bool(all(p1a[n] <= 2.0 / L[n] for n in p1a)))
out['P1b'] = dict(ratios=p1b, hit=bool(all(p1b[n] <= 2.0 / L[n] for n in p1b)))
hi = {n: max(x for x in (GR[(n, 3)], GR[(n, 4)]) if np.isfinite(x)) for n in (64, 128, 256)}
out['P2'] = dict(G3_128=G[(128, 3)], G3_256=G[(256, 3)], G4_128=G[(128, 4)], best_order_ge3_G_RQMC=hi,
                 hit=bool(G[(128, 3)] < 1 and G[(256, 3)] < 1 and G[(128, 4)] < 1 and all(v < 0.5 for v in hi.values())))
g3 = [G[(n, 3)] for n in (32, 64, 128, 256)]
out['P5a'] = dict(G3=g3, hit=bool(all(g3[i] > g3[i + 1] for i in range(3))))
out['P5b'] = dict(G2_32=G[(32, 2)], G2_256=G[(256, 2)], hit=bool(G[(256, 2)] < G[(32, 2)]))
p3 = []
for s in SEEDS[256]:
    rr = [rows[(256, s, v)] for v in ORD[2] if (256, s, v) in rows]
    b = min(rr, key=lambda r: r['nmse'])
    p3.append(rqmc_cost(SL.rqmc_curve(256, 32, s), b['nmse']) / b['passes'])
out['P3'] = dict(crossover_ratio=p3, hit=bool(sum(x <= 4 for x in p3) >= 4))
print(json.dumps(out, indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(out, open(sys.argv[1], 'w'), indent=1, default=float)
