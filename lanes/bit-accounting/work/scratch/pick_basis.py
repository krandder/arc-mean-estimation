"""Basis for the learned run of a cell (PREREG A1 M2): the basis whose linear 'gauss' code has the lower nMSE at C = 64
in runs/lin_<net>_<seed>.json. usage: pick_basis.py arc 4000 16 -> prints 'as' or 'lin'."""
import json
import sys

d = json.load(open(f'runs/lin_{sys.argv[1]}_{sys.argv[2]}.json'))
ent = d['layers'][sys.argv[3]]
best, bv = 'lin', float('inf')
for b in ['as', 'lin']:
    if f'{b}_gauss' in ent:
        v = [c['nmse'] for c in ent[f'{b}_gauss']['curve'] if c['rate'] == 64][0]
        if v < bv:
            best, bv = b, v
print(best)
