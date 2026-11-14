"""Insert results/scorecard.md (and Amendment 1's scores if present) into future-aware.md between the scorecard markers."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, '..', 'results'); P = os.path.join(HERE, '..', 'future-aware.md')
card = open(os.path.join(R, 'scorecard.md')).read().strip()
a1 = os.path.join(R, 'score_amend1.json')
if os.path.exists(a1):
    s = json.load(open(a1))
    rows = []
    desc = {'P10': 'median k3f nMSE at 512 x 64 in [1e-4, 4e-4]',
            'P11': 'q_proj(futmf2, n/4)/q_3 >= 0.6 at 512 and q_proj(futmf2, 16) at 512 < at 256',
            'P12': 'best-case G_RQMC of k3p(futmf2, n/4) at 512 <= at 256',
            'P13': 'ARC k2 G_RQMC at 512 < at 256'}
    for k in ('P10', 'P11', 'P12', 'P13'):
        meas = '; '.join(f'{kk} {vv:.3g}' if isinstance(vv, float) else f'{kk} {vv}' for kk, vv in s[k].items() if kk != 'holds')
        rows.append(f'| {k} (Amendment 1) | {desc[k]} | {meas} | {"HOLDS" if s[k]["holds"] else "FAILS"} |')
    card = card + '\n' + '\n'.join(rows)
doc = open(P).read()
i0 = doc.index('<!-- scorecard start -->') + len('<!-- scorecard start -->')
i1 = doc.index('<!-- scorecard end -->')
doc = doc[:i0] + '\nScorecard (results/scorecard.md from the hashed scorers; wording abbreviated, PREREG.md has the exact text):\n\n' + card + '\n' + doc[i1:]
open(P, 'w').write(doc)
print('inserted')
