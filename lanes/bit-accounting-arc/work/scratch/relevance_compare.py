"""Extract the relevance lane's per-layer quantities for comparison (read-only use of work/relevance/runs):
N(l, eps) = smallest tested k with residual / V <= eps, best of three bases (active subspace, cloud axes, degree-1),
Gaussian convention (reproduces its table); its water-filling prediction R_1(eps) = reverse water-filling over the
degree-1 relevance spectrum R1_evals (top 96) at distortion eps * V_1 (DEFINITIONS 3); and reverse water-filling over
the active-subspace spectrum AS_evals (top 96) at eps * V (the high-resolution local price).
usage: relevance_compare.py <out json>
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import vra  # noqa: E402

REL = '/home/agent/workspaces/mats/work/relevance/runs'
out = {}
files = [(f'arc', s, f'{REL}/eval_arc_n256_L32_seed{s}.json') for s in (4000, 4001, 4002, 4003)] + \
        [(f'nd', s, f'{REL}/eval_nd_n8_L256_seed{s}.json') for s in (203, 216, 217, 220, 221, 223)]
for fam, seed, p in files:
    if not os.path.exists(p):
        continue
    for c in json.load(open(p)):
        l = c['l']
        V = c['V_gauss'][0]
        V1 = c['V1_gauss'][0]
        rec = dict(V_gauss=V, V1_gauss=V1, s1=V1 / V, AS_trace=c.get('AS_trace'), cloud_PR=c.get('cloud_PR'))
        for eps in (0.1, 0.03, 0.01, 0.003, 0.001):
            N = None
            for key in ('res_AS_gauss', 'res_PCA_gauss', 'res_R1_gauss'):
                if key not in c:
                    continue
                for k in sorted(int(x) for x in c[key]):
                    if c[key][str(k)][0] / V <= eps:
                        N = k if N is None else min(N, k)
                        break
            rec[f'N_{eps}'] = N
            rec[f'R1wf_{eps}'] = vra.rwf_rate(c['R1_evals'], eps * V1)
            rec[f'ASwf_{eps}'] = vra.rwf_rate(c['AS_evals'], eps * V)
        out[f'{fam}_s{seed}_l{l}'] = rec
json.dump(out, open(sys.argv[1], 'w'), indent=1)
for k, v in out.items():
    if k.startswith('arc_s4000') or k.startswith('nd_s203'):
        print(k, {kk: (round(vv, 1) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk.startswith(('N_', 'R1wf', 'ASwf', 's1'))})
