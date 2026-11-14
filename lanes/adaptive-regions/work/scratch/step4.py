"""Step 4: a layered mixture of linear experts (validity zones, masses, internal means, transitions), measured.

Per state layer l (from the output end back) and number of experts K:
- zones: K-means (nearest centroid) on the top-d PCA coordinates of h_l (training paths); validity zone of expert k =
  {h : nearest centroid is k and distance <= R_k}, R_k = 99th percentile of its training distances;
- expert map: ridge regression of the output f (all n outputs, through the top-r output principal components plus the
  zone mean of the rest) on [PCA coords of h_l, 1] within the zone;
- uncertainty: the expert's training residual variance (trace over outputs).
Held-out metrics: coverage (fraction inside some validity zone), accuracy (pointwise nMSE of the expert prediction on
covered and on all points, as a fraction of tr Var f), calibration (held-out / training residual variance), and the
model's mean estimate sum_k (A_k m_k + c_k p_k) with p_k, m_k from held-out paths (a structured sampling estimator,
error against the 2^26-path truth).
Transitions (l-1 -> l, both zoned with K experts): T[k', k] = P(lands in k' | in k) and the landing-conditioned
internal means m_{k->k'} = E[h_l 1{k, k'}]; the error of three approximations of m_{k->k'}: (i) T x E[h_l 1{k}]
(landing independent of position), (ii) Gaussian per expert at l-1 (mean, covariance), pushed through W_l by sampling
and conditioned on landing in k'; priced through the layer-l expert maps as an output error (nMSE-equivalent).
Mixture closure (variant b): from the true zones at l0 (weights, means, covariances), propagate each component as a
Gaussian through layers l0+1..L by moment matching (sampling 2^11 per component per layer; this measures the closure's
own error, not a deductive cost), output mean sum_k p_k E_k f; error against the truth for K = 1, 4, 16, 64.
MEASURED (exploratory). Usage: step4.py SEED n L [--log2N 14]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=14)
ap.add_argument('--layers', default=None)
ap.add_argument('--Ks', default='1,4,16,64,256')
ap.add_argument('--d', type=int, default=64, help='PCA dims of h_l used for zones and expert inputs')
ap.add_argument('--r', type=int, default=32, help='output PCs modelled by the experts')
ap.add_argument('--trans_layers', default=None)
ap.add_argument('--closure_from', default=None)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
KS = [int(k) for k in args.Ks.split(',')]
LAYERS = [int(x) for x in args.layers.split(',')] if args.layers else \
    sorted(set([L - 1 - b for b in (0, 1, 2, 3, 4, 5, 6, 7, 11, 15, 23, 27, 29, 30, 31) if L - 1 - b >= 0]), reverse=True)
TRANS = [int(x) for x in args.trans_layers.split(',')] if args.trans_layers else [l for l in LAYERS if (l - 1) in LAYERS]
CLOS = [int(x) for x in args.closure_from.split(',')] if args.closure_from else [l for l in (L - 8, L - 16) if l >= 0]
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
keep = set(LAYERS) | set(CLOS)


@torch.no_grad()
def sample(gen_seed, M, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    H = {l: np.zeros((M, n), dtype=np.float32) for l in keep}
    F = np.zeros((M, n), dtype=np.float32)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        if 0 in H:
            H[0][done:done + k] = h.numpy()
        for l in range(L):
            h = torch.relu(h @ W[l].T)
            if (l + 1) in H:
                H[l + 1][done:done + k] = h.numpy()
        F[done:done + k] = h.numpy()
        done += k
    return H, F


H_tr, F_tr = sample(9_000_000 + seed, N)
H_te, F_te = sample(10_000_000 + seed, N)
F_tr = F_tr.astype(np.float64); F_te = F_te.astype(np.float64)
try:
    truth = ar.au.load_arc_truth(seed, n, L)
    mu_true = truth['mean'][-1] if truth['mean'].ndim == 2 else truth['mean']
    V_true = float(truth['var'][-1].sum() if truth['var'].ndim == 2 else truth['var'].sum())
except Exception:
    tr = np.load(f'/home/agent/workspaces/mats/work/arc-update/runs/truth_n{n}_L{L}_s{seed}.npz')
    S1 = tr['S1'] if 'S1' in tr else tr['S1A'] + tr['S1B']
    mu_true = None; V_true = None
VF = float(F_te.var(0).sum())
muF = F_tr.mean(0)
# output PCs (train)
_, svo, Vo = np.linalg.svd(F_tr - muF, full_matrices=False)
Po = Vo[:args.r].T                                  # (n, r)
print(f'sampled {2 * N} in {time.time() - t0:.0f}s; output PCs r={args.r} capture '
      f'{(svo[:args.r] ** 2).sum() / (svo ** 2).sum():.4f} of tr Var', flush=True)


def pca(Htr, d):
    c = Htr.mean(0)
    _, sv, Vt = np.linalg.svd(Htr - c, full_matrices=False)
    P = Vt[:d].T
    frac = float((sv[:d] ** 2).sum() / max((sv ** 2).sum(), 1e-300))
    return c, P, frac


def fit_experts(Xtr, Ftr, lab, K, lam=1e-2):
    """Per-zone ridge regression of the output PCs on [X, 1]; residual (rest of f) modelled by the zone mean."""
    d = Xtr.shape[1]
    Ytr = (Ftr - muF) @ Po                            # (N, r)
    Rest = (Ftr - muF) - Ytr @ Po.T                   # (N, n), outside the PCs
    experts = []
    for k in range(K):
        idx = lab == k
        m = int(idx.sum())
        if m == 0:
            experts.append(None); continue
        Xk = np.concatenate([Xtr[idx], np.ones((m, 1))], 1)
        A = Xk.T @ Xk
        A[np.arange(d), np.arange(d)] += lam * (np.trace(A[:d, :d]) / d + 1e-12)
        B = np.linalg.solve(A, Xk.T @ Ytr[idx])          # (d+1, r)
        rest_mean = Rest[idx].mean(0)
        pred = Xk @ B
        res = ((Ytr[idx] - pred) ** 2).sum(1) + ((Rest[idx] - rest_mean) ** 2).sum(1)
        experts.append(dict(B=B, rest=rest_mean, m=m, train_res=float(res.mean())))
    return experts


def predict(experts, X, lab):
    out = np.zeros((X.shape[0], n))
    for k, e in enumerate(experts):
        idx = lab == k
        if e is None or not idx.any():
            continue
        Xk = np.concatenate([X[idx], np.ones((int(idx.sum()), 1))], 1)
        out[idx] = muF + (Xk @ e['B']) @ Po.T + e['rest'][None, :]
    return out


res = dict(n=n, L=L, seed=seed, N=N, Ks=KS, d=args.d, r=args.r, VF=VF, layers=[], transitions=[], closure=[])
zones = {}
for l in LAYERS:
    t1 = time.time()
    Htr = H_tr[l].astype(np.float64); Hte = H_te[l].astype(np.float64)
    c, P, frac = pca(Htr, args.d)
    Xtr = (Htr - c) @ P; Xte = (Hte - c) @ P
    rows = []
    for K in KS:
        if K == 1:
            lab_tr = np.zeros(N, dtype=int); lab_te = np.zeros(N, dtype=int)
            cent = Xtr.mean(0, keepdims=True)
        else:
            km = KMeans(n_clusters=K, n_init=1, max_iter=50, random_state=seed, init='k-means++').fit(Xtr)
            cent = km.cluster_centers_
            lab_tr = km.labels_; lab_te = km.predict(Xte)
        dtr = np.linalg.norm(Xtr - cent[lab_tr], axis=1); dte = np.linalg.norm(Xte - cent[lab_te], axis=1)
        R = np.array([np.quantile(dtr[lab_tr == k], 0.99) if (lab_tr == k).any() else 0.0 for k in range(K)])
        covered = dte <= R[lab_te]
        ex = fit_experts(Xtr, F_tr, lab_tr, K)
        pred = predict(ex, Xte, lab_te)
        err2 = ((F_te - pred) ** 2).sum(1)
        nmse_cov = float(err2[covered].mean() / (VF)) if covered.any() else None
        nmse_all = float(err2.mean() / VF)
        # calibration per zone: held-out / train residual
        cal = []
        for k in range(K):
            if ex[k] is None:
                continue
            idx = lab_te == k
            if idx.sum() >= 20 and ex[k]['train_res'] > 0:
                cal.append(float(err2[idx].mean() / ex[k]['train_res']))
        pred_res_total = float(sum(ex[k]['train_res'] * ex[k]['m'] for k in range(K) if ex[k] is not None) / N / VF)
        # structured-sampling mean estimate from held-out masses and internal means
        est = pred.mean(0)
        est_err = float(((est - mu_true) ** 2).sum() / V_true) if mu_true is not None else None
        mc_err = float(((F_te.mean(0) - mu_true) ** 2).sum() / V_true) if mu_true is not None else None
        rows.append(dict(K=K, coverage=float(covered.mean()), nmse_covered=nmse_cov, nmse_all=nmse_all,
                         pred_res_nmse=pred_res_total, calib_median=(float(np.median(cal)) if cal else None),
                         calib_p90=(float(np.quantile(cal, 0.9)) if cal else None),
                         est_nmse=est_err, heldout_mc_nmse=mc_err, n_te=N))
        zones[(l, K)] = dict(c=c, P=P, cent=cent, R=R, ex=ex, lab_tr=lab_tr, lab_te=lab_te)
    res['layers'].append(dict(l=l, back=L - 1 - l, pca_frac=frac, rows=rows, secs=time.time() - t1))
    print(f"l={l:2d} back={L - 1 - l:2d} (PCA{args.d} {frac:.3f}) " + ' | '.join(
        f"K={r_['K']}: cov {r_['coverage']:.3f} nMSE {r_['nmse_all']:.4f} pred {r_['pred_res_nmse']:.4f} cal {r_['calib_median'] if r_['calib_median'] is None else round(r_['calib_median'], 2)}"
        for r_ in rows) + f"  ({time.time() - t1:.0f}s)", flush=True)
    json.dump(res, open(out, 'w'))

# transitions and landing-conditioned means (zones at l-1 and l with the same K)
Wnp = [w.double().numpy() for w in W]
for l in TRANS:
    for K in [k for k in KS if k in (16, 64)]:
        if (l, K) not in zones or (l - 1, K) not in zones:
            continue
        zl, zp = zones[(l, K)], zones[(l - 1, K)]
        Hl_te = H_te[l].astype(np.float64); Hp_te = H_te[l - 1].astype(np.float64)
        Hp_tr = H_tr[l - 1].astype(np.float64)
        a_te, b_te = zp['lab_te'], zl['lab_te']             # source (l-1) and landing (l) zones
        T = np.zeros((K, K)); mtrue = np.zeros((K, K, n)); msrc = np.zeros((K, n)); psrc = np.zeros(K)
        for k in range(K):
            idx = a_te == k
            psrc[k] = idx.mean()
            if not idx.any():
                continue
            msrc[k] = Hl_te[idx].sum(0) / N                 # E[h_l 1{k}]
            for k2 in np.unique(b_te[idx]):
                jj = idx & (b_te == k2)
                T[k2, k] = jj.sum() / idx.sum()
                mtrue[k, k2] = Hl_te[jj].sum(0) / N         # E[h_l 1{k, k2}]
        # approximation (i): m_{k->k'} ~ T[k', k] E[h_l 1{k}]
        m_i = T.T[:, :, None] * msrc[:, None, :]
        # approximation (ii): Gaussian per source zone (train mean, covariance), push by sampling, condition on landing
        m_ii = np.zeros_like(mtrue)
        p_ii = np.zeros((K, K))
        g = np.random.RandomState(seed + l)
        for k in range(K):
            idx = zp['lab_tr'] == k
            if idx.sum() < 5:
                continue
            mu_k = Hp_tr[idx].mean(0); C_k = np.cov(Hp_tr[idx].T) + 1e-9 * np.eye(n)
            A_, clip = ar.au.psd_sqrt(C_k)
            Zs = g.standard_normal((4096, n)) @ A_.T + mu_k
            Hs = np.maximum(Zs @ Wnp[l - 1].T, 0)           # push through layer l
            Xs = (Hs - zl['c']) @ zl['P']
            ds = ((Xs[:, None, :] - zl['cent'][None, :, :]) ** 2).sum(-1)
            land = ds.argmin(1)
            for k2 in range(K):
                sel = land == k2
                p_ii[k, k2] = psrc[k] * sel.mean()
                if sel.any():
                    m_ii[k, k2] = psrc[k] * sel.mean() * Hs[sel].mean(0)
        # price through the layer-l expert maps: E[pred 1{k2}] = p (muF + rest + B_1 Po^T - (c P) B_x Po^T)
        #                                                         + (m P) B_x Po^T, so an error (dm, dp) costs
        # dp (muF + rest + B_1 Po^T - (c P) B_x Po^T) + (dm P) B_x Po^T in the output mean
        ptrue = np.zeros((K, K))
        for k in range(K):
            ptrue[k] = T[:, k] * psrc[k]
        def out_err(m_apx, p_apx):
            e = np.zeros(n)
            for k2 in range(K):
                ex = zl['ex'][k2]
                if ex is None:
                    continue
                dm = (m_apx[:, k2, :] - mtrue[:, k2, :]).sum(0)
                dp = float((p_apx[:, k2] - ptrue[:, k2]).sum())
                Bx = ex['B'][:-1]; B1 = ex['B'][-1]
                const = muF + ex['rest'] + B1 @ Po.T - ((zl['c'] @ zl['P']) @ Bx) @ Po.T
                e += dp * const + ((dm @ zl['P']) @ Bx) @ Po.T
            return float((e ** 2).sum() / V_true) if V_true else float((e ** 2).sum() / VF)
        res['transitions'].append(dict(l=l, K=K, T_entropy_bits=float(np.mean([-(T[:, k][T[:, k] > 0] * np.log2(T[:, k][T[:, k] > 0])).sum() for k in range(K) if psrc[k] > 0])),
                                       err_i_nmse=out_err(m_i, ptrue), err_ii_nmse=out_err(m_ii, p_ii),
                                       rel_internal_err_i=float(np.abs(m_i - mtrue).sum() / max(np.abs(mtrue).sum(), 1e-300)),
                                       rel_internal_err_ii=float(np.abs(m_ii - mtrue).sum() / max(np.abs(mtrue).sum(), 1e-300))))
        print(f"transition {l - 1}->{l} K={K}: landing entropy {res['transitions'][-1]['T_entropy_bits']:.2f} bits; "
              f"output error of landing-mean approx (i) {res['transitions'][-1]['err_i_nmse']:.2e}, (ii) Gaussian "
              f"{res['transitions'][-1]['err_ii_nmse']:.2e} (nMSE units)", flush=True)
        json.dump(res, open(out, 'w'))


# mixture closure from oracle zones at l0
@torch.no_grad()
def closure(l0, K, m_per=None):
    m_per = m_per or max(2048, 16384 // K)
    Hp = H_tr[l0].astype(np.float64)
    if K == 1:
        lab = np.zeros(N, dtype=int)
    else:
        c, P, _ = pca(Hp, args.d)
        lab = KMeans(n_clusters=K, n_init=1, max_iter=50, random_state=seed).fit((Hp - c) @ P).labels_
    g = torch.Generator().manual_seed(seed * 7 + l0 + K)
    est = np.zeros(n)
    for k in range(K):
        idx = lab == k
        pk = idx.mean()
        if idx.sum() < 3:
            continue
        mu = Hp[idx].mean(0); C = np.cov(Hp[idx].T) + 1e-9 * np.eye(n)
        for l in range(l0, L):
            A_, _ = ar.au.psd_sqrt(C)
            Z = torch.randn(m_per, n, generator=g, dtype=torch.float64) @ torch.from_numpy(A_.T) + torch.from_numpy(mu)
            Hn = torch.relu(Z @ torch.from_numpy(Wnp[l].T))
            mu = Hn.mean(0).numpy(); C = np.cov(Hn.numpy().T) + 1e-12 * np.eye(n)
        est += pk * mu
    return est


if mu_true is not None:
    for l0 in CLOS:
        for K in (1, 4, 16, 64):
            t1 = time.time()
            e = closure(l0, K)
            err = float(((e - mu_true) ** 2).sum() / V_true)
            res['closure'].append(dict(l0=l0, K=K, nmse=err, secs=time.time() - t1))
            print(f"mixture closure from l0={l0} K={K}: nMSE {err:.2e} ({time.time() - t1:.0f}s)", flush=True)
            json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
