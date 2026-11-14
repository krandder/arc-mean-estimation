"""Score PREREG Part S2 from runs/S_chain (run from the lane's work dir). Writes results/S2_scores.json."""
import json
import os
import sys

import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else 'runs/S_chain'
CFG = [(16, 4), (16, 16), (32, 8), (32, 32)]
EVAL = [5000, 5001, 5002]


def get(n, L, s, cls):
    p = os.path.join(D, f'C_n{n}_L{L}_s{s}_{cls}.json')
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    return d if 'per_b' in d else None          # placeholders for skipped chains


S = {}
c1, c1b, c2, sanity, c3, c4, c5 = [], [], [], [], [], [], []
for n, L in CFG:
    for s in EVAL:
        r = get(n, L, s, 'local')
        u = get(n, L, s, 'unres')
        if r is not None:
            for b, ent in r['per_b'].items():
                for i, tr in enumerate(ent['transitions']):
                    acc1 = tr['majority_ptf_acc']['1']
                    c1.append(acc1 >= 0.9)
                    ltf = tr['baselines']['ltf']['ptf_acc']['1']
                    perm = tr['baselines']['perm']['ptf_acc']['1']
                    c1b.append(abs(acc1 - ltf) < abs(acc1 - perm))
                    W = tr['learned_T']['W_by_degree']
                    c2.append(sum(W[:3]) >= 0.8)
                    if int(b) >= 8:
                        for k in ('perm', 'xor'):
                            sanity.append(sum(tr['baselines'][k]['W_by_degree'][:3]) <= 0.1)
                    c4.append(dict(n=n, L=L, seed=s, b=int(b), i=i, H_out_given_in=tr['H_out_given_in'],
                                   H_in=tr['H_in'], coverage=tr['coverage']))
                c5.append(ent['chain_nmse'][-1] <= 1.5 * ent['own_nmse'][-1])
        if u is not None:
            for b, ent in u['per_b'].items():
                for tr in ent['transitions']:
                    c3.append(tr['learned_T']['n_relevant'] <= 2)
f = lambda x: (float(np.mean(x)) if x else None)  # noqa: E731
S['S2.1'] = dict(frac_ptf1=f(c1), frac_closer_ltf=f(c1b), n=len(c1),
                 hit=(bool(c1) and f(c1) >= 0.75 and f(c1b) >= 0.9))
S['S2.2'] = dict(frac=f(c2), sanity_frac=f(sanity), n=len(c2), hit=(bool(c2) and f(c2) >= 0.75))
S['S2.3'] = dict(frac=f(c3), n=len(c3), hit=(bool(c3) and f(c3) >= 0.75))
S['S2.4'] = dict(cells=c4, hit=None)
S['S2.5'] = dict(frac=f(c5), n=len(c5), hit=(bool(c5) and f(c5) >= 0.75))
os.makedirs('results', exist_ok=True)
json.dump(S, open('results/S2_scores.json', 'w'), indent=1)
for k, v in S.items():
    print(k, 'HIT' if v['hit'] else ('MISS' if v['hit'] is False else 'n/a'),
          {kk: vv for kk, vv in v.items() if kk != 'cells'})
