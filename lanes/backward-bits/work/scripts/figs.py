"""Figures for the backward-bits report (plain matplotlib; reference palette slots in fixed order).
usage: figs.py <root> <scores.json> <figdir>
  bits_by_layer.png  per config (columns): top, information about the output code (truth I*_l and each chain's I_out);
                     bottom, the rate of each chain's code (and I*_l for reference). Median over seeds, band = min-max.
  ib_<net>_l<l>.png  the rate-relevance plane at one step of chain K: every candidate code (test set), the target T, the
                     line I = H, the selected codes of the rate and relevance rules, the Gaussian-channel curve.
  crn_by_layer.png   shared-noise output distortion (cell-mean decoder) by layer for chain K, chain PR, the direct code
                     at rate I*_l and the 0-bit code.
"""
import json
import os
import statistics as stx
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ROOT, SCORES, FIG = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(FIG, exist_ok=True)
S = json.load(open(SCORES))
rows = S['rows']
COL = {'truth': '#0b0b0b', 'K': '#2a78d6', 'PR': '#eb6834', 'P': '#1baf7a', 'R': '#eda100', 'dir': '#6250d6'}
NAME = {'truth': 'truth I(h_l; c_L)', 'K': "chain K (Kelvin's rule)", 'R': 'chain R (next code, 95% rule)',
        'P': 'chain P (output code, rate rule)', 'PR': 'chain PR (output code, 95% rule)',
        'dir': 'direct code at rate I*'}
cfgs = sorted(set(r['cfg'] for r in rows), key=lambda c: [int(v) for v in c.split('x')])


def series(rs, key):
    ls = sorted(set(r['l'] for r in rs))
    out = []
    for l in ls:
        xs = [r[key] for r in rs if r['l'] == l and r.get(key) is not None]
        if xs:
            out.append((l, stx.median(xs), min(xs), max(xs)))
    return out


def draw(ax, rs, key, who, ls='-'):
    s = series(rs, key)
    if not s:
        return
    x = [a[0] for a in s]
    ax.plot(x, [a[1] for a in s], ls, color=COL[who], lw=1.6, marker='o', ms=3.5, label=NAME[who])
    ax.fill_between(x, [a[2] for a in s], [a[3] for a in s], color=COL[who], alpha=0.12, lw=0)


fig, axes = plt.subplots(2, len(cfgs), figsize=(4.2 * len(cfgs), 7.2), squeeze=False)
for j, cfg in enumerate(cfgs):
    rs = [r for r in rows if r['cfg'] == cfg]
    ax = axes[0][j]
    draw(ax, rs, 'I_star', 'truth')
    for ch in ('K', 'R', 'P', 'PR'):
        draw(ax, rs, f'{ch}_I_out', ch)
    ax.set_title(f'{cfg}: information about c_L (bits)', fontsize=10)
    ax.set_xlabel('layer l')
    ax.grid(alpha=0.25)
    ax = axes[1][j]
    draw(ax, rs, 'I_star', 'truth', ls='--')
    for ch in ('K', 'R', 'P', 'PR'):
        draw(ax, rs, f'{ch}_H', ch)
    ax.set_title(f'{cfg}: rate H(c_l) of each chain (bits)', fontsize=10)
    ax.set_xlabel('layer l')
    ax.grid(alpha=0.25)
axes[0][0].legend(fontsize=8, loc='upper left')
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'bits_by_layer.png'), dpi=130)
plt.close(fig)

# crn by layer
fig, axes = plt.subplots(1, len(cfgs), figsize=(4.2 * len(cfgs), 3.6), squeeze=False)
for j, cfg in enumerate(cfgs):
    rs = [r for r in rows if r['cfg'] == cfg]
    ax = axes[0][j]
    for key, who in [('crn_chainK', 'K'), ('crn_chainPR', 'PR'), ('crn_direct_rate_truth', 'dir'),
                     ('crn_zero_bit', 'truth')]:
        s = series(rs, key)
        if s:
            ax.plot([a[0] for a in s], [a[1] for a in s], '-' if who != 'truth' else ':', color=COL[who], lw=1.6,
                    marker='o', ms=3.5, label=NAME[who] if who != 'truth' else '0-bit code')
    ax.set_yscale('log')
    ax.set_title(f'{cfg}: shared-noise output nMSE', fontsize=10)
    ax.set_xlabel('layer l')
    ax.grid(alpha=0.25)
axes[0][0].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(FIG, 'crn_by_layer.png'), dpi=130)
plt.close(fig)

# rate-relevance planes at chosen steps
for net in sorted(set(r['net'] for r in rows)):
    if not net.endswith('K64') or '_s5000_' not in net and '_s9100_' not in net:
        continue
    pK = os.path.join(ROOT, net, 'chainK', 'chain.json')
    if not os.path.exists(pK):
        continue
    cK = json.load(open(pK))
    gK = os.path.join(ROOT, net, 'chainK', 'gauss.json')
    gauss = json.load(open(gK)) if os.path.exists(gK) else {}
    cR = os.path.join(ROOT, net, 'chainR', 'chain.json')
    cR = json.load(open(cR)) if os.path.exists(cR) else None
    L = cK['args']['L']
    for l in sorted(set([L - 2, 0])):
        st = cK['steps'].get(str(l))
        if not st or 'cands' not in st:
            continue
        fig, ax = plt.subplots(figsize=(5.2, 4.2))
        H = [e['H'] for e in st['cands']]
        I = [e['I'] for e in st['cands']]
        ax.scatter(H, I, s=8, color='#9a9994', label='partition codes (candidates)')
        T = st['target']['T']
        hmax = max(H + [T]) * 1.05
        ax.plot([0, hmax], [0, hmax], ':', color='#52514e', lw=1, label='I = H')
        ax.axhline(T, color=COL['truth'], lw=1, label=f'target T = {T:.2f}')
        ax.plot(st['selected']['H'], st['selected']['I'], 'o', color=COL['K'], ms=8, label="Kelvin's rule (H <= T)")
        if cR and l == L - 2 and str(l) in cR['steps']:
            sr = cR['steps'][str(l)]['selected']
            ax.plot(sr['H'], sr['I'], 's', color=COL['R'], ms=8, label='95% rule')
        if str(l) in gauss:
            pts = sorted((row['rate_mc'], row['I_dec']) for row in gauss[str(l)]['rows'])
            ax.plot([p[0] for p in pts], [p[1] for p in pts], '-', color=COL['PR'], lw=1.6, marker='^', ms=4,
                    label='Gaussian channel (info rate)')
        ax.set_xlabel('rate (bits): entropy of the partition / information of the channel')
        ax.set_ylabel('bits carried about the next code')
        ax.set_title(f'{net}, step l = {l}', fontsize=9)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7, loc='lower right')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, f'ib_{net}_l{l}.png'), dpi=130)
        plt.close(fig)
print('figures written to', FIG)
