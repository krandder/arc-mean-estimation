"""Figure for the report (descriptive): (a) cloud dimension against n/l; (b) frozen and radial merge residuals against
t phi (mean-field scaling law, lines; registered E2 net medians, markers); (c) merge residual against the number of
references at three layers. Writes figs/fig1_bits.png. Palette: reference categorical slots 1-3 (validated)."""
import os
import glob
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), '..')
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
INK, MUTED = '#0b0b0b', '#52514e'


def main():
    nets = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'eval_n*_L*_s*.json')))]
    nets = [r for r in nets if not r.get('dead')]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    # (a)
    X = np.array([r['n'] / e['l'] for r in nets for e in r['E1']])
    Y = np.array([e['PR'] for r in nets for e in r['E1']])
    a, b = np.polyfit(X, Y, 1)
    ax[0].scatter(X, Y, s=14, color=BLUE, alpha=0.6, linewidths=0)
    xs = np.linspace(0, X.max() * 1.02, 50)
    ax[0].plot(xs, a * xs + b, color=INK, lw=1.2)
    ax[0].text(0.05, 0.92, f'PR = {a:.2f} n/l + {b:.2f}', transform=ax[0].transAxes, color=INK)
    ax[0].set_xlabel('n / l')
    ax[0].set_ylabel('participation ratio of the angular cloud')
    ax[0].set_title('(a) the past: about n/l directions at layer l')
    # (b)
    x = np.logspace(-2, 2, 200)
    tphi = x * 3 * math.pi
    DF = 1 + (1 + x) ** -2 - 2 * (1 + x) ** -3
    DR = (1 + x) ** -2
    ax[1].plot(tphi, DF, color=BLUE, lw=2, label='frozen gates (mean field)')
    ax[1].plot(tphi, DR, color=ORANGE, lw=2, label='radial merge (mean field)')
    tf, mf, mr = [], [], []
    for f in sorted(glob.glob(os.path.join(ROOT, 'runs', 'pairs_n*_L*_s*.npz'))):
        P = dict(np.load(f))
        r = json.load(open(f.replace('pairs_', 'eval_').replace('.npz', '.json')))
        for e in r['E1']:
            A = P.get(f"l{e['l']}")
            if A is None:
                continue
            for d in sorted(set(A[:, 1])):
                s = A[:, 1] == d
                phi = np.median(A[s, 2])
                if phi <= 0:
                    continue
                tf.append(e['Lp'] * phi)
                mf.append(np.mean(A[s, 3]) / phi ** 2)
                mr.append(np.mean(A[s, 4]) / phi ** 2)
    tf, mf, mr = map(np.array, (tf, mf, mr))
    bins = np.logspace(-2, 2.5, 19)
    idx = np.digitize(tf, bins)
    for k in range(1, len(bins)):
        sel = idx == k
        if sel.sum() >= 5:
            c = math.sqrt(bins[k - 1] * bins[k])
            ax[1].plot(c, np.median(mf[sel]), 'o', ms=7, color=BLUE, mec='white', mew=1.5)
            ax[1].plot(c, np.median(mr[sel]), 's', ms=7, color=ORANGE, mec='white', mew=1.5)
    ax[1].plot([], [], 'o', color=BLUE, label='frozen, nets (median of bin means)')
    ax[1].plot([], [], 's', color=ORANGE, label='radial, nets (median of bin means)')
    ax[1].axvline(3 * math.pi * (2 ** (1 / 3) - 1), color=MUTED, lw=1, ls='--')
    ax[1].text(2.6, 0.02, 't phi = 2.45', color=MUTED)
    ax[1].set_xscale('log')
    ax[1].set_yscale('log')
    ax[1].set_xlabel("t phi  (layers to go x angle to the reference)")
    ax[1].set_ylabel('residual / phi^2')
    ax[1].set_title('(b) the future: smooth below t phi = 2.45')
    ax[1].legend(fontsize=8, frameon=False, loc='lower left')
    # (c)
    cases = [((256, 32), 16, BLUE, "ARC 256x32, l = 16 (rough)"), ((128, 128), 64, ORANGE, '128x128, l = 64'),
             ((128, 128), 96, AQUA, '128x128, l = 96 (smooth)')]
    Ms = [1, 4, 16, 64, 256]
    for (cfg, l, col, lab), mk in zip(cases, ['o', 's', '^']):
        rs = [r for r in nets if (r['n'], r['L']) == cfg]
        D = []
        for M in Ms:
            vals = []
            for r in rs:
                e = [e for e in r['E1'] if e['l'] == l][0]
                d = e['fwd'][str(M)]
                vals.append(min(d['D_R'], d['D_F']) if M == 1 else d['D_best'])
            D.append(np.median(vals))
        ax[2].plot(Ms, D, '-' + mk, color=col, lw=2, ms=7, mec='white', mew=1.5, label=lab)
    ax[2].set_xscale('log', base=2)
    ax[2].set_yscale('log')
    ax[2].set_xlabel('number of reference cells M')
    ax[2].set_ylabel('merge residual / output variance')
    ax[2].set_title('(c) cells: many where rough, few where smooth')
    ax[2].legend(fontsize=8, frameon=False, loc='lower left')
    for a_ in ax:
        a_.grid(True, color='#e6e5e1', lw=0.6)
        a_.set_axisbelow(True)
    fig.tight_layout()
    os.makedirs(os.path.join(ROOT, 'figs'), exist_ok=True)
    fig.savefig(os.path.join(ROOT, 'figs', 'fig1_bits.png'), dpi=130)
    print('saved')


if __name__ == '__main__':
    main()
