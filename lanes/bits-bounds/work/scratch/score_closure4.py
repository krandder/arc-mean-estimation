"""Score PREREG Amendment 4 (B3, B4) with the gain definition of scratch/score_closure.py, and print POST HOC
statistics of the closure's error across widths (geometric means of per-net nMSE with standard errors, log-log slopes
over all nets, the annealed ratio n E[err^2]/E[V] of co-prover round 3). Writes results/closure4_scores.json and
results/posthoc_closure.md."""
import os
import json
import glob
import math
import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), '..')


def load(n, L):
    rs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'runs', f'closure_n{n}_L{L}_s*.json')))]
    return [r for r in rs if r.get('nMSE_closure') is not None and r['V'] > 0]


def gain(r):
    return (1.0 / r['cost_passes_matmul']) / max(r['nMSE_closure'], 1e-300)


def main():
    med = {}
    for (n, L) in [(128, 128), (256, 256), (128, 64), (256, 128)]:
        med[(n, L)] = float(np.median([gain(r) for r in load(n, L)]))
    scores = {
        'B3': {'median_gain_256x256': med[(256, 256)], 'median_gain_128x128': med[(128, 128)],
               'pass': bool(med[(256, 256)] <= med[(128, 128)])},
        'B4': {'median_gain_256x128': med[(256, 128)], 'median_gain_128x64': med[(128, 64)],
               'pass': bool(med[(256, 128)] <= 2 * med[(128, 64)])},
    }
    json.dump(scores, open(os.path.join(ROOT, 'results', 'closure4_scores.json'), 'w'), indent=1)
    lines = ['# Closure test across widths (POST HOC statistics; registered scores in closure_scores.json and '
             'closure4_scores.json)', '',
             'Per net: nMSE = |a - mu|^2 / V by the unbiased cross-product; gain = (1/(2n)) / nMSE (MC at the '
             "closure's matrix-product cost of 2n passes).", '',
             '| n x L | nets | median gain | geo-mean nMSE | log10 nMSE mean +- SE | n E[err^2]/E[V] |',
             '|---|---|---|---|---|---|']
    slopes = {}
    for alpha, cfgs in [(1.0, [16, 32, 64, 128, 192, 256]), (0.5, [16, 32, 64, 128, 256])]:
        xs, ys = [], []
        for n in cfgs:
            L = int(round(alpha * n))
            rs = load(n, L)
            if not rs:
                continue
            lg = np.log10([r['nMSE_closure'] for r in rs])
            e = np.array([r['closure_sqerr_unbiased'] for r in rs])
            V = np.array([r['V'] for r in rs])
            lines.append(f'| {n} x {L} | {len(rs)} | {np.median([gain(r) for r in rs]):.2f} | {10 ** lg.mean():.2e} | '
                         f'{lg.mean():.2f} +- {lg.std(ddof=1) / math.sqrt(len(lg)):.2f} | {n * e.sum() / V.sum():.3f} |')
            xs += [math.log10(n)] * len(rs)
            ys += list(lg)
        xs, ys = np.array(xs), np.array(ys)
        for lo, hi in [(16, 128), (128, 256), (16, 256)]:
            sel = (xs >= math.log10(lo) - 1e-9) & (xs <= math.log10(hi) + 1e-9)
            if sel.sum() >= 3 and len(set(xs[sel])) >= 2:
                A = np.vstack([xs[sel], np.ones(sel.sum())]).T
                coef, res, _, _ = np.linalg.lstsq(A, ys[sel], rcond=None)
                resid = ys[sel] - A @ coef
                s2 = float(resid @ resid) / max(sel.sum() - 2, 1)
                cov = s2 * np.linalg.inv(A.T @ A)
                slopes[f'alpha={alpha} n={lo}-{hi}'] = (float(coef[0]), float(math.sqrt(cov[0, 0])))
    lines += ['', 'Log-log slope of per-net nMSE against n (all nets, least squares; slope +- SE):']
    for k, (s, se) in slopes.items():
        lines.append(f'- {k}: {s:.2f} +- {se:.2f}')
    lines += ['', 'Extrapolation test: fit log10 nMSE on log10 n over n = 16-128 (all nets), predict the mean at larger n',
              '(prediction SE from the fit covariance), compare with the observed mean +- SE; z = (obs - pred)/SE_comb.']
    for alpha, big in [(1.0, [192, 256]), (0.5, [256])]:
        xs, ys = [], []
        for n in [16, 32, 64, 128]:
            lg = np.log10([r['nMSE_closure'] for r in load(n, int(round(alpha * n)))])
            xs += [math.log10(n)] * len(lg)
            ys += list(lg)
        A = np.vstack([np.array(xs), np.ones(len(xs))]).T
        coef = np.linalg.lstsq(A, np.array(ys), rcond=None)[0]
        resid = np.array(ys) - A @ coef
        cov = float(resid @ resid) / (len(ys) - 2) * np.linalg.inv(A.T @ A)
        for n in big:
            lg = np.log10([r['nMSE_closure'] for r in load(n, int(round(alpha * n)))])
            x = np.array([math.log10(n), 1.0])
            pred, sep = float(x @ coef), math.sqrt(float(x @ cov @ x))
            obs, seo = float(lg.mean()), float(lg.std(ddof=1) / math.sqrt(len(lg)))
            z = (obs - pred) / math.sqrt(sep ** 2 + seo ** 2)
            lines.append(f'- alpha={alpha} n={n}: predicted {pred:.2f} +- {sep:.2f}, observed {obs:.2f} +- {seo:.2f}, '
                         f'z = {z:.2f}')
    open(os.path.join(ROOT, 'results', 'posthoc_closure.md'), 'w').write('\n'.join(lines) + '\n')
    print(json.dumps(scores, indent=1))
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
