"""Scorer for Amendment 1 (T1b-T3b on CS2b, T5-T6 on UNB). Writes results/scores_a1.json."""
import json
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/frozen')
import ndx  # noqa: E402
from score import interp  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'


def main():
    out = dict(nets={})
    cnt = dict(T1b=0, T2b=0, T3b=0, T5=0, T6=0)
    for s in ndx.EVAL_SEEDS:
        b = json.load(open(BASE + f'runs/baselines_s{s}.json'))
        cur = {k: [(v[k]['cost_mv'], v[k]['nmse']) for v in b['res'].values() if k in v] for k in ('RQMC', 'RQMCJ')}
        cs = json.load(open(BASE + f'runs/cs2b_s{s}.json'))
        pts = [(p['cost_mv'], p['nmse']) for p in cs['points']]
        rec = {}
        for name, key in (('T1b', 'RQMC'), ('T2b', 'RQMCJ')):
            best = None
            for c, e in pts:
                if 2 ** 16 <= c <= 2 ** 24:
                    r = interp(cur[key], c)
                    if r is not None:
                        best = r / e if best is None or r / e > best else best
            rec[name + '_best_ratio'] = best
            rec[name + '_pass'] = bool(best is not None and best >= 3.0)
            cnt[name] += rec[name + '_pass']
        sel = [(c, e) for c, e in pts if 2 ** 18 <= c <= 2 ** 24 and e > 0]
        slope = float(np.polyfit(np.log2([c for c, _ in sel]), np.log2([e for _, e in sel]), 1)[0]) if len(sel) >= 3 else None
        bits = (2.0 / -slope) if slope is not None and slope < 0 else float('inf')
        rec['T3b_bits_per_halving'] = bits
        rec['T3b_pass'] = bool(bits > 2.0)
        cnt['T3b'] += rec['T3b_pass']
        u = json.load(open(BASE + f'runs/unbiased_s{s}.json'))
        for name, key in (('T5', 'RQMCJ'), ('T6', 'RQMC')):
            best = None
            for k, v in u['res'].items():
                if k.startswith('RQMC_'):
                    r = interp(cur[key], v['cost_mv'])
                    if r is not None:
                        best = r / v['nmse'] if best is None or r / v['nmse'] > best else best
            rec[name + '_best_ratio'] = best
            rec[name + '_pass'] = bool(best is not None and best >= 3.0)
            cnt[name] += rec[name + '_pass']
        out['nets'][str(s)] = rec
        print(s, rec)
    out['verdicts'] = {k: dict(nets=v, holds=v >= 4) for k, v in cnt.items()}
    json.dump(out, open(BASE + 'results/scores_a1.json', 'w'), indent=1)
    print(json.dumps(out['verdicts']))


if __name__ == '__main__':
    main()
