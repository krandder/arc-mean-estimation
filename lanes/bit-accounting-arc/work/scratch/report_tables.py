"""Report tables (A4 conventions, lib/vrb.py): per family, layer and class the bits needed at each accuracy (median
over nets [min-max] of the mean over base restarts 0-1), the 'h1' start (local), slopes, the analytic references, the
Gaussian bound on the output, the relevance lane's N(l, eps) and its water-filling numbers, and certificate flags.
usage: report_tables.py <runs base> <score_v2 json> <out md>
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402
import vrb  # noqa: E402

BASE, SCORE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
EPS_T = [0.3, 0.1, 0.03, 0.01, 0.003, 0.001]
runs, refs, idx = vrb.load(BASE)
score = json.load(open(SCORE)) if os.path.exists(SCORE) else {'cells': {}, 'flags': []}
rel = json.load(open('results/relevance_compare.json')) if os.path.exists('results/relevance_compare.json') else {}


def f(x):
    if x is None:
        return '-'
    if not math.isfinite(x):
        return '>max'
    return '%.0f' % x if x >= 20 else ('%.1f' % x if x >= 1 else '%.2f' % x)


def med(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return '-'
    m = float(np.median(v))
    fin = [x for x in v if math.isfinite(x)]
    s = f(m)
    if len(v) > 1:
        lo, hi = min(v), max(v)
        s += ' [%s-%s]' % (f(lo), f(hi))
    if len(fin) < len(v):
        s += ' (%d unreached)' % (len(v) - len(fin))
    return s + ' (n=%d)' % len(v) if len(v) not in (4, 6) else s


L = []
for fam in ('arc', 'nd'):
    S = vrb.SEEDS[fam]
    L.append(f'\n### {fam}: bits for output nMSE eps (median over {len(S)} nets [min-max]; each net = mean of restarts 0-1)\n')
    L.append('| layer | class | ' + ' | '.join(f'eps {e}' for e in EPS_T) + ' | slope 0.03-0.01 | slope 0.003-0.001 |')
    L.append('|' + '---|' * (2 + len(EPS_T) + 2))
    for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
        for cls in (('local', 'unres') if l < vrb.LOUT[fam] else ('out',)):
            cells = {s: {e: vrb.cellR(vrb.base_runs(idx, fam, s, l, cls), e) for e in EPS_T + [0.03, 0.01, 0.003, 0.001]}
                     for s in S}
            row = [med([cells[s][e]['mean'] if cells[s][e] else None for s in S]) for e in EPS_T]
            sl1 = [vrb.slope(cells[s][0.03]['mean'], cells[s][0.01]['mean'], 0.03, 0.01) if cells[s][0.03] else None for s in S]
            sl2 = [vrb.slope(cells[s][0.003]['mean'], cells[s][0.001]['mean'], 0.003, 0.001) if cells[s][0.003] else None
                   for s in S]
            has_h1 = cls == 'local' and any(idx.get((fam, s, l, 'local', 'h1')) for s in S)
            if all(x == '-' for x in row) and not has_h1:
                continue
            if not all(x == '-' for x in row):
                L.append(f'| {l} | {cls} | ' + ' | '.join(row) + f' | {med(sl1)} | {med(sl2)} |')
            if has_h1:
                hr, br = [], []
                for e in EPS_T:
                    v = [vrb.cellR(idx.get((fam, s, l, 'local', 'h1'), []), e) for s in S]
                    hr.append(med([x['mean'] if x else None for x in v]))
                    # the class count per net: the better of the two starts (where a start ran)
                    bv = []
                    for s, x in zip(S, v):
                        c = cells[s][e]
                        cand = [y for y in ((c['mean'] if c else None), (x['mean'] if x else None)) if y is not None]
                        bv.append(min(cand) if cand else None)
                    br.append(med(bv))
                L.append(f'| {l} | local h1 start | ' + ' | '.join(hr) + ' | | |')
                L.append(f'| {l} | local, better start | ' + ' | '.join(br) + ' | | |')
    # references
    L.append(f'\n### {fam}: analytic linear reference codes, bits (median over nets) and the Gaussian bound\n')
    L.append('| layer | gram 0.1 | gram 0.01 | gram 0.001 | mean-J 0.1 | mean-J 0.01 | Gaussian-convention 0.1 | 0.01 |')
    L.append('|---|---|---|---|---|---|---|---|')
    for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
        cols = []
        for kind, es in (('gram', (0.1, 0.01, 0.001)), ('mean', (0.1, 0.01)), ('gauss', (0.1, 0.01))):
            for e in es:
                v = []
                for s in S:
                    rf = refs.get((fam, s, l))
                    if rf is not None:
                        r = vrb.ref_R(rf, kind, e)
                        v.append(math.inf if r is None else r)
                cols.append(med(v))
        if all(c == '-' for c in cols):
            continue
        L.append(f'| {l} | ' + ' | '.join(cols) + ' |')
    gb = []
    for e in EPS_T:
        v = []
        for s in S:
            rs = idx.get((fam, s, vrb.LOUT[fam], 'out', 'base'), [])
            if rs:
                v.append(vra.gauss_bound(rs[0]['out_evals'], rs[0].get('V_net', rs[0]['V']), e))
        gb.append(f'{e}: {med(v)}')
    L.append('\nGaussian bound on the output (reverse water-filling over eig Cov a): ' + '; '.join(gb))
    # relevance lane
    if fam in ('arc', 'nd'):
        L.append(f'\n### {fam}: the relevance lane at the layers both lanes measured (median over nets)\n')
        L.append('| layer | N(0.1) | N(0.01) | N(0.001) | R1 water-filling 0.1 | 0.01 | active-subspace water-filling 0.1 | 0.01 |')
        L.append('|---|---|---|---|---|---|---|---|')
        for l in vrb.LAYERS[fam]:
            ks = [f'{fam}_s{s}_l{l}' for s in S if f'{fam}_s{s}_l{l}' in rel]
            if not ks:
                continue
            cols = [med([rel[k][c] for k in ks]) for c in ('N_0.1', 'N_0.01', 'N_0.001', 'R1wf_0.1', 'R1wf_0.01',
                                                           'ASwf_0.1', 'ASwf_0.01')]
            L.append(f'| {l} | ' + ' | '.join(cols) + ' |')
L.append('\n### Certificate flags (score_P1_v2.py)\n')
cnt = Counter((a, b) for a, b, _ in score.get('flags', []))
L.append('; '.join(f'{a} {b}: {n}' for (a, b), n in sorted(cnt.items())) or 'none')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))


# ---------------------------------------------------------------- directions used by the codes vs the relevance lane
def n_dirs(rs, eps):
    """number of latents carrying > 0.05 bit at the evaluated point whose nMSE is closest to eps (log scale), mean over
    runs; None if no point within a factor 2 of eps."""
    out = []
    for r in rs:
        best = None
        for c, pc in zip(r['curve'], r['pc']):
            if pc['nmse'] <= 0:
                continue
            dd = abs(math.log(pc['nmse'] / eps))
            if dd < math.log(2) and (best is None or dd < best[0]):
                best = (dd, c['n_active'])
        if best:
            out.append(best[1])
    return float(np.mean(out)) if out else None


L2 = ['\n### Directions used by the local codes (latents carrying > 0.05 bit at the point nearest each accuracy; the '
      'reference start where it ran, else the look-ahead start) and '
      "the relevance lane's linear-feature count N(l, eps) (median over nets)\n",
      '| family | layer | used at 0.1 | N(0.1) | used at 0.01 | N(0.01) | used at 0.001 | N(0.001) |', '|---|---|---|---|---|---|---|---|']
for fam in ('arc', 'nd'):
    for l in vrb.LAYERS[fam]:
        row = []
        for e in (0.1, 0.01, 0.001):
            used = [n_dirs(vrb.base_runs(idx, fam, s, l, 'local') or idx.get((fam, s, l, 'local', 'h1'), []), e)
                    for s in vrb.SEEDS[fam]]   # the reference start where it ran, else the look-ahead start
            Ns = [rel.get(f'{fam}_s{s}_l{l}', {}).get(f'N_{e}') for s in vrb.SEEDS[fam]]
            row += [med(used), med(Ns)]
        if all(x == '-' for x in row[::2]):
            continue
        L2.append(f'| {fam} | {l} | ' + ' | '.join(row) + ' |')
open(OUT, 'a').write('\n'.join(L2) + '\n')
print('\n'.join(L2))


# ---------------------------------------------------------------- the report's main table: per-layer profile
def best_local(fam, s, l, e):
    """the local class count of one net: the better of the two starts (mean over base restarts; 'h1' restart 0)."""
    cand = []
    c = vrb.cellR(vrb.base_runs(idx, fam, s, l, 'local'), e)
    if c and math.isfinite(c['mean']):
        cand.append(c['mean'])
    h = vrb.cellR(idx.get((fam, s, l, 'local', 'h1'), []), e)
    if h and math.isfinite(h['mean']):
        cand.append(h['mean'])
    return min(cand) if cand else None


def best_out(fam, s, e):
    """the best upper bound on the output's rate-distortion function found: every code of every layer is also a code of
    the output (rate >= I(h_l; z) >= I(a; z), reconstruction f(h_hat)), so the lower envelope over the output cell and
    every layer's local (both starts) and unrestricted base curves of this net."""
    cand = []
    c = vrb.cellR(vrb.base_runs(idx, fam, s, vrb.LOUT[fam], 'out'), e)
    if c and math.isfinite(c['mean']):
        cand.append(c['mean'])
    for l in vrb.LAYERS[fam]:
        b = best_local(fam, s, l, e)
        if b is not None:
            cand.append(b)
        c = vrb.cellR(vrb.base_runs(idx, fam, s, l, 'unres'), e)
        if c and math.isfinite(c['mean']):
            cand.append(c['mean'])
    return min(cand) if cand else None


L3 = []
for fam in ('arc', 'nd'):
    S = vrb.SEEDS[fam]
    L3.append(f'\n### {fam}: per-layer profile (local = better of the two starts; median over the nets that have the cell '
              f'[min-max], n = number of nets if not all {len(S)}; ratio = local / the output\'s own curve, median; '
              'slope = bits per halving of the output RMS error)\n')
    L3.append('| layer | local 0.1 | local 0.01 | local 0.001 | ratio 0.1 | ratio 0.01 | slope 0.03-0.01 | slope 0.003-0.001 | '
              'unres 0.1 | unres 0.01 | starts |')
    L3.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
        row = []
        if l == vrb.LOUT[fam]:
            vals = {e: [best_out(fam, s, e) for s in S] for e in (0.1, 0.01, 0.001, 0.03, 0.003)}
            row = [med(vals[e]) for e in (0.1, 0.01, 0.001)] + ['1', '1']
            sl = [vrb.slope(a, b, 0.03, 0.01) for a, b in zip(vals[0.03], vals[0.01])]
            sl2 = [vrb.slope(a, b, 0.003, 0.001) for a, b in zip(vals[0.003], vals[0.001])]
            row += [med(sl), med(sl2), '', '', 'output: lower envelope of every code of this net']
            L3.append(f'| out | ' + ' | '.join(row) + ' |')
            continue
        vals = {e: [best_local(fam, s, l, e) for s in S] for e in (0.1, 0.01, 0.001, 0.03, 0.003)}
        if all(v is None for v in vals[0.1]):
            continue
        row = [med(vals[e]) for e in (0.1, 0.01, 0.001)]
        for e in (0.1, 0.01):
            rr = [(a / b) if (a is not None and b) else None for a, b in zip(vals[e], [best_out(fam, s, e) for s in S])]
            row.append(med(rr).replace(' (n=', ' (n='))
        sl = [vrb.slope(a, b, 0.03, 0.01) for a, b in zip(vals[0.03], vals[0.01])]
        sl2 = [vrb.slope(a, b, 0.003, 0.001) for a, b in zip(vals[0.003], vals[0.001])]
        row += [med(sl), med(sl2)]
        for e in (0.1, 0.01):
            u = [vrb.cellR(vrb.base_runs(idx, fam, s, l, 'unres'), e) for s in S]
            row.append(med([x['mean'] if x else None for x in u]))
        nb = sum(1 for s in S if vrb.base_runs(idx, fam, s, l, 'local'))
        nh = sum(1 for s in S if idx.get((fam, s, l, 'local', 'h1')))
        row.append(f'reference {nb}/{len(S)}, look-ahead {nh}/{len(S)}')
        L3.append(f'| {l} | ' + ' | '.join(row) + ' |')
open(OUT, 'a').write('\n'.join(L3) + '\n')
print('\n'.join(L3))


# ---------------------------------------------------------------- learned codes against the analytic linear reference
L4 = []
for fam in ('arc', 'nd'):
    S = vrb.SEEDS[fam]
    L4.append(f'\n### {fam}: learned code / analytic linear reference (gram spectrum, realised through the net), median over '
              'nets [min-max]; < 1 = the learned code needs fewer bits\n')
    L4.append('| layer | class | 0.3 | 0.1 | 0.03 | 0.01 | 0.003 | 0.001 |')
    L4.append('|---|---|---|---|---|---|---|---|')
    for l in vrb.LAYERS[fam] + [vrb.LOUT[fam]]:
        for cls in (('local', 'unres') if l < vrb.LOUT[fam] else ('out',)):
            row = []
            for e in (0.3, 0.1, 0.03, 0.01, 0.003, 0.001):
                v = []
                for s in S:
                    rf = refs.get((fam, s, l))
                    r = vrb.ref_R(rf, 'gram', e) if rf is not None else None
                    if cls == 'local':
                        x = best_local(fam, s, l, e)
                    else:
                        c = vrb.cellR(vrb.base_runs(idx, fam, s, l, cls), e)
                        x = c['mean'] if c and math.isfinite(c['mean']) else None
                    if x is not None and r:
                        v.append(x / r)
                row.append(med(v))
            if all(x == '-' for x in row):
                continue
            L4.append(f'| {l} | {cls} | ' + ' | '.join(row) + ' |')
open(OUT, 'a').write('\n'.join(L4) + '\n')
print('\n'.join(L4))
