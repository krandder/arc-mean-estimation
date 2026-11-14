"""POST HOC scoring correction (found after the final scoring, deviations item 7): the hashed scorer looks up the D1
variant f'{kind}64', i.e. 'futmf264', but the registered queue named the runs 'futmf2_64' (with an underscore), so P8's
futmf2 half found no data and P8 failed as scored. This recomputes P8 with the runs' actual names and the registered
formula unchanged. Output results/score_corrections_posthoc.json. The hashed outputs are kept."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402  (side-effect free; importing score_part1 would rewrite its output)

n, L = 256, 32
p8 = {}
for kind, name in (('futmf2', 'futmf2_64'), ('futv', 'futv64')):
    gs = []
    for s in range(200, 205):
        d = S.load('k3p', n, L, s)
        if d is None or name not in d['variants']:
            continue
        k = 64
        cback = (1 << 11) * 3 * (L - 1) / 2.0 if kind == 'futv' else 2.0 * n
        cded = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + cback
        e = d['variants'][name]['nmse']
        gs.append(S.rqmc_err(S.rqmc_curve(n, L, s), cded)[0] / e)
    p8[kind] = dict(G=gs, median=S.med(gs), holds=(len(gs) > 0 and S.med(gs) <= 3))
out = dict(P8_posthoc=dict(kinds=p8, holds=all(v['holds'] for v in p8.values())))
json.dump(out, open(os.path.join(S.RES, 'score_corrections_posthoc.json'), 'w'), indent=1)
print(out)
