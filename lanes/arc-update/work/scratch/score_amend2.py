"""Score PREREG Amendment 2 (radial lead) on nets 201-204; report net 200 separately.
R1: median over nets of Gamma_rad(l)/Gamma*_2(l) <= 0.33 at >= 2 of l = 1, 2, 4.
R2: median over nets of Z = max_{l in {8,16,24}} Gamma_rad(l) >= 5e-5.
R3: cost (passes) at which RQMC's nMSE equals Z is <= 2e4 on >= 3 of 4 nets.
Reporting: X = RQMC nMSE at the assumed closure cost (393 and 1200 passes) / Z; also MC and Kerdock (0.40/N).
usage: score_amend2.py [OUT_JSON]"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_lad as SL  # noqa: E402

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')


def b2(A, model, l):
    for r in A['models'][model]['rows']:
        if r['l'] == l:
            return r['b2']
    return float('nan')


def rqmc_cost_for(cur, target):
    Ns, es = cur
    if target >= es[0]:
        return float(Ns[0] * es[0] / target)
    if target <= es[-1]:
        return float(Ns[-1] * es[-1] / target)
    return float(np.exp(np.interp(-np.log(target), -np.log(es), np.log(Ns))))


out = {}
for s in (200, 201, 202, 203, 204):
    p = os.path.join(RUNS, f'attr_s{s}.json')
    if not os.path.exists(p):
        continue
    A = json.load(open(p))
    ratios = {l: b2(A, 'oracle_radgauss', l) / b2(A, 'oracle_gauss', l) for l in (1, 2, 4)}
    Z = max(b2(A, 'oracle_radgauss', l) for l in (8, 16, 24))
    cur = SL.rqmc_curve(256, 32, s)
    row = dict(ratios_early=ratios, Z=Z)
    if cur is not None:
        row['rqmc_cost_at_Z'] = rqmc_cost_for(cur, Z)
        for c in (393, 1200):
            row[f'X_rqmc_at_{c}'] = SL.rqmc_at(cur, c) / Z
            row[f'X_mc_at_{c}'] = (1.0 / c) / Z
            row[f'X_kerdock_at_{c}'] = (0.40 / c) / Z
    out[s] = row
ev = [s for s in out if s != 200]
sc = {}
if ev:
    med_ratio = {l: float(np.median([out[s]['ratios_early'][l] for s in ev])) for l in (1, 2, 4)}
    sc['R1'] = dict(median_ratios=med_ratio, hit=bool(sum(v <= 0.33 for v in med_ratio.values()) >= 2))
    medZ = float(np.median([out[s]['Z'] for s in ev]))
    sc['R2'] = dict(median_Z=medZ, hit=bool(medZ >= 5e-5))
    costs = [out[s].get('rqmc_cost_at_Z', float('nan')) for s in ev]
    sc['R3'] = dict(costs=costs, hit=bool(sum(c <= 2e4 for c in costs if np.isfinite(c)) >= 3))
print(json.dumps(dict(per_net=out, scores=sc), indent=1, default=float))
if len(sys.argv) > 1:
    json.dump(dict(per_net=out, scores=sc), open(sys.argv[1], 'w'), indent=1, default=float)
