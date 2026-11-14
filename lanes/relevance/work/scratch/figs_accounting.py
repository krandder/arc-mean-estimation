"""Figures for the accounting (post-processing; plain matplotlib defaults).
fig1: ARC 256 x 32, residual 1 - S(P_k) against k at l = 0, 8, 16, 31 (measured AS basis, cloud-axes basis, v2 rule,
first-chaos lower bound), one net (seed 4000) or the first available.
fig2: ARC per-layer shares: radial channel, degree-1 share (measured, v2), mean degree (measured, v2 identity).
fig3: stationary residual after one direction (AS) and after the radial feature, against t, n = 32, 64, 128, 256."""
import glob
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import theory_v2 as t2  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/relevance/'
ANG = json.load(open(BASE + 'results/angular_spectra.json'))


def curve(c, V):
    ks = sorted(int(k) for k in c)
    return np.array(ks), np.array([c[str(k)][0] / V for k in ks])


def fig1():
    d = json.load(open(BASE + 'runs/eval_arc_n256_L32_seed4000.json'))
    fig, axs = plt.subplots(1, 4, figsize=(16, 3.8), sharey=True)
    for ax, l in zip(axs, (0, 8, 16, 31)):
        o = next(x for x in d if x['l'] == l)
        V = o['V_gauss'][0]
        k, r = curve(o['res_AS_gauss'], V)
        ax.plot(np.maximum(k, 0.5), np.maximum(r, 1e-4), 'o-', label='measured, active-subspace basis')
        k2, r2 = curve(o['res_PCA_gauss'], V)
        ax.plot(np.maximum(k2, 0.5), np.maximum(r2, 1e-4), 's--', label='measured, cloud-axes basis')
        lp = o.get('cloud_evals_perp') or ANG.get(f'arc|256|4000|{l}')
        p = t2.predict_N(o, lam_perp=lp)
        rv = np.array(p['res_vec'])
        kk = np.arange(len(rv))
        ax.plot(np.maximum(kk, 0.5), np.maximum(rv, 1e-4), '-', label='theory v2')
        lam = np.maximum(np.array(o['R1_evals']) - V / 4096, 0)
        beyond = max(o['V1_gauss'][0] - lam.sum(), 0)
        tails = np.array([lam[j:].sum() + beyond for j in range(len(lam))]) / V
        ax.plot(np.maximum(np.arange(len(tails)), 0.5), np.maximum(tails, 1e-4), ':', label='first-chaos estimate (uncertified)')
        for e in (0.1, 0.01, 0.001):
            ax.axhline(e, color='grey', lw=0.5)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(f'ARC 256 x 32, layer {l} (t = {32 - l})')
        ax.set_xlabel('k (directions kept)')
    axs[0].set_ylabel('unexplained share of V_l')
    axs[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(BASE + 'figs/fig1_residual_curves_arc.png', dpi=130)


def fig2():
    recs = json.load(open(BASE + 'results/report_tables.json'))
    arc = [r for r in recs if r['mode'] == 'arc']
    ls = sorted(set(r['lab'] for r in arc))

    def med(key, l):
        xs = [r.get(key) for r in arc if r['lab'] == l and r.get(key) is not None]
        return np.median(xs) if xs else np.nan
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.6))
    axs[0].plot(ls, [med('rad_share', l) for l in ls], 'o-', label='radial feature (measured)')
    axs[0].plot(ls, [med('s1', l) for l in ls], 's-', label='degree 1 (measured)')
    axs[0].plot(ls, [med('v2_s1', l) for l in ls], '--', label='degree 1 (theory)')
    axs[0].plot(ls, [l / 32 for l in ls], ':', label='l/L (kernel asymptote)')
    axs[0].set_xlabel('layer l')
    axs[0].set_ylabel('share of V_l')
    axs[0].legend(fontsize=7)
    axs[1].plot(ls, [med('D', l) for l in ls], 'o-', label='measured')
    axs[1].plot(ls, [med('v2_D', l) for l in ls], '--', label='theory (gradient-energy identity)')
    axs[1].set_yscale('log')
    axs[1].set_xlabel('layer l')
    axs[1].set_ylabel('mean Hermite degree D_l')
    axs[1].legend(fontsize=7)
    for e, mk, col in ((0.1, 'o', 'C0'), (0.01, 's', 'C1'), (0.001, '^', 'C2')):
        axs[2].plot(ls, [med(f'N_{e}', l) for l in ls], mk + '-', color=col, label=f'measured, eps = {e}')
        axs[2].plot(ls, [med(f'v2_N_{e}', l) for l in ls], mk + '--', color=col, alpha=0.6)
        axs[2].plot(ls, [med(f'lo_{e}', l) for l in ls], mk + ':', color=col, alpha=0.6)
    axs[2].set_yscale('log')
    axs[2].set_xlabel('layer l')
    axs[2].set_ylabel('N(l, eps), vector output')
    axs[2].set_title('solid measured (point estimates), dashed theory v2, dotted uncertified first-chaos estimate', fontsize=8)
    axs[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(BASE + 'figs/fig2_arc_shares.png', dpi=130)


def fig3():
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for fn in sorted(glob.glob(BASE + 'runs/eval_stat_n*_seed1000.json')):
        d = json.load(open(fn))
        n = d[0]['n']
        ts, r1, rr, M = [], [], [], []
        for o in d:
            V = o['V_gauss'][0]
            Mt = o['V_true'][0] / o['totvar_true'][0]
            if not (V > 3 * o['V_gauss'][1]) or Mt < 0.02:
                continue
            ts.append(o['t'])
            r1.append(max(o['res_AS_gauss']['1'][0] / V, 1e-4))
            rr.append(max(o['res_radial_gauss'][0] / V, 1e-4))
            M.append(Mt)
        if ts:
            ax[0].plot(ts, r1, 'o-', label=f'n = {n}: top active-subspace direction')
            ax[0].plot(ts, rr, 'x--', label=f'n = {n}: radial feature e.X')
            ax[1].plot(ts, M, 'o-', label=f'n = {n}')
    ax[0].set_xscale('log')
    ax[0].set_yscale('log')
    ax[0].set_xlabel('t = layers to go')
    ax[0].set_ylabel('unexplained share of V_l')
    ax[0].legend(fontsize=7)
    ax[1].set_xscale('log')
    ax[1].set_yscale('log')
    ax[1].set_xlabel('t')
    ax[1].set_ylabel('memory share V_l / tr Var(a)')
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(BASE + 'figs/fig3_stationary.png', dpi=130)


if __name__ == '__main__':
    fig1()
    fig2()
    fig3()
    print('figs written')
