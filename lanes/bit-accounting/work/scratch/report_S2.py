"""Tables for Part S2 (jointly trained chains) and the part-C deductive estimates. -> results/S2_table.md"""
import json
import os

import numpy as np

D = 'runs/S_chain'
CFG = [(16, 4), (32, 8), (16, 16), (32, 32)]
EVAL = [5000, 5001, 5002]


def get(n, L, s, cls):
    p = os.path.join(D, f'C_n{n}_L{L}_s{s}_{cls}.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    return d if 'per_b' in d else None          # placeholders for skipped chains


def med(v):
    v = [x for x in v if x is not None]
    return float(np.median(v)) if v else float('nan')


lines = ['# Part S2: scrambling test on jointly trained chains (median over seeds 5000-5002)', '',
         'Per transition i (grid layer l_i -> l_{i+1}): ptf_d = accuracy of the best degree-d polynomial threshold fit of '
         'the data majority map on the reachable codes (weighted); baselines on the same reachable codes. W<=1, W<=2: '
         'Walsh weight of the learned transition T at degree <= 1, <= 2 (uniform over all 2^b codes). H = H(c_{i+1} | '
         'c_i) in bits. cov = reachable fraction of the 2^b codes.', '']
for cls in ['local', 'unres']:
    lines.append(f'## encoder class: {cls}')
    lines.append('| net | b | i | cov | H | ptf1 | ptf2 | ptf3 | ltf ptf1 | junta2 ptf1 | perm ptf1 | xor ptf1 | W<=1 T | '
                 'W<=2 T | perm W<=2 | own nMSE (last) | chain nMSE (last) |')
    lines.append('|' + '---|' * 17)
    for n, L in CFG:
        rs = [get(n, L, s, cls) for s in EVAL]
        rs = [r for r in rs if r is not None]
        if not rs:
            continue
        for b in rs[0]['bs']:
            m = len(rs[0]['per_b'][str(b)]['transitions'])
            for i in range(m):
                T = [r['per_b'][str(b)]['transitions'][i] for r in rs]
                row = [f'{n}x{L}', str(b), str(i), f'{med([t["coverage"] for t in T]):.3f}',
                       f'{med([t["H_out_given_in"] for t in T]):.2f}']
                for d in ['1', '2', '3']:
                    row.append(f'{med([t["majority_ptf_acc"][d] for t in T]):.3f}')
                for k in ['ltf', 'junta2', 'perm', 'xor']:
                    row.append(f'{med([t["baselines"][k]["ptf_acc"]["1"] for t in T]):.3f}')
                row.append(f'{med([sum(t["learned_T"]["W_by_degree"][:2]) for t in T]):.2f}')
                row.append(f'{med([sum(t["learned_T"]["W_by_degree"][:3]) for t in T]):.2f}')
                row.append(f'{med([sum(t["baselines"]["perm"]["W_by_degree"][:3]) for t in T]):.2f}')
                if i == m - 1:
                    row.append(f'{med([r["per_b"][str(b)]["own_nmse"][-1] for r in rs]):.3f}')
                    row.append(f'{med([r["per_b"][str(b)]["chain_nmse"][-1] for r in rs]):.3f}')
                else:
                    row += ['', '']
                lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')
lines.append('## Part C: deductive estimates of E a through the learned chains (local class), median over seeds')
lines.append('Errors |est - E a|^2 / V. exact0 = exact law of c_0 pushed through T; fact0 = product of c_0 marginals pushed '
             'through T; mf = marginals re-factorised after every T. MC at equal cost (2^b decoder+future evaluations): '
             '2^-b. chain mean = mean error of the chain-run reconstruction on samples.')
lines.append('')
lines.append('| net | b | exact0 | fact0 | mf | chain mean (samples) | MC at equal cost |')
lines.append('|---|---|---|---|---|---|---|')
for n, L in CFG:
    rs = [get(n, L, s, 'local') for s in EVAL]
    rs = [r for r in rs if r is not None and 'deductive' in r['per_b'][str(r['bs'][0])]]
    if not rs:
        continue
    for b in rs[0]['bs']:
        dd = [r['per_b'][str(b)]['deductive'] for r in rs]
        lines.append(f'| {n}x{L} | {b} | {med([d["exact0"] for d in dd]):.2e} | {med([d["fact0"] for d in dd]):.2e} | '
                     f'{med([d["mf"] for d in dd]):.2e} | '
                     f'{med([r["per_b"][str(b)]["chain_mean_err"][-1] for r in rs]):.2e} | {2.0 ** -b:.2e} |')
os.makedirs('results', exist_ok=True)
open('results/S2_table.md', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
