"""POST HOC (not registered): paired single-cut comparison of future vs PCA vs random directions (B1). With common random
numbers the per-net difference b2(cond_pca k) - b2(cond_futnl k) has less noise than either value. Reports, per width,
cut and k, the median over nets of each b2, the median paired difference, the number of nets where the future
directions are better, and the noise scale (median |b2| of the 'true' variant, whose expectation is 0)."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, '..', 'runs'); RES = os.path.join(HERE, '..', 'results')
CONF = [(64, 8, range(300, 308)), (128, 16, range(300, 308)), (256, 32, range(200, 205))]
out = {}
lines = []
for n, L, seeds in CONF:
    ds = [json.load(open(os.path.join(RUNS, f'cut_n{n}_L{L}_s{s}.json'))) for s in seeds
          if os.path.exists(os.path.join(RUNS, f'cut_n{n}_L{L}_s{s}.json'))]
    if not ds:
        continue
    cuts = sorted({int(c) for d in ds for c in d['cuts']})
    for k in sorted({16, n // 4}):
        for c in cuts:
            rows = [d['cuts'][str(c)]['variants'] for d in ds if str(c) in d['cuts']]
            f = [r[f'cond_futnl{k}']['b2'] for r in rows if f'cond_futnl{k}' in r]
            p = [r[f'cond_pca{k}']['b2'] for r in rows if f'cond_pca{k}' in r]
            q = [r[f'cond_rand{k}']['b2'] for r in rows if f'cond_rand{k}' in r]
            g = [r['gauss']['b2'] for r in rows]
            t = [abs(r['true']['b2']) for r in rows]
            if not f or not p:
                continue
            diff = [b - a for a, b in zip(f, p)]
            key = f'n{n}_l{c}_k{k}'
            out[key] = dict(nets=len(f), gauss=float(np.median(g)), futnl=float(np.median(f)), pca=float(np.median(p)),
                            rand=float(np.median(q)) if q else None, diff_median=float(np.median(diff)),
                            future_better=int(sum(1 for x in diff if x > 0)), noise=float(np.median(t)))
            lines.append(f'n={n:3d} l={c:2d} k={k:3d}: gauss {np.median(g):.2e} futnl {np.median(f):.2e} pca {np.median(p):.2e} '
                         f'rand {np.median(q) if q else float("nan"):.2e} | pca - futnl median {np.median(diff):+.2e}, future better on '
                         f'{sum(1 for x in diff if x > 0)}/{len(diff)} nets | noise {np.median(t):.1e}')
json.dump(out, open(os.path.join(RES, 'paired_cut.json'), 'w'), indent=1)
print('\n'.join(lines))
