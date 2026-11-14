"""Figure for the convergence subset (A18/A19): ARC net 4000, layers 0, 16, 31, local and unrestricted; bits needed for
nMSE 0.1 and 0.01 against training steps, one line per start and depth (every run of the cell), so a line that is
still falling at its last doubling is not converged.
usage: fig_conv.py <runs base> <figs dir>
"""
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vrb  # noqa: E402

BASE, FIGS = sys.argv[1], sys.argv[2]
runs, refs, idx = vrb.load(BASE)
SEED = 4000
SPEC = {'base': ('reference/output start', 3, 12), 'steps2': ('reference/output start', 3, 24),
        'steps4': ('reference/output start', 3, 48), 'steps8': ('reference/output start', 3, 96),
        'cap2': ('reference/output start, depth 6', 6, 12), 'cap2steps4': ('reference/output start, depth 6', 6, 48),
        'cap2steps8': ('reference/output start, depth 6', 6, 96), 'cap4steps4': ('reference start, depth 12', 12, 48),
        'h1': ('look-ahead start', 3, 12), 'h1s2': ('look-ahead start', 3, 24), 'h1s4': ('look-ahead start', 3, 48),
        'h1s8': ('look-ahead start', 3, 96), 'h1c2': ('look-ahead start, depth 6', 6, 12),
        'bwd': ('backward curriculum', 3, 12), 'bwds2': ('backward curriculum', 3, 24),
        'wide2steps2': ('output start, width 2048', 3, 24)}
COL = {'reference/output start': '#2a78d6', 'reference/output start, depth 6': '#0b4a8f',
       'reference start, depth 12': '#06264a', 'look-ahead start': '#7a4fc9', 'look-ahead start, depth 6': '#4b2a85',
       'backward curriculum': '#d1495b', 'output start, width 2048': '#eb6834'}
fig, axs = plt.subplots(2, 6, figsize=(17, 5.6), sharex=True)
for ci, (l, cls) in enumerate([(0, 'local'), (16, 'local'), (31, 'local'), (0, 'unres'), (16, 'unres'), (31, 'unres')]):
    for ri, e in enumerate((0.1, 0.01)):
        ax = axs[ri, ci]
        lines = {}
        for v, (lab, d, k) in SPEC.items():
            rs = vrb.base_runs(idx, 'arc', SEED, l, cls) if v == 'base' else idx.get(('arc', SEED, l, cls, v), [])
            if not rs:
                continue
            x = [vrb.R_lin(r['pc'], e) for r in rs]
            if any(y is None for y in x):
                continue
            lines.setdefault(lab, []).append((k, sum(x) / len(x)))
        if not lines:
            ax.text(0.5, 0.5, 'not reached', transform=ax.transAxes, ha='center', va='center', fontsize=8,
                    color='#8a8984')
        best = min((p[1] for pts in lines.values() for p in pts), default=None)
        for lab, pts in lines.items():
            pts.sort()
            ax.plot([p[0] for p in pts], [100 * (p[1] / best - 1) for p in pts], marker='o', ms=3.5, lw=1.4,
                    color=COL.get(lab, '#8a8984'), label=lab)
        if best is not None:
            ax.axhline(3, color='#8a8984', lw=0.8, ls=':')
            ax.text(0.98, 0.95, f'lowest {best:.0f} bits' if best >= 20 else f'lowest {best:.1f} bits',
                    transform=ax.transAxes, ha='right', va='top', fontsize=7)
        ax.set_xscale('log', base=2)
        ax.set_xticks([12, 24, 48, 96])
        ax.set_xticklabels(['12k', '24k', '48k', '96k'])
        ax.grid(True, color='#e5e4e0', lw=0.6)
        ax.set_title(f'layer {l} {cls}, nMSE {e}', fontsize=8)
        if ci == 0:
            ax.set_ylabel('% above the lowest found')
        if ri == 1:
            ax.set_xlabel('training steps')
handles, labels = [], []
for ax in axs.ravel():
    for h, lb in zip(*ax.get_legend_handles_labels()):
        if lb not in labels:
            handles.append(h)
            labels.append(lb)
fig.legend(handles, labels, loc='lower center', ncol=4, fontsize=8, frameon=False)
fig.suptitle('ARC net 4000: bits needed vs training steps, per start and capacity, in % above the lowest count found '
             '(dotted: 3%; a line still falling has not converged)',
             fontsize=10)
fig.tight_layout(rect=(0, 0.07, 1, 0.96))
fig.savefig(os.path.join(FIGS, 'convergence_arc_s4000.png'), dpi=130)
print('wrote', os.path.join(FIGS, 'convergence_arc_s4000.png'))
