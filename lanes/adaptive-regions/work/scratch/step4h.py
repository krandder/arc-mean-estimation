"""Hard-cell oracle (main, ~17:45Z): one exact linear map per observed gate pattern, sharp membership.

Full coordinates (d = n, so the projection is exact). Per layer l -> l+1 the cells are the sign patterns of the
layer-(l+1) pre-activations; the P most frequent patterns on the pilot paths are kept, each with its exact map
h_{l+1} = D_pattern W h_l. A population component N(m, S) is propagated by Monte Carlo draws (4,096, standardised):
draws whose pattern is kept use their exact map (identical to the true layer); the others use the most frequent
pattern's map (P < all) or the soft-gate oracle prediction. After each layer the component is re-fitted as a Gaussian
(mean, covariance of the mapped draws): with all patterns kept the only error is that per-layer Gaussian re-fit.
Compared with the soft-gate oracle of step4c at K = P. MEASURED (exploratory). Usage: step4h.py SEED n L --Ps 1,16,256,4096,all
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--Ps', default='1,4,16,64,256,1024,4096,all')
ap.add_argument('--log2pilot', type=int, default=16)
ap.add_argument('--draws', type=int, default=4096)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4h_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = [w.double().numpy() for w in ar.weights(seed, n, L)]
rng = np.random.RandomState(seed)
NP = 1 << args.log2pilot
X = rng.standard_normal((NP, n))
H = [X]
for l in range(L):
    H.append(np.maximum(H[-1] @ W[l].T, 0))
# patterns per layer (layer l+1 signs), ranked by frequency
pat = []
for l in range(L):
    bits = (H[l] @ W[l].T > 0)
    keys = np.packbits(bits, axis=1)
    keys = [bytes(k) for k in keys]
    uniq, cnt = np.unique(np.array(keys, dtype=object), return_counts=True)
    order = np.argsort(-cnt)
    pat.append((uniq[order], cnt[order]))
    print(f'layer {l + 1}: {len(uniq)} distinct patterns among {NP} pilot paths; top-1 share {cnt[order][0] / NP:.4f}', flush=True)
# truth
S1 = np.zeros(n); S2 = np.zeros(n); gT = np.random.RandomState(4242); NTr = 1 << 20
for _ in range(NTr // 65536):
    h = gT.standard_normal((65536, n))
    for l in range(L):
        h = np.maximum(h @ W[l].T, 0)
    S1 += h.sum(0); S2 += (h * h).sum(0)
mu_true = S1 / NTr; V_true = float((S2 / NTr - mu_true ** 2).sum())
E = rng.standard_normal((args.draws, n)); E -= E.mean(0); E = E @ np.linalg.inv(np.linalg.cholesky(E.T @ E / len(E))).T


def propagate(P):
    m, S = np.zeros(n), np.eye(n)
    for l in range(L):
        Lc = np.linalg.cholesky(S + 1e-12 * np.eye(n))
        Z = m + E @ Lc.T
        pre = Z @ W[l].T
        bits = pre > 0
        if P == 'all':
            Hn = np.maximum(pre, 0)
        else:
            keys = [bytes(k) for k in np.packbits(bits, axis=1)]
            kept = set(pat[l][0][:P].tolist())
            top = np.unpackbits(np.frombuffer(pat[l][0][0], dtype=np.uint8))[:n].astype(bool)
            inkept = np.array([k in kept for k in keys])
            Hn = np.where(inkept[:, None], np.maximum(pre, 0), pre * top[None, :])
        m = Hn.mean(0); D = Hn - m; S = D.T @ D / len(Hn)
    return m


res = dict(n=n, L=L, seed=seed, NP=NP, draws=args.draws, V_true=V_true, rows=[],
           distinct_patterns=[int(len(p[0])) for p in pat])
for Pspec in args.Ps.split(','):
    P = 'all' if Pspec == 'all' else int(Pspec)
    m = propagate(P)
    e = float(((m - mu_true) ** 2).sum() / V_true)
    res['rows'].append(dict(P=Pspec, nmse=e))
    print(f'patterns kept per layer {Pspec}: estimand nMSE {e:.2e}', flush=True)
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
