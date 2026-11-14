"""Report tables (post-processing): per (regime, layer) medians over nets of the accounting quantities, with v1 and v2
predictions, the first-chaos lower bound, and N for the best exhibited basis (min over AS, degree-1, cloud-axes bases).
Prospective cells for v2 (not seen before the v2 freeze at 21:48:41Z): ARC seeds 4002-4005, stationary n >= 128.
Default: the registered Part 1 ARC nets 4000-4003, written to results/report_tables.md and .json.
With --arc6: ARC nets 4000-4005 (adds the Amendment 3A nets), written to results/report_tables_arc6.md and .json."""
import glob
import json
import math
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/scratch')
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import score_part1 as sp  # noqa: E402
import theory_v2 as t2  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
ANG = json.load(open(BASE + 'results/angular_spectra.json'))


def nbest(o, V, eps):
    best = None
    for key in ('res_AS_gauss', 'res_R1_gauss', 'res_PCA_gauss'):
        c = o[key]
        for k in sorted(c, key=int):
            if c[k][0] <= eps * V:
                best = int(k) if best is None else min(best, int(k))
                break
    return best


def record(o):
    c = sp.cell_record(o)
    lab = o.get('l') if o['mode'] != 'stat' else o.get('s')
    key = f"{o['mode']}|{o['n']}|{o['seed']}|{lab}"
    lp = o.get('cloud_evals_perp') or ANG.get(key)
    V = o['V_gauss'][0]
    P = 2048 if (o['mode'] == 'stat' and o['n'] == 256) else (8192 if o['mode'] == 'nd' else 4096)
    r = dict(mode=o['mode'], n=o['n'], seed=o['seed'], lab=lab, t=o['t'], resolved=c['resolved'],
             s1=c['s1'], s1r=c['s1r'], D=c['D'], rad_share=1 - c['radial_gauss'],
             M=c.get('M', 1.0), Vrel=V / o['Ea2_true'] if o.get('Ea2_true') else None)
    for e in (0.1, 0.01, 0.001):
        r[f'N_{e}'] = c[f'Nvec_{e}'][1]
        r[f'Nsc_{e}'] = c[f'Nsc_{e}'][1]
        r[f'Nbest_{e}'] = nbest(o, V, e)
    if o['mode'] != 'nd' and lp is not None and c['resolved']:
        p2 = t2.predict_N(o, lam_perp=lp)
        pl = t2.predict_layer(o)
        lo = t2.first_chaos_lower_bound(o, P)
        r.update(v2_s1=pl['s1'], v2_D=pl['D'], v2_Vrel=pl['V_rel'],
                 split=pl['s1_split'], v1_s1=c.get('pred_s1'))
        for e in (0.1, 0.01, 0.001):
            r[f'v1_N_{e}'] = c.get(f'pred_Nvec_{e}')
            r[f'v2_N_{e}'] = p2['N_vec'][str(e)]
            r[f'v2_Nsc_{e}'] = p2['N_sc'][str(e)]
            r[f'lo_{e}'] = lo[str(e)]
    if o['mode'] == 'nd':
        r['radial_true'] = c['radial_true']
    r['prospective_v2'] = (o['mode'] == 'arc' and o['seed'] in (4002, 4003, 4004, 4005)) or \
        (o['mode'] == 'stat' and o['n'] >= 128)
    return r


def med(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return float(np.median(xs)) if xs else None


def main():
    arc6 = '--arc6' in sys.argv
    arc_seeds = (4000, 4001, 4002, 4003, 4004, 4005) if arc6 else (4000, 4001, 4002, 4003)
    out = BASE + ('results/report_tables_arc6' if arc6 else 'results/report_tables')
    recs = []
    for fn in sorted(glob.glob(BASE + 'runs/eval_*.json')):
        for o in json.load(open(fn)):
            if o['seed'] >= 9000 or (o['mode'] == 'arc' and o['seed'] not in arc_seeds):
                continue
            recs.append(record(o))
    json.dump(recs, open(out + '.json', 'w'), default=float, indent=1)
    groups = defaultdict(list)
    for r in recs:
        groups[(r['mode'], r['n'], r['lab'])].append(r)
    lines = ['# Report tables (medians over nets; measured / v2 prediction; lo = first-chaos estimate, heuristically noise-corrected, uncertified)',
             f'ARC nets: {", ".join(map(str, arc_seeds))}', '']
    hdr = ('| regime | n | l or s | t | nets | M | V/E|a|^2 meas / v2 | s1 meas / v2 | D meas / v2 | radial share | '
           'N(.1) meas [best] / v2 / lo | N(.01) | N(.001) | Nsc(.1, .01, .001) meas / v2 |')
    lines += [hdr, '|' + '---|' * 14]
    for key in sorted(groups, key=lambda k: (k[0], k[1], k[2] if k[2] is not None else -1)):
        g = groups[key]
        gr = [r for r in g if r['resolved']]
        if not gr:
            lines.append(f'| {key[0]} | {key[1]} | {key[2]} | {g[0]["t"]} | 0 of {len(g)} resolved |' + ' |' * 9)
            continue

        def m(k):
            return med([r.get(k) for r in gr])

        def f(x, p=3):
            return '-' if x is None else (f'{x:.{p}f}' if isinstance(x, float) else str(x))

        Ncols = []
        for e in (0.1, 0.01, 0.001):
            Ncols.append(f"{f(m(f'N_{e}'), 0)} [{f(m(f'Nbest_{e}'), 0)}] / {f(m(f'v2_N_{e}'), 0)} / {f(m(f'lo_{e}'), 0)}")
        sc = ', '.join(f(m(f'Nsc_{e}'), 0) for e in (0.1, 0.01, 0.001)) + ' / ' + \
            ', '.join(f(m(f'v2_Nsc_{e}'), 0) for e in (0.1, 0.01, 0.001))
        lines.append(f"| {key[0]} | {key[1]} | {key[2]} | {g[0]['t']} | {len(gr)} | {f(m('M'))} | "
                     f"{f(m('Vrel'), 4)} / {f(m('v2_Vrel'), 4)} | {f(m('s1'))} / {f(m('v2_s1'))} | "
                     f"{f(m('D'), 2)} / {f(m('v2_D'), 2)} | {f(m('rad_share'))} | {Ncols[0]} | {Ncols[1]} | {Ncols[2]} | {sc} |")
    open(out + '.md', 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
