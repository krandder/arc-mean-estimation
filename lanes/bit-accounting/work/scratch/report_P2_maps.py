"""P2.0 parts 2-4 tables and the registered H2-H4 scores from results/P2_maps_all.json -> results/P2_maps_table.md,
results/P2_maps_scores.json. Medians over seeds; lambda = 0.01 unless stated."""
import json

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'
D = json.load(open(f'{W}/results/P2_maps_all.json'))


def pos(L, l):
    return {0: 'input', L // 4: 'L/4', L // 2: 'L/2'}.get(l, '3L/4')


rows = {}
for k, v in D.items():
    key = (v['kind'], f'{v["n"]}x{v["L"]}', pos(v['L'], v['l']), v['cls'])
    rows.setdefault(key, []).append(v)
med = lambda xs, nd=2: ('-' if not [x for x in xs if x is not None] else f'{np.median([x for x in xs if x is not None]):.{nd}f}')  # noqa: E731
lines = ['# P2.0 parts 2-4: the code map from layer l to l+1 against the layer map (lambda = 0.01; medians over seeds)', '',
         'T lin / T mlp = R^2 of the best affine / MLP map from the code at l to the code at l+1 (held out); path = R^2 of '
         'the layer path (decode at l, real layer l+1, encode at l+1) against the true next code; agree = R^2 between '
         'the MLP map and the layer path; lin share = R^2 of an affine fit to each map; gates = share of layer-(l+1) '
         'units whose gate the code at l predicts with accuracy >= 0.95 (top / bottom quartile of gradient energy); '
         'rot = mean cos^2 between the next code\'s subspace and the image of this code\'s subspace under the '
         'cloud-averaged Jacobian (identity image in brackets).', '',
         '| net | l -> l+1 | class | T lin | T mlp | path | agree | lin share T / path | lin share T at lambda 0.1 / 0.001 | '
         'gates tracked (top / bottom energy) | rot (identity) | seeds |', '|' + '---|' * 12]
order = ['input', 'L/4', 'L/2', '3L/4']
for key in sorted(rows, key=lambda k: (k[0] != 'relu', k[0], k[1], order.index(k[2]), k[3])):
    vs = rows[key]
    g = lambda f, lam='0.01': [v[lam].get(f) for v in vs]  # noqa: E731
    lines.append(f'| {key[0]} {key[1]} | {key[2]} | {key[3]} | {med(g("r2_Tlin"))} | {med(g("r2_Tmlp"))} | {med(g("r2_path"))} | '
                 f'{med(g("agree_Tmlp_path"))} | {med(g("linshare_Tmlp"))} / {med(g("linshare_path"))} | '
                 f'{med(g("linshare_Tmlp", "0.1"))} / {med(g("linshare_Tmlp", "0.001"))} | {med(g("tracked_frac"))} '
                 f'({med(g("tracked_top_energy"))} / {med(g("tracked_low_energy"))}) | {med(g("rot_cos2"))} '
                 f'({med(g("rot_cos2_identity"))}) | {len(vs)} |')
# registered H2-H4 (P2.0): ReLU 16x16/32x32 at lambda = 0.01 with l >= L/4; tanh4 all grid layers (l <= L/2 for H1 only)
relu = [v for v in D.values() if v['kind'] == 'relu' and v['l'] >= v['L'] // 4]
tanh = [v for v in D.values() if v['kind'] == 'tanh4']
S = {}
h2r = [v['0.01']['agree_Tmlp_path'] >= 0.8 for v in relu]
h2t = [v['0.01']['agree_Tmlp_path'] < 0.5 for v in tanh]
S['H2'] = dict(relu=f'{sum(h2r)}/{len(h2r)}', tanh4_below_0_5=f'{sum(h2t)}/{len(h2t)}',
               hit=bool(np.mean(h2r) >= 0.75 and all(h2t)))
h3 = [v['0.1']['linshare_Tmlp'] >= v['0.001']['linshare_Tmlp'] for v in relu]
S['H3'] = dict(relu=f'{sum(h3)}/{len(h3)}', hit=bool(np.mean(h3) >= 0.75))
rr = [v['0.01'].get('rot_cos2') for v in relu if v['0.01'].get('rot_cos2') is not None]
rt = [v['0.01'].get('rot_cos2') for v in tanh if v['0.01'].get('rot_cos2') is not None]
S['H4'] = dict(relu_median=float(np.median(rr)), tanh4_median=(float(np.median(rt)) if rt else None),
               hit=bool(np.median(rr) >= 0.7 and rt and np.median(rt) < 0.4))
json.dump(S, open(f'{W}/results/P2_maps_scores.json', 'w'), indent=1)
lines += ['', '## Registered predictions (P2.0)', ''] + [f'- {k}: {json.dumps(v)}' for k, v in S.items()]
open(f'{W}/results/P2_maps_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines[6:]))
