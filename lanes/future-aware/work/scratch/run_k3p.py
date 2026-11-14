"""Deductive (b)/(a): ARC's K = 3 'simple' cumulant propagation with the third cumulant restricted, at every hidden
layer, to a k-dim feature span (lib/fa_kprop.py), against ARC's k2 and full k3 on the same net.
Variants: none (= ARC k3), pca<k>, futmf<k> (deductive mean-field backward sweep), futv<k> (VJPs at samples of the
method's own Gaussian state; sampled backward pass). Cost in passes = (ARC counter flops + hook flops + backward
flops) / (2 n^2 L), plus for futmf the K = 2 forward run and the mean-field sweep.
usage: run_k3p.py N L SEED --variants none,pca16,futmf16,futv16 [--tag T] -> runs/k3p_n{N}_L{L}_s{SEED}{T}.json"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import fa, fa_kprop as FK  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--variants', default='none,pca16,futmf16,futv16'); ap.add_argument('--tag', default='')
ap.add_argument('--mvjp', type=int, default=11)
ap.add_argument('--dense', action='store_true')
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'k3p_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
t0 = time.time()
res = dict(n=n, L=L, seed=seed, V=V, args=vars(args), variants={})
probs, k2run = FK.k2_gate_probs(W)
Jmf = FK.mf_jacobians(W, probs)
Rmf = FK.mf_relevance(W, probs)
res['k2'] = dict(nmse=float(((k2run['mean'] - Y) ** 2).sum() / V), passes=k2run['flops'] / PASS)
mf_cost = (k2run['flops'] + L * 2.0 * n ** 3) / PASS
print(f'n={n} L={L} s={seed} k2: nMSE {res["k2"]["nmse"]:.3e} passes {res["k2"]["passes"]:.0f}', flush=True)
for v in args.variants.split(','):
    if v == 'none':
        kind, k = 'none', 0
    else:
        for kd in ('futmf2', 'futmf', 'futv', 'pca'):
            if v.startswith(kd):
                kind, k = kd, int(v[len(kd):].lstrip('_'))
                break
    r = FK.arc_k3_proj(W, kind=kind, k=k, Jmf=Jmf, mvjp=1 << args.mvjp, seed=seed, Rmf=Rmf, factor=not args.dense)
    passes = (r['flops'] + r['hook_flops'] + r['backward_flops']) / PASS + (mf_cost if kind in ('futmf', 'futmf2') else 0.0)
    row = dict(kind=kind, k=k, nmse=float(((r['mean'] - Y) ** 2).sum() / V), passes=passes,
               arc_passes=r['flops'] / PASS, hook_passes=r['hook_flops'] / PASS, backward_passes=r['backward_flops'] / PASS,
               secs=r['secs'])
    res['variants'][v] = row
    print(f'n={n} L={L} s={seed} {v}: nMSE {row["nmse"]:.3e} passes {passes:.0f} (ARC {row["arc_passes"]:.0f}, '
          f'hook {row["hook_passes"]:.0f}, backward {row["backward_passes"]:.0f}) {r["secs"]:.0f}s', flush=True)
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
