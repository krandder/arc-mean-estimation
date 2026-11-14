"""The final update for Kelvin against the 11:33Z table: cells that moved > 5% in the per-layer profile (from
table_diff.py's output), status changes (certified cells, A18 convergence verdicts, prediction statuses), and the
one-line convergence answer per subset cell by the registered rule (A18 with A20's matched partners).
usage: final_update.py <table diff md> <conv_subset json> <export json> <v2 scores at 11:33Z> <v3 scores now> <out md>
"""
import json
import sys

DIFF, CONV, EXPORT, OLD, NEW, OUT = sys.argv[1:7]
L = []
rows = [l for l in open(DIFF).read().split('\n') if l.startswith('| arc: per-layer profile') or
        l.startswith('| nd: per-layer profile')]
L.append('Per-layer profile cells that moved by more than 5% since the 11:33Z table (median over nets; full list: '
         + DIFF + '):')
L.append('')
L.append('| table / layer / column | 11:33Z | now | change |')
L.append('|---|---|---|---|')
L += rows
L.append('')
ex = json.load(open(EXPORT))
cert = sorted(f"{c['family']} net {c['net']} layer {c['layer']} {c['cls']}" for c in ex['cells']
              if c['status'] == 'certified')
L.append('Certified cells now (registered certificates, A19 consistency and C7 included): ' + (', '.join(cert) or 'none'))
L.append('')
old = json.load(open(OLD)).get('pred', {})
new = json.load(open(NEW)).get('pred', {})


def st(p):
    if p is None:
        return '-'
    if 'status' in p:
        return p['status']
    return 'pass' if p.get('hit') else ('fail, too few cells' if p.get('n', 1) < p.get('need', 0) else 'fail')


ch = [f'{k}: {st(old.get(k))} -> {st(new.get(k))}' for k in sorted(new, key=lambda x: int(x.split('.')[1]))
      if st(old.get(k)) != st(new.get(k))]
L.append('Prediction statuses changed (11:33Z A4 scorer -> final A20 scorer): ' + ('; '.join(ch) or 'none'))
L.append('')
L.append('Is the count converged by the registered rule (A18; A20 matched partners)? ARC net 4000:')
L.append('')
L.append('| layer | class | error | converged? | lowest found (registered count) | why |')
L.append('|---|---|---|---|---|---|')
for q in json.load(open(CONV)):
    v = q['verdict']
    yn = 'yes' if v == 'converged' else ('no' if v.startswith('not converged') else
                                        ('not reached' if v == 'not reached' else 'unverified'))
    low = q['lowest']
    lows = '-' if low is None else ('%.0f' % low if low >= 20 else '%.1f' % low)
    reg = q['registered']
    regs = '-' if reg is None else ('%.0f' % reg if reg >= 20 else '%.1f' % reg)
    L.append(f"| {q['layer']} | {q['cls']} | {int(round(100 * q['eps']))}% | {yn} | {lows} ({regs}) | {v}; "
             f"{q.get('doublings', '')} |")
open(OUT, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
