"""Shared helpers for the tables, figures and export (the A4 scoring conventions of scratch/score_P1_v2.py):
point rate = trained prior's held-out rate; point nMSE = plain decoder (local), better of plain and refined on the
refinement subset (unrestricted/output, where refinement ran); R(eps) by linear interpolation in nMSE (time-sharing)."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vra  # noqa: E402

LAYERS = {'arc': [0, 2, 4, 8, 12, 16, 20, 24, 28, 31], 'nd': [0, 8, 16, 32, 64, 128, 192, 255]}
LOUT = {'arc': 32, 'nd': 256}
SEEDS = {'arc': [4000, 4001, 4002, 4003], 'nd': [203, 216, 217, 220, 221, 223]}


def point_curve(d):
    out = []
    unr = d['cls'] in ('unres', 'out')
    for c in d['curve']:
        nm = c['nmse']
        if unr and c.get('nmse_refined') is not None and c.get('nmse_plain_on_refset') is not None:
            nm = min(c['nmse_plain_on_refset'], c['nmse_refined'])
        out.append(dict(t=c['t'], rate=c['rate'], nmse=nm))
    return out


def R_adj(curve, eps):
    """the A4 rule: linear interpolation in nMSE between adjacent Pareto points (kept for comparison)."""
    env = vra.envelope(curve)
    for i, (r, dd) in enumerate(env):
        if dd <= eps:
            if i == 0:
                return r
            r0, d0 = env[i - 1]
            return r0 + (d0 - eps) / (d0 - dd) * (r - r0)
    return None


def hull(curve):
    """lower convex hull of a run's evaluated (nMSE, rate) points: every point reachable by time-sharing two codes
    (PREREG A20). Returns [(D, R)] sorted by D ascending."""
    pts = sorted({(float(c['nmse']), float(c['rate'])) for c in curve
                  if c.get('rate') is not None and c['nmse'] > 0 and math.isfinite(c['nmse'])})
    h = []
    for p in pts:
        while len(h) >= 2:
            (x1, y1), (x2, y2) = h[-2], h[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0:   # h[-1] is not below the chord: drop it
                h.pop()
            else:
                break
        h.append(p)
    # keep the decreasing part (lower-left boundary): rate falls as nMSE grows
    out = [h[0]]
    for p in h[1:]:
        if p[1] < out[-1][1]:
            out.append(p)
    return out


def R_lin(curve, eps):
    """bits needed for nMSE eps by time-sharing the run's evaluated codes: the lower convex hull (PREREG A20; the
    name is kept for the callers). None if no code reaches eps."""
    h = hull(curve)
    if not h or eps < h[0][0]:
        return None
    for (d0, r0), (d1, r1) in zip(h, h[1:]):
        if d0 <= eps <= d1:
            return r0 + (eps - d0) / (d1 - d0) * (r1 - r0) if d1 > d0 else min(r0, r1)
    return h[-1][1]


def load(base='runs'):
    runs, refs = vra.load_p1(base)
    for d in runs:
        d['pc'] = point_curve(d)
    idx = {}
    for d in runs:
        idx.setdefault((vra.fam_tag(d), d['seed'], d['layer'], d['cls'], d['variant']), []).append(d)
    return runs, refs, idx


def base_runs(idx, fam, seed, l, cls, restarts=(0, 1)):
    return [r for r in idx.get((fam, seed, l, cls, 'base'), []) if r.get('restart') in restarts]


def cellR(rs, eps):
    """mean, min, max over runs of R_lin(eps); None if no runs; inf if any run does not reach eps."""
    if not rs:
        return None
    v = [R_lin(r['pc'], eps) for r in rs]
    if any(x is None for x in v):
        return dict(mean=math.inf, min=min([x for x in v if x is not None], default=math.inf), max=math.inf, n=len(v))
    return dict(mean=float(np.mean(v)), min=min(v), max=max(v), n=len(v))


def ref_R(ref, kind, eps):
    return R_lin(ref['refs'][kind]['curve'], eps) if ref is not None else None


def slope(rmean_hi, rmean_lo, e_hi, e_lo):
    if rmean_hi is None or rmean_lo is None or not math.isfinite(rmean_hi) or not math.isfinite(rmean_lo):
        return None
    return 2 * (rmean_lo - rmean_hi) / math.log2(e_hi / e_lo)
