"""What sets a layer's bits: the future-weighted spectrum. For each net and layer, the eigenvalues lam_i of the whitened
future Gram G = E[J^T J] (J = da/dh_l, whitened h_l; saved by ref_curve.py as refs['gram']['lam']) relative to the output
variance V: tr G / V, its participation ratio, the number of eigenvalues above the water level at nMSE eps, and the
closed-form reverse water-filling rate R_wf(eps) = sum_i max(0, 1/2 log2(lam_i / theta)) with sum_i min(lam_i, theta) =
eps V (a linear-Gaussian prediction, no net evaluation); beside it the realised reference rate (the same code run
through the net) and the learned local count (better of the two starts). Also a figure of the spectra.
usage: spectrum_table.py <runs base> <out md> <figs dir>
"""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, OUT, FIGS = sys.argv[1], sys.argv[2], sys.argv[3]
runs, refs, idx = vrb.load(BASE)


def wf(lam, D):
    lo, hi = 0.0, float(lam.max())
    for _ in range(200):
        th = (lo + hi) / 2
        if np.minimum(lam, th).sum() > D:
            hi = th
        else:
            lo = th
    th = (lo + hi) / 2
    act = lam > th
    return float(0.5 * np.log2(lam[act] / th).sum()), int(act.sum())


def best_local(fam, s, l, e):
    cand = []
    c = vrb.cellR(vrb.base_runs(idx, fam, s, l, 'local'), e)
    if c and math.isfinite(c['mean']):
        cand.append(c['mean'])
    h = vrb.cellR(idx.get((fam, s, l, 'local', 'h1'), []), e)
    if h and math.isfinite(h['mean']):
        cand.append(h['mean'])
    return min(cand) if cand else None


def f(x):
    return '-' if x is None else ('%.0f' % x if x >= 20 else '%.1f' % x)


L = []
spectra = {}
for fam in ('arc', 'nd'):
    L.append(f'\n### {fam}: the future-weighted spectrum and the bits (per net; nMSE 0.1 / 0.01)\n')
    L.append('| net | layer | tr G / V | participation ratio | directions above the water level | closed-form water-filling | '
             'realised reference | learned local (better start) | learned / closed-form |')
    L.append('|---|---|---|---|---|---|---|---|---|')
    for s in vrb.SEEDS[fam]:
        for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
            rf = refs.get((fam, s, l))
            if rf is None:
                continue
            lam = np.maximum(np.array(rf['refs']['gram']['lam'], dtype=float), 0.0)
            V = rf['V']
            spectra[(fam, s, l)] = lam / V
            Vn = rf.get('V_net', V)          # A20: distortion budget in the common normalisation
            tr = lam.sum()
            pr = tr ** 2 / max((lam ** 2).sum(), 1e-300)
            w1, k1 = wf(lam, 0.1 * Vn)
            w2, k2 = wf(lam, 0.01 * Vn)
            rr = [vrb.ref_R(rf, 'gram', e) for e in (0.1, 0.01)]
            if l < vrb.LOUT[fam]:
                ll = [best_local(fam, s, l, e) for e in (0.1, 0.01)]
            else:
                ll = [None, None]
            ratio = ' / '.join('-' if (a is None) else '%.2f' % (a / b) for a, b in zip(ll, (w1, w2)))
            L.append(f'| {s} | {l if l < vrb.LOUT[fam] else "output"} | {tr / V:.2f} | {pr:.1f} | {k1} / {k2} | '
                     f'{f(w1)} / {f(w2)} | {f(rr[0])} / {f(rr[1])} | {f(ll[0])} / {f(ll[1])} | {ratio} |')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))

import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
for fam, seed in (('arc', 4000), ('nd', 203)):
    Ls = vrb.LAYERS[fam]
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    cmap = plt.get_cmap('viridis')
    for i, l in enumerate(Ls + [vrb.LOUT[fam]]):
        sp = spectra.get((fam, seed, l))
        if sp is None:
            continue
        sp = np.sort(sp)[::-1]
        sp = sp[sp > 1e-12]
        ax.plot(np.arange(1, len(sp) + 1), sp, color=cmap(i / max(1, len(Ls))), lw=1.3,
                label=(f'layer {l}' if l < vrb.LOUT[fam] else 'output'))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('direction (sorted)')
    ax.set_ylabel('eigenvalue of whitened E[J^T J] / output variance')
    ax.set_title(f'{fam} net {seed}: how much the output depends on each direction of the layer', fontsize=9)
    ax.grid(True, color='#e5e4e0', lw=0.6)
    ax.legend(fontsize=6, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f'spectra_{fam}_s{seed}.png'), dpi=130)
    plt.close(fig)
