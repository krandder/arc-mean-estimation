"""POST HOC: where the output variance is made, in mean field, against the registered E1 data (runs/eval_*.json).

Mean-field ingredients (annealed, large width, fixed depth; HEURISTIC at L ~ n):
- angle contraction: cos theta_{j+1} = kappa(cos theta_j);
- per-layer variance of the log-gain difference of two states at angle theta (gain G = |relu(W h)|/|h|):
  v(theta) = (3 - 2 k2(cos theta))/n, k2(r) = E[z_+^2 z'_+^2] for unit Gaussians with correlation r
  (= (3 sin t cos t + (pi - t)(1 + 2 cos^2 t))/(2 pi), t = arccos r); v ~ 2 theta^2/n for small theta;
- output variance of unit inputs (two independent inputs start orthogonal, c_0 = 0):
  V_ang/E|A|^2 = 1 - cos(theta_L) exp(-S_0/2), S_0 = sum_{j=0}^{L-1} v(theta_j);
- residual of one radial merge at layer l with a reference at angle phi from a typical member:
  D_R(1) E|A|^2 / V_ang with D_R(1)/E|A|^2 = S_l(phi) + 2(1 - cos theta_L(phi)), S_l(phi) = sum_{j>=l} v(theta_j(phi)).
For small residuals, D_R(1)/V_ang ~ 2 S_l(phi)/S_0: the factor 1/n cancels (width-free), and with
theta_j ~ 3 pi/(j + 3 pi/phi), S_l(phi) ~ (6 pi/n) phi, so D_R(1)/V ~ (12 pi phi_l / S_0 n) n = 12 pi phi_l/(n S_0/n).
Compares (a) V_ang/E|A|^2 predicted against measured, (b) D_R(1) predicted from the measured spread phi (RMS angle of
the cloud to its centre, E1 'median_cell_spread' at M = 1) and the measured V_ang/E|A|^2 (future half only), and
(c) the fully mean-field D_R(1) (phi from the mean-field pairwise angle / sqrt 2, V from (a)).
Writes results/variance_made.md."""
import os
import glob
import json
import math
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def kappa(c):
    c = min(1.0, max(-1.0, c))
    return (math.sqrt(max(0.0, 1 - c * c)) + (math.pi - math.acos(c)) * c) / math.pi


def k2(c):
    c = min(1.0, max(-1.0, c))
    t = math.acos(c)
    return (3 * math.sin(t) * math.cos(t) + (math.pi - t) * (1 + 2 * math.cos(t) ** 2)) / (2 * math.pi)


def v(c, n):
    return (3 - 2 * k2(c)) / n


def S_from(c0, steps, n):
    """Sum of v over `steps` layers starting at cosine c0, and the final cosine."""
    c, s = c0, 0.0
    for _ in range(steps):
        s += v(c, n)
        c = kappa(c)
    return s, c


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json'))):
        r = json.load(open(f))
        if r.get('dead'):
            continue
        n, L = r['n'], r['L']
        EA2 = r['Vang'] + r['mu2']
        vrat_meas = r['Vang'] / EA2
        S0, cL0 = S_from(0.0, L, n)
        vrat_mf = 1 - cL0 * math.exp(-S0 / 2)
        for e in r['E1']:
            l, Lp = e['l'], e['Lp']
            phi = e['fwd']['1']['median_cell_spread']
            Sl, cLp = S_from(math.cos(phi), Lp, n)
            DR_future = (Sl + 2 * (1 - cLp)) / vrat_meas
            # mean-field pairwise angle at l, reference angle = pairwise / sqrt 2
            c = 0.0
            for _ in range(l):
                c = kappa(c)
            phi_mf = math.acos(c) / math.sqrt(2)
            Sl2, cLp2 = S_from(math.cos(phi_mf), Lp, n)
            DR_mf = (Sl2 + 2 * (1 - cLp2)) / vrat_mf
            rows.append({'cfg': f'{n}x{L}', 'n': n, 'L': L, 'l': l, 'frac': l / L, 'DR_meas': e['fwd']['1']['D_R'],
                         'DR_future': DR_future, 'DR_mf': DR_mf, 'vrat_meas': vrat_meas, 'vrat_mf': vrat_mf,
                         'phi': phi, 'phi_mf': phi_mf})
    cfgs = sorted(set(x['cfg'] for x in rows), key=lambda s: (int(s.split('x')[1]) / int(s.split('x')[0]),
                                                             int(s.split('x')[0])))
    lines = ['# Where the variance is made: mean field against registered E1 data (POST HOC)', '',
             'Medians over nets. V/E|A|^2: measured and mean-field. D_R(1): measured; predicted from the measured',
             'spread and measured V (future half); fully mean-field. Ratios are measured / predicted.', '',
             '| config | l | V/E|A|^2 meas | MF | D_R(1) meas | future-half pred | ratio | full MF pred | ratio |',
             '|---|---|---|---|---|---|---|---|---|']
    allr1, allr2 = [], []
    for cfg in cfgs:
        for l in sorted(set(x['l'] for x in rows if x['cfg'] == cfg)):
            sel = [x for x in rows if x['cfg'] == cfg and x['l'] == l]
            med = lambda k: float(np.median([x[k] for x in sel]))
            r1 = [x['DR_meas'] / x['DR_future'] for x in sel]
            r2 = [x['DR_meas'] / x['DR_mf'] for x in sel]
            allr1 += r1
            allr2 += r2
            lines.append(f"| {cfg} | {l} | {med('vrat_meas'):.3g} | {med('vrat_mf'):.3g} | {med('DR_meas'):.3g} | "
                         f"{med('DR_future'):.3g} | {np.median(r1):.2f} | {med('DR_mf'):.3g} | {np.median(r2):.2f} |")
    q = lambda a: np.percentile(a, [10, 50, 90])
    lines += ['', f'All (net, layer) cells: measured/future-half ratio 10-50-90%: '
              f'{np.round(q(allr1), 2).tolist()}; measured/full-MF ratio: {np.round(q(allr2), 2).tolist()} '
              f'({len(allr1)} cells).']
    open(os.path.join(ROOT, 'results', 'variance_made.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
