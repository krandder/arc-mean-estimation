"""Depth saturation of the number of linear regions at small width (Kelvin via main, 3 Nov). MEASURED (exploratory).
One deep net per (n, seed); the cells of the depth-l prefix net are the distinct gate prefixes (layers 1..l), so one run
gives the whole cells-vs-depth curve. Also per layer: distinct patterns, dead units (never on), always-on units, the
participation ratio of E[h_l h_l^T] (effective dimension of the image), and held-out coverage of the seen prefixes.
Usage: depth_saturation.py --ns 4,5,6,7,8 --seeds 9701,9702,9703 --L 24
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--ns', default='4,5,6,7,8'); ap.add_argument('--seeds', default='9701,9702,9703')
ap.add_argument('--L', type=int, default=24); ap.add_argument('--log2', type=int, default=20)
args = ap.parse_args()
L = args.L; N = 1 << args.log2
out = []
for n in [int(x) for x in args.ns.split(',')]:
    for seed in [int(x) for x in args.seeds.split(',')]:
        t0 = time.time()
        W = [w.double().numpy() for w in ar.weights(seed, n, L)]
        rows = []
        for split in ('train', 'heldout'):
            X = np.random.RandomState(seed + (0 if split == 'train' else 1)).standard_normal((N, n))
            h = X; prefix = np.zeros(N, dtype=np.int64); per = []
            seen = None
            for l in range(L):
                z = h @ W[l].T; g = z > 0; h = z * g
                lp = np.unique(np.packbits(g, axis=1), axis=0, return_inverse=True)[1].ravel()
                prefix = np.unique(np.stack([prefix, lp], 1), axis=0, return_inverse=True)[1].ravel()
                C = h.T @ h / N; ev = np.linalg.eigvalsh(C); pr = float(ev.sum() ** 2 / max((ev ** 2).sum(), 1e-300))
                per.append(dict(layer=l + 1, patterns=int(lp.max() + 1), cells=int(prefix.max() + 1), dead=int((~g.any(0)).sum()),
                                always_on=int(g.all(0).sum()), part_ratio=pr))
            rows.append(per)
        # held-out coverage needs a joint key: recompute with both splits together for each depth (cheap enough)
        X = np.concatenate([np.random.RandomState(seed).standard_normal((N, n)), np.random.RandomState(seed + 1).standard_normal((N, n))])
        h = X; prefix = np.zeros(2 * N, dtype=np.int64); cov = []
        for l in range(L):
            z = h @ W[l].T; g = z > 0; h = z * g
            lp = np.unique(np.packbits(g, axis=1), axis=0, return_inverse=True)[1].ravel()
            prefix = np.unique(np.stack([prefix, lp], 1), axis=0, return_inverse=True)[1].ravel()
            tr = np.zeros(prefix.max() + 1, bool); tr[prefix[:N]] = True
            cov.append(float(tr[prefix[N:]].mean()))
        r = dict(n=n, seed=seed, L=L, paths=N, per_layer=rows[0], heldout_cov=cov, secs=time.time() - t0)
        out.append(r)
        print(f"n={n} seed={seed}: cells by depth {[d['cells'] for d in rows[0]]}", flush=True)
        print(f"   patterns {[d['patterns'] for d in rows[0]]}  dead {[d['dead'] for d in rows[0]]}  on {[d['always_on'] for d in rows[0]]}", flush=True)
        print(f"   PR {[round(d['part_ratio'], 2) for d in rows[0]]}  held-out cov {[round(c, 4) for c in cov]}", flush=True)
        json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', 'depth_saturation.json'), 'w'))
