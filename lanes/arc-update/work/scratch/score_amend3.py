"""Score PREREG Amendment 3 (P13, P14): gamma_{2->3} = ln(e_2/e_3)/ln(C_3/C_2), best variant per order by median nMSE,
its median cost; against log(n/L)/log n.  usage: score_amend3.py [OUT_JSON]"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

SEEDS = {32: list(range(300, 308)), 64: list(range(300, 308)), 128: list(range(300, 308)), 256: list(range(200, 205))}
ORD = {2: ('k2', 'k2a'), 3: ('k3', 'k3f', 'k3fa'), 4: ('k4', 'k4f')}
rows = SL.score(SEEDS)


def med(xs):
    return float(np.median(xs)) if xs else float('nan')


out = {}
for n in SEEDS:
    best = {}
    for K in (2, 3, 4):
        cand = []
        for v in ORD[K]:
            e = [r['nmse'] for (nn, s, vv), r in rows.items() if nn == n and vv == v]
            c = [r['passes'] for (nn, s, vv), r in rows.items() if nn == n and vv == v]
            if e:
                cand.append((med(e), med(c), v, len(e)))
        if cand:
            best[K] = min(cand)
    if 2 in best and 3 in best:
        g = math.log(best[2][0] / best[3][0]) / math.log(best[3][1] / best[2][1])
        pred = math.log(8) / math.log(n)
        out[n] = dict(e2=best[2][0], c2=best[2][1], v2=best[2][2], e3=best[3][0], c3=best[3][1], v3=best[3][2],
                      nets=(best[2][3], best[3][3]), gamma23=g, pred=pred,
                      gamma34=(math.log(best[3][0] / best[4][0]) / math.log(best[4][1] / best[3][1])
                               if 4 in best else None))
sc = dict(P13=dict(hit=bool(all(v['gamma23'] < 1 for v in out.values()) and len(out) == 4)),
          P14=dict(hit=bool(all(0.5 * out[n]['pred'] <= out[n]['gamma23'] <= 1.5 * out[n]['pred']
                                for n in (128, 256) if n in out) and 128 in out and 256 in out)))
print(json.dumps(dict(per_width=out, scores=sc), indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(dict(per_width=out, scores=sc), open(sys.argv[1], 'w'), indent=1, default=float)
