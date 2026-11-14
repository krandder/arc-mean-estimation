"""Registered scorer for PREREG Part 1 (tests T1-T4). Reads runs/baselines_s*.json, runs/cs2_s*.json,
runs/region_code_s*.json; writes results/scores.json and prints the verdicts."""
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/frozen')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
ORACLE_MV_PER_REGION = 9.0


def interp(curve, c):
    """Log-log interpolation of [(cost, nmse)] at cost c; None outside the measured range."""
    pts = sorted((x, y) for x, y in curve if x and y and y > 0)
    if not pts or c < pts[0][0] or c > pts[-1][0]:
        return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= c <= x1:
            if x1 == x0:
                return y0
            t = (math.log(c) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return math.exp(math.log(y0) + t * (math.log(y1) - math.log(y0)))
    return pts[-1][1] if c == pts[-1][0] else None


def main():
    out = dict(nets={})
    t1 = t2 = t3 = t4 = 0
    for s in ndx.EVAL_SEEDS:
        b = json.load(open(BASE + f'runs/baselines_s{s}.json'))
        cs = json.load(open(BASE + f'runs/cs2_s{s}.json'))
        orc = json.load(open(BASE + f'runs/region_code_s{s}.json'))
        cur = {k: [(v[k]['cost_mv'], v[k]['nmse']) for v in b['res'].values() if k in v] for k in
               ('MC', 'RQMC', 'RQMCJ', 'RADQ')}
        pts = [(p['cost_mv'], p['nmse']) for p in cs['points']]
        rec = dict(cs=pts)
        # T1, T2
        for name, key in (('T1', 'RQMC'), ('T2', 'RQMCJ')):
            best = None
            for c, e in pts:
                if 2 ** 16 <= c <= 2 ** 24:
                    r = interp(cur[key], c)
                    if r is not None:
                        ratio = r / e
                        best = ratio if best is None or ratio > best else best
            rec[name + '_best_ratio'] = best
            rec[name + '_pass'] = bool(best is not None and best >= 3.0)
        t1 += rec['T1_pass']
        t2 += rec['T2_pass']
        # T3 slope over [2^18, 2^24]
        sel = [(c, e) for c, e in pts if 2 ** 18 <= c <= 2 ** 24 and e > 0]
        if len(sel) >= 3:
            x = np.log2([c for c, _ in sel])
            y = np.log2([e for _, e in sel])
            slope = float(np.polyfit(x, y, 1)[0])     # nMSE ~ cost^slope
            sdec = -slope
            bits = (2.0 / sdec) if sdec > 0 else float('inf')
        else:
            slope, bits = None, None
        rec['T3_nmse_slope'] = slope
        rec['T3_bits_per_halving'] = bits
        rec['T3_pass'] = bool(bits is not None and bits > 2.0)
        t3 += rec['T3_pass']
        # T4 oracle
        comps = []
        for p in orc['curves']['32']['curve']:
            if p['nmse_ho'] >= 10 * p['noise_ho'] and p['nmse_ho'] > 0:
                c = ORACLE_MV_PER_REGION * p['R']
                r = interp(cur['RQMCJ'], c)
                if r is not None:
                    comps.append(dict(R=p['R'], cost=c, oracle=p['nmse_ho'], rqmcj=r, oracle_worse=p['nmse_ho'] > r,
                                      oracle_in_sample=p['nmse_in']))
        rec['T4_comparisons'] = comps
        rec['T4_pass'] = bool(comps and all(cmp['oracle_worse'] for cmp in comps))
        t4 += rec['T4_pass']
        out['nets'][str(s)] = rec
        print(s, 'T1 best RQMC/CS ratio', rec['T1_best_ratio'], 'T2 best RQMCJ/CS ratio', rec['T2_best_ratio'],
              'T3 bits/halving', bits, 'T4 comparisons', len(comps), 'pass', rec['T4_pass'])
    out['verdicts'] = dict(T1=dict(nets=t1, holds=t1 >= 4), T2=dict(nets=t2, holds=t2 >= 4),
                           T3=dict(nets=t3, holds=t3 >= 4), T4=dict(nets=t4, holds=t4 >= 5))
    json.dump(out, open(BASE + 'results/scores.json', 'w'), indent=1)
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
