"""Exponent fits for curves.py outputs: alpha = -slope of log nMSE (replicate variance) against log cost (passes),
least squares over a window of the curve (default: the upper half of its budgets, at least 4 points), with a
replicate-bootstrap-free standard error from the regression residuals; and nMSE interpolated (log-log) at a common
cost. Usage: fit.py RUN.json [RUN.json ...] [--at COST] [--frac 0.5]"""
import json
import math
import sys

import numpy as np


def fit_curve(rows, frac=0.5, key='nmse_rep'):
    c = np.array([r['cost'] for r in rows])
    y = np.array([r[key] for r in rows])
    ok = np.isfinite(y) & (y > 0)
    c, y = c[ok], y[ok]
    if c.size < 3:
        return None
    k0 = min(int(math.floor(c.size * (1 - frac))), c.size - 4) if c.size >= 4 else 0
    k0 = max(k0, 0)
    X = np.log(c[k0:])
    Y = np.log(y[k0:])
    A = np.vstack([X, np.ones_like(X)]).T
    coef, res, _, _ = np.linalg.lstsq(A, Y, rcond=None)
    slope, icpt = coef
    if X.size > 2:
        resid = Y - A @ coef
        s2 = (resid ** 2).sum() / (X.size - 2)
        se = math.sqrt(s2 / ((X - X.mean()) ** 2).sum())
    else:
        se = float('nan')
    return dict(alpha=-slope, se=se, icpt=icpt, cmin=float(c[k0]), cmax=float(c[-1]), npts=int(X.size))


def interp_at(rows, cost, key='nmse_rep'):
    c = np.array([r['cost'] for r in rows])
    y = np.array([r[key] for r in rows])
    if cost < c.min() or cost > c.max():
        return float('nan')
    return float(np.exp(np.interp(math.log(cost), np.log(c), np.log(y))))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    at = None
    frac = 0.5
    if '--at' in sys.argv:
        at = float(sys.argv[sys.argv.index('--at') + 1])
    if '--frac' in sys.argv:
        frac = float(sys.argv[sys.argv.index('--frac') + 1])
    args = [a for a in args if not a.replace('.', '').replace('e', '').isdigit()]
    for f in args:
        d = json.load(open(f))
        for m, rows in d['methods'].items():
            r = fit_curve(rows, frac)
            if r is None:
                continue
            extra = ''
            if at:
                extra = '  nMSE@%g = %.3e' % (at, interp_at(rows, at))
            print('%-28s %-11s alpha %.3f +- %.3f  window %.3g-%.3g passes (%d pts)%s' % (
                f.split('/')[-1], m, r['alpha'], r['se'], r['cmin'], r['cmax'], r['npts'], extra))


if __name__ == '__main__':
    main()
