"""EXPLORATORY (not registered): ARC's dense K = 4 'simple' propagation with the third- and fourth-cumulant cores
projected at every hidden layer on a k-dim span (lib/fa_kprop4.py), against ARC's k2, k3 and k4 on the same net.
Question: does the low-rank (future-weighted) truncation that keeps order-3 accuracy (D1) also keep order 4?
usage: run_k4p.py N L SEED --variants none,futv8,pca8 [--orders 3,4] [--tag T] -> runs/k4p_n{N}_L{L}_s{SEED}{T}.json"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa, fa_kprop as FK, fa_kprop4 as FK4  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--variants', default='none,futv8,pca8'); ap.add_argument('--orders', default='3,4')
ap.add_argument('--tag', default=''); ap.add_argument('--mvjp', type=int, default=11)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
orders = tuple(int(x) for x in args.orders.split(','))
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'k4p_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
t0 = time.time()
res = dict(n=n, L=L, seed=seed, V=V, args=vars(args), variants={}, exploratory=True)
probs, k2run = FK.k2_gate_probs(W)
Rmf = FK.mf_relevance(W, probs)
res['k2'] = dict(nmse=float(((k2run['mean'] - Y) ** 2).sum() / V), passes=k2run['flops'] / PASS)
k3 = FK.arc_k3_proj(W, kind='none', k=0)
res['k3'] = dict(nmse=float(((k3['mean'] - Y) ** 2).sum() / V), passes=k3['flops'] / PASS)
print(f'n={n} L={L} s={seed} k2 {res["k2"]["nmse"]:.3e} k3 {res["k3"]["nmse"]:.3e}', flush=True)
for v in args.variants.split(','):
    if v == 'none':
        kind, k = 'none', 0
    else:
        for kd in ('futmf2', 'futv', 'pca'):
            if v.startswith(kd):
                kind, k = kd, int(v[len(kd):].lstrip('_'))
                break
    r = FK4.arc_kK_proj(W, K_max=4, kind=kind, k=k, Rmf=Rmf, mvjp=1 << args.mvjp, seed=seed, orders=orders)
    row = dict(kind=kind, k=k, nmse=float(((r['mean'] - Y) ** 2).sum() / V),
               passes=(r['flops'] + r['hook_flops'] + r['backward_flops']) / PASS, arc_passes=r['flops'] / PASS,
               secs=r['secs'], tower=r['tower'])
    res['variants'][v] = row
    print(f'n={n} L={L} s={seed} k4 {v}: nMSE {row["nmse"]:.3e} (ARC passes {row["arc_passes"]:.0f}) {r["secs"]:.0f}s',
          flush=True)
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
