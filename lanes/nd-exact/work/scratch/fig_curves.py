"""Figure: nMSE against compute (mv) on the six evaluation nets. Palette: reference categorical slots 1-4 (validated:
scripts/validate_palette.js, light mode, all checks pass; contrast relief by direct labels and the report's tables).
Writes results/fig_curves.png."""
import json
import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, '/home/agent/workspaces/mats/work/nd-exact/lib')
import ndx  # noqa: E402

BASE = '/home/agent/workspaces/mats/work/nd-exact/'
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#fcfcfb'
SER = [('RQMC', '#2a78d6', 'o'), ('RQMCJ (same exact tail as the code)', '#eb6834', 's'),
       ('certified deterministic code CS2', '#1baf7a', '^'), ('exact region code, free integration', '#eda100', 'D')]


def main():
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6), sharex=True, sharey=True, facecolor=SURF)
    for ax, s in zip(axes.flat, ndx.EVAL_SEEDS):
        ax.set_facecolor(SURF)
        b = json.load(open(BASE + f'runs/baselines_s{s}.json'))
        cs = json.load(open(BASE + f'runs/cs2_s{s}.json'))
        rc = json.load(open(BASE + f'runs/region_code_s{s}.json'))
        xs = [2 ** k for k in range(12, 27)]
        ax.plot(xs, [257.0 / x for x in xs], color='#8a8984', lw=1.5, ls='--', label='MC (nMSE = 1/N)')
        curves = [
            sorted((v['RQMC']['cost_mv'], v['RQMC']['nmse']) for v in b['res'].values() if 'RQMC' in v),
            sorted((v['RQMCJ']['cost_mv'], v['RQMCJ']['nmse']) for v in b['res'].values() if 'RQMCJ' in v),
            [(p['cost_mv'], p['nmse']) for p in cs['points']],
            [(p['cost_mv'], p['nmse_ho']) for p in rc['curves']['32']['curve']
             if p['nmse_ho'] >= 10 * p['noise_ho'] and p['cost_mv'] >= 2 ** 10],
        ]
        for (name, col, mk), cur in zip(SER, curves):
            ax.plot([c for c, _ in cur], [e for _, e in cur], color=col, lw=2, marker=mk, ms=5, label=name)
        try:
            pc = json.load(open(BASE + f'runs/posthoc_cs2c_s{s}.json'))
            ax.plot([q['cost_mv'] for q in pc['points']], [q['nmse'] for q in pc['points']], color='#1baf7a', lw=1.5,
                    ls=':', label='CS2c, root-cell defect fixed (post hoc)')
        except FileNotFoundError:
            pass
        try:
            ds = json.load(open(BASE + f'runs/posthoc_dsob_s{s}.json'))
            ax.plot([q['cost_mv'] for q in ds['rows']], [q['rqmcj_median'] for q in ds['rows']], color='#eb6834',
                    lw=1.2, ls='--', label='RQMCJ, median single scrambled run (post hoc)')
            ax.plot([q['cost_mv'] for q in ds['rows']], [q['dsob'] for q in ds['rows']], color='#52514e', lw=1.0,
                    ls='-', marker='x', ms=5, label='fixed Sobol cubature with exact tail (post hoc)')
        except FileNotFoundError:
            pass
        ax.set_xscale('log', base=2)
        ax.set_yscale('log')
        ax.set_ylim(1e-8, 3)
        ax.grid(True, color=GRID, lw=0.8)
        for sp in ax.spines.values():
            sp.set_color('#b5b4ae')
        ax.tick_params(colors=INK2, labelsize=9)
        ax.set_title(f'net {s}', color=INK, fontsize=11)
    for ax in axes[1]:
        ax.set_xlabel('compute (mv = 128 FLOPs)', color=INK2)
    for ax in axes[:, 0]:
        ax.set_ylabel('nMSE of E[a]', color=INK2)
    h, lab = axes[0, 0].get_legend_handles_labels()
    fig.suptitle('Width 8, depth 256: error of the mean against compute', color=INK, y=0.985, fontsize=12)
    fig.legend(h, lab, loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=3, frameon=False, fontsize=9.5,
               labelcolor=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(BASE + 'results/fig_curves.png', dpi=150, facecolor=SURF)
    print('wrote results/fig_curves.png')


if __name__ == '__main__':
    main()
