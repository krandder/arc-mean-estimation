"""Tables and figures for Part S1 (small nets): counts by class and layer, rate-loss curves.
-> results/S1_table.md, figs/S1_curves_n{n}_L{L}.png, figs/S1_profile.png"""
import json
import os
import sys

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

D = 'runs/S_curves'
CFG = [(16, 4), (32, 8), (16, 16), (32, 32)]
EVAL = [5000, 5001, 5002]
TH = json.load(open('results/theory_small.json')) if os.path.exists('results/theory_small.json') else {}


def grid(L):
    return sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))


sys.path.insert(0, 'gpu_src/lib')
ENV = os.environ.get('ENVELOPE', '1') == '1'


def crossing(rates, y, eps):
    import math
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def get(n, L, s, l, cls):
    p = os.path.join(D, f'S_n{n}_L{L}_s{s}_l{l}_{cls}.json')
    if not os.path.exists(p):
        return None
    r = json.load(open(p))
    for kind, cu in r['curves'].items():
        y = np.minimum.accumulate(np.asarray(cu['nmse'])) if ENV else np.asarray(cu['nmse'])
        cu['env'] = y.tolist()
        cu['cross'] = {e: crossing(cu['rate'], cu['env'], float(e)) for e in ['0.1', '0.01', '0.001']}
    return r


def fmt(vals):
    v = [x for x in vals if x is not None]
    miss = len(vals) - len(v)
    if not vals:
        return '-'
    if not v:
        return '>32'
    srt = sorted([x if x is not None else float('inf') for x in vals])
    k = len(srt)
    mid = srt[(k - 1) // 2: k // 2 + 1]
    s = '>32' if any(np.isinf(mid)) else f'{np.mean(mid):.1f}'
    s += f' [{min(v):.1f}-{max(v):.1f}]' if len(v) > 1 else ''
    if miss:
        s += f' ({miss} >32)'
    return s


lines = ['# Part S1: bits needed at each layer (median [min-max] over evaluation seeds 5000-5002)', '',
         'C = Gaussian-channel capacity (bits), b = sign bits; rates 1..32; ">32" = not reached. RWF = reverse '
         'water-filling over eig Cov(a) (layer-free; attained in output space by the linear analog code).', '']
for n, L in CFG:
    lines.append(f'## {n} x {L}')
    rw = [TH.get(f'n{n}_L{L}_s{s}', {}).get('rwf_out', {}) for s in EVAL]
    lines.append('RWF over Cov(a): C(0.1) = ' + fmt([r.get('0.1') for r in rw]) + ', C(0.01) = ' +
                 fmt([r.get('0.01') for r in rw]))
    lines.append('')
    lines.append('| layer | class | C(0.1) | C(0.01) | b(0.1) | b(0.01) |')
    lines.append('|---|---|---|---|---|---|')
    for l in grid(L) + [L]:
        for cls in (['local', 'linear', 'unres'] if l < L else ['unres']):
            rs = [get(n, L, s, l, cls) for s in EVAL]
            if all(r is None for r in rs):
                continue
            row = [str(l) if l < L else 'out', cls]
            for kind, e in [('gauss', '0.1'), ('gauss', '0.01'), ('bin', '0.1'), ('bin', '0.01')]:
                row.append(fmt([None if r is None else r['curves'][kind]['cross'][e] for r in rs if r is not None]))
            lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
os.makedirs('results', exist_ok=True)
open('results/S1_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

os.makedirs('figs', exist_ok=True)
for n, L in CFG:
    s = 5000
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    for ax, cls in zip(axes, ['unres', 'local', 'linear']):
        cmap = plt.get_cmap('viridis')
        for j, l in enumerate(grid(L) + [L]):
            r = get(n, L, s, l, cls if l < L else 'unres')
            if r is None:
                continue
            col = cmap(j / max(1, len(grid(L))))
            for kind, ls in [('gauss', '-'), ('bin', '--')]:
                cu = r['curves'][kind]
                ax.plot(cu['rate'], np.maximum(cu['nmse'], 1e-5), ls, color=col, marker='o', ms=2.5,
                        label=(f'l={l}' if l < L else 'output') if kind == 'gauss' else None)
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        ax.set_title(f'{n}x{L} seed {s}: {cls} encoder')
        ax.set_xlabel('bits (solid: channel C, dashed: sign bits b)')
        ax.axhline(0.1, color='grey', lw=0.5)
        ax.axhline(0.01, color='grey', lw=0.5)
    axes[0].set_ylabel('nMSE of the output')
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f'figs/S1_curves_n{n}_L{L}.png', dpi=120)
    plt.close(fig)

fig, axes = plt.subplots(1, 4, figsize=(15, 3.6))
for ax, (n, L) in zip(axes, CFG):
    for cls, mk in [('local', 'o-'), ('linear', 's--'), ('unres', '^-')]:
        for s in EVAL:
            xs, ys = [], []
            for l in grid(L):
                r = get(n, L, s, l, cls)
                if r is not None:
                    c = r['curves']['gauss']['cross']['0.1']
                    xs.append(l / L)
                    ys.append(c if c is not None else 40)
            if xs:
                ax.plot(xs, ys, mk, ms=3, alpha=0.7, label=cls if s == EVAL[0] else None,
                        color={'local': 'C0', 'linear': 'C1', 'unres': 'C2'}[cls])
        out = [get(n, L, s, L, 'unres') for s in EVAL]
        co = [o['curves']['gauss']['cross']['0.1'] for o in out if o is not None]
        if co:
            ax.axhline(np.median([c for c in co if c is not None] or [np.nan]), color='k', lw=1, ls=':',
                       label='output space')
    ax.set_title(f'{n} x {L}: C(nMSE 0.1)')
    ax.set_xlabel('l / L')
    ax.set_ylim(0, 42)
axes[0].set_ylabel('channel bits (40 = not reached at 32)')
axes[0].legend(fontsize=7)
fig.tight_layout()
fig.savefig('figs/S1_profile.png', dpi=120)
print('figures written')
