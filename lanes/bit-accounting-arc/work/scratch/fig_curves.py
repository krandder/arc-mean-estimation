"""Figures: (1) per-layer bits-vs-accuracy curves of one net (local, unrestricted, the output's own curve, the analytic
'gram' reference; every restart drawn); (2) bits needed vs layer at three accuracies (median over nets, min-max band);
(3) slope (bits per halving of the output RMS error) vs accuracy per layer.
usage: fig_curves.py <runs root> <figs dir> [family] [seed]
"""
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402
import vrb  # noqa: E402

RUNS, FIGS = sys.argv[1], sys.argv[2]
FAMS = [sys.argv[3]] if len(sys.argv) > 3 else ['arc', 'nd']
LAYERS = {'arc': [0, 2, 4, 8, 12, 16, 20, 24, 28, 31], 'nd': [0, 8, 16, 32, 64, 128, 192, 255]}
LOUT = {'arc': 32, 'nd': 256}
SEEDS = {'arc': [4000, 4001, 4002, 4003], 'nd': [203, 216, 217, 220, 221, 223]}
C_LOCAL, C_UNRES, C_OUT, C_REF, C_H1 = '#2a78d6', '#eb6834', '#0b0b0b', '#8a8984', '#7a4fc9'
os.makedirs(FIGS, exist_ok=True)


runs, refs, idx = vrb.load(RUNS)
for d in runs:
    d['bcurve'] = d['pc']


def env_xy(curve):
    e = vra.envelope(curve)
    return [p[1] for p in e], [max(p[0], 0.05) for p in e]


for fam in FAMS:
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else SEEDS[fam][0]
    Ls = LAYERS[fam]
    ncol = 5
    nrow = math.ceil(len(Ls) / ncol)
    fig, axs = plt.subplots(nrow, ncol, figsize=(3.2 * ncol, 2.9 * nrow), sharex=True, sharey=True)
    axs = np.atleast_1d(axs).ravel()
    out_rs = vrb.base_runs(idx, fam, seed, LOUT[fam], 'out', restarts=(0, 1, 2))
    for i, l in enumerate(Ls):
        ax = axs[i]
        for r in out_rs:
            x, y = env_xy(r['bcurve'])
            ax.plot(x, y, color=C_OUT, lw=1.0, ls=':', label='output' if r is out_rs[0] else None)
        rf = refs.get((fam, seed, l))
        if rf is not None:
            x, y = env_xy(rf['refs']['gram']['curve'])
            ax.plot(x, y, color=C_REF, lw=1.0, label='linear reference')
        for cls, col, ls in (('local', C_LOCAL, '-'), ('unres', C_UNRES, '--')):
            rs = vrb.base_runs(idx, fam, seed, l, cls, restarts=(0, 1, 2))
            for j, r in enumerate(rs):
                x, y = env_xy(r['bcurve'])
                ax.plot(x, y, color=col, lw=1.4, ls=ls, label=(cls if j == 0 else None))
        for j, r in enumerate(idx.get((fam, seed, l, 'local', 'h1'), [])):
            x, y = env_xy(r['bcurve'])
            ax.plot(x, y, color=C_H1, lw=1.2, ls='-.', label=('local, look-ahead start' if j == 0 else None))
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim(1.0, 1e-3)
        ax.set_title(f'layer {l}', fontsize=9)
        ax.grid(True, which='major', color='#e5e4e0', lw=0.6)
        if i % ncol == 0:
            ax.set_ylabel('bits')
        if i >= (nrow - 1) * ncol:
            ax.set_xlabel('output nMSE')
    for j in range(len(Ls), len(axs)):
        axs[j].axis('off')
    axs[0].legend(fontsize=7, frameon=False)
    fig.suptitle(f'{fam} net {seed}: bits needed for each accuracy, per layer', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f'curves_{fam}_s{seed}.png'), dpi=130)
    plt.close(fig)

    # profile: bits vs layer at three accuracies
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    for k, eps in enumerate((0.1, 0.01, 0.001)):
        ax = axs[k]
        for cls, col, ls in (('local', C_LOCAL, '-'), ('unres', C_UNRES, '--')):
            med, lo, hi, xs = [], [], [], []
            per_net = {s: ([], []) for s in SEEDS[fam]}
            for l in Ls:
                vals = []
                for s in SEEDS[fam]:
                    rs = vrb.base_runs(idx, fam, s, l, cls)
                    v = [vrb.R_lin(r['bcurve'], eps) for r in rs]
                    cand = [float(np.mean(v))] if rs and all(x is not None for x in v) else []
                    if cls == 'local':   # the class count: the better of the two starts
                        hv = [vrb.R_lin(r['bcurve'], eps) for r in idx.get((fam, s, l, 'local', 'h1'), [])]
                        cand += [x for x in hv if x is not None]
                    if cand:
                        vals.append(min(cand))
                        per_net[s][0].append(l)
                        per_net[s][1].append(min(cand))
                if len(vals) == len(SEEDS[fam]):   # the median only where every net has the cell
                    xs.append(l)
                    med.append(np.median(vals))
                    lo.append(min(vals))
                    hi.append(max(vals))
            for j, (s, (lx, ly)) in enumerate(per_net.items()):
                if lx:
                    ax.plot(lx, ly, color=col, ls=ls, lw=0.6, alpha=0.45, marker='.', ms=2,
                            label=(f'{cls}: each net' if j == 0 and k == 0 else None))
            if xs:
                ax.plot(xs, med, color=col, ls=ls, marker='o', ms=3.5, lw=1.6,
                        label=('local (better start): median over nets' if cls == 'local' else 'unres: median'))
        vals = []
        for s in SEEDS[fam]:
            rs = vrb.base_runs(idx, fam, s, LOUT[fam], 'out')
            v = [vrb.R_lin(r['bcurve'], eps) for r in rs]
            if rs and all(x is not None for x in v):
                vals.append(float(np.mean(v)))
        if vals:
            ax.axhline(np.median(vals), color=C_OUT, ls=':', lw=1.0, label='output cell (median)')
        ax.set_yscale('log')
        ax.set_title(f'nMSE {eps}', fontsize=9)
        ax.set_xlabel('layer')
        ax.grid(True, color='#e5e4e0', lw=0.6)
    axs[0].set_ylabel('bits')
    axs[0].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f'profile_{fam}.png'), dpi=130)
    plt.close(fig)

    # slopes vs accuracy
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    cmap = plt.get_cmap('Blues')
    for k, cls in enumerate(('local', 'unres')):
        ax = axs[k]
        for i, l in enumerate(Ls):
            rs = vrb.base_runs(idx, fam, seed, l, cls, restarts=(0, 1, 2))
            hs = idx.get((fam, seed, l, 'local', 'h1'), []) if cls == 'local' else []
            if not rs and not hs:
                continue

            def Rmat(rr):
                return np.array([[np.nan if vrb.R_lin(r['bcurve'], e) is None else vrb.R_lin(r['bcurve'], e)
                                  for e in vra.EPS] for r in rr]).mean(0)
            Rs = Rmat(rs) if rs else None
            if hs:   # the class curve: the better of the two starts at each accuracy
                Rh = Rmat(hs)
                Rs = Rh if Rs is None else np.fmin(Rs, Rh)
            sl = vra.slopes(list(Rs))
            xs = [e for e, s in sl if s is not None and np.isfinite(s)]
            ys = [s for e, s in sl if s is not None and np.isfinite(s)]
            ax.plot(xs, ys, color=cmap(0.3 + 0.7 * i / max(1, len(Ls) - 1)), lw=1.3, marker='o', ms=2.5,
                    label=f'l={l}')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim(0.5, 1e-3)
        ax.set_title(f"{'local (better start)' if cls == 'local' else cls}: bits per halving of output RMS error", fontsize=9)
        ax.set_xlabel('output nMSE')
        ax.grid(True, color='#e5e4e0', lw=0.6)
    axs[0].set_ylabel('slope (bits)')
    axs[0].legend(fontsize=6, frameon=False, ncol=2)
    axs[1].legend(fontsize=6, frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f'slopes_{fam}_s{seed}.png'), dpi=130)
    plt.close(fig)
print('figures in', FIGS)
