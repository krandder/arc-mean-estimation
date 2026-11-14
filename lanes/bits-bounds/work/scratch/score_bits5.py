"""Score PREREG Amendment 5 (Q1-Q5) from runs5/bits5_*.json; writes results/bits5_scores.json.
Usage: python scratch/score_bits5.py [--dev | --old]. --dev reads runs5_dev/; --old applies Q2-Q5 to the registered
E1 runs (runs/eval_*.json; POST HOC calibration only, not a score).
Mean field (MF): c_0 = 0, c_{j+1} = kappa(c_j); v(c) = (3 - 2 k2(c))/n is the conditional variance of the log-gain
difference of two states at cosine c; MF log-radius variance after l layers = (1/2) sum_{j<l} v(c_j);
MF V/E|A|^2 = 1 - c_L exp(-S_0/2), S_0 = sum_{j<L} v(c_j). One radial merge at layer l with a reference at angle phi:
D_R(1) = (S_l(phi) + 2(1 - c_{L'}(phi))) / (V/E|A|^2), S_l(phi) = sum over the L' future layers of v along the pair's
MF cosines from cos phi; "future half": phi = the measured M = 1 spread and the measured V/E|A|^2; "full MF": phi = MF
pairwise angle at l over sqrt 2 and the MF V/E|A|^2."""
import os
import sys
import glob
import json
import math
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def kappa(c):
    c = min(1.0, max(-1.0, c))
    return (math.sqrt(max(0.0, 1 - c * c)) + (math.pi - math.acos(c)) * c) / math.pi


def k2(c):
    c = min(1.0, max(-1.0, c))
    t = math.acos(c)
    return (3 * math.sin(t) * math.cos(t) + (math.pi - t) * (1 + 2 * math.cos(t) ** 2)) / (2 * math.pi)


def S_from(c0, steps, n):
    c, s = c0, 0.0
    for _ in range(steps):
        s += (3 - 2 * k2(c)) / n
        c = kappa(c)
    return s, c


def mf_cos(l):
    c = 0.0
    for _ in range(l):
        c = kappa(c)
    return c


def gamma_R(e):
    Ms = [4, 16, 64, 256]
    D = [e['fwd'][str(M)]['D_R'] for M in Ms]
    if min(D) <= 0:
        return None
    return float(-np.polyfit(np.log(Ms), np.log(D), 1)[0])


def bits_measured(e, eps2):
    """log2 of the least M with D_R(M) <= eps2 on the grid {1, 4, 16, 64, 256}, interpolated log-linearly; None if
    D_R(256) > eps2 (more than 8 bits)."""
    Ms = [1, 4, 16, 64, 256]
    D = [e['fwd'][str(M)]['D_R'] for M in Ms]
    if D[0] <= eps2:
        return 0.0
    for i in range(1, len(Ms)):
        if D[i] <= eps2:
            x0, x1 = math.log2(Ms[i - 1]), math.log2(Ms[i])
            y0, y1 = math.log(D[i - 1]), math.log(max(D[i], 1e-300))
            return x0 + (math.log(eps2) - y0) * (x1 - x0) / (y1 - y0) if y1 != y0 else x1
    return None


def main():
    mode = 'dev' if '--dev' in sys.argv else ('old' if '--old' in sys.argv else 'eval')
    if mode == 'old':
        files = sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json')))
    else:
        files = sorted(glob.glob(os.path.join(ROOT, 'runs5_dev' if mode == 'dev' else 'runs5', 'bits5_*.json')))
    nets = [json.load(open(f)) for f in files]
    nets = [r for r in nets if not r.get('dead')]
    q1, q2, q3, q4, q5, q6 = [], [], {}, [], [], []
    for r in nets:
        n, L = r['n'], r['L']
        cfg = f'{n}x{L}'
        EA2 = r.get('EA2', r['Vang'] + r['mu2'])
        vr = r['Vang'] / EA2
        S0, cL = S_from(0.0, L, n)
        vr_mf = 1 - cL * math.exp(-S0 / 2)
        q2.append({'cfg': cfg, 'seed': r['seed'], 'meas': vr, 'mf': vr_mf, 'ratio': vr / vr_mf})
        if 'logr_var_profile' in r:
            for l in sorted(set([max(1, L // 8), max(1, L // 4), L // 2, L])):
                mf = 0.5 * S_from(0.0, l, n)[0]
                meas = r['logr_var_profile'][l]
                q1.append({'cfg': cfg, 'seed': r['seed'], 'l': l, 'meas': meas, 'mf': mf, 'ratio': meas / mf})
        for e in r['E1']:
            l, Lp = e['l'], e['Lp']
            phi = e['fwd']['1']['median_cell_spread']
            Sl, cp = S_from(math.cos(phi), Lp, n)
            pred = (Sl + 2 * (1 - cp)) / vr
            q3.setdefault(cfg, []).append(e['fwd']['1']['D_R'] / pred)
            rho = e['theta_median'] * Lp / 2
            if rho > 2:
                g = gamma_R(e)
                if g is not None:
                    q4.append({'cfg': cfg, 'l': l, 'gPR': g * e['PR']})
                phi_mf = math.acos(mf_cos(l)) / math.sqrt(2)
                Sl2, cp2 = S_from(math.cos(phi_mf), Lp, n)
                D1_mf = (Sl2 + 2 * (1 - cp2)) / vr_mf
                PR_law = 1.04 * n / l + 1.38
                pred256 = D1_mf * 256.0 ** (-0.72 / PR_law)
                q5.append({'cfg': cfg, 'l': l, 'ratio': e['fwd']['256']['D_R'] / pred256})
                D1 = e['fwd']['1']['D_R']
                for eps2 in [0.1, 0.03, 0.01]:
                    pred_bits = max(0.0, (e['PR'] / 0.72) * math.log2(D1 / eps2))
                    meas_bits = bits_measured(e, eps2)
                    if meas_bits is None:
                        agree = pred_bits > 8
                    else:
                        agree = pred_bits <= 8 + 2 and abs(pred_bits - meas_bits) <= 2
                    q6.append({'cfg': cfg, 'l': l, 'eps2': eps2, 'pred': pred_bits, 'meas': meas_bits,
                               'agree': bool(agree)})
    out = {'mode': mode, 'nets': len(nets)}
    if q1:
        rat = np.array([x['ratio'] for x in q1])
        out['Q1'] = {'cells': len(rat), 'frac_in_0.5_1.5': float(np.mean((rat >= 0.5) & (rat <= 1.5))),
                     'median_ratio': float(np.median(rat)), 'pass': bool(np.mean((rat >= 0.5) & (rat <= 1.5)) >= 0.75),
                     'by_cfg': {c: float(np.median([x['ratio'] for x in q1 if x['cfg'] == c]))
                                for c in sorted(set(x['cfg'] for x in q1))}}
    rat = np.array([x['ratio'] for x in q2])
    byc = {c: float(np.median([x['ratio'] for x in q2 if x['cfg'] == c])) for c in sorted(set(x['cfg'] for x in q2))}
    f2 = float(np.mean((rat >= 2 / 3) & (rat <= 1.5)))
    out['Q2'] = {'nets': len(rat), 'frac_in_2/3_1.5': f2, 'median_ratio': float(np.median(rat)), 'by_cfg': byc,
                 'pass': bool(f2 >= 0.75 and all(0.8 <= v <= 1.25 for v in byc.values()))}
    out['Q3'] = {'by_cfg_median_ratio': {c: float(np.median(v)) for c, v in q3.items()},
                 'pass': bool(all(1 / 3 <= float(np.median(v)) <= 3 for v in q3.values()))}
    g = np.array([x['gPR'] for x in q4])
    out['Q4'] = {'rough_cells': len(g), 'median_gamma_PR': float(np.median(g)) if len(g) else None,
                 'pass': bool(len(g) > 0 and 0.45 <= float(np.median(g)) <= 1.1)}
    r5 = np.array([x['ratio'] for x in q5])
    out['Q5'] = {'rough_cells': len(r5), 'frac_within_3x': float(np.mean((r5 >= 1 / 3) & (r5 <= 3))) if len(r5) else None,
                 'median_ratio': float(np.median(r5)) if len(r5) else None,
                 'pass': bool(len(r5) > 0 and np.mean((r5 >= 1 / 3) & (r5 <= 3)) >= 0.6)}
    a6 = np.array([x['agree'] for x in q6])
    out['Q6'] = {'pairs': len(a6), 'frac_agree': float(a6.mean()) if len(a6) else None,
                 'pass': bool(len(a6) > 0 and a6.mean() >= 0.7)}
    name = {'eval': 'bits5_scores.json', 'dev': 'bits5_scores_dev.json', 'old': 'bits5_posthoc_old.json'}[mode]
    json.dump(out, open(os.path.join(ROOT, 'results', name), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
