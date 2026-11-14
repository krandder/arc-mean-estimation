"""Plain figures from results/score.json (formatting only). usage: figs.py SCORE_JSON OUT_DIR"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open(sys.argv[1]))
out = sys.argv[2]
os.makedirs(out, exist_ok=True)


def med(v):
    v = [x for x in v if x is not None]
    return float(np.median(v)) if v else None


def frontier(setname, title, fname, budget=None, raw=False):
    rows = d['per_net'].get(setname)
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    scale = med([r.get('avgvar') for r in rows]) if raw else 1.0
    Cs = np.logspace(0, 6, 100)
    ax.plot(Cs, scale / Cs, 'k--', lw=1, label='Monte Carlo')
    if all('rqmc' in r for r in rows):
        Ns = rows[0]['rqmc']['N']
        ax.plot(Ns, [scale * med([r['rqmc']['e'][i] for r in rows if len(r['rqmc']['e']) > i]) for i in range(len(Ns))], 'k-o',
                ms=3, lw=1, label='RQMC (median over nets)')
    groups = [('ARC', ['ARC-k1', 'ARC-k2', 'ARC-k2a', 'ARC-k3', 'ARC-k3f', 'ARC-k3fa', 'ARC-k4f'], 's', 'tab:orange'),
              ('scale-mode claim', ['LVTV2', 'SL3'], 'o', 'tab:blue')]
    for lab, names, mk, col in groups:
        first = True
        for nm in names:
            es = [r['m'][nm]['e'] for r in rows if nm in r['m']]
            cs = [r['m'][nm]['C'] for r in rows if nm in r['m']]
            if not es:
                continue
            ax.plot(med(cs), scale * med(es), mk, color=col, ms=7, label=lab if first else None)
            ax.annotate(nm.replace('ARC-', ''), (med(cs), scale * med(es)), textcoords='offset points', xytext=(5, 4), fontsize=8)
            first = False
    if budget:
        ax.axvline(budget, color='grey', lw=0.8)
        ax.text(budget * 1.15, 0.5, 'contest budget', rotation=90, fontsize=8, color='grey', transform=ax.get_xaxis_transform(), va='center')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('cost (forward passes, ARC flop counter)')
    ax.set_ylabel('raw final-layer MSE' if raw else 'nMSE = |est - Y|^2 / tr Var')
    ax.set_title(title)
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(out, fname), dpi=150); plt.close(fig)


frontier('E1', '256 x 32 (Phase 1 shape), nets 200-204: medians', 'fig1_256x32.png', budget=64850)
frontier('E4', '1024 x 16 (Phase 2 shape), public MLPs 0-11: medians', 'fig3_1024x16.png', budget=65536, raw=True)

# fig2: gain over RQMC at own cost vs width, L = n/8 and L = n/4
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for lab, sets, mk in (('L = n/8', [('E2_n32', 32), ('E2_n64', 64), ('E2_n128', 128), ('E1', 256)], 'o-'),
                      ('L = n/4', [('E3_n64', 64), ('E3_n128', 128), ('E3_n256', 256), ('E3_n512', 512), ('E3_n1024', 1024)], 's-')):
    xs, ys, lo, hi = [], [], [], []
    for s, n in sets:
        rows = d['per_net'].get(s)
        if not rows:
            continue
        g = [r['m']['LVTV2'].get('G_RQ') for r in rows if 'LVTV2' in r['m']]
        g = [x for x in g if x]
        if not g:
            continue
        xs.append(n); ys.append(np.median(g)); lo.append(min(g)); hi.append(max(g))
    if xs:
        ax.errorbar(xs, ys, yerr=[np.array(ys) - np.array(lo), np.array(hi) - np.array(ys)], fmt=mk, capsize=3, label=f'LVTV2, {lab}')
ax.axhline(1, color='k', lw=0.8)
ax.set_xscale('log', base=2); ax.set_yscale('log')
ax.set_xlabel('width n'); ax.set_ylabel('RQMC error / LVTV2 error at LVTV2 cost')
ax.set_title('LVTV2 vs RQMC at its own cost (median, min-max)')
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(out, 'fig2_gain_vs_width.png'), dpi=150); plt.close(fig)
print('figures written to', out)
