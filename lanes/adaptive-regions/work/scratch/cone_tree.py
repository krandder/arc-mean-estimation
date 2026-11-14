"""Cone tree: merge similar linear regions of a bias-free n x L ReLU net (Kelvin via main ~21:50Z). MEASURED (exploratory).

Cells: joint gate-pattern cones C seen among the 2^20 advice paths (training samples); exact map A_C (f = A_C x on C)
and first moment m_C = E[x 1_C] by lib/cones.py (facet formula; Gaussian measures of the facet cones by exact 3-D
solid angles / closed-form orthant probabilities at n = 4, Plackett quadrature (agrees with Genz to ~1e-9) above).
Tree: start from one leaf holding every cell; a leaf's merged map is the advice-mass-weighted average of its cells'
exact maps (uses the advice samples), its contribution is Abar_leaf sum_{C in leaf} m_C. Split rule (Kelvin): the
unit (layer, index) whose gate changes the map most, mass-weighted: score = p_on p_off / (p_on + p_off) |Abar_on -
Abar_off|_F^2 (the drop in the leaf's within-leaf map dispersion). Always split the leaf with the largest score.
A leaf is the set of cells agreeing on its split units; when a split unit's upstream gates are not all fixed this set is
a cone but not a polyhedral one, and its moment is the sum of its member cells' exact moments (so the tree reduces the
number of maps, not the moment computations; stated in the report).
Reported against the number of leaves: full-input mean error (nMSE vs an RQMC 2^26 truth) next to MC and RQMC with the
same 2^20 advice paths; units fixed per leaf; within-leaf map dispersion; the first splits (layer, unit, score).
Usage: cone_tree.py SEED n [L=4]
"""
import argparse, heapq, json, math, os, sys, time
import numpy as np
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import cones  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int, nargs='?', default=4)
ap.add_argument('--log2train', type=int, default=20)
ap.add_argument('--log2truth', type=int, default=26)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
t0 = time.time()
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
W = [w.double().numpy() for w in ar.weights(seed, n, L)]


def fwd_pat(X):
    h = X; P = []
    for l in range(L):
        z = h @ W[l].T; P.append(z > 0); h = np.maximum(z, 0)
    return h, np.concatenate(P, 1)


NT = 1 << args.log2train
Xtr = np.random.RandomState(seed).standard_normal((NT, n)); _, Ptr = fwd_pat(Xtr)
keys, first, inv, cnt = np.unique(np.packbits(Ptr, axis=1), axis=0, return_index=True, return_inverse=True, return_counts=True)
NC = len(keys); p = cnt / NT
bits = Ptr[first]                                                      # (NC, L n) gate values per cell
print(f'[{time.time() - t0:.0f}s] {NC} cells among {NT} advice paths', flush=True)

# cell maps and exact moments (cached)
cache = os.path.join(RUNS, f'cell_moments_n{n}_L{L}_s{seed}.npz')
if os.path.exists(cache):
    z = np.load(cache); A = z['A']; m = z['m']; assert len(A) == NC
else:
    A = np.zeros((NC, n, n)); m = np.zeros((NC, n)); st = {}; t1 = time.time()
    invr0 = inv.ravel(); S1c = np.zeros((NC, n)); np.add.at(S1c, invr0, Xtr)
    fallback = []                    # cells whose exact moment exceeded the Genz budget: advice-sample moment instead
    for c in range(NC):
        x = Xtr[first[c]]; M = np.eye(n); rows = []
        for l in range(L):
            Gl = W[l] @ M; on = (Gl @ x) > 0
            rows.append(np.where(on[:, None], Gl, -Gl)); M = on[:, None] * Gl
        A[c] = M
        cones.GENZ_CALLS = 0; cones.GENZ_BUDGET = 300
        try:
            m[c] = cones.first_moment(np.concatenate(rows), st)
        except cones.BudgetExceeded:
            m[c] = S1c[c] / NT; fallback.append(c)
        if (c + 1) % 200 == 0:
            print(f'  moments {c + 1}/{NC} [{time.time() - t1:.0f}s, simplices {st.get("simplices", 0)}, fails {st.get("qhull_fail", 0)}]', flush=True)
    np.savez(cache, A=A, m=m, keys=keys, fallback=np.array(fallback, dtype=int))
    print(f'  {len(fallback)} cells (advice mass {p[fallback].sum() if fallback else 0:.2e}) used the sample moment (Genz budget)', flush=True)
    print(f'[{time.time() - t0:.0f}s] moments done in {time.time() - t1:.0f}s; simplices {st.get("simplices", 0)}, triangulation failures {st.get("qhull_fail", 0)}', flush=True)

# validation of the exact moments against the advice paths' own cell moments (z-scores)
invr = inv.ravel()
S1 = np.zeros((NC, n)); S2 = np.zeros((NC, n)); np.add.at(S1, invr, Xtr); np.add.at(S2, invr, Xtr ** 2)
zsc = np.abs(m - S1 / NT) / (np.sqrt(S2) / NT + 1e-12)
n_bad = int((zsc.max(1) > 5).sum())
print(f'  moment check: {n_bad} of {NC} cells with |exact - sample| > 5 se', flush=True)

# truth (RQMC 2^26, 4 scrambles), VF, RQMC at the advice count
reps = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1009 + 77 + r_); acc = np.zeros(n); NR = 1 << (args.log2truth - 2)
    for _ in range(max(1, NR >> 22)):
        F, _ = fwd_pat(ndtri(np.clip(eng.random(min(NR, 1 << 22)), 1e-15, 1 - 1e-15))); acc += F.sum(0)
    reps.append(acc / NR)
reps = np.array(reps); m0 = reps.mean(0)
Fv, _ = fwd_pat(np.random.RandomState(seed + 4242).standard_normal((1 << 22, n))); VF = float(Fv.var(0).sum())
truth_noise = float(reps.var(0, ddof=1).sum() / 4 / VF)
rq = []
for r_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 31 + r_)
    F, _ = fwd_pat(ndtri(np.clip(eng.random(NT), 1e-15, 1 - 1e-15))); rq.append(float(((F.mean(0) - m0) ** 2).sum() / VF))
rqmc_adv = float(np.mean(rq)); mc_adv = 1.0 / NT
nm = lambda e: float(((e - m0) ** 2).sum() / VF)
est_exact = np.einsum('cij,cj->i', A, m); err_exact = nm(est_exact)
print(f'[{time.time() - t0:.0f}s] exact cells: err {err_exact:.2e} (truth noise {truth_noise:.1e}); MC(2^{args.log2train}) {mc_adv:.2e}, RQMC {rqmc_adv:.2e}', flush=True)

# ---------------- the tree
Anorm2 = (A ** 2).sum((1, 2))


class Leaf:
    __slots__ = ('idx', 'fixed', 'pm', 'Abar', 'M', 'disp')

    def __init__(self, idx, fixed):
        self.idx = idx; self.fixed = fixed
        w = p[idx]; self.pm = float(w.sum())
        self.Abar = np.einsum('c,cij->ij', w, A[idx]) / self.pm
        self.M = m[idx].sum(0)
        self.disp = float((w * ((A[idx] - self.Abar) ** 2).sum((1, 2))).sum())   # within-leaf map dispersion (mass-weighted)

    def best_split(self):
        best = (0.0, None)
        B = bits[self.idx]; w = p[self.idx]
        for u in range(L * n):
            if u in self.fixed:
                continue
            on = B[:, u]
            if on.all() or (~on).all():
                continue
            pon = w[on].sum(); poff = w[~on].sum()
            Aon = np.einsum('c,cij->ij', w[on], A[self.idx[on]]) / pon
            Aoff = np.einsum('c,cij->ij', w[~on], A[self.idx[~on]]) / poff
            sc = pon * poff / (pon + poff) * float(((Aon - Aoff) ** 2).sum())
            if sc > best[0]:
                best = (sc, u)
        return best


root = Leaf(np.arange(NC), {})
leaves = {0: root}; nid = 1
heap = []
sc, u = root.best_split()
if u is not None:
    heapq.heappush(heap, (-sc, 0, u))
est = root.Abar @ root.M
disp_tot = root.disp; normA = float((p * Anorm2).sum())
curve = [dict(leaves=1, err=nm(est), disp_rel=disp_tot / normA, units_fixed_mean=0.0, units_fixed_max=0)]
splits = []
while heap:
    negsc, lid, u = heapq.heappop(heap)
    lf = leaves.pop(lid)
    on = bits[lf.idx, u]
    kids = []
    for side in (True, False):
        fx = dict(lf.fixed); fx[u] = side
        kids.append(Leaf(lf.idx[on == side], fx))
    est = est - lf.Abar @ lf.M + sum(k.Abar @ k.M for k in kids)
    disp_tot = disp_tot - lf.disp + sum(k.disp for k in kids)
    if len(splits) < 40:
        splits.append(dict(layer=u // n + 1, unit=u % n, score=-negsc, node_mass=lf.pm, node_depth=len(lf.fixed),
                           rank1_norm=float(np.sqrt(-negsc * (kids[0].pm + kids[1].pm) / (kids[0].pm * kids[1].pm)))))
    for k in kids:
        leaves[nid] = k
        s2, u2 = k.best_split()
        if u2 is not None:
            heapq.heappush(heap, (-s2, nid, u2))
        nid += 1
    nl = len(leaves)
    if nl <= 64 or nl % max(1, nl // 32) == 0 or not heap:
        fx = np.array([len(v.fixed) for v in leaves.values()]); pm = np.array([v.pm for v in leaves.values()])
        curve.append(dict(leaves=nl, err=nm(est), disp_rel=disp_tot / normA, units_fixed_mean=float((fx * pm).sum() / pm.sum()),
                          units_fixed_max=int(fx.max())))


def first_reach(th):
    for r in curve:
        if r['err'] <= th:
            return r['leaves']
    return None


res = dict(seed=seed, n=n, L=L, cells=NC, moment_check_bad=n_bad, advice_paths=NT, err_exact=err_exact, truth_noise=truth_noise, mc_adv=mc_adv,
           rqmc_adv=rqmc_adv, leaves_to_mc=first_reach(mc_adv), leaves_to_rqmc=first_reach(rqmc_adv),
           leaves_to_exact=first_reach(2 * err_exact + truth_noise), final_leaves=len(leaves), curve=curve, first_splits=splits,
           secs=time.time() - t0)
out = args.out or os.path.join(RUNS, f'cone_tree_n{n}_L{L}_s{seed}.json')
json.dump(res, open(out, 'w'))
print(json.dumps({k: v for k, v in res.items() if k not in ('curve', 'first_splits')}), flush=True)
for r in curve:
    if r['leaves'] in (1, 2, 4, 8, 16, 32, 64) or r is curve[-1] or r['leaves'] % 128 == 0:
        print(f"leaves {r['leaves']:6d}: err {r['err']:.2e}  within-leaf map dispersion {r['disp_rel']:.2e}  units fixed {r['units_fixed_mean']:.1f} (max {r['units_fixed_max']})")
print('first splits (layer, unit, rank-one |dA|_F, node mass, node depth):')
for s_ in splits[:15]:
    print(f"  L{s_['layer']} u{s_['unit']}  |dA| {s_['rank1_norm']:.3f}  mass {s_['node_mass']:.3f}  depth {s_['node_depth']}")
