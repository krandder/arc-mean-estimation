"""Markdown tables for the lane report, printed from results/*.json."""
import json, os, math
import numpy as np

W = '/home/agent/workspaces/mats/work/gram-chain/'
A = json.load(open(W + 'results/partA_scores.json'))
print('### Table A (two replicas, independent noise)')
print('| n | median delta/delta*(Q) | mean | SD(delta/delta*) n^{1/3} | SD(ell) n^{1/3} (limit 1.887) | 1/e lag: angle / ratio / log q (layers) |')
print('|---|---|---|---|---|---|')
for n in sorted(A['r2'], key=int):
    r = A['r2'][n]
    L = r['ac_lag_1e']
    print('| %s | %.3f (%.3f) | %.4f (%.4f) | %.2f | %.3f (%.3f) | %s / %s / %s |' % (
        n, r['median_ratio'], r['median_ratio_se'], r['mean_ratio'], r['mean_ratio_se'], r['sd_ratio_n13'],
        r['sd_ell_n13'], r['sd_ell_n13_se'], L['ratio'], L['ell'], L['logq']))
print()
print('### Table A4 (four replicas: participation ratio of the direction cloud)')
print('| n | PR_w (4-replica) | ratio-of-means PR | 1/k value | 1.0865 n^{2/3} | across-net CV of tr C (chain) |')
print('|---|---|---|---|---|---|')
PRk = {16: 9.7, 32: 15.2, 64: 22.3, 128: 30.8, 256: 41.0, 512: 52.6, 1024: 65.8}
for n in sorted(A['r4'], key=int):
    r = A['r4'][n]
    print('| %s | %.2f (%.2f) | %.2f | %.1f | %.1f | %.3f |' % (n, r['PR_4rep'], r['PR_4rep_se'], r['PR_rom'], PRk[int(n)],
                                                       1.0865 * int(n) ** (2 / 3), r['cv_chain']))
print()
if A['share']:
    print('### Table A-share (noise-stability curves C(t) of the hidden direction)')
    for n in sorted(A['share'], key=int):
        rows = A['share'][n]
        s = []
        for kind in ('corr', 'coord', 'block'):
            vals = ['%.3f' % x['C'] for x in rows if x['kind'] == kind and x['t'] in (0.25, 0.5, 0.75)]
            ge = [x['G_over_eps'] for x in rows if x['kind'] == kind and abs(x['t'] - 0.99) < 1e-9]
            ge97 = [x['G_over_eps'] for x in rows if x['kind'] == kind and abs(x['t'] - 0.97) < 1e-9]
            s.append('%s %s, G/eps(0.01) %s, (0.03) %s' % (kind, '/'.join(vals), ('%.2f' % ge[0]) if ge else '-',
                                                        ('%.2f' % ge97[0]) if ge97 else '-'))
        anti = [x for x in rows if x['kind'] == 'corr' and x['t'] == -1.0]
        print('n = %s: %s; antithetic E delta(-1)/E delta(0) = %s' % (n, '; '.join(s), ('%.3f' % (1 - anti[0]['C'])) if anti else '-'))
print()
for nm in ('partB_scores.json', 'partC_scores.json'):
    f = W + 'results/' + nm
    if os.path.exists(f):
        print(nm, json.dumps(json.load(open(f))['scores'], default=str)[:3000])
