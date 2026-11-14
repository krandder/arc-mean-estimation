"""Table of vertices along lines vs the Rice prediction (results/pieces.md)."""
import glob, json, math, numpy as np
rows = []
for f in sorted(glob.glob('runs/pieces_*.json')):
    d = json.load(open(f))
    n, L, fam = d['n'], d['L'], d['family']
    for mode, r in d['modes'].items():
        pl = r['per_layer']
        # Rice: full half circle 3 + n l ; window: 3 + n l (2 psi0 / pi)
        frac = 1.0 if mode == 'full' else 2 * d['psi0'] / math.pi
        for l in sorted(set([1, 2, 4, 8, 16, 32, 64, 128, 256, L])):
            if l > L: continue
            pred = 3 + n * l * frac
            rows.append((fam, n, L, d['seed'], mode, l, pl[l]['mean'], pl[l]['median'], pred, r['cost_passes']['mean'] if l == L else None, r['sec_per_line']['mean'] if l == L else None))
out = ['| family | n | L | seed | mode | layer l | vertices mean | median | Rice 3 + n l (window: x 2 psi0/pi) | ratio | cost/line (passes, at L) | s/line |', '|' + '---|' * 12]
for fam, n, L, s, mode, l, mean, med, pred, cost, sec in rows:
    out.append('| %s | %d | %d | %d | %s | %d | %.1f | %.0f | %.0f | %.2f | %s | %s |' % (fam, n, L, s, mode, l, mean, med, pred, mean / pred,
               '%.1f' % cost if cost else '', '%.3f' % sec if sec else ''))
open('results/pieces.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
