"""Exactly solvable illustration of the gap (FORMAL Props 2-3) and of partition vs analog codes.
h ~ N(0, 1); next code c = Q(h + sigma xi), Q a uniform K-level quantiser on [-2, 2]; target T = I(h; c) (quadrature).
(a) Optimal K'-cell partitions of h for c (contiguous intervals; dynamic programming on a 2001-point quadrature grid):
    rate H(c') and relevance I(c'; c), K' = 1..48.
(b) Linear Gaussian-channel codes z = a h + nu, nu ~ N(0, 1): rate I(h; z) = (1/2) log2(1 + a^2), relevance I(z; c) by
    quadrature (h | z ~ N(a z / (1 + a^2), 1 / (1 + a^2))).
Writes results/exact_1d.json and figs/exact_1d.png.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.special import ndtr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..')
K, SIG = 16, 0.3


def post(h):
    t = np.concatenate([[-np.inf], np.linspace(-2, 2, K + 1)[1:-1], [np.inf]])
    return np.clip(np.diff(ndtr((t[None, :] - h[:, None]) / SIG), axis=1), 0, 1)


def H(p):
    return -(p * np.log2(np.clip(p, 1e-300, 1))).sum(-1)


x = np.linspace(-6, 6, 2001)
w = np.exp(-x ** 2 / 2)
w /= w.sum()
P = post(x)
pc = (w[:, None] * P).sum(0)
T = float(H(pc[None])[0] - (w * H(P)).sum())

# (a) DP over contiguous intervals: minimal weighted KL loss for each number of cells
N = len(x)
cs = np.vstack([np.zeros((1, K)), np.cumsum(w[:, None] * P, 0)])
cw = np.concatenate([[0.0], np.cumsum(w)])
plp = np.concatenate([[0.0], np.cumsum(w * (P * np.log2(np.clip(P, 1e-300, 1))).sum(1))])


def cost(a, b):
    n = cw[b] - cw[a]
    mu = (cs[b][None, :] - cs[a]) / np.maximum(n, 1e-300)[:, None]
    return (plp[b] - plp[a]) - n * (mu * np.log2(np.clip(mu, 1e-300, 1))).sum(1)


KMAX = 48
D = np.full((KMAX + 1, N + 1), np.inf)
arg = np.zeros((KMAX + 1, N + 1), int)
D[0, 0] = 0.0
for k in range(1, KMAX + 1):
    for b in range(1, N + 1):
        a = np.arange(0, b)
        v = D[k - 1, a] + cost(a, b)
        j = int(np.argmin(v))
        D[k, b], arg[k, b] = v[j], j
part = []
for k in range(1, KMAX + 1):
    b, cuts = N, []
    for kk in range(k, 0, -1):
        a = arg[kk, b]
        cuts.append((a, b))
        b = a
    probs = np.array([cw[b_] - cw[a_] for a_, b_ in cuts])
    part.append(dict(cells=k, H=float(H(probs[probs > 0][None])[0]), I=T - float(D[k, N])))

# (b) linear analog codes
analog = []
for a in np.concatenate([np.linspace(0.05, 1, 12), np.linspace(1.2, 12, 30), np.linspace(13, 60, 20)]):
    z = np.linspace(-8, 8, 1601) * math.sqrt(1 + a * a)
    s2 = 1.0 / (1 + a * a)
    pz = np.exp(-z ** 2 / (2 * (1 + a * a)))
    pz /= pz.sum()
    # p(c | z) = E[p(c | h) | z], h | z ~ N(a z s2, s2)
    hh, ww = np.polynomial.hermite_e.hermegauss(60)
    ww = ww / ww.sum()
    pcz = np.zeros((len(z), K))
    for hi, wi in zip(hh, ww):
        pcz += wi * post(a * z * s2 + math.sqrt(s2) * hi)
    rel = float(H(pc[None])[0] - (pz * H(pcz)).sum())
    analog.append(dict(a=float(a), rate=0.5 * math.log2(1 + a * a), I=rel))


def interp(curve, xkey, R):
    pts = sorted((c[xkey], c['I']) for c in curve)
    for (r0, i0), (r1, i1) in zip(pts, pts[1:]):
        if r0 <= R <= r1:
            return i0 + (i1 - i0) * (R - r0) / max(r1 - r0, 1e-12)
    return None


best_part_at_T = max(c['I'] for c in part if c['H'] <= T)
res = dict(K=K, sigma=SIG, T=T, partitions=part, analog=analog, partition_best_at_rate_T=best_part_at_T,
           analog_at_rate_T=interp(analog, 'rate', T),
           partition_rate_for_95=min(c['H'] for c in part if c['I'] >= 0.95 * T),
           analog_rate_for_95=min(c['rate'] for c in analog if c['I'] >= 0.95 * T))
os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)
json.dump(res, open(os.path.join(OUT, 'results', 'exact_1d.json'), 'w'), indent=1)
print(f"T = {T:.4f}; best partition with H <= T carries {best_part_at_T:.4f} ({best_part_at_T / T:.0%}); linear analog "
      f"code at rate T carries {res['analog_at_rate_T']:.4f} ({res['analog_at_rate_T'] / T:.0%}); rate for 95% of T: "
      f"partition {res['partition_rate_for_95']:.3f}, analog {res['analog_rate_for_95']:.3f}")
for c in part[:12] + part[15::8]:
    print(f"  {c['cells']:2d} cells: H {c['H']:.3f} I {c['I']:.4f} shortfall {T - c['I']:.4f}")

if '--fig' in sys.argv:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    ax.plot([c['H'] for c in part], [c['I'] for c in part], 'o-', color='#2a78d6', ms=3.5, lw=1.6,
            label='best partition with k cells (exact)')
    ax.plot([c['rate'] for c in analog], [c['I'] for c in analog], '-', color='#eb6834', lw=1.6,
            label='linear Gaussian channel (exact)')
    hm = max(c['H'] for c in part)
    ax.plot([0, T], [0, T], ':', color='#52514e', lw=1, label='I = rate')
    ax.axhline(T, color='#0b0b0b', lw=1, label=f'target T = {T:.2f} bits')
    ax.axvline(T, color='#0b0b0b', lw=0.8, ls='--')
    ax.set_xlim(0, hm)
    ax.set_xlabel('rate (bits)')
    ax.set_ylabel('bits carried about the next code')
    ax.set_title(f'1-D exact case: h ~ N(0,1), next code = {K}-level quantiser of h + {SIG} xi', fontsize=8.5)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7.5, loc='lower right')
    fig.tight_layout()
    os.makedirs(os.path.join(OUT, 'figs'), exist_ok=True)
    fig.savefig(os.path.join(OUT, 'figs', 'exact_1d.png'), dpi=130)
