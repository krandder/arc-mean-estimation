"""bit-accounting-arc analysis: curves R(eps), slopes, restart error bars and the certificate statistics.
Pure numpy; reads the JSONs written by gpu_src/scripts/run_vr.py and ref_curve.py.

Conventions:
- A curve is a list of evaluation points (t, rate, nmse, ...). R(eps) = the rate at which the monotone lower envelope
  of (rate, nMSE) first reaches nMSE eps (log-linear interpolation between envelope points; None if not reached).
- Slope s(eps) = bits per halving of the output RMS error = 2 dR / dlog2(1/eps), by finite differences between
  adjacent eps on EPS; reported at the geometric midpoints.
- Gaussian bound R_G(eps) = reverse water-filling over eig Cov(a) at distortion eps V.
"""
import glob
import json
import math
import os

import numpy as np

EPS = [0.5, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.003, 0.002, 0.001]
EPS_CORE = [0.1, 0.03, 0.01, 0.003, 0.001]


def envelope(curve, rkey='rate'):
    pts = sorted([(float(c[rkey]), float(c['nmse'])) for c in curve if c.get(rkey) is not None and c['nmse'] > 0])
    env, best = [], float('inf')
    for r, d in pts:
        if d < best:
            env.append((r, d))
            best = d
    return env


def R_at(curve, eps, rkey='rate'):
    env = envelope(curve, rkey)
    for i, (r, d) in enumerate(env):
        if d <= eps:
            if i == 0:
                return r
            r0, d0 = env[i - 1]
            f = (math.log(d0) - math.log(eps)) / (math.log(d0) - math.log(d))
            return r0 + f * (r - r0)
    return None


def D_at(curve, rate, rkey='rate'):
    """nMSE of the envelope at a given rate (log-linear interpolation); None outside the curve's rate range."""
    env = envelope(curve, rkey)
    if not env or rate < env[0][0] or rate > env[-1][0]:
        return None
    for i in range(1, len(env)):
        r0, d0 = env[i - 1]
        r1, d1 = env[i]
        if r0 <= rate <= r1:
            f = (rate - r0) / max(r1 - r0, 1e-12)
            return math.exp(math.log(d0) + f * (math.log(d1) - math.log(d0)))
    return env[-1][1]


def R_curve(curve, rkey='rate', eps_list=EPS):
    return [R_at(curve, e, rkey) for e in eps_list]


def slopes(Rs, eps_list=EPS):
    """[(eps_mid, slope)] between adjacent reached eps."""
    out = []
    for i in range(len(eps_list) - 1):
        a, b = Rs[i], Rs[i + 1]
        if a is None or b is None:
            out.append((math.sqrt(eps_list[i] * eps_list[i + 1]), None))
            continue
        out.append((math.sqrt(eps_list[i] * eps_list[i + 1]), 2.0 * (b - a) / math.log2(eps_list[i] / eps_list[i + 1])))
    return out


def rwf_rate(lam, D):
    lam = np.sort(np.maximum(np.asarray(lam, float), 0.0))[::-1]
    if D <= 0:
        return float('inf')
    if D >= lam.sum():
        return 0.0
    lo, hi = 0.0, lam[0]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if np.minimum(lam, mid).sum() > D:
            hi = mid
        else:
            lo = mid
    th = 0.5 * (lo + hi)
    k = lam > th
    return float(0.5 * np.log2(lam[k] / th).sum())


def gauss_bound(out_evals, V, eps):
    return rwf_rate(out_evals, eps * V)


def load_runs(root):
    """All VR_*.json under root (recursively) -> list of dicts (with 'path')."""
    out = []
    for p in glob.glob(os.path.join(root, '**', 'VR_*.json'), recursive=True):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        d['path'] = p
        out.append(d)
    return out


def load_refs(root):
    out = {}
    for p in glob.glob(os.path.join(root, '**', 'REF_*.json'), recursive=True):
        d = json.load(open(p))
        out[(d['family'] if d['family'] != 'toy' else f"toy{d['toy_k']}", d['seed'], d['layer'])] = d
    return out


def fam_tag(d):
    return d['family'] if d['family'] != 'toy' else f"toy{d['toy_k']}"


def index(runs):
    """(fam, seed, layer, cls, variant) -> list of runs (restarts or fixed lambdas)."""
    idx = {}
    for d in runs:
        idx.setdefault((fam_tag(d), d['seed'], d['layer'], d['cls'], d['variant']), []).append(d)
    return idx


def cell_stats(runs, rkey='rate', eps_list=EPS):
    """Per eps: mean, sd, min, max over runs of R(eps); n_reached. Unreached counts as None (excluded) and reported."""
    Rs = [R_curve(d['curve'], rkey, eps_list) for d in runs]
    out = []
    for i, e in enumerate(eps_list):
        v = [r[i] for r in Rs if r[i] is not None]
        out.append(dict(eps=e, n=len(v), n_runs=len(Rs), mean=(float(np.mean(v)) if v else None),
                        sd=(float(np.std(v, ddof=1)) if len(v) > 1 else None), min=(min(v) if v else None),
                        max=(max(v) if v else None)))
    return out


def ref_best_R(ref, eps, rkey='rate'):
    """Best (lowest) realised reference rate over the two clouds at nMSE eps."""
    vals = [R_at(r['curve'], eps, rkey) for r in ref['refs'].values()]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def load_p1(base='runs', common_norm=True):
    """Evaluation outputs pulled from every VM: base/bitarc-*/P1/VR_*.json (not recursive: excludes superseded and dev
    runs) and base/bitarc-*/P1/REF/REF_*.json; a name seen twice keeps the newest file. Returns (runs, refs)."""
    def newest(pattern):
        best = {}
        for p in glob.glob(os.path.join(base, pattern)):
            k = os.path.basename(p)
            if k not in best or os.path.getmtime(p) > os.path.getmtime(best[k]):
                best[k] = p
        return sorted(best.values())
    runs = []
    for p in newest('bitarc-*/P1/VR_*.json'):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        d['path'] = p
        runs.append(d)
    refs = {}
    for p in newest('bitarc-*/P1/REF/REF_*.json'):
        d = json.load(open(p))
        refs[(d['family'] if d['family'] != 'toy' else f"toy{d['toy_k']}", d['seed'], d['layer'])] = d
    if common_norm and os.environ.get('BITARC_NO_NORM') != '1':     # BITARC_NO_NORM=1 reproduces the pre-A20 scoring
        normalise(runs, refs)
    return runs, refs


NMSE_KEYS = ('nmse', 'nmse_plain_on_refset', 'nmse_refined', 'nmse_head', 'nmse_plain', 'mean_err', 'mean_floor')


def normalise(runs, refs):
    """PREREG A20: every run's distortions were divided by its own layer's pilot estimate of the output variance (one
    sample per layer). Rescale them to one variance per net, V_net = the mean of the net's per-layer pilot estimates
    (runs and references), so that equal nMSE means equal distortion across layers. In place; idempotent."""
    per = {}
    for d in list(runs) + list(refs.values()):
        if d.get('V') is None:
            continue
        per.setdefault((fam_tag(d), d['seed']), {})[d['layer']] = float(d['V'])
    vnet = {k: sum(v.values()) / len(v) for k, v in per.items()}
    for d in list(runs) + list(refs.values()):
        if d.get('V') is None or d.get('_normalised'):
            continue
        f = float(d['V']) / vnet[(fam_tag(d), d['seed'])]
        curves = [d.get('curve', [])]
        if 'refs' in d:
            curves += [r.get('curve', []) for r in d['refs'].values()]
        for cv in curves:
            for c in cv:
                for k in NMSE_KEYS:
                    if isinstance(c.get(k), (int, float)):
                        c[k] = c[k] * f
                    elif isinstance(c.get(k), dict):
                        c[k] = {kk: (vv * f if isinstance(vv, (int, float)) else vv) for kk, vv in c[k].items()}
        d['V_net'] = vnet[(fam_tag(d), d['seed'])]
        d['nmse_scale'] = f
        d['_normalised'] = True
