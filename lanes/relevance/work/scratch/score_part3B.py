"""PREREG Amendment 3B scorer: prospective test of theory v3.3 (quenched gain ratio, lib/theory_v33.py) and a third
prospective test of theory v2 on fresh E-ARC nets 4006-4009 (layers 0, 4, 8, 16, 24, 28, 31).
Default: seeds 4006-4009, writes results/part3B_scores.json.
--seen: the same computation on the seen nets 4000-4005 (post hoc reference), writes results/part3B_seen_check.json."""
import glob
import json
import math
import sys

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel  # noqa: E402
import score_part1 as sp  # noqa: E402
import theory_v2 as t2  # noqa: E402
import theory_v33 as t33  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
ANG = json.load(open(BASE + 'results/angular_spectra.json'))  # angular spectra of the runs made before the field existed


def main():
    seen = '--seen' in sys.argv
    seeds = range(4000, 4006) if seen else range(4006, 4010)
    out = BASE + ('results/part3B_seen_check.json' if seen else 'results/part3B_scores.json')
    cells = []
    for seed in seeds:
        fn = BASE + f'runs/eval_arc_n256_L32_seed{seed}.json'
        if not glob.glob(fn):
            print('missing', fn)
            continue
        Ws = rel.input_weights(seed, 256, 32)
        for o in json.load(open(fn)):
            c = sp.cell_record(o)
            pl = t2.predict_layer(o)
            lp = o.get('cloud_evals_perp') or ANG.get(f"arc|256|{seed}|{o['l']}")
            pN = t2.predict_N(o, lam_perp=lp)
            Rp = t33.r_perp(Ws, o['l'], 1024, np.random.default_rng(7000000 + 100 * seed + o['l']))
            q = t33.predict_quenched(o, Rp)
            Vrel = o['V_gauss'][0] / o['Ea2_true']
            r = dict(seed=seed, l=o['l'], Vrel=Vrel, Vrel_v2=pl['V_rel'], s1=c['s1'], D=c['D'],
                     R_meas=t33.measured_R(o), **q)
            r['B1'] = bool(0.75 <= q['D_q'] / c['D'] <= 1.33)
            r['B2'] = bool(abs(c['s1'] - q['s1_q']) <= 0.08)
            r['Q1'] = bool(abs(pl['V_rel'] / Vrel - 1) <= 0.2)
            r['Q2'] = bool(abs(c['s1'] - pl['s1']) <= 0.08)
            r['Q3'] = bool(0.75 <= pl['D'] / c['D'] <= 1.33)
            for e in (0.1, 0.01):
                r[f'Q4_{e}'] = bool(sp.within2(pN['N_vec'][str(e)], *c[f'Nvec_{e}']))
            cells.append(r)
            print(f"{seed} l={o['l']:2d} D={c['D']:6.2f} v2={pl['D']:6.2f} q={q['D_q']:6.2f} R_meas={r['R_meas']:.2f} "
                  f"R_q={q['R_q']:.2f} s1={c['s1']:.3f} v2={pl['s1']:.3f} q={q['s1_q']:.3f}", flush=True)
    S = {}
    for k in ('B1', 'B2', 'Q1', 'Q2', 'Q3', 'Q4_0.1', 'Q4_0.01'):
        S[k] = (sum(r[k] for r in cells), len(cells))
    early = [r for r in cells if r['l'] <= 8]
    S['B1_early'] = (sum(r['B1'] for r in early), len(early))
    S['Q3_early'] = (sum(r['Q3'] for r in early), len(early))
    S['B4_R_within_1.33'] = (sum(abs(math.log(r['R_q'] / r['R_meas'])) <= math.log(1.33) for r in cells), len(cells))
    S['per_net'] = {str(s): {k: sum(r[k] for r in cells if r['seed'] == s) for k in ('B1', 'B2', 'Q3', 'Q2')}
                    for s in sorted(set(r['seed'] for r in cells))}
    S['logR_meas_l0'] = [math.log(r['R_meas']) for r in cells if r['l'] == 0]
    json.dump(dict(scores=S, cells=cells), open(out, 'w'), default=float, indent=1)
    for k, v in S.items():
        print(k, v)


if __name__ == '__main__':
    main()
