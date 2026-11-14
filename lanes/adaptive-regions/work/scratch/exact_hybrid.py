"""Hybrid exact-cell estimator for n x L ReLU nets (MEASURED, exploratory; exact part NUMERICAL).

E f = sum_{C in S} A_C E[x 1_C]  +  E[f(x) 1{x not in S}]
S = the most frequent joint gate-pattern cells among the advice paths, up to a target advice coverage q; the first term
is computed by lib/cones.py (facet formula + Plackett orthant probabilities, no network passes), the second by plain MC
or RQMC on N_h fresh paths (only paths outside S contribute). Truth: mean of 4 scrambled-Sobol runs of 2^(log2truth-2).
Reported: cells used, facets, simplices, seconds of the exact part, residual mass, and errors (nMSE = |est - mu|^2 /
tr Var f) at N_h = 2^8 .. 2^20 against MC and RQMC with N_h paths and with the advice's own path count.
Usage: exact_hybrid.py SEED n [L=4] --q 0.99
"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import cones  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int, nargs='?', default=4)
ap.add_argument('--q', type=float, default=0.99)
ap.add_argument('--max_cells', type=int, default=4000)
ap.add_argument('--log2train', type=int, default=20)
ap.add_argument('--log2truth', type=int, default=26)
ap.add_argument('--reps', type=int, default=16)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
t0 = time.time()
W = [w.double().numpy() for w in ar.weights(seed, n, L)]


def fwd_pat(X):
    h = X; P = []
    for l in range(L):
        z = h @ W[l].T; P.append(z > 0); h = np.maximum(z, 0)
    return h, np.packbits(np.concatenate(P, 1), axis=1)


NT = 1 << args.log2train
Xtr = np.random.RandomState(seed).standard_normal((NT, n)); _, Ktr = fwd_pat(Xtr)
keys, inv, cnt = np.unique(Ktr, axis=0, return_inverse=True, return_counts=True)
order = np.argsort(-cnt)
cum = np.cumsum(cnt[order]) / NT
nS = int(min(args.max_cells, np.searchsorted(cum, args.q) + 1, len(keys)))
S = order[:nS]
inS = np.zeros(len(keys), bool); inS[S] = True
Sset = set(bytes(keys[i]) for i in S)
print(f'[{time.time() - t0:.0f}s] {len(keys)} cells among {NT} advice paths; using top {nS} (advice coverage {cum[nS - 1]:.6f})', flush=True)

# exact part
first_idx = {}
invr = inv.ravel()
for i in range(NT):
    c = invr[i]
    if inS[c] and c not in first_idx:
        first_idx[c] = i
        if len(first_idx) == nS:
            break
st = {}; exact = np.zeros(n); nfac = 0; t1 = time.time()
for c in S:
    x = Xtr[first_idx[c]]
    h = x; M = np.eye(n); rows = []
    for l in range(L):
        Gl = W[l] @ M; z = Gl @ x
        on = z > 0
        rows.append(np.where(on[:, None], Gl, -Gl)); M = on[:, None] * Gl
    G = np.concatenate(rows)
    G = cones._unit_dedupe(G); nfac += len(G)
    exact += M @ cones.first_moment(G, st)
t_exact = time.time() - t1
print(f'[{time.time() - t0:.0f}s] exact part: {nS} cells, {nfac} constraint rows, {st.get("simplices", 0)} simplices, '
      f'{st.get("qhull_fail", 0)} triangulation failures, {t_exact:.0f}s', flush=True)

# truth
reps = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1009 + 77 + r_); acc = np.zeros(n); NR = 1 << (args.log2truth - 2)
    for _ in range(max(1, NR >> 22)):
        F, _ = fwd_pat(ndtri(np.clip(eng.random(min(NR, 1 << 22)), 1e-15, 1 - 1e-15))); acc += F.sum(0)
    reps.append(acc / NR)
reps = np.array(reps); m0 = reps.mean(0)
Fv, Kv = fwd_pat(np.random.RandomState(seed + 4242).standard_normal((1 << 22, n))); VF = float(Fv.var(0).sum())
truth_noise = float(reps.var(0, ddof=1).sum() / 4 / VF)
resid_mass = float(np.mean([bytes(k) not in Sset for k in Kv[:1 << 18]]))
print(f'[{time.time() - t0:.0f}s] truth noise {truth_noise:.1e}; residual mass outside S {resid_mass:.2e}', flush=True)


def nmse(e):
    return float(((e - m0) ** 2).sum() / VF)


rows = []
rs = np.random.RandomState(seed + 99)
for lg in (8, 12, 16, 20):
    N = 1 << lg
    eh, em, ehq, eq = [], [], [], []
    for r_ in range(args.reps if lg < 20 else 4):
        X = rs.standard_normal((N, n)); F, K = fwd_pat(X)
        out = np.array([bytes(k) not in Sset for k in K])   # review 2 item 12: always test membership
        eh.append(nmse(exact + (F * out[:, None]).sum(0) / N)); em.append(nmse(F.mean(0)))
        eng = qmc.Sobol(d=n, scramble=True, seed=seed * 131 + r_ + 7 * lg)
        Xq = ndtri(np.clip(eng.random(N), 1e-15, 1 - 1e-15)); Fq, Kq = fwd_pat(Xq)
        outq = np.array([bytes(k) not in Sset for k in Kq])
        ehq.append(nmse(exact + (Fq * outq[:, None]).sum(0) / N)); eq.append(nmse(Fq.mean(0)))
    row = dict(N=N, hybrid_mc=float(np.mean(eh)), hybrid_rqmc=float(np.mean(ehq)), mc=float(np.mean(em)), rqmc=float(np.mean(eq)))
    rows.append(row)
    print(f'N=2^{lg}: hybrid(MC) {row["hybrid_mc"]:.2e}  hybrid(RQMC) {row["hybrid_rqmc"]:.2e}  MC {row["mc"]:.2e}  RQMC {row["rqmc"]:.2e}', flush=True)
e_exact_only = nmse(exact)
res = dict(seed=seed, n=n, L=L, cells_seen=int(len(keys)), cells_used=nS, advice_cov=float(cum[nS - 1]), resid_mass=resid_mass,
           constraint_rows=nfac, simplices=st.get('simplices', 0), tri_fail=st.get('qhull_fail', 0), secs_exact=t_exact,
           err_exact_part_only=e_exact_only, truth_noise=truth_noise, mc_at_advice=1.0 / NT, rows=rows, secs=time.time() - t0)
print(json.dumps({k: v for k, v in res.items() if k != 'rows'}), flush=True)
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'exact_hybrid_n{n}_L{L}_s{seed}_q{args.q}.json')
json.dump(res, open(out, 'w'))
