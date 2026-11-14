"""ARC 256 x 32 accounting columns (post-processing, medians over the evaluation nets present):
s_1 (Stein), s_2u = (2V - D(.5) - D(-.5))/(0.5 V) = s_2 + s_4/4 + ... (an upper estimate of the degree-2 share),
interaction share lower estimate 1 - s_1 - s_2u, radial share, V/E|a|^2, and the gain bound of the best k-feature
control (exact conditional mean on the top-k active-subspace directions as a control variate: gain = 1/residual(k)).
Default: the registered Part 1 nets 4000-4003, written to results/arc_accounting.json. With --arc6: nets 4000-4005
(adds the Amendment 3A nets), written to results/arc_accounting_arc6.json; per-net rows are stored in both."""
import glob
import json
import sys

import numpy as np

BASE = '/home/agent/workspaces/mats/work/relevance/'


def main():
    arc6 = '--arc6' in sys.argv
    seeds = (4000, 4001, 4002, 4003, 4004, 4005) if arc6 else (4000, 4001, 4002, 4003)
    rows = {}
    for fn in sorted(glob.glob(BASE + 'runs/eval_arc_n256_L32_seed*.json')):
        for o in json.load(open(fn)):
            if o['seed'] not in seeds:
                continue
            V = o['V_gauss'][0]
            md = o['mehler_D']
            s1 = o['V1_gauss'][0] / V
            s2u = (2 * V - md['0.5'][0] - md['-0.5'][0]) / (0.5 * V)
            r = o['res_AS_gauss']
            gains = {k: 1.0 / max(r[str(k)][0] / V, 1e-6) for k in (1, 16, 64, 128) if str(k) in r}
            rows.setdefault(o['l'], []).append(dict(seed=o['seed'], s1=s1, s2u=s2u, inter=1 - s1 - s2u,
                                                    rad=1 - o['res_radial_gauss'][0] / V,
                                                    Vrel=V / o['Ea2_true'], gains=gains,
                                                    s1r=o['V1r_gauss'][0] / o['Vr_gauss'][0]))
    out = {}
    print('| l | nets | s_1 | s_2 (upper est.) | interactions (lower est.) | radial share | best k-feature control gain, k = 1 / 16 / 64 / 128 |')
    print('|---|---|---|---|---|---|---|')
    for l in sorted(rows):
        rs = rows[l]
        med = lambda k: float(np.median([x[k] for x in rs]))
        g = {k: float(np.median([x['gains'][k] for x in rs])) for k in (1, 16, 64, 128)}
        out[l] = dict(nets=len(rs), s1=med('s1'), s2u=med('s2u'), inter=med('inter'), rad=med('rad'), gains=g,
                      s1_range=[min(x['s1'] for x in rs), max(x['s1'] for x in rs)], per_net=rs)
        print(f"| {l} | {len(rs)} | {med('s1'):.2f} | {med('s2u'):.2f} | {med('inter'):.2f} | {med('rad'):.2f} | "
              f"{g[1]:.2f} / {g[16]:.2f} / {g[64]:.2f} / {g[128]:.1f} |")
    json.dump(out, open(BASE + ('results/arc_accounting_arc6.json' if arc6 else 'results/arc_accounting.json'), 'w'),
              indent=1)


if __name__ == '__main__':
    main()
