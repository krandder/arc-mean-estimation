"""Slopes of held-out error vs estimation flops as K grows (A4 model-only estimate), against MC and RQMC on the same
populations. Reads runs/step4f_*.json (any number of files; rows merged by K). Prints a table per width."""
import glob, json, math, os, sys
import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
pat = sys.argv[1] if len(sys.argv) > 1 else 'step4f_n32_L4_s9611_d32_K*.json'
rows = {}
meta = None
for f in sorted(glob.glob(os.path.join(HERE, 'runs', pat))):
    d = json.load(open(f))
    meta = d
    for r in d['rows']:
        rows[r['K']] = r
Ks = sorted(rows)
if not Ks:
    print('no rows'); sys.exit()
widths = sorted(set(p['s'] for p in rows[Ks[0]]['pops']))
out = []
print('K:', Ks)
for s in widths:
    e = [float(np.median([p['e_model'] for p in rows[K]['pops'] if p['s'] == s])) for K in Ks]
    c = [rows[K]['pops'][0]['model_cost_passes'] for K in Ks]
    mc = [float(np.median([p['mc_at_model_cost'] for p in rows[K]['pops'] if p['s'] == s])) for K in Ks]
    lo = [float(np.median([p['cv'][-1]['err'] for p in rows[K]['pops'] if p['s'] == s])) for K in Ks]
    slope = -np.polyfit(np.log(c), np.log(e), 1)[0] if len(Ks) >= 2 else float('nan')
    # RQMC slope on the same populations (budgets 16..1024), from the first file's baseline
    rq = [p for p in rows[Ks[0]]['pops'] if p['s'] == s]
    Ns = [x['N'] for x in rq[0]['cv']]
    rqe = [float(np.median([p['cv'][i]['rqmc_at_N'] for p in rq])) for i in range(len(Ns))]
    rq_slope = -np.polyfit(np.log(Ns), np.log(rqe), 1)[0]
    print(f"s={s}: model-only error {['%.2e' % x for x in e]} at estimation cost {['%.3g' % x for x in c]} passes;"
          f" slope {slope:.2f} (MC 1.00, RQMC {rq_slope:.2f}); MC at those costs {['%.2e' % x for x in mc]};"
          f" CV(N={Ns[-1]}) {['%.2e' % x for x in lo]}")
    out.append(dict(s=s, K=Ks, e_model=e, cost=c, mc=mc, slope=float(slope), rqmc_slope=float(rq_slope), cv=lo))
json.dump(out, open(os.path.join(HERE, 'results', 'slope4.json'), 'w'), indent=1)
