"""POST HOC: the D1 half-width variants completed with the rank guard (scratch/run_k3p_guard.py, eval_G.sh).
(1) reproduction: guarded reruns of registered successes vs the registered nMSE; (2) the full half-width table: per
width and future kind, the retained factor e_k3 / e_proj on every net (registered value where it succeeded, guarded
value where the registered run returned NaN), median, range, nets beating k3, and the gain over RQMC at the
implemented cost. Side-effect free apart from results/guard.json."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score_helpers as S  # noqa: E402

out = {'reproduction': [], 'half': {}}
for n, L, seeds in S.CONF:
    for kind in ('futv', 'futmf2'):
        v = f'{kind}{n // 2}' if kind == 'futv' else f'{kind}_{n // 2}'
        rf, src, G = [], [], []
        for s in seeds:
            d = S.load('k3p', n, L, s)
            gp = os.path.join(S.RUNS, f'k3p_n{n}_L{L}_s{s}_guard.json')
            g = json.load(open(gp)) if os.path.exists(gp) else None
            if d is None or v not in d['variants']:
                continue
            e3 = d['variants']['none']['nmse']; reg = d['variants'][v]
            if g is not None and v in g['variants'] and np.isfinite(reg['nmse']):
                out['reproduction'].append(dict(n=n, seed=s, variant=v, registered=reg['nmse'],
                                                guarded=g['variants'][v]['nmse'],
                                                rel_diff=abs(g['variants'][v]['nmse'] / reg['nmse'] - 1),
                                                guard=g['variants'][v]['guard']))
            if np.isfinite(reg['nmse']):
                e, c, which = reg['nmse'], reg['passes'], 'registered'
            elif g is not None and v in g['variants'] and np.isfinite(g['variants'][v]['nmse']):
                e, c, which = g['variants'][v]['nmse'], g['variants'][v]['passes'], 'guarded'
            else:
                continue
            rf.append(e3 / e); src.append((s, which, round(e3 / e, 3)))
            G.append(S.rqmc_err(S.rqmc_curve(n, L, s), c)[0] / e)
        if rf:
            out['half'][f'{n}:{v}'] = dict(nets=len(rf), median=S.med(rf), min=min(rf), max=max(rf),
                                           beats_k3=sum(x >= 1 for x in rf), per_net=src, G_impl_median=S.med(G),
                                           G_impl_max=max(G))
json.dump(out, open(os.path.join(S.RES, 'guard.json'), 'w'), indent=1, default=float)
for r in out['reproduction']:
    print(f'repro n={r["n"]} s={r["seed"]} {r["variant"]}: registered {r["registered"]:.4e} guarded {r["guarded"]:.4e} '
          f'rel {r["rel_diff"]:.1e} guard {r["guard"]}')
for k, v in out['half'].items():
    print(f'{k}: {v["nets"]} nets, retained median {v["median"]:.3f} (range {v["min"]:.3f}-{v["max"]:.3f}), beats k3 on '
          f'{v["beats_k3"]}, G at implemented cost median {v["G_impl_median"]:.3g} max {v["G_impl_max"]:.3g}; {v["per_net"]}')
