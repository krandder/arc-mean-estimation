"""Score PREREG Amendment 4 (P15-P18): width scaling of the single-cut oracle defects (runs/width_n*_s*.json).
usage: score_amend4.py [OUT_JSON]"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RUNS = os.path.join(HERE, 'runs')
SEEDS = {32: list(range(300, 308)), 64: list(range(300, 308)), 128: list(range(300, 308)), 256: list(range(200, 205))}
FIT = (64, 128, 256)
rows = SL.score(SEEDS)


def med(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.median(xs)) if xs else float('nan')


def rqmc_cost(cur, e):
    Ns, es = cur
    if e >= es[0]:
        return Ns[0] * es[0] / e
    if e <= es[-1]:
        return Ns[-1] * es[-1] / e
    return float(np.exp(np.interp(-np.log(e), -np.log(es), np.log(Ns))))


def slope_p(stat, ns):
    xs = [(math.log(n), math.log(stat[n])) for n in ns if n in stat and stat[n] > 0 and np.isfinite(stat[n])]
    if len(xs) < len(ns):
        return float('nan')
    x, y = np.array(xs).T
    return float(-np.polyfit(x, y, 1)[0])


per = {}
for n, seeds in SEEDS.items():
    L = SL.CFG[n]
    mid = {n // 32, n // 16, 3 * n // 32}
    c_k2 = med([r['passes'] for (nn, s, v), r in rows.items() if nn == n and v == 'k2'])
    G1, F1, Zm, Z2m, Zmax, Wr, X = [], [], [], [], [], [], []
    for s in seeds:
        p = os.path.join(RUNS, f'width_n{n}_L{L}_s{s}.json')
        if not os.path.exists(p):
            continue
        R = {r['l']: r for r in json.load(open(p))['rows']}
        G1.append(R[1]['gauss']); F1.append(R[1]['radgauss'])
        zm = float(np.mean([R[l]['radgauss'] for l in sorted(mid)]))
        Zm.append(zm); Z2m.append(float(np.mean([R[l]['gauss'] for l in sorted(mid)])))
        Zmax.append(max(R[l]['radgauss'] for l in mid))
        cur = SL.rqmc_curve(n, L, s)
        if cur is not None and np.isfinite(c_k2) and zm > 0:
            Wr.append(rqmc_cost(cur, zm) / c_k2)
            X.append(SL.rqmc_at(cur, c_k2) / zm)
    per[n] = dict(nets=len(G1), c_k2=c_k2, G1=med(G1), F1=med(F1), Zm=med(Zm), Z2m=med(Z2m), Zmax=med(Zmax),
                  Wr=med(Wr), X=med(X), per_net=dict(G1=G1, F1=F1, Zm=Zm, Z2m=Z2m, Wr=Wr))
stat = lambda k: {n: per[n][k] for n in per if per[n]['nets'] > 0}  # noqa: E731
p = {k: slope_p(stat(k), FIT) for k in ('G1', 'F1', 'Zm', 'Z2m', 'Zmax')}
p_all = {k: slope_p(stat(k), (32, 64, 128, 256)) for k in ('G1', 'F1', 'Zm', 'Z2m', 'Zmax')}
wr_ratio = per[256]['Wr'] / per[64]['Wr'] if per[64]['nets'] and per[256]['nets'] else float('nan')
sc = dict(P15=dict(p_G1=p['G1'], hit=bool(0.6 <= p['G1'] <= 1.4)),
          P16=dict(p_F1=p['F1'], p_G1=p['G1'], hit=bool(p['F1'] >= p['G1'] + 0.4)),
          P17=dict(p_Zm=p['Zm'], hit=bool(0.5 <= p['Zm'] <= 1.5)),
          P18=dict(Wr_256_over_64=wr_ratio, hit=bool(wr_ratio <= 2)))
res = dict(per_width=per, p_fit_64_256=p, p_fit_32_256=p_all, scores=sc)
print(json.dumps(res, indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(res, open(sys.argv[1], 'w'), indent=1, default=float)
