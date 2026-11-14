"""Step 4 (Kelvin's variant a): a layered mixture of composed linear experts learned from samples of the same net.

Experts at state layer l: zones = sign patterns of p routing units of layer l+1 (cones in h_l; at l = 0, cones cut by
p first-layer hyperplanes). Routing units = the switching units of layer l+1 with the largest downstream effect
E[|A_{l+1, zone}[:, i]|^2 r_i^2] (r_i = relu(z_i) minus its best global affine fit; main's proxy, with the composed
downstream maps of the experts already built). Layer map on zone k: routing (pinned) units exact; every other unit's
relu replaced by its best affine fit on the zone's training samples (constant-sign units are exact).
Composition (no free regression): A_{l,k} = sum_k' T(k->k') A_{l+1,k'} diag(alpha_k) W_{l+1},
c_{l,k} = sum_k' T(k->k') (A_{l+1,k'} beta_k + c_{l+1,k'}), T = landing shares counted on training samples; at the
output A_L = Po^T (top-r output principal components), c_L = -Po^T mu (mu = training mean).
Surrogate g_l(h) = mu + Po (A_{l,k(h)} h + c_{l,k(h)}). Reports per layer the held-out leftover variance
Var(f - g_l)/tr Var f (also on training paths), zones, coverage (held-out zone seen in training).
Estimates at the input: input zones are cones cut by p_0 first-layer hyperplanes with internal means E[x 1_cone]
from k-dimensional Gaussian sampling (2^22 draws, charged); (1) model-only: mu + Po sum_k (A_0k m_k + c_0k p_k);
(2) unbiased: (1) + mean over fresh paths of f - g_0. Errors against the truth; costs in passes (training paths,
fitting flops, cone draws, fresh paths) and RQMC's nMSE at the same cost (arc-update curves, log-log interpolation).
MEASURED (exploratory). Usage: step4b.py SEED n L [--log2N 14] [--p_deep 2,6,10] [--p0 0,2,4,6,8,10]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=14)
ap.add_argument('--p_deep', default='2,6,10')
ap.add_argument('--p0', default='0,2,4,6,8,10')
ap.add_argument('--r', type=int, default=32)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
PD = [int(x) for x in args.p_deep.split(',')]
P0 = [int(x) for x in args.p0.split(',')]
r = min(args.r, n)
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4b_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
Wn = [w.double().numpy() for w in W]
PASS = 2.0 * n * n * L


@torch.no_grad()
def sample(gen_seed, M, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    Z = np.zeros((L, M, n), dtype=np.float32)
    X = np.zeros((M, n), dtype=np.float32)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        X[done:done + k] = h.numpy()
        for l in range(L):
            z = h @ W[l].T
            Z[l, done:done + k] = z.numpy()
            h = torch.relu(z)
        done += k
    return Z, X


Z_tr, X_tr = sample(11_000_000 + seed, N)
Z_te, X_te = sample(12_000_000 + seed, N)
F_tr = np.maximum(Z_tr[L - 1], 0).astype(np.float64); F_te = np.maximum(Z_te[L - 1], 0).astype(np.float64)
mu = F_tr.mean(0)
_, svo, Vo = np.linalg.svd(F_tr - mu, full_matrices=False)
Po = Vo[:r].T
Y_tr = (F_tr - mu) @ Po; Y_te = (F_te - mu) @ Po
rest_te = (F_te - mu) - Y_te @ Po.T
# truth
try:
    tr = ar.au.load_arc_truth(seed, n, L)
    mu_true = tr['mean'][-1] if tr['mean'].ndim == 2 else tr['mean']
    V_true = float((tr['var'][-1] if tr['var'].ndim == 2 else tr['var']).sum())
except Exception:
    d = np.load(f'/home/agent/workspaces/mats/work/arc-update/runs/truth_n{n}_L{L}_s{seed}.npz')
    NN = float(d['N'])
    m_ = (d['S1A'] + d['S1B']) / NN
    v_ = (d['S2A'] + d['S2B']) / NN - m_ ** 2
    mu_true, V_true = m_[L - 1], float(v_[L - 1].sum())
VF = float(F_te.var(0).sum())
print(f'sampled {2 * N} paths in {time.time() - t0:.0f}s; r={r} PCs capture {(svo[:r] ** 2).sum() / (svo ** 2).sum():.4f}; '
      f'V(held-out)={VF:.3f} V(truth)={V_true:.3f}', flush=True)
# RQMC curve
rq = None
try:
    rj = json.load(open(f'/home/agent/workspaces/mats/work/arc-update/runs/rqmc_n{n}_L{L}_s{seed}.json'))
    rq = (np.array([x['N'] for x in rj['rows']], dtype=float), np.array([x['mean_nmse'] for x in rj['rows']]))
except Exception:
    pass


def rqmc_at(cost):
    if rq is None:
        return None
    lx, ly = np.log(rq[0]), np.log(rq[1])
    if cost <= rq[0][0]:
        s = (ly[1] - ly[0]) / (lx[1] - lx[0])
    elif cost >= rq[0][-1]:
        s = (ly[-1] - ly[-2]) / (lx[-1] - lx[-2])
        return float(np.exp(ly[-1] + s * (math.log(cost) - lx[-1])))
    else:
        return float(np.exp(np.interp(math.log(cost), lx, ly)))
    return float(np.exp(ly[0] + s * (math.log(cost) - lx[0])))


def state(Z, X, l):
    return X.astype(np.float64) if l == 0 else np.maximum(Z[l - 1], 0).astype(np.float64)


def codes(Zl1, units):
    if len(units) == 0:
        return np.zeros(Zl1.shape[0], dtype=np.int64)
    return ((Zl1[:, units] > 0).astype(np.int64) << np.arange(len(units), dtype=np.int64)[None, :]).sum(1)


def build_layer(l, p, nxt, flops):
    """One backward step: experts at state layer l from the next layer's experts nxt = (lab_tr, lab_te, A, c)."""
    lab_n_tr, lab_n_te, A_n, c_n = nxt
    zt = Z_tr[l].astype(np.float64); ze = Z_te[l].astype(np.float64)        # pre-activations of layer l+1
    # global affine fit of relu per unit, residual r_i, and downstream effect
    rz = np.maximum(zt, 0)
    mz, mr = zt.mean(0), rz.mean(0)
    vz = ((zt - mz) ** 2).mean(0) + 1e-12
    al = ((zt - mz) * (rz - mr)).mean(0) / vz
    be = mr - al * mz
    res2 = (rz - (al * zt + be)) ** 2
    colnorm2 = (A_n ** 2).sum(1)                                            # (K_n, n)
    eff = (colnorm2[lab_n_tr] * res2).mean(0)
    fon = (zt > 0).mean(0)
    switching = np.where((fon > 0.001) & (fon < 0.999))[0]
    route = switching[np.argsort(-eff[switching])][:p]
    ctr = codes(zt, route); cte = codes(ze, route)
    uniq, lab_tr = np.unique(ctr, return_inverse=True)
    K = len(uniq)
    pos = np.searchsorted(uniq, cte); pos = np.clip(pos, 0, K - 1)
    seen = uniq[pos] == cte
    lab_te = np.where(seen, pos, -1)
    # per-zone affine fits of relu(z_i) for every unit of layer l+1
    cnt = np.bincount(lab_tr, minlength=K).astype(float)
    order = np.argsort(lab_tr, kind='stable')
    starts = np.concatenate([[0], np.cumsum(cnt)[:-1]]).astype(int)
    zo, ro = zt[order], rz[order]
    Sz = np.add.reduceat(zo, starts, axis=0); Sr = np.add.reduceat(ro, starts, axis=0)
    Szz = np.add.reduceat(zo * zo, starts, axis=0); Szr = np.add.reduceat(zo * ro, starts, axis=0)
    Mz = Sz / cnt[:, None]; Mr = Sr / cnt[:, None]
    Vz = Szz / cnt[:, None] - Mz ** 2; Czr = Szr / cnt[:, None] - Mz * Mr
    alpha = np.where(Vz > 1e-10, Czr / np.maximum(Vz, 1e-10), (Mz > 0).astype(float))
    beta = Mr - alpha * Mz
    # landing shares T(k -> k') on training paths
    pair = lab_tr.astype(np.int64) * (A_n.shape[0] + 1) + lab_n_tr
    pu, pc = np.unique(pair, return_counts=True)
    ks, kn = pu // (A_n.shape[0] + 1), pu % (A_n.shape[0] + 1)
    Abar = np.zeros((K, r, n)); cbar = np.zeros((K, r))
    for k_, k2, cc in zip(ks, kn, pc):
        w = cc / cnt[k_]
        Abar[k_] += w * A_n[k2]; cbar[k_] += w * c_n[k2]
    Wl = Wn[l]                                                            # layer l+1 weights
    A = np.matmul(Abar * alpha[:, None, :], Wl)
    c = np.einsum('krn,kn->kr', Abar, beta) + cbar
    flops += K * (2 * r * n * n + 4 * r * n) + 12 * N * n + 2 * len(pu) * r * n
    # fallback for unseen held-out zones: p = 0 map (single expert) built the same way
    return dict(lab_tr=lab_tr, lab_te=lab_te, A=A, c=c, K=K, route=route.tolist(), seen=float(seen.mean()),
                n_switching=int(len(switching))), flops


def leftover(l, ex, fallback=None):
    H_te = state(Z_te, X_te, l); H_tr = state(Z_tr, X_tr, l)
    lab = ex['lab_te'].copy()
    pred = np.zeros((N, r))
    pred_tr = np.zeros((N, r))
    for k in range(ex['K']):
        idx = lab == k
        if idx.any():
            pred[idx] = H_te[idx] @ ex['A'][k].T + ex['c'][k]
        jdx = ex['lab_tr'] == k
        if jdx.any():
            pred_tr[jdx] = H_tr[jdx] @ ex['A'][k].T + ex['c'][k]
    ok = lab >= 0
    if (~ok).any() and fallback is not None:
        pred[~ok] = H_te[~ok] @ fallback['A'][0].T + fallback['c'][0]
    lo_te = float((((Y_te - pred) ** 2).sum(1) + (rest_te ** 2).sum(1)).mean() / VF)
    lo_tr = float(((Y_tr - pred_tr) ** 2).sum(1).mean() / VF)
    return lo_te, lo_tr, pred


res = dict(n=n, L=L, seed=seed, N=N, r=r, VF=VF, V_true=V_true, runs=[])
A_out = Po.T[None, :, :].copy(); c_out = (-(Po.T @ mu))[None, :]
for pd in PD:
    t1 = time.time()
    nxt = (np.zeros(N, dtype=int), np.zeros(N, dtype=int), A_out, c_out)
    nxt0 = nxt                                             # p = 0 chain for fallback
    flops = 0.0
    layers = []
    for l in range(L - 1, 0, -1):
        ex, flops = build_layer(l, pd, nxt, flops)
        ex0, _ = build_layer(l, 0, nxt0, 0.0)
        lo_te, lo_tr, _ = leftover(l, ex, ex0)
        layers.append(dict(l=l, back=L - 1 - l, K=ex['K'], seen=ex['seen'], n_switching=ex['n_switching'],
                           leftover_te=lo_te, leftover_tr=lo_tr))
        nxt = (ex['lab_tr'], np.where(ex['lab_te'] >= 0, ex['lab_te'], 0), ex['A'], ex['c'])
        nxt0 = (ex0['lab_tr'], ex0['lab_te'], ex0['A'], ex0['c'])
        if l in (L - 1, L - 2, L - 4, L - 8, L // 2, 4, 2, 1):
            print(f"p_deep={pd} l={l:2d}: zones {ex['K']:4d} seen {ex['seen']:.3f} switching {ex['n_switching']:3d} "
                  f"leftover held-out {lo_te:.4f} (train {lo_tr:.4f})", flush=True)
    # input layer: several p0
    inp = []
    for p0 in P0:
        ex, fl = build_layer(0, p0, nxt, 0.0)
        ex0, _ = build_layer(0, 0, nxt0, 0.0)
        lo_te, lo_tr, pred = leftover(0, ex, ex0)
        # exact-ish cone masses and internal means for the input zones (routing units of layer 1)
        units = ex['route']
        cone_flops = 0.0
        if len(units):
            gc = ar.gate_cone_probs(Wn[0], units, 1 << 18, seed=seed + p0, centroids=True)
            cone_flops = gc['flops']
            # map cone labels (bit b = sign of units[b]) to zone ids
            all_codes = np.arange(1 << len(units))
            # zone uniq codes from training
            ctr = codes(Z_tr[0].astype(np.float64), np.array(units))
            uniq = np.unique(ctr)
            est_y = np.zeros(r)
            for code in all_codes:
                pk = gc['p'][code]
                if pk == 0:
                    continue
                mk = pk * np.nan_to_num(gc['centroid'][code])
                zi = np.searchsorted(uniq, code)
                if zi < len(uniq) and uniq[zi] == code:
                    est_y += ex['A'][zi] @ mk + ex['c'][zi] * pk
                else:
                    est_y += ex0['A'][0] @ mk + ex0['c'][0] * pk
        else:
            est_y = ex['c'][0]                              # E x = 0
        est_model = mu + Po @ est_y
        # unbiased: add the fresh-path mean of f - g_0 (held-out paths are fresh: independent of the fit)
        g_te = mu + pred @ Po.T
        est_unb = est_model + (F_te - g_te).mean(0)
        e_model = float(((est_model - mu_true) ** 2).sum() / V_true)
        e_unb = float(((est_unb - mu_true) ** 2).sum() / V_true)
        e_mc_tr = float(((mu - mu_true) ** 2).sum() / V_true)
        cost_model = N + (flops + fl + cone_flops) / PASS
        cost_unb = cost_model + N
        inp.append(dict(p0=p0, zones=ex['K'], seen=ex['seen'], leftover_te=lo_te, leftover_tr=lo_tr,
                        nmse_model=e_model, nmse_unbiased=e_unb, nmse_train_mc=e_mc_tr,
                        expected_unbiased=lo_te * VF / V_true / N, cost_model=cost_model, cost_unbiased=cost_unb,
                        rqmc_at_cost_model=rqmc_at(cost_model), rqmc_at_cost_unbiased=rqmc_at(cost_unb),
                        mc_at_cost_unbiased=1.0 / cost_unb))
        print(f"p_deep={pd} input p0={p0}: zones {ex['K']} leftover {lo_te:.4f} | nMSE model {e_model:.2e} unbiased "
              f"{e_unb:.2e} (expected {lo_te * VF / V_true / N:.2e}) | cost {cost_unb:.0f} passes: RQMC "
              f"{rqmc_at(cost_unb) if rqmc_at(cost_unb) is None else f'{rqmc_at(cost_unb):.2e}'}, MC {1 / cost_unb:.2e}", flush=True)
    res['runs'].append(dict(p_deep=pd, layers=layers, input=inp, secs=time.time() - t1))
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
