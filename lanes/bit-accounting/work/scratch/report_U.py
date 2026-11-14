"""Part U (unscrambling at fixed rate): the price of forcing simple code dynamics, and the registered U1-U4 scores.
Reads runs/U/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_*.json -> results/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_table.md, results/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_scores.json. Written and hashed before any U result was read.
Price of forcing at mu (per pair) = sum over the two layers of (Lagrangian(mu) - Lagrangian(0)) / lambda, in bits at
fixed distortion (first order along the rate-distortion curve), where Lagrangian = nMSE + lambda x rate at the end of
training and mu = 0 is the control (the same fine-tuning without the penalty)."""
import glob
import json
import sys

import numpy as np

W = '/home/agent/workspaces/mats/work/bit-accounting'
U = [json.load(open(f)) for f in sorted(glob.glob(f'{W}/runs/U/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_*.json'))]


def pos(L, l):
    return {0: 'input', L // 4: 'L/4', L // 2: 'L/2'}.get(l, '3L/4')


def lag(e, j, mi, lam):
    return e[f'nmse_{j}'][mi] + lam * e[f'rate_{j}'][mi]


rows, S = {}, {}
u1, u2, u3, u4 = [], [], [], []
for r in U:
    e, lam, mus = r['end'], r['lam'], r['mus']
    i0 = mus.index(0.0)
    key = (r['kind'], f'{r["n"]}x{r["L"]}', pos(r['L'], r['l']), r['lam'], r['smap'])
    for mi, mu in enumerate(mus):
        price = sum((lag(e, j, mi, lam) - lag(e, j, i0, lam)) / lam for j in range(2))
        rel = [lag(e, j, mi, lam) / max(lag(e, j, i0, lam), 1e-12) - 1.0 for j in range(2)]
        p = e['predict']
        ent = rows.setdefault(key + (mu,), dict(price=[], rel=[], lin=[], diag=[], mlp=[], ratio=[]))
        ent['price'].append(price)
        ent['rel'].append(max(rel))
        ent['lin'].append(p['lin'][mi])
        ent['diag'].append(p['diag'][mi])
        ent['mlp'].append(p['mlp'][mi])
        ent['ratio'].append(p['lin'][mi] / max(p['mlp'][mi], 1e-9))
    if lam == 0.01 and 1.0 in mus:
        m1 = mus.index(1.0)
        p = e['predict']
        rel1 = [lag(e, j, m1, lam) / max(lag(e, j, i0, lam), 1e-12) - 1.0 for j in range(2)]
        if r['smap'] == 'linear':
            if r['kind'] == 'relu' and r['l'] >= r['L'] // 4:
                u1.append(p['lin'][m1] >= 0.9 * p['mlp'][m1] and max(rel1) <= 0.02)
            if r['kind'] == 'tanh4':
                u2.append(p['lin'][m1] <= 0.7 * p['mlp'][m1] or max(rel1) > 0.05)
            u3.append(p['mlp'][m1] - p['mlp'][i0] <= 0.05)
        if r['smap'] == 'diag' and r['kind'] == 'relu' and r['l'] >= r['L'] // 2:
            u4.append(p['diag'][m1] >= 0.8 * p['mlp'][m1])
frac = lambda v: (f'{sum(v)}/{len(v)}', bool(v) and float(np.mean(v)) >= 0.75)  # noqa: E731
for name, v in (('U1', u1), ('U2', u2), ('U3', u3), ('U4', u4)):
    c, h = frac(v)
    S[name] = dict(count=c, hit=h if v else None)
med = lambda xs, nd=2: ('-' if not xs else f'{np.median(xs):.{nd}f}')  # noqa: E731
lines = ['# Part U: the price of forcing simple code dynamics (unscrambling at fixed rate)', '',
         'Price = extra bits at fixed distortion over both layers of the pair, (Lagrangian(mu) - Lagrangian(0)) / lambda '
         '(median over seeds and pairs; mu = 0 is the control). max rel = largest relative Lagrangian rise of the two '
         'layers. Predictability of the next code from this one (held out): lin = best affine map, diag = '
         'coordinate-wise affine (identity up to scale), mlp = MLP (the ceiling of what is predictable at all); ratio = '
         'lin / mlp.', '',
         '| net | layer | lambda | map | mu | price (bits) | max rel | lin | diag | mlp | lin / mlp | pairs |', '|' + '---|' * 12]
order = ['input', 'L/4', 'L/2', '3L/4']
for key in sorted(rows, key=lambda k: (k[0] != 'relu', k[0], k[1], order.index(k[2]), k[3], k[4], k[5])):
    v = rows[key]
    lines.append(f'| {key[0]} {key[1]} | {key[2]} | {key[3]} | {key[4]} | {key[5]} | {med(v["price"])} | {med(v["rel"], 3)} | '
                 f'{med(v["lin"], 3)} | {med(v["diag"], 3)} | {med(v["mlp"], 3)} | {med(v["ratio"], 3)} | {len(v["price"])} |')
lines += ['', '## Registered predictions (Part U)', ''] + [f'- {k}: {json.dumps(v)}' for k, v in S.items()]
json.dump(S, open(f'{W}/results/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_scores.json', 'w'), indent=1)
open(f'{W}/results/' + (sys.argv[1] if len(sys.argv) > 1 else 'U') + '_table.md', 'w').write('\n'.join(lines) + '\n')
# compact: price per mu, ReLU (all pairs, lambda 0.01, linear map) vs tanh4
for kind in ('relu', 'tanh4'):
    out = []
    for mu in (0.1, 0.3, 1.0, 3.0):
        pr = [x for k, v in rows.items() if k[0] == kind and k[3] == 0.01 and k[4] == 'linear' and k[5] == mu for x in v['price']]
        rt = [x for k, v in rows.items() if k[0] == kind and k[3] == 0.01 and k[4] == 'linear' and k[5] == mu for x in v['ratio']]
        out.append(f'mu {mu}: price {med(pr)} bits, lin/mlp {med(rt, 3)}')
    print(kind, '|', '; '.join(out))
print(json.dumps(S))
