"""Side-effect-free helpers for the POST HOC scripts (GPT-6 review round 2, finding 2). Importing score_part1 re-runs the
hashed scorer, which rewrites results/score_part1.json; the post hoc scripts import these copies instead. The functions
are copied unchanged from scratch/score_part1.py (lines 11-44 and rec_b2), so the numbers are the same."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, '..', 'runs'); RES = os.path.join(HERE, '..', 'results')
AU_RUNS = '/home/agent/workspaces/mats/work/arc-update/runs'
CONF = [(64, 8, list(range(300, 308))), (128, 16, list(range(300, 308))), (256, 32, list(range(200, 205)))]
# truth floors (PREREG: values below 10x the truth's nMSE floor are not used in ratios)
FLOOR = {64: 6e-8, 128: 6e-8, 256: 1.5e-8}


def load(kind, n, L, s):
    p = os.path.join(RUNS, f'{kind}_n{n}_L{L}_s{s}.json')
    return json.load(open(p)) if os.path.exists(p) else None


def rqmc_curve(n, L, s):
    d = json.load(open(os.path.join(AU_RUNS, f'rqmc_n{n}_L{L}_s{s}.json')))
    return np.array([r['N'] for r in d['rows']], float), np.array([r['mean_nmse'] for r in d['rows']], float)


def rqmc_err(curve, C):
    N, e = curve
    if C <= N[0]:
        return float(e[0] * N[0] / C), True
    if C >= N[-1]:
        return float(e[-1] * N[-1] / C), True
    return float(np.exp(np.interp(np.log(C), np.log(N), np.log(e)))), False


def rqmc_cost(curve, err):
    N, e = curve
    if err >= e[0]:
        return float(N[0] * e[0] / err)
    if err <= e[-1]:
        return float(N[-1] * e[-1] / err)
    return float(np.exp(np.interp(np.log(err), np.log(e[::-1]), np.log(N[::-1]))))


def med(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.median(x)) if x else float('nan')


def rec_b2(d, v):
    """The hashed scorer's FLOORED recursion statistic max(b2, noise, 1e-7) (not the raw b2)."""
    r = d['variants'].get(v)
    if r is None or 'b2' not in r:
        return None
    return max(r['b2'], r.get('noise', 0.0), 1e-7)


def raw_b2(d, v):
    """The raw recursion b2 (no floor), as the PREREG wording reads."""
    r = d['variants'].get(v)
    return None if r is None or 'b2' not in r else r['b2']
