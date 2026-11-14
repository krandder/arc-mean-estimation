"""EXPLORATORY (not registered): the claim's arms re-costed with flopscope prices for their special functions
(ndtr 96, exp 16 flops per element, passes_fs in score.json), against RQMC. usage: explore_fs.py SCORE_JSON"""
import json, math, sys
import numpy as np

d = json.load(open(sys.argv[1]))


def rq_at(N, Ns, es):
    if N <= Ns[0]:
        return es[0] * Ns[0] / N
    if N >= Ns[-1]:
        return es[-1] * Ns[-1] / N
    return float(np.exp(np.interp(math.log(N), np.log(Ns), np.log(es))))


for s, rows in d['per_net'].items():
    g, gfs, c, cfs = [], [], [], []
    for r in rows:
        m = r['m'].get('LVTV2')
        if not m or 'rqmc' not in r or 'passes_fs' not in m:
            continue
        Ns, es = r['rqmc']['N'], r['rqmc']['e']
        g.append(rq_at(m['C'], Ns, es) / m['e']); gfs.append(rq_at(m['passes_fs'], Ns, es) / m['e'])
        c.append(m['C']); cfs.append(m['passes_fs'])
    if g:
        print(f'{s:9s} LVTV2 cost {np.median(c):7.0f} -> flopscope-priced {np.median(cfs):7.0f} passes; median G_RQ {np.median(g):.2f} -> {np.median(gfs):.2f}; '
              f'nets beating RQMC {sum(x > 1 for x in g)}/{len(g)} -> {sum(x > 1 for x in gfs)}/{len(gfs)}')
