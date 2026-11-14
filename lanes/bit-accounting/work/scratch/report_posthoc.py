"""Tables for the post-hoc chain statistics (results/S2_posthoc.json) -> results/S2_posthoc_table.md, and a figure
figs/S2_posthoc.png: held-out per-bit accuracy of degree-1 threshold maps against the Bayes limit and the matched null."""
import json
import os

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

d = json.load(open('results/S2_posthoc.json'))
lines = ['# Post-hoc scrambling statistics of the jointly trained chains (held-out half of 2^17 inputs)', '',
         'Per next-code bit, averaged over bits: trivial = best constant predictor; bayes = per-code majority map (the '
         'best any map from the current code can do, fitted on the other half); ptf1, ptf2 = degree-1, degree-2 '
         'polynomial threshold maps of the current code bits (fitted lower bounds); j1-j3 = best 1-3 juntas '
         '(exhaustive, b <= 12); null = the same with the current codes relabelled by a random bijection of the '
         'reachable codes (keeps the joint law up to relabelling); whole = Bayes accuracy for the whole next code.', '',
         '| chain | b | T | trivial | bayes | ptf1 | ptf2 | j1 | j2 | j3 | null ptf1 | null ptf2 | null j3 | whole |',
         '|' + '---|' * 14]
rows = []
for tag, ent in sorted(d.items()):
    for b, trs in ent.items():
        for i, t in enumerate(trs):
            r, nl = t['real'], t['null']
            g = lambda x, k: (f'{x[k]:.3f}' if k in x and x[k] is not None else '')  # noqa: E731
            lines.append(f'| {tag[2:]} | {b} | {i} | {g(r, "trivial")} | {g(r, "bayes_bit")} | {g(r, "ptf1")} | '
                         f'{g(r, "ptf2")} | {g(r, "junta1")} | {g(r, "junta2")} | {g(r, "junta3")} | {g(nl, "ptf1")} | '
                         f'{g(nl, "ptf2")} | {g(nl, "junta3")} | {g(r, "bayes_whole_code")} |')
            gap = r['bayes_bit'] - r['trivial']
            rows.append(dict(tag=tag, b=int(b), i=i, cls=tag.split('_')[-1],
                             frac_ptf1=(r['ptf1'] - r['trivial']) / gap if gap > 1e-3 else np.nan,
                             frac_null=(nl['ptf1'] - r['trivial']) / gap if gap > 1e-3 else np.nan))
lines.append('')
for cls in ['local', 'unres']:
    sel = [x for x in rows if x['cls'] == cls and np.isfinite(x['frac_ptf1'])]
    if sel:
        lines.append(f'{cls}: share of the predictable part (bayes - trivial) captured by a degree-1 threshold map: '
                     f'median {np.median([x["frac_ptf1"] for x in sel]):.3f} (range {min(x["frac_ptf1"] for x in sel):.3f}'
                     f'-{max(x["frac_ptf1"] for x in sel):.3f}); by the same map after random relabelling: median '
                     f'{np.median([x["frac_null"] for x in sel]):.3f}; {len(sel)} (chain, b, transition) cells.')
open('results/S2_posthoc_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines[-3:]))
os.makedirs('figs', exist_ok=True)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for k, cls in enumerate(['local', 'unres']):
    sel = [x for x in rows if x['cls'] == cls and np.isfinite(x['frac_ptf1'])]
    for b, col in zip([4, 8, 12, 16], ['C0', 'C1', 'C2', 'C3']):
        s = [x for x in sel if x['b'] == b]
        ax[k].scatter([x['frac_null'] for x in s], [x['frac_ptf1'] for x in s], s=12, color=col, label=f'b={b}')
    ax[k].plot([-0.2, 1.05], [-0.2, 1.05], 'k:', lw=0.8)
    ax[k].set_xlabel('null (codes relabelled): share captured by degree-1 map')
    ax[k].set_ylabel('learned codes: share captured by degree-1 map')
    ax[k].set_title(f'{cls} chains')
    ax[k].legend(fontsize=7)
fig.tight_layout()
fig.savefig('figs/S2_posthoc.png', dpi=120)

# one-step decoding (what the lossy part is)
if os.path.exists('results/S2_onestep.json'):
    o = json.load(open('results/S2_onestep.json'))
    L2 = ['', '# One-step decoding of the transitions (nMSE of the output, held-out)', '',
          'own_i: the current code decoded at its layer; own_next: the true next code at the next layer; bayes_next: the '
          'best prediction of the next code from the current code, decoded at the next layer; T_next: the learned '
          'transition, decoded at the next layer. gain = own_i - own_next (information the next code has and the current '
          'lacks); loss = bayes_next - own_i (what the step loses of the current code).', '',
          '| chain | b | T | own_i | own_next | bayes_next | T_next | gain | loss |', '|' + '---|' * 9]
    gains, losses = [], []
    for tag, ent in sorted(o.items()):
        for b, trs in ent.items():
            for i, t in enumerate(trs):
                g, ls = t['own_i'] - t['own_next'], t['bayes_next'] - t['own_i']
                if b == '16':
                    gains.append(g)
                    losses.append(ls)
                L2.append(f'| {tag[2:]} | {b} | {i} | {t["own_i"]:.3f} | {t["own_next"]:.3f} | {t["bayes_next"]:.3f} | '
                          f'{t["T_next"]:.3f} | {g:+.3f} | {ls:+.3f} |')
    if gains:
        L2.append('')
        L2.append(f'b = 16: gain median {np.median(gains):+.3f} (range {min(gains):+.3f} to {max(gains):+.3f}); loss median '
                  f'{np.median(losses):+.3f} (range {min(losses):+.3f} to {max(losses):+.3f}); {len(gains)} transitions.')
    open('results/S2_posthoc_table.md', 'a').write('\n'.join(L2) + '\n')
    print('\n'.join(L2[-2:]))
