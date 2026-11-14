"""Figure 1: channel bits for nMSE 0.1 against the layer, with and without the shortcut.
Panels: ARC 256 x 32 (linear local codes, four nets; output-space count dotted), narrow-deep 8 x 256 (linear local codes,
six nets), and the four small nets (best code found per class: min of the learned code and, for local/linear, the
linear transform code; unrestricted: learned). Unreached counts are drawn at the top of the panel. -> figs/bits_by_layer.png"""
import json
import math
import os

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]


def crossing(rates, y, eps):
    y = np.minimum.accumulate(np.asarray(y, float))
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def lin_best(path, l, e='0.1', kind='gauss'):
    if not os.path.exists(path):
        return 'na'
    ent = json.load(open(path))['layers'].get(str(l))
    if ent is None:
        return 'na'
    v = [ent[f'{b}_{kind}']['cross'][e][1] for b in ['as', 'lin'] if f'{b}_{kind}' in ent]
    v = [x for x in v if x is not None]
    return min(v) if v else None


def learned(n, L, s, l, cls, e=0.1):
    p = f'runs/S_curves/S_n{n}_L{L}_s{s}_l{l}_{cls}.json'
    if not os.path.exists(p):
        return 'na'
    return crossing(RATES, json.load(open(p))['curves']['gauss']['nmse'], e)


def best(*vals):
    v = [x for x in vals if x != 'na']
    if not v:
        return 'na'
    num = [x for x in v if x is not None]
    return min(num) if num else None


fig, axes = plt.subplots(2, 3, figsize=(15, 8))
ax = axes[0, 0]
top = 300
for s in [4000, 4001, 4002, 4003]:
    xs, ys = [], []
    for l in [0, 2, 4, 8, 16, 24, 31]:
        v = lin_best(f'runs/lin_arc_{s}.json', l)
        if v != 'na':
            xs.append(l)
            ys.append(top if v is None else v)
    ax.plot(xs, ys, 'o-', color='C0', alpha=0.7, label='local (linear code)' if s == 4000 else None)
    o = lin_best(f'runs/lin_arc_{s}.json', 32)
    if o not in ('na', None):
        ax.axhline(o, color='k', ls=':', lw=0.8, label='output space' if s == 4000 else None)
ax.set_yscale('log')
ax.set_ylim(10, top * 1.3)
ax.set_title('ARC 256 x 32 (top = not reached at 256)')
ax.set_xlabel('layer l')
ax.set_ylabel('channel bits for nMSE 0.1')
ax.legend(fontsize=7)
ax = axes[0, 1]
for s in [203, 216, 217, 220, 221, 223]:
    xs, ys = [], []
    for l in [0, 8, 32, 64, 128, 192, 255, 256]:
        v = lin_best(f'runs/lin_nd_{s}.json', l)
        if v != 'na':
            xs.append(l)
            ys.append(40 if v is None else v)
    ax.plot(xs, ys, 'o-', color='C1', alpha=0.7)
ax.axhline(0.5 * math.log2(10), color='k', ls=':', lw=0.8, label='one Gaussian number')
ax.set_title('narrow-deep 8 x 256 (local linear codes)')
ax.set_xlabel('layer l (256 = output)')
ax.set_yscale('log')
ax.legend(fontsize=7)
axes[0, 2].axis('off')
for ax, (n, L) in zip([axes[1, 0], axes[1, 1], axes[1, 2], axes[0, 2]], [(16, 4), (32, 8), (16, 16), (32, 32)]):
    ax.axis('on')
    grid = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1]))
    for s in [5000, 5001, 5002]:
        for cls, col in [('local', 'C0'), ('unres', 'C2')]:
            xs, ys = [], []
            for l in grid:
                lv = lin_best(f'runs/lin_small{n}x{L}_{s}.json', l) if cls == 'local' else 'na'
                v = best(learned(n, L, s, l, cls), lv)
                if v != 'na':
                    xs.append(l)
                    ys.append(40 if v is None else v)
            ax.plot(xs, ys, 'o-', color=col, alpha=0.7, label=(cls if s == 5000 else None))
        o = best(learned(n, L, s, L, 'unres'), lin_best(f'runs/lin_small{n}x{L}_{s}.json', L))
        if o not in ('na', None):
            ax.axhline(o, color='k', ls=':', lw=0.8, label='output space' if s == 5000 else None)
    ax.set_title(f'{n} x {L}: best code found (40 = not reached at 32)')
    ax.set_xlabel('layer l')
    ax.set_ylim(0, 42)
    ax.legend(fontsize=7)
fig.tight_layout()
os.makedirs('figs', exist_ok=True)
fig.savefig('figs/bits_by_layer.png', dpi=120)
print('written figs/bits_by_layer.png')
