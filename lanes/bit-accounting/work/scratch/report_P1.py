"""Phase-1 figures and summary tables from runs/P1/P_*.json (run from the work dir; after score_P1.py).
figs/P1_curves_<net>.png: best bits-vs-error curve per layer (Pareto front over the class's codes), local and unres.
results/P1_summary.md: R*(0.1) and R*(0.01) by layer (median and range over seeds) and the slopes (bits per halving).
"""
import glob
import json
import math
import os

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

RUNS = 'runs/P1'
cells = {}
for p in sorted(glob.glob(f'{RUNS}/P_*.json')):
    d = json.load(open(p))
    cells[(d['netkind'], d['n'], d['L'], d['seed'], d['l'], d['cls'])] = d
sc = json.load(open('results/P1_scores.json'))['cells'] if os.path.exists('results/P1_scores.json') else {}


def front(d):
    """Pareto front (rate up, nMSE down) over all curves of the class (wide only for unres), incl. refitted rates."""
    pts = []
    for g in d['groups'].values():
        for name, cv in g['curves'].items():
            if name == 'wide' and d['cls'] == 'local':
                continue
            pts += [(r, e) for r, e in zip(cv['rate'], cv['nmse']) if np.isfinite(r) and np.isfinite(e)]
    if 'refit' in d:
        rb = [min(x['rate_trained_B'], x['rate_refit_mix8'], x['rate_refit_fullgauss']) for x in d['refit']]
        pts += [(r, e) for r, e in zip(rb, d['groups']['G1']['curves']['r0']['nmse']) if np.isfinite(r) and np.isfinite(e)]
    xp = f"runs/P1X/X_{d['netkind']}_n{d['n']}_L{d['L']}_s{d['seed']}_l{d['l']}_{d['cls']}.json"
    if os.path.exists(xp):                       # amendment P1-A: explorer and wide-decoder codes of the class
        x = json.load(open(xp))
        for cv in list(x.get('explorer', {}).values()) + ([x['wdec']] if 'wdec' in x else []):
            pts += [(r, e) for r, e in zip(cv['rate'], cv['nmse']) if np.isfinite(r) and np.isfinite(e)]
    pts.sort()
    out, best = [], float('inf')
    for r, e in pts:
        if e < best:
            out.append((max(r, 0.0), e))
            best = e
    return out


os.makedirs('figs', exist_ok=True)
nets = sorted({k[:4] for k in cells})
for (kind, n, L, s) in nets:
    if s != min(x[3] for x in nets if x[:3] == (kind, n, L)):
        continue
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    layers = sorted({k[4] for k in cells if k[:4] == (kind, n, L, s)})
    cmap = plt.get_cmap('viridis')
    for j, cls in enumerate(['local', 'unres']):
        for i, l in enumerate(layers):
            d = cells.get((kind, n, L, s, l, 'unres' if l == L else cls))
            if d is None:
                continue
            f = front(d)
            ax[j].plot([e for r, e in f], [r for r, e in f], '-', color=('k' if l == L else cmap(i / max(1, len(layers) - 1))),
                       lw=(2 if l == L else 1.3), label=('output' if l == L else f'l = {l}'))
        ax[j].set_xscale('log')
        ax[j].invert_xaxis()
        ax[j].set_xlabel('output nMSE (held out)')
        ax[j].set_title(f'{kind} {n}x{L} seed {s}: {cls} encoder')
        ax[j].grid(alpha=0.3)
    ax[0].set_ylabel('bits (information rate)')
    ax[0].legend(fontsize=7)
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f'figs/P1_curves_{kind}_{n}x{L}.png', dpi=120)
    plt.close(fig)

lines = ['# Phase 1 summary: bits needed per layer (median over seeds, [min, max]); slope = bits per halving of the '
         'output error between D = 0.1 and 0.01 (median)', '',
         '| net | l | class | R*(0.1) | R*(0.01) | R*(0.001) | slope 0.1->0.01 | seeds | flagged cells |', '|' + '---|' * 9]


def agg(v):
    v2 = [x for x in v if x is not None]
    if not v2:
        return 'unreached'
    s = f'{np.median(v2):.1f}'
    if len(v2) > 1:
        s += f' [{min(v2):.1f}, {max(v2):.1f}]'
    if len(v2) < len(v):
        s += f' ({len(v) - len(v2)} unreached)'
    return s


for (kind, n, L) in sorted({k[:3] for k in cells}, key=lambda x: (x[0] != 'relu', x)):
    layers = sorted({k[4] for k in cells if k[:3] == (kind, n, L)})
    for l in layers:
        for cls in (['unres'] if l == L else ['local', 'unres']):
            keys = [k for k in cells if k[:3] == (kind, n, L) and k[4] == l and k[5] == cls]
            if not keys:
                continue
            Rs = [sc.get('_'.join(map(str, k)), {}).get('R', {}) for k in keys]
            sl = []
            for R in Rs:
                a, b = R.get('0.1'), R.get('0.01')
                if a is not None and b is not None:
                    sl.append((b - a) / math.log2(10))
            fl = sum(1 for k in keys if sc.get('_'.join(map(str, k)), {}).get('flags'))
            lines.append(f'| {kind} {n}x{L} | {"out" if l == L else l} | {cls} | {agg([R.get("0.1") for R in Rs])} | '
                         f'{agg([R.get("0.01") for R in Rs])} | {agg([R.get("0.001") for R in Rs])} | '
                         f'{(f"{np.median(sl):.2f}" if sl else "-")} | {len(keys)} | {fl} |')
open('results/P1_summary.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
