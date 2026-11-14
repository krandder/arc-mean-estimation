"""Tables for P2.0 part 1 (how linear the anchored codes are, per layer) next to the phase-1 'price of linearity':
results/P2_identity_part*.json + results/P1_scores.json + runs/P1X -> results/P2_identity_table.md"""
import glob
import json
import math

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'
P = {}
for f in glob.glob(f'{W}/results/P2_identity_part*.json'):
    P.update(json.load(open(f)))
S = json.load(open(f'{W}/results/P1_scores.json'))['cells']


def ts(rates, nmse, D):
    pts = sorted((r, e) for r, e in zip(rates, nmse) if r is not None and e is not None and np.isfinite(r) and np.isfinite(e))
    env, best = [], float('inf')
    for r, e in pts:
        if e < best:
            env.append((max(r, 0.0), e))
            best = e
    for i, (r, e) in enumerate(env):
        if e <= D:
            return r if i == 0 else env[i - 1][0] + (env[i - 1][1] - D) / (env[i - 1][1] - e) * (r - env[i - 1][0])
    return None


def pos(L, l):
    if l == L:
        return 'output'
    return {0: 'input', L // 4: 'L/4', L // 2: 'L/2'}.get(l, '3L/4 to L-1')


rows = {}
for name, v in P.items():
    kind, n, L, s, l, cls = v['kind'], v['n'], v['L'], v['seed'], v['l'], v['cls']
    key = (kind, f'{n}x{L}', pos(L, l), cls)
    r = rows.setdefault(key, dict(lin=[], cos=[], cap=[], gate=[], k=[], plin=[], plin_r0=[], expl=[]))
    for lam in ('0.1', '0.01'):
        q = v[lam]
        r['lin'].append(q['lin_share'])
        if q['cos2_G'] is not None:
            r['cos'].append(q['cos2_G'])
            r['cap'].append(q['G_capture'])
        if q['gate_active'] is not None:
            r['gate'].append(q['gate_active'])
        r['k'].append(q['k'])
    c = S.get(f'{kind}_{n}_{L}_{s}_{l}_{cls}')
    if c is not None:
        for D in ('0.1', '0.01'):
            a, b, b0 = c['R_linref'].get(D), c['R'].get(D), c['R_r0'].get(D)
            if a is not None and b is not None and b > 0:
                r['plin'].append(a / b)
            if a is not None and b0 is not None and b0 > 0:
                r['plin_r0'].append(a / b0)
    xf = f'{W}/runs/P1X/X_{kind}_n{n}_L{L}_s{s}_l{l}_{cls}.json'
    try:
        x = json.load(open(xf))
        for D in (0.1, 0.01):
            ex = [ts(e['rate'], e['nmse'], D) for e in x.get('explorer', {}).values()]
            ex = [q for q in ex if q is not None]
            g = x.get('gates_explorer', {}).get(str(D))
            if g:
                r.setdefault('xgate', []).extend(g)
            if ex and c is not None and c['R_linref'].get(str(D)) is not None:
                r['expl'].append(min(ex) / c['R_linref'][str(D)])
    except FileNotFoundError:
        pass

med = lambda v, nd=2: ('-' if not v else f'{np.median(v):.{nd}f}')  # noqa: E731
order = ['input', 'L/4', 'L/2', '3L/4 to L-1', 'output']
lines = ['# P2.0 part 1: how linear are the anchored codes, and what does linearity cost? (medians over seeds and the '
         'prices lambda = 0.1, 0.01; error levels 10% and 1%)', '',
         'lin share = R^2 of the best linear map from the layer state to the code mean (1 = the code is a linear '
         'function of the layer). k = code directions above the noise. cos^2 G = mean cos^2 of the principal angles '
         'between the code\'s directions and the top-k eigenvectors of G = E[J^T J] (the Jacobian linearisation from '
         'the output back to this layer); G capture = the share of G\'s energy the code\'s directions capture relative '
         'to the best k directions. gates = share of local ReLU units switching inside the data cloud (0 = affine on the '
         'data). Price of linearity = bits of the linear reference code (G\'s directions, water-filled power, linear '
         'MMSE decoding, real net) / bits of the best code found (R*) or of the anchored single model (r0). Explorer / '
         'linear = bits of the best local code with gates inside the cloud / bits of the linear reference.', '',
         '| net | layer | class | lin share | k | cos^2 G | G capture | gates (anchored) | gates (explorer) | '
         'linear / R* | linear / r0 | explorer / linear | cells |', '|' + '---|' * 13]
for key in sorted(rows, key=lambda k: (k[0] != 'relu', k[0], k[1], order.index(k[2]), k[3])):
    r = rows[key]
    lines.append(f'| {key[0]} {key[1]} | {key[2]} | {key[3]} | {med(r["lin"], 3)} | {med(r["k"], 0)} | {med(r["cos"])} | '
                 f'{med(r["cap"])} | {med(r["gate"])} | {med(r.get("xgate", []))} | {med(r["plin"])} | '
                 f'{med(r["plin_r0"])} | {med(r["expl"])} | {len(r["lin"]) // 2} |')
open(f'{W}/results/P2_identity_table.md', 'w').write('\n'.join(lines) + '\n')
# compact relu-only aggregate by layer position and class
agg = {}
for (kind, net, p, cls), r in rows.items():
    if kind != 'relu':
        continue
    a = agg.setdefault((p, cls), dict(lin=[], cos=[], cap=[], plin=[], plin_r0=[], expl=[], gate=[], xgate=[]))
    for k in a:
        a[k] += r.get(k, [])
print('relu, all shapes: position, class: lin share | cos2 G | G capture | linear/R* | linear/r0 | explorer/linear | gates anchored / explorer')
for p in order:
    for cls in ('local', 'unres'):
        if (p, cls) in agg:
            a = agg[(p, cls)]
            print(p, cls, med(a['lin'], 3), med(a['cos']), med(a['cap']), med(a['plin']), med(a['plin_r0']), med(a['expl']),
                  med(a['gate']), '/', med(a['xgate']))
