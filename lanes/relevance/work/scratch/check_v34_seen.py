import json, math, sys
import numpy as np
sys.path.insert(0, '/home/agent/workspaces/mats/work/relevance/lib')
import rel, theory_v2 as t2, theory_v34_astra as t34, theory_v33 as t33
B = '/home/agent/workspaces/mats/work/relevance/'
out = []
for seed in range(4000, 4006):
    Ws = rel.input_weights(seed, 256, 32)
    for o in json.load(open(B + f'runs/eval_arc_n256_L32_seed{seed}.json')):
        st = t34.astra_stats(Ws, o['l'], np.random.default_rng(8000000 + 100 * seed + o['l']))
        p = t34.predict_astra(o, st)
        V = o['V_gauss'][0]; D = o['J1_gauss'][0] / V; s1 = o['V1_gauss'][0] / V
        G = t33.measured_R(o)
        out.append(dict(seed=seed, l=o['l'], D=D, s1=s1, G=G, **p))
        print(seed, o['l'], 'Gamma %.3f / %.3f simple %.3f  D_A/D %.2f  s1_A %.3f / %.3f' % (p['gamma'], G, p['gamma_simple'], p['D_A'] / D, p['s1_A'], s1), flush=True)
e = [abs(r['gamma'] / r['G'] - 1) for r in out]; es = [abs(r['gamma_simple'] / r['G'] - 1) for r in out]
print('Gamma rel err median %.3f max %.3f; simple %.3f %.3f' % (np.median(e), max(e), np.median(es), max(es)))
print('D_A in band', sum(0.75 <= r['D_A'] / r['D'] <= 1.33 for r in out), 'of', len(out), '; l<=8', sum(0.75 <= r['D_A'] / r['D'] <= 1.33 for r in out if r['l'] <= 8))
print('s1_A within 0.08', sum(abs(r['s1_A'] - r['s1']) <= 0.08 for r in out), 'of', len(out))
json.dump(out, open(B + 'results/v34_seen_check.json', 'w'), indent=1)
