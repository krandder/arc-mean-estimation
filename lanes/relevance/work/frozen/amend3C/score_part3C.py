"""PREREG Amendment 3C scorer: prospective test of theory v3.4 [A] (gpt-6-astra round 3, lib/theory_v34_astra.py) on the
fresh E-ARC nets 4006-4009 (layers 0, 4, 8, 16, 24, 28, 31). Default: seeds 4006-4009, writes results/part3C_scores.json.
--seen: nets 4000-4005 (post hoc reference; the co-prover developed the rule on them), writes results/part3C_seen_check.json."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402
import theory_v33 as t33  # noqa: E402
import theory_v34_astra as t34  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'


def main():
    seen = '--seen' in sys.argv
    seeds = range(4000, 4006) if seen else range(4006, 4010)
    out = BASE + ('results/part3C_seen_check.json' if seen else 'results/part3C_scores.json')
    cells = []
    for seed in seeds:
        fn = BASE + f'runs/eval_arc_n256_L32_seed{seed}.json'
        if not glob.glob(fn):
            print('missing', fn)
            continue
        Ws = rel.input_weights(seed, 256, 32)
        for o in json.load(open(fn)):
            st = t34.astra_stats(Ws, o['l'], np.random.default_rng(8000000 + 100 * seed + o['l']))
            p = t34.predict_astra(o, st)
            V = o['V_gauss'][0]
            r = dict(seed=seed, l=o['l'], D=o['J1_gauss'][0] / V, s1=o['V1_gauss'][0] / V, Gamma_meas=t33.measured_R(o),
                     **p)
            r['C1'] = bool(0.75 <= p['D_A'] / r['D'] <= 1.33)
            r['C2'] = bool(abs(r['s1'] - p['s1_A']) <= 0.08)
            r['gamma_relerr'] = abs(p['gamma'] / r['Gamma_meas'] - 1)
            cells.append(r)
            print(f"{seed} l={o['l']:2d} Gamma {p['gamma']:.3f}/{r['Gamma_meas']:.3f} D_A/D {p['D_A'] / r['D']:.2f} "
                  f"s1_A {p['s1_A']:.3f}/{r['s1']:.3f}", flush=True)
    S = {k: (sum(r[k] for r in cells), len(cells)) for k in ('C1', 'C2')}
    early = [r for r in cells if r['l'] <= 8]
    S['C1_early'] = (sum(r['C1'] for r in early), len(early))
    if cells:
        S['gamma_relerr_median_max'] = (float(np.median([r['gamma_relerr'] for r in cells])),
                                        float(max(r['gamma_relerr'] for r in cells)))
    json.dump(dict(scores=S, cells=cells), open(out, 'w'), default=float, indent=1)
    for k, v in S.items():
        print(k, v)


if __name__ == '__main__':
    main()
