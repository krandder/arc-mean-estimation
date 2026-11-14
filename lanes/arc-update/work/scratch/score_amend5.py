"""Score PREREG Amendment 5 (P19-P23): ideal projection recursions (runs/ipr_n*_s*.json).
usage: score_amend5.py [OUT_JSON]"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RUNS = os.path.join(HERE, 'runs')
SEEDS = {64: list(range(300, 308)), 128: list(range(300, 308)), 256: list(range(200, 205))}
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


per = {}
for n, seeds in SEEDS.items():
    L = SL.CFG[n]
    c_k2 = med([r['passes'] for (nn, s, v), r in rows.items() if nn == n and v == 'k2'])
    d = dict(gauss={}, radgauss={}, ratio={}, rqmc_cost={}, X_full={}, k2={}, exact_deductive={})
    for s in seeds:
        p = os.path.join(RUNS, f'ipr_n{n}_L{L}_s{s}.json')
        if not os.path.exists(p):
            continue
        R = json.load(open(p))['models']
        g, r = R['gauss']['b2'], R['radgauss']['b2']
        d['gauss'][s], d['radgauss'][s] = g, r
        d['ratio'][s] = r / g if g > 0 else float('nan')
        if (n, s, 'k2') in rows:
            d['k2'][s] = rows[(n, s, 'k2')]['nmse']
        cur = SL.rqmc_curve(n, L, s)
        if cur is not None and r > 0:
            d['rqmc_cost'][s] = rqmc_cost(cur, r)
            d['X_full'][s] = SL.rqmc_at(cur, c_k2) / r
        pa = os.path.join(RUNS, f'attr_s{s}.json')
        if n == 256 and os.path.exists(pa):
            d['exact_deductive'][s] = json.load(open(pa))['models']['exact_gauss']['total']
    d['c_k2'] = c_k2
    d['med'] = {k: med(list(d[k].values())) for k in ('gauss', 'radgauss', 'ratio', 'rqmc_cost', 'X_full', 'k2')}
    per[n] = d
# Zm(256) as in score_amend4 (median over nets of the mean mid-cut Gamma_rad)
zm = []
for s in SEEDS[256]:
    p = os.path.join(RUNS, f'width_n256_L32_s{s}.json')
    if os.path.exists(p):
        Rw = {r['l']: r for r in json.load(open(p))['rows']}
        zm.append(float(np.mean([Rw[l]['radgauss'] for l in (8, 16, 24)])))
Zm256 = med(zm)
d256 = per[256]
p19 = [abs(math.log(d256['gauss'][s] / d256['exact_deductive'][s])) <= math.log(1.5)
       for s in d256['gauss'] if s in d256['exact_deductive'] and d256['gauss'][s] > 0]
xs = [(math.log(n), math.log(per[n]['med']['radgauss'])) for n in (64, 128, 256)
      if per[n]['radgauss'] and per[n]['med']['radgauss'] > 0]
p_full = float(-np.polyfit(*np.array(xs).T, 1)[0]) if len(xs) == 3 else float('nan')
costs = list(d256['rqmc_cost'].values())
sc = dict(P19=dict(per_net_ok=p19, hit=bool(p19 and len(p19) == len(d256['gauss']) and all(p19))),
          P20=dict(median_radial_ipr=d256['med']['radgauss'], Zm256=Zm256,
                   hit=bool(d256['med']['radgauss'] >= 0.5 * Zm256)),
          P21=dict(median_ratio=d256['med']['ratio'], hit=bool(d256['med']['ratio'] <= 0.5)),
          P22=dict(p_full=p_full, hit=bool(0.5 <= p_full <= 1.5)),
          P23=dict(rqmc_costs=costs, hit=bool(sum(c <= 2e4 for c in costs) >= 4)))
res = dict(per_width=per, scores=sc)
print(json.dumps(res, indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(res, open(sys.argv[1], 'w'), indent=1, default=float)
