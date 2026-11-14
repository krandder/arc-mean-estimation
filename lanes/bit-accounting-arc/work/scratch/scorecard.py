"""Scorecard of the registered predictions P1.1-P1.12 under the three scorers: v1 (registered, scratch/score_P1.py), v2
(A4 rules) and v3 (A20 corrections). usage: scorecard.py <v1 json> <v2 json> <v3 json> <out md>
"""
import json
import sys

V1, V2, V3, OUT = sys.argv[1:5]
TEXT = {
    'P1.1': 'C1 passes at L - l <= 8 (both curves reached) on >= 75% of cells',
    'P1.2': 'ARC local R(0.1) at l in {0, 2, 4} >= 4 x R_out(0.1), 4 of 4 nets',
    'P1.3': 'ARC local l = 31 within 15% of R_out at 0.1 and 0.01, >= 3 of 4 nets',
    'P1.4': 'local R(0.1) non-increasing in l (10% + 1 bit), ARC >= 3 of 4, narrow-deep >= 5 of 6',
    'P1.5': 'slopes: ARC l = 0 above l = 31 near 0.01 (4 of 4); narrow-deep l >= 32 in [0.8, 1.6] (>= 5 of 6)',
    'P1.6': 'ARC local slope near 0.01 within [0.5, 2] x N(l, 0.01) at l = 16-31 on >= 75%',
    'P1.7': 'ARC 4000 local R(0.1) within 2x of the bits-bounds formula (d = PR) at l = 4, 8, 16',
    'P1.8': 'C6 passes on >= 90%; layer 31 local within 10% of the gram reference at 0.1 and 0.01 (>= 3 of 4)',
    'P1.9': 'C2 passes on all nets; R_out(0.01) <= 0.8 R_G(0.01) on >= 3 of 4 ARC nets',
    'P1.10': 'narrow-deep: both classes at l >= 32 within max(0.5 bit, 10%) of R_out; local R(0.1) at l = 0 >= 3 R_out',
    'P1.11': 'output-mean error < nMSE / 10 on >= 90% of resolved points with nMSE <= 0.1',
    'P1.12': 'C5 (planted toy) passes for both classes at k = 4 and 16 (registered random local start)',
}


def verdict(p):
    if p is None:
        return '-'
    if 'status' in p:
        st = p['status']
    else:   # the historical scorers had no 'not evaluable': show their verdict and flag too few cells
        st = 'pass' if p.get('hit') else ('fail, too few cells' if p.get('n', 1) < p.get('need', 0) else 'fail')
    det = []
    for k in ('hits', 'n', 'need'):
        if k in p:
            det.append(f'{k} {p[k]}')
    for k in ('arc_hits', 'arc_n', 'nd_hits', 'nd_n', 'sync_hits', 'input_hits', 'c6_pass', 'c6_n', 'l31_hits',
              'l31_n', 'c2_pass', 'c2_n', 'ratio_hits'):
        if k in p:
            det.append(f'{k} {p[k]}')
    return f'{st} ({", ".join(det)})' if det else st


d = [json.load(open(f)).get('pred', {}) for f in (V1, V2, V3)]
L = ['| prediction | registered scorer (v1) | A4 scorer (v2) | A20 scorer (v3) |', '|---|---|---|---|']
for k in sorted(TEXT, key=lambda x: int(x.split('.')[1])):
    L.append(f'| {k}: {TEXT[k]} | ' + ' | '.join(verdict(x.get(k)) for x in d) + ' |')
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
