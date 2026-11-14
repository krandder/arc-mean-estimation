"""Step 2 of the certified-linear backward probe: eps-certified composed certificates over z-box domains.

Certificate at state layer l for output j: C_l = (D_l, a_l, c_l, eps_l) with D_l = {h_l : z_{l+1}(h_l) in Z_{l+1}}
(box mode: a box in the coordinates of the next layer's pre-activations; cone mode: the same box for the
scale-normalised pre-activations zeta_{l+1} = z_{l+1} / s_l(h_l), s_l(h) = mhat_l . h for l >= 1, s_0 = |x|).
FORMAL P2(d): the composition check relu(W_{l+1} h') in D_{l+1} for h' in D_l is exact interval arithmetic (box mode)
or sound interval arithmetic (cone mode), and the slack of an unpinned unit on [lo, u] is |a_i| t(lo, u),
t = -lo u / (2 (u - lo)) (Chebyshev). Built backward from the output:
- top (state layer L-1): zero piece z_{L,j} <= eps_j (a = 0); linear piece z_{L,j} >= -eps_j (a = w_j, c = eps_j/2,
  error eps_j/2); switching outputs get both pieces.
- each step back: start from the empirical [min, max] box of the covered training states' pre-activations, then shrink
  greedily (move one bound of one unit, excluding the fewest covered training samples per unit of violation removed)
  until (i) every finite bound of the next box is implied and (ii) the step's slack fits its budget.
Budget: total eps_j = e x RMS_j; each step may use half of what is left (geometric). Coverage = fraction of held-out
states inside D_l (checked to be nested). MEASURED (exploratory). Pure numpy/torch; no third-party verifier.
Usage: step2.py SEED n L [--log2N 13] [--per_class 6] [--eps 0,1e-3,1e-2,1e-1] [--modes box,cone]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--log2N', type=int, default=13)
ap.add_argument('--per_class', type=int, default=6)
ap.add_argument('--eps', default='0,1e-3,1e-2,1e-1')
ap.add_argument('--modes', default='box,cone')
ap.add_argument('--step_frac', type=float, default=0.002, help='fraction of covered samples excluded per move')
ap.add_argument('--max_back', type=int, default=None)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
N = 1 << args.log2N
EPS = [float(e) for e in args.eps.split(',')]
MODES = args.modes.split(',')
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step2_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
W64 = [w.double().numpy() for w in W]


@torch.no_grad()
def sample(gen_seed, M, chunk=1 << 12):
    gen = torch.Generator().manual_seed(gen_seed)
    Z = np.zeros((L, M, n), dtype=np.float32)      # Z[k] = pre-activation of layer k+1
    S = np.zeros((L, M), dtype=np.float64)          # S[k] = norm of the state h_k (k = 0: |x|), filled later
    X0n = np.zeros(M)
    done = 0
    while done < M:
        k = min(chunk, M - done)
        h = torch.randn(k, n, generator=gen)
        X0n[done:done + k] = h.double().norm(dim=1).numpy()
        for l in range(L):
            z = h @ W[l].T
            Z[l, done:done + k] = z.numpy()
            h = torch.relu(z)
        done += k
    return Z, X0n


Z_tr, x0_tr = sample(3_000_000 + seed, N)
Z_te, x0_te = sample(4_000_000 + seed, N)
F_tr = np.maximum(Z_tr[L - 1], 0).astype(np.float64); F_te = np.maximum(Z_te[L - 1], 0).astype(np.float64)
pz = ((F_tr == 0).mean(0) + (F_te == 0).mean(0)) / 2
cls = np.where(pz >= 0.999, 'zero', np.where(pz <= 0.001, 'on', 'switching'))
rms = np.sqrt((F_te ** 2).mean(0))
var = F_te.var(0)
# scale functionals: mhat_k = normalised train mean of h_k (k >= 1); s_0 = |x|
mhat = [None] + [np.maximum(Z_tr[k - 1], 0).mean(0) / np.linalg.norm(np.maximum(Z_tr[k - 1], 0).mean(0)) for k in range(1, L)]


def scales(Z, x0):
    S = np.zeros((L, Z.shape[1]))
    S[0] = x0
    for k in range(1, L):
        S[k] = np.maximum(Z[k - 1], 0).astype(np.float64) @ mhat[k]
    return S


S_tr, S_te = scales(Z_tr, x0_tr), scales(Z_te, x0_te)
t_fwd = time.time() - t0
print(f'sampled {2 * N} paths in {t_fwd:.0f}s; classes', {c: int((cls == c).sum()) for c in ('zero', 'on', 'switching')}, flush=True)


def cheb_t(lo, u):
    """Chebyshev error of the best linear approx of relu on [lo, u] (0 if stable)."""
    lo = np.asarray(lo, dtype=np.float64); u = np.asarray(u, dtype=np.float64)
    uns = (lo < 0) & (u > 0)
    t = np.zeros_like(lo)
    lo_f = np.where(np.isfinite(lo), lo, -1e300)
    with np.errstate(invalid='ignore', over='ignore', divide='ignore'):
        tt = np.where(np.isfinite(lo), -lo_f * u / (2 * (u - lo_f)), u / 2.0)
    t[uns] = tt[uns]
    return t


def cheb_lambda_mu(lo, u):
    """Slope and intercept of the surrogate (1, 0 if stable on; 0, 0 if off; Chebyshev line if unstable)."""
    lam = np.where(lo >= 0, 1.0, 0.0)
    mu = np.zeros_like(lo)
    uns = (lo < 0) & (u > 0)
    lo_f = np.where(np.isfinite(lo), lo, -1e300)
    with np.errstate(invalid='ignore', over='ignore', divide='ignore'):
        s = np.where(np.isfinite(lo), u / (u - lo_f), 0.0)
        tt = np.where(np.isfinite(lo), -lo_f * u / (2 * (u - lo_f)), u / 2.0)
    lam = np.where(uns, s, lam)
    mu = np.where(uns, tt, mu)
    return lam, mu


def constraint_rows(k, Znext, mode):
    """Rows g with sense: the image constraints that box Z_k (pre-activations of layer k) must imply for the next
    box Znext = (lo, u) on layer k+1 pre-activations. Returns (G_up, b_up) meaning max_r G_up r <= b_up and
    (G_lo, b_lo) meaning min_r G_lo r >= b_lo, r ranging over relu(Z_k) (box mode: r = relu(z_k); cone mode:
    r = relu(zeta_k), next-layer ratio constraints become homogeneous: b = 0)."""
    lo, u = Znext
    Wn = W64[k]                  # layer k+1 weights (0-based index k)
    up = np.isfinite(u); dn = np.isfinite(lo)
    if mode == 'box':
        return (Wn[up], u[up]), (Wn[dn], lo[dn])
    m = mhat[k]
    return (Wn[up] - u[up, None] * m[None, :], np.zeros(up.sum())), (Wn[dn] - lo[dn, None] * m[None, :], np.zeros(dn.sum()))


def violation(rlo, rhi, Gu, bu, Gl, bl):
    """Exact separable range of G r over the box [rlo, rhi]; returns the positive parts of the violations."""
    mx = np.maximum(Gu * rlo[None, :], Gu * rhi[None, :]).sum(1) - bu if len(bu) else np.zeros(0)
    mn = np.minimum(Gl * rlo[None, :], Gl * rhi[None, :]).sum(1) - bl if len(bl) else np.zeros(0)
    return np.maximum(mx, 0), np.maximum(-mn, 0)


def shrink(V_cov, a, Gu, bu, Gl, bl, budget, step_frac):
    """Greedy box for one layer's (normalised) pre-activations V_cov (m, n) of covered training samples.
    Returns lo, u, keep-mask over the covered samples, slack used."""
    m = V_cov.shape[0]
    keep = np.ones(m, dtype=bool)
    lo = V_cov.min(0).astype(np.float64); u = V_cov.max(0).astype(np.float64)
    absa = np.abs(a)
    it = 0
    while True:
        rlo, rhi = np.maximum(lo, 0), np.maximum(u, 0)
        vu, vl = violation(rlo, rhi, Gu, bu, Gl, bl)
        slack = float((absa * cheb_t(lo, u)).sum())
        tot = vu.sum() + vl.sum() + max(slack - budget, 0.0)
        if tot <= 1e-12 * (1 + abs(budget)):
            return lo, u, keep, slack
        if keep.sum() == 0:
            return lo, u, keep, slack
        it += 1
        Vk = V_cov[keep]
        mk = Vk.shape[0]
        step = max(1, int(math.ceil(step_frac * mk)))
        if mk <= step:
            keep[:] = False
            return lo, u, keep, slack
        # candidate new bounds: exclude the `step` largest (upper move) or smallest (lower move) covered values
        srt_hi = -np.partition(-Vk, step, axis=0)[step]          # (step+1)-th largest value per unit
        srt_lo = np.partition(Vk, step, axis=0)[step]            # (step+1)-th smallest
        new_u = np.minimum(u, srt_hi); new_lo = np.maximum(lo, srt_lo)
        # change in violation for each candidate (one unit's bound moves)
        best, best_gain = None, 0.0
        for kind, nb in (('u', new_u), ('lo', new_lo)):
            if kind == 'u':
                rhi_n = np.maximum(nb, 0)
                d_hi = rhi_n - rhi; d_lo = np.zeros(n)
                t_new = cheb_t(lo, nb)
            else:
                rlo_n = np.maximum(nb, 0)
                d_lo = rlo_n - rlo; d_hi = np.zeros(n)
                t_new = cheb_t(nb, u)
            # max G r for each row changes only through the moved unit's contribution
            cur_u = np.maximum(Gu * rlo[None, :], Gu * rhi[None, :]) if len(bu) else None
            new_u_c = np.maximum(Gu * (rlo + d_lo)[None, :], Gu * (rhi + d_hi)[None, :]) if len(bu) else None
            cur_l = np.minimum(Gl * rlo[None, :], Gl * rhi[None, :]) if len(bl) else None
            new_l_c = np.minimum(Gl * (rlo + d_lo)[None, :], Gl * (rhi + d_hi)[None, :]) if len(bl) else None
            gain = np.zeros(n)
            if len(bu):
                base = (cur_u.sum(1) - bu)[:, None]
                newv = base + (new_u_c - cur_u)
                gain += (np.maximum(base, 0) - np.maximum(newv, 0)).sum(0)
            if len(bl):
                base = (cur_l.sum(1) - bl)[:, None]
                newv = base + (new_l_c - cur_l)
                gain += (np.maximum(-base, 0) - np.maximum(-newv, 0)).sum(0)
            # slack change
            cur_t = cheb_t(lo, u)
            s_new = slack + absa * (t_new - cur_t)
            gain += max(slack - budget, 0.0) - np.maximum(s_new - budget, 0.0)
            j = int(np.argmax(gain))
            if gain[j] > best_gain:
                best_gain, best = gain[j], (kind, j, nb[j])
        if best is None:
            # no single move reduces violation: shrink every unit with infinite contribution or give up
            keep[:] = False
            return lo, u, keep, slack
        kind, j, val = best
        if kind == 'u':
            u[j] = val
        else:
            lo[j] = val
        inside = (V_cov[:, j] <= u[j]) & (V_cov[:, j] >= lo[j])
        keep &= inside


def run_piece(j, piece, e, mode):
    """Backward chain for output j, piece 'zero' or 'lin', eps level e, mode 'box' or 'cone'."""
    eps_tot = e * rms[j]
    Wl = W64[L - 1]
    # top: constraint on z_{L,j} (box mode) or zeta_{L,j} = z_{L,j} / s_{L-1} (cone mode)
    lo_t = np.full(n, -np.inf); u_t = np.full(n, np.inf)
    s_med = float(np.median(S_tr[L - 1]))
    e_top = eps_tot if mode == 'box' else eps_tot / s_med
    if piece == 'zero':
        u_t[j] = e_top
        a = np.zeros(n); c = 0.0; eps_acc = eps_tot           # |f - 0| <= eps on z <= eps
        val_tr = Z_tr[L - 1, :, j] / (1 if mode == 'box' else S_tr[L - 1])
        val_te = Z_te[L - 1, :, j] / (1 if mode == 'box' else S_te[L - 1])
        cov_tr = val_tr <= e_top; cov_te = val_te <= e_top
    else:
        lo_t[j] = -e_top
        a = Wl[j].copy(); c = eps_tot / 2; eps_acc = eps_tot / 2
        val_tr = Z_tr[L - 1, :, j] / (1 if mode == 'box' else S_tr[L - 1])
        val_te = Z_te[L - 1, :, j] / (1 if mode == 'box' else S_te[L - 1])
        cov_tr = val_tr >= -e_top; cov_te = val_te >= -e_top
    # cone mode: eps is carried as a coefficient of the current scale s_l(h_l); convert with ratio bounds
    eps_coef = (eps_acc / s_med) if mode == 'cone' else eps_acc
    Znext = (lo_t, u_t)
    rows = [dict(l=L - 1, back=0, cov_te=float(cov_te.mean()), cov_tr=float(cov_tr.mean()),
                 vshare=float(((F_te[:, j] - F_te[:, j].mean()) ** 2 * cov_te).sum() / max(((F_te[:, j] - F_te[:, j].mean()) ** 2).sum(), 1e-300)),
                 eps_rel=float(eps_acc / max(rms[j], 1e-300)), pinned=None, unstable=None, slack=0.0)]
    remaining = eps_tot - eps_acc
    max_back = args.max_back or (L - 1)
    for l in range(L - 1, max(L - 1 - max_back, 0) - 1, -1):
        if l == 0 and False:
            break
        # build Z_l for pre-activations of layer l (0-based index l-1), i.e. the domain of state layer l-1
        k = l - 1                                  # index into Z arrays and W64 for layer l
        if k < 0:
            break
        if cov_tr.sum() < 2:
            rows.append(dict(l=l - 1, back=L - l, cov_te=0.0, cov_tr=0.0, vshare=0.0, eps_rel=None, pinned=None,
                             unstable=None, slack=None, dead=True))
            break
        if mode == 'box':
            V_all_tr = Z_tr[k].astype(np.float64); V_all_te = Z_te[k].astype(np.float64)
        else:
            V_all_tr = Z_tr[k] / S_tr[k][:, None]; V_all_te = Z_te[k] / S_te[k][:, None]
        (Gu, bu), (Gl, bl) = constraint_rows(l, Znext, mode) if l < L else ((np.zeros((0, n)), np.zeros(0)), (np.zeros((0, n)), np.zeros(0)))
        # slack budget for this step (in the mode's units)
        if mode == 'box':
            budget = remaining / 2.0
        else:
            budget = (remaining / 2.0) / float(np.quantile(S_tr[k][cov_tr], 0.99))
        Vc = V_all_tr[cov_tr]
        lo, u, keep, slack = shrink(Vc, a, Gu, bu, Gl, bl, budget, args.step_frac)
        inside_te = np.all((V_all_te >= lo[None, :]) & (V_all_te <= u[None, :]), axis=1)
        inside_tr = np.all((V_all_tr >= lo[None, :]) & (V_all_tr <= u[None, :]), axis=1)
        nested_viol = int((inside_te & ~cov_te).sum())        # must be 0 (containment)
        cov_tr, cov_te = inside_tr, inside_te
        lam, mu = cheb_lambda_mu(lo, u)
        stable_on = int((lo >= 0).sum()); stable_off = int((u <= 0).sum()); uns = int(((lo < 0) & (u > 0)).sum())
        # backward functional
        if mode == 'box':
            c = c + float((a * mu).sum())
            eps_acc = eps_acc + slack
            remaining = eps_tot - eps_acc
            a = W64[k].T @ (a * lam)
            eps_rel = eps_acc / max(rms[j], 1e-300)
        else:
            # ratio bound s_l / s_{l-1} <= mhat_l . relu(u) on the box (for l >= 1 state scale); intercepts are
            # homogeneous (mu * s) and fold into the functional through s_{l-1} = mhat_{l-1}.h (or |x| at l-1 = 0)
            rho = float(mhat[l] @ np.maximum(u, 0)) if l < L and mhat[l] is not None else 1.0
            eps_coef = eps_coef * rho + slack
            gamma = float((a * mu).sum())          # intercepts mu_i scale with s_{l-1}: fold into the functional
            a = W64[k].T @ (a * lam)
            if k >= 1:
                a = a + gamma * mhat[k]            # s_k(h_k) = mhat_k . h_k is linear: exact fold
            else:
                c = c + gamma                      # input layer: the term gamma |x| stays radial (reported as c)
            s99 = float(np.quantile(S_te[k][cov_te], 0.99)) if cov_te.any() else float('nan')
            eps_acc = eps_coef * s99
            remaining = eps_tot - eps_acc
            eps_rel = eps_acc / max(rms[j], 1e-300)
        dev = (F_te[:, j] - F_te[:, j].mean()) ** 2
        rows.append(dict(l=l - 1, back=L - l, cov_te=float(cov_te.mean()), cov_tr=float(cov_tr.mean()),
                         vshare=float((dev * cov_te).sum() / max(dev.sum(), 1e-300)), eps_rel=float(eps_rel),
                         pinned_on=stable_on, pinned_off=stable_off, unstable=uns, slack=float(slack),
                         nested_violations=nested_viol, budget=float(budget)))
        Znext = (lo, u)
        if cov_te.mean() == 0 and cov_tr.mean() == 0:
            break
    return rows


rng = np.random.RandomState(seed)
picked = {}
for c in ('zero', 'on', 'switching'):
    idx = np.where(cls == c)[0]
    if len(idx):
        # spread over variance: sort by variance, take evenly spaced
        idx = idx[np.argsort(var[idx])]
        sel = idx[np.linspace(0, len(idx) - 1, min(args.per_class, len(idx))).round().astype(int)]
        picked[c] = sorted(set(sel.tolist()))
res = dict(n=n, L=L, seed=seed, N=N, eps=EPS, modes=MODES, classes={c: int((cls == c).sum()) for c in ('zero', 'on', 'switching')},
           picked=picked, t_forward=t_fwd, results=[])
for mode in MODES:
    for e in EPS:
        for c, js in picked.items():
            for j in js:
                pieces = ['zero'] if c == 'zero' else (['lin'] if c == 'on' else ['zero', 'lin'])
                for pc in pieces:
                    t1 = time.time()
                    rows = run_piece(j, pc, e, mode)
                    res['results'].append(dict(mode=mode, eps=e, cls=c, j=int(j), piece=pc, rows=rows, secs=time.time() - t1))
                    covs = ' '.join(f"{r['cov_te']:.3f}" for r in rows[:8])
                    print(f'{mode} e={e:g} {c:9s} j={j:3d} {pc:4s}: cov by back 0..: {covs}  ({time.time() - t1:.0f}s)', flush=True)
        json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
