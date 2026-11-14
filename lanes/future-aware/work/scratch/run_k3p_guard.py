"""POST HOC: scratch/run_k3p.py with the rank guard of lib/fa_kprop_guard.py (the frozen projection hook is unchanged;
whiten and the future features keep only the S-positive, R-relevant part of the kept span). Same costs, same seeds.
usage: run_k3p_guard.py N L SEED --variants futv128,futmf2_128 -> runs/k3p_n{N}_L{L}_s{SEED}_guard.json"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa, fa2, fa_kprop as FK, fa_kprop_guard as FG  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--variants', required=True); ap.add_argument('--tag', default='_guard')
ap.add_argument('--mvjp', type=int, default=11)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'k3p_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa2.load_net(n, L, seed)   # this lane's truths first (n = 512), else arc-update's (identical for n <= 256)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
res = json.load(open(out)) if os.path.exists(out) else dict(n=n, L=L, seed=seed, V=V, args=vars(args), variants={})
probs, k2run = FK.k2_gate_probs(W)
Jmf = FK.mf_jacobians(W, probs)
Rmf = FK.mf_relevance(W, probs)
res['k2'] = dict(nmse=float(((k2run['mean'] - Y) ** 2).sum() / V), passes=k2run['flops'] / PASS)
mf_cost = (k2run['flops'] + L * 2.0 * n ** 3) / PASS
for v in args.variants.split(','):
    for kd in ('futmf2', 'futmf', 'futv', 'pca'):
        if v.startswith(kd):
            kind, k = kd, int(v[len(kd):].lstrip('_'))
            break
    r = FG.arc_k3_proj_guard(W, kind=kind, k=k, Jmf=Jmf, mvjp=1 << args.mvjp, seed=seed, Rmf=Rmf, factor=True)
    passes = (r['flops'] + r['hook_flops'] + r['backward_flops']) / PASS + (mf_cost if kind in ('futmf', 'futmf2') else 0.0)
    row = dict(kind=kind, k=k, nmse=float(((r['mean'] - Y) ** 2).sum() / V), passes=passes, guard=r['guard'],
               secs=r['secs'])
    res['variants'][v] = row
    print(f'n={n} L={L} s={seed} {v} (guard): nMSE {row["nmse"]:.3e} passes {passes:.0f} guard {r["guard"]} '
          f'{r["secs"]:.0f}s', flush=True)
    json.dump(res, open(out, 'w'))
print('done', out, flush=True)
