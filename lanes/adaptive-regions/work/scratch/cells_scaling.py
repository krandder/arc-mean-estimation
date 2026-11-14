"""How many exact linear pieces (joint gate-pattern cones) does an n x 4 ReLU net need? MEASURED (exploratory).

For each width, 2^20 training (advice) paths list the cells; cells are ranked by training frequency; 2^20 held-out
paths measure the coverage of the top-k cells. Reported: distinct cells seen, cells needed (in training rank order) for
99% / 99.99% held-out coverage, held-out coverage of all training cells, per-layer distinct patterns, and the mean
number of non-redundant constraints per cell (LP) for the 50 most frequent cells (the facet count of the exact formula).
Usage: cells_scaling.py --widths 4,6,8,12,16 --seeds 9701,9702,9703
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--widths', default='4,6,8,12,16')
ap.add_argument('--seeds', default='9701,9702,9703')
ap.add_argument('--L', type=int, default=4)
ap.add_argument('--log2', type=int, default=20)
ap.add_argument('--out', default=None)
args = ap.parse_args()
L = args.L
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', 'cells_scaling.json')
res = []


def pats(W, X):
    h = X; P = []
    for l in range(L):
        z = h @ W[l].T; P.append(z > 0); h = np.maximum(z, 0)
    return np.concatenate(P, 1)


def nonredundant(G):
    """Count constraints g_i . x >= 0 that are not implied by the others (LP: minimise g_i . x over the others, |x|_inf <= 1)."""
    G = G[np.linalg.norm(G, axis=1) > 1e-12]; G = G / np.linalg.norm(G, axis=1, keepdims=True)
    G = np.unique(np.round(G, 10), axis=0)
    cnt = 0
    for i in range(len(G)):
        A = -np.delete(G, i, 0)
        r = linprog(G[i], A_ub=A, b_ub=np.zeros(len(A)), bounds=[(-1, 1)] * G.shape[1], method='highs')
        if r.status == 0 and r.fun < -1e-9:
            cnt += 1
    return cnt


for n in [int(w) for w in args.widths.split(',')]:
    for seed in [int(s) for s in args.seeds.split(',')]:
        t0 = time.time()
        W = [w.double().numpy() for w in ar.weights(seed, n, L)]
        rs = np.random.RandomState(seed)
        Ptr = pats(W, rs.standard_normal((1 << args.log2, n)))
        Pho = pats(W, np.random.RandomState(seed + 1).standard_normal((1 << args.log2, n)))
        ktr = np.packbits(Ptr, axis=1); kho = np.packbits(Pho, axis=1)
        keys, inv, cnt = np.unique(ktr, axis=0, return_inverse=True, return_counts=True)
        order = np.argsort(-cnt)
        rank = {bytes(keys[i]): r for r, i in enumerate(order)}
        ho_rank = np.array([rank.get(bytes(k), -1) for k in kho])
        seen = ho_rank >= 0
        cov_all = float(seen.mean())
        sr = np.sort(ho_rank[seen])
        def need(q):
            m = int(np.ceil(q * len(ho_rank)))
            return int(sr[m - 1] + 1) if m <= len(sr) else None   # None: not reached by all training cells
        per_layer = [int(len(np.unique(np.packbits(Ptr[:, l * n:(l + 1) * n], axis=1), axis=0))) for l in range(L)]
        # facet counts for the top cells
        fc = []
        for ci in order[:50]:
            pat = Ptr[np.argmax(inv.ravel() == ci)].reshape(L, n)
            M = np.eye(n); rows = []
            for l in range(L):
                Gl = W[l] @ M; rows.append(np.where(pat[l][:, None], Gl, -Gl)); M = pat[l][:, None] * Gl
            fc.append(nonredundant(np.concatenate(rows)))
        r = dict(n=n, L=L, seed=seed, paths=1 << args.log2, cells_seen=int(len(keys)), heldout_cov_all=cov_all,
                 cells_for_99=need(0.99), cells_for_9999=need(0.9999), per_layer_patterns=per_layer,
                 mean_facets_top50=float(np.mean(fc)), max_facets_top50=int(np.max(fc)), secs=time.time() - t0)
        res.append(r); print(json.dumps(r), flush=True)
        json.dump(res, open(out, 'w'))
