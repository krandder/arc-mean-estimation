"""Score T-ATTR and T-RANK runs (registered predictions P6-P9 of PREREG Part 1) and print tables.
usage: score_attr.py SEEDS [OUT_JSON]   (comma-separated seeds; reads runs/attr_s{seed}.json, runs/rank_s{seed}.json,
runs/rank_control.json)"""
import json, os, sys
import numpy as np

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
seeds = [int(s) for s in sys.argv[1].split(',')]
A = {s: json.load(open(os.path.join(RUNS, f'attr_s{s}.json'))) for s in seeds
     if os.path.exists(os.path.join(RUNS, f'attr_s{s}.json'))}
R = {s: json.load(open(os.path.join(RUNS, f'rank_s{s}.json'))) for s in seeds
     if os.path.exists(os.path.join(RUNS, f'rank_s{s}.json'))}
out = dict(attr={}, rank={}, scores={})


def row(s, model, l):
    for r in A[s]['models'][model]['rows']:
        if r['l'] == l:
            return r
    return None


for model in ('arc_k2', 'exact_gauss', 'oracle_gauss', 'oracle_radgauss'):
    tab = {}
    for s in A:
        if model not in A[s]['models']:
            continue
        m = A[s]['models'][model]
        tab[s] = dict(total=m['total'], rows=m['rows'])
    out['attr'][model] = tab
    if not tab:
        continue
    cuts = A[next(iter(A))]['cuts']
    print(f'== {model}')
    for l in cuts:
        b2 = [row(s, model, l)['b2'] for s in tab]
        line = f'  l={l:2d} b2 median {np.median(b2):.2e} [{min(b2):.1e}, {max(b2):.1e}]'
        if model in ('arc_k2', 'exact_gauss'):
            a2 = [row(s, model, l)['a2'] for s in tab]
            line += f'  a2 median {np.median(a2):.2e}'
        print(line)
    if model in ('arc_k2', 'exact_gauss'):
        print('  total median', f"{np.median([t['total'] for t in tab.values()]):.3e}",
              [f"{t['total']:.2e}" for t in tab.values()])

# P6: attribution for arc_k2 and exact_gauss
sc = {}
for model in ('arc_k2', 'exact_gauss'):
    tab = out['attr'].get(model, {})
    if not tab:
        continue
    p6a = [row(s, model, 8)['b2'] >= 0.3 * tab[s]['total'] for s in tab]
    p6b = [all(tab[s]['total'] >= 0.4 * (row(s, model, l)['a2'] + row(s, model, l)['b2']) for l in (4, 8, 16))
           for s in tab]
    a31 = [abs(row(s, model, 31)['a2']) for s in tab]
    sc[f'P6a_{model}'] = dict(pass_count=int(sum(p6a)), nets=len(p6a), hit=bool(sum(p6a) >= max(1, len(p6a) - 1)))
    sc[f'P6b_{model}'] = dict(pass_count=int(sum(p6b)), nets=len(p6b), hit=bool(sum(p6b) >= max(1, len(p6b) - 1)))
    sc[f'CHECK_a31_{model}'] = dict(max_abs=float(max(a31)), hit=bool(max(a31) < 1e-5))
# P7: oracle Gaussian single-cut defect
tab = out['attr'].get('oracle_gauss', {})
if tab:
    med = {l: float(np.median([row(s, 'oracle_gauss', l)['b2'] for s in tab])) for l in (4, 8, 16)}
    k2tot = float(np.median([t['total'] for t in out['attr']['arc_k2'].values()]))
    sc['P7'] = dict(medians=med, k2_total_median=k2tot,
                    hit=bool(all(v >= 5e-5 for v in med.values()) and med[16] >= 0.2 * k2tot))
# P8: radial-Gaussian oracle against the Gaussian oracle at l = 16, 24
tabr = out['attr'].get('oracle_radgauss', {})
if tabr and tab:
    ratios = {l: float(np.median([row(s, 'oracle_radgauss', l)['b2'] / row(s, 'oracle_gauss', l)['b2']
                                  for s in tabr])) for l in (4, 8, 16, 24)}
    sc['P8_ratios_radgauss_over_gauss'] = ratios
# P9: rank
if R:
    ok_a = all(R[s]['layers'][str(l)]['pr'] <= R[s]['layers'][str(l)]['cov_pr']
               for s in R for l in R[s]['layers'])
    pr1 = [R[s]['layers']['1']['pr'] for s in R]
    prdeep = [R[s]['layers'][str(l)]['pr'] for s in R for l in (16, 20, 24, 28, 31)]
    cap1 = [R[s]['layers']['1']['capk']['32'] for s in R]
    cap16 = [R[s]['layers']['16']['capk']['32'] for s in R]
    sc['P9a'] = dict(hit=bool(ok_a))
    sc['P9b'] = dict(pr_l1=pr1, pr_deep_max=float(max(prdeep)), hit=bool(min(pr1) >= 40 and max(prdeep) <= 4))
    sc['P9c'] = dict(cap32_l1=cap1, cap32_l16=cap16, hit=bool(max(cap1) <= 0.2 and min(cap16) >= 0.9))
    print('== rank: layer, median PR3, median covPR, median cap8, median cap32, median fro2_std')
    for l in R[next(iter(R))]['layers']:
        g = [R[s]['layers'][l] for s in R]
        print(f"  l={int(l):2d} PR3 {np.median([x['pr'] for x in g]):6.1f} covPR {np.median([x['cov_pr'] for x in g]):6.1f}"
              f" cap8 {np.median([x['capk']['8'] for x in g]):.3f} cap32 {np.median([x['capk']['32'] for x in g]):.3f}"
              f" std {np.median([x['fro2_std'] for x in g]):.2e}")
    out['rank'] = {s: R[s]['layers'] for s in R}
pc = os.path.join(RUNS, 'rank_control.json')
if os.path.exists(pc):
    C = json.load(open(pc))
    sc['control'] = {k: dict(pr=C[k]['pr'], cap=C[k]['capk']) for k in C}
    if 'planted32' in C:
        sc['P9d_control_planted32'] = dict(pr=C['planted32']['pr'], hit=bool(24 <= C['planted32']['pr'] <= 40))
out['scores'] = sc
print(json.dumps(sc, indent=1))
if len(sys.argv) > 2:
    json.dump(out, open(sys.argv[2], 'w'), indent=1)
