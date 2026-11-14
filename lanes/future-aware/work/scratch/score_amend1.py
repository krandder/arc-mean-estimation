"""Scorer for PREREG Amendment 1 (P10-P13): width extension of D1 and ARC K = 2 to n = 512, L = 64 (nets 500-502),
compared with the Part 1 medians at 256 x 32 (nets 200-204). Writes results/score_amend1.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_part1 as S  # noqa: E402  (also re-runs the Part 1 scorer)

RUNS = S.RUNS


def curve(n, L, s):
    p = os.path.join(RUNS, f'rqmc_n{n}_L{L}_s{s}.json')
    if os.path.exists(p):
        d = json.load(open(p))
        return np.array([r['N'] for r in d['rows']], float), np.array([r['mean_nmse'] for r in d['rows']], float)
    return S.rqmc_curve(n, L, s)


def stats(n, L, seeds):
    out = dict(k3=[], k2G=[], q3=[], qp_q=[], qp16=[], Gded=[])
    for s in seeds:
        d = S.load('k3p', n, L, s)
        if d is None:
            continue
        cur = curve(n, L, s)
        e2 = d['k2']['nmse']; e3 = d['variants']['none']['nmse']
        out['k3'].append(e3); out['q3'].append(e2 / e3)
        out['k2G'].append(S.rqmc_err(cur, d['k2']['passes'])[0] / e2)
        r = d['variants'].get(f'futmf2_{n // 4}') or d['variants'].get(f'futmf2{n // 4}')
        if r is not None and np.isfinite(r['nmse']):
            out['qp_q'].append((e2 / r['nmse']) / (e2 / e3))
            k = n // 4
            cded = d['k2']['passes'] + k + 1.5 * k ** 4 / n ** 2 + 2.0 * n
            out['Gded'].append(S.rqmc_err(cur, cded)[0] / r['nmse'])
        r16 = d['variants'].get('futmf2_16') or d['variants'].get('futmf216')
        if r16 is not None and np.isfinite(r16['nmse']):
            out['qp16'].append(e2 / r16['nmse'])
    return {k: (S.med(v), v) for k, v in out.items()}


a = stats(512, 64, [500, 501, 502]); b = stats(256, 32, list(range(200, 205)))
sc = {}
sc['P10'] = dict(k3_512=a['k3'][0], holds=(1e-4 <= a['k3'][0] <= 4e-4))
sc['P11'] = dict(qp_over_q3_512=a['qp_q'][0], qp16_512=a['qp16'][0], qp16_256=b['qp16'][0],
                 holds=(a['qp_q'][0] >= 0.6 and a['qp16'][0] < b['qp16'][0]))
sc['P12'] = dict(Gded_512=a['Gded'][0], Gded_256=b['Gded'][0], holds=(a['Gded'][0] <= b['Gded'][0]))
sc['P13'] = dict(k2G_512=a['k2G'][0], k2G_256=b['k2G'][0], holds=(a['k2G'][0] < b['k2G'][0]))
sc['raw'] = dict(n512=a, n256=b)
json.dump(sc, open(os.path.join(S.RES, 'score_amend1.json'), 'w'), indent=1, default=float)
for k in ('P10', 'P11', 'P12', 'P13'):
    print(k, 'HOLDS' if sc[k]['holds'] else 'FAILS', {kk: vv for kk, vv in sc[k].items() if kk != 'holds'})
