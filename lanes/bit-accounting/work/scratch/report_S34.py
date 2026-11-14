"""Tables for S3 (Kelvin's curriculum autoencoder) and S4 (noisy nets, common random numbers).
-> results/S3_table.md, results/S4_table.md"""
import json
import math
import os

import numpy as np

RATES = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32]
EVAL = [5000, 5001, 5002]


def crossing(rates, y, eps):
    y = np.minimum.accumulate(np.asarray(y, float))
    for i in range(len(rates)):
        if y[i] <= eps:
            if i == 0:
                return float(rates[0])
            y0, y1 = math.log(max(y[i - 1], 1e-30)), math.log(max(y[i], 1e-30))
            f = (y0 - math.log(eps)) / (y0 - y1) if y0 != y1 else 1.0
            return float(rates[i - 1] + f * (rates[i] - rates[i - 1]))
    return None


def med(v, unreached=33):
    if not v:
        return '-'
    srt = sorted([x if x is not None else float('inf') for x in v])
    k = len(srt)
    mid = srt[(k - 1) // 2: k // 2 + 1]
    return '>32' if any(np.isinf(mid)) else f'{np.mean(mid):.1f}'


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


# ---------------- S3
L3 = ['# S3: your curriculum autoencoder (median over seeds; sign bits; counts use the monotone envelope over b)', '',
      'Horizons: recon = h_l itself; fwd = decode to h_l and run the true net; out = decode the output directly; '
      'fwdnext = decode the next grid layer and run the true net. b(0.1) = sign bits for nMSE 0.1 of that horizon; '
      'recon32 = reconstruction nMSE of h_l at b = 32 (the shortcut diagnostic: it grows when the code stops '
      'describing h_l). Floors: reconstruction weight left at the end (0 or 0.05).', '']
for n, L in [(16, 4), (32, 8), (16, 16), (32, 32)]:
    ks = [load(f'runs/S_kelvin/K_n{n}_L{L}_s{s}.json') for s in EVAL]
    ks = [k for k in ks if k is not None]
    if not ks:
        continue
    lay = ks[0]['layers']
    L3.append(f'## {n} x {L} ({len(ks)} seeds)')
    L3.append('| layer | floor | phase | recon32 | b fwd(0.1) | b out(0.1) | b fwdnext(0.1) | fwd nMSE at b=32 |')
    L3.append('|---|---|---|---|---|---|---|---|')
    for i, l in enumerate(lay):
        for fl in [0, 1]:
            for ph in ['A', 'B', 'C']:
                rec = [k['phases'][ph]['nmse'][str(i)]['recon'][-1][fl] for k in ks]
                fw = [crossing(RATES, [v[fl] for v in k['phases'][ph]['nmse'][str(i)]['fwd']], 0.1) for k in ks]
                ou = [crossing(RATES, [v[fl] for v in k['phases'][ph]['nmse'][str(i)]['out']], 0.1) for k in ks]
                fn = [crossing(RATES, [v[fl] for v in k['phases'][ph]['nmse'][str(i)]['fwdnext']], 0.1) for k in ks] \
                    if i < len(lay) - 1 else []
                f32 = [k['phases'][ph]['nmse'][str(i)]['fwd'][-1][fl] for k in ks]
                L3.append(f'| {l} | {ks[0]["floors"][fl]} | {ph} | {np.median(rec):.3f} | {med(fw)} | {med(ou)} | '
                          f'{med(fn)} | {np.median(f32):.3f} |')
    L3.append('')
    # transitions
    L3.append('| transition | b | floor | coverage | H(next given current) | majority ptf1 | perm ptf1 | ltf ptf1 | W<=2 learned |')
    L3.append('|---|---|---|---|---|---|---|---|---|')
    for b in ['4', '8', '12', '16']:
        for i in range(len(lay) - 1):
            for fl in [0, 1]:
                T = [k['transitions'][b][i][fl] for k in ks if b in k['transitions']]
                if not T:
                    continue
                L3.append(f'| {lay[i]}->{lay[i + 1]} | {b} | {T[0]["floor"]} | {np.median([t["coverage"] for t in T]):.3f} | '
                          f'{np.median([t["H_out_given_in"] for t in T]):.2f} | '
                          f'{np.median([t["majority_ptf_acc"]["1"] for t in T]):.3f} | '
                          f'{np.median([t["baselines"]["perm"]["ptf_acc"]["1"] for t in T]):.3f} | '
                          f'{np.median([t["baselines"]["ltf"]["ptf_acc"]["1"] for t in T]):.3f} | '
                          f'{np.median([sum(t["learned_T"]["W_by_degree"][:3]) for t in T]):.2f} |')
    L3.append('')
open('results/S3_table.md', 'w').write('\n'.join(L3) + '\n')

# ---------------- S4
L4 = ['# S4: noisy nets (sigma = 1), decoded state run through the real future with the same noise (median over seeds)',
      '', 'M_l = memory share (tr Var E[a | h_l] / tr Var a). crn = per-sample output match under the shared noise '
      '(primary), avg = noise-averaged distortion |g(h_hat) - g(h)|^2, dist = Gelbrich W2^2 between output laws, mean '
      '= error of the output mean, all / tr Var a, channel codes. C_crn(eps) = capacity for crn <= eps.', '']
for n, L in [(16, 16), (32, 32)]:
    lay = sorted(set([0, L // 4, L // 2, (3 * L) // 4, L - 1])) + [L]
    L4.append(f'## {n} x {L}')
    L4.append('| layer | class | M_l | crn at 1 bit | crn at 32 | avg at 32 | dist at 32 | mean at 32 | C_crn(0.1) | '
              'C_crn(0.01) | C_avg(0.01) | max power |')
    L4.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for l in lay:
        for cls in (['local', 'unres'] if l < L else ['unres']):
            rs = [load(f'runs/S_noisy/N_n{n}_L{L}_s{s}_l{l}_{cls}.json') for s in EVAL]
            rs = [r for r in rs if r is not None]
            if not rs:
                continue
            g = [r['curves']['gauss'] for r in rs]
            M = [r['memory_share'].get(str(l), 1.0) for r in rs]
            L4.append(f'| {l if l < L else "out"} | {cls} | {np.median(M):.3f} | {np.median([x["crn"][0] for x in g]):.4f} | '
                      f'{np.median([x["crn"][-1] for x in g]):.4f} | {np.median([x["avg"][-1] for x in g]):.4f} | '
                      f'{np.median([x["dist"][-1] for x in g]):.4f} | {np.median([x["mean_err"][-1] for x in g]):.2e} | '
                      f'{med([crossing(RATES, x["crn"], 0.1) for x in g])} | {med([crossing(RATES, x["crn"], 0.01) for x in g])} | '
                      f'{med([crossing(RATES, [max(v, 1e-12) for v in x["avg"]], 0.01) for x in g])} | '
                      f'{np.max([max(x.get("power_max", [float("nan")])) for x in g]):.3f} |')
    L4.append('')
open('results/S4_table.md', 'w').write('\n'.join(L4) + '\n')
print('\n'.join(L3[:4]))
print('\n'.join(L4))
