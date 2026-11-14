"""Amendment A4: exact-mean bump experts, end to end on true outputs, unbiased importance-sampled correction.

Model (in the input's downstream-read projection u = Pi_0^T x, d dims; outputs in the top-r output principal
components y = Pi_L^T (f - c_L)):
  g(x) = A x + a0 + sum_k exp(-1/2 (u - c_k)^T M_k (u - c_k)) (alpha_k^T u + d_k),
with a global affine term (all n input directions) and K unnormalised Gaussian bumps (M_k = B_k B_k^T + eps I).
E_{x ~ N(mu, s^2 I)}[g] is closed form: E[bump_k] = det(I + s^2 M_k)^{-1/2} exp(-1/2 (m - c_k)^T (M_k^{-1} + s^2 I)^{-1}
(m - c_k)) with m = Pi_0^T mu, and E[bump_k u] = E[bump_k] (S^{-1} + M_k)^{-1} (S^{-1} m + M_k c_k), S = s^2 I.
Training (end to end against the true outputs): pointwise MSE on training paths + lam_pop x population-mean loss over
input populations N(sqrt(1 - s^2) mu, s^2 I) (closed-form model means vs empirical means) (the teacher term of A4 is
not used in this version). Confidence: per-expert held-out residual variance (responsibility-weighted).
Estimate: E[g] (exact) + mean of f - g over fresh paths, either uniform (x ~ N(0, I)) or importance-sampled from
q = 0.5 N(0, I) + 0.5 sum_k w_k q_k, q_k = the bump-k posterior Gaussian in u (other coordinates N(0, I)), w_k
proportional to E[bump_k] x confidence variance, with exact weights N(u; 0, I)/q(u) (unbiased).
Reports: held-out leftover Var(f - g)/Var f; estimand error (uniform and IS) against the truth; compute in passes
(training paths, VJPs, optimisation flops, closed-form means, fresh paths); MC and RQMC at that compute.
MEASURED (exploratory, A4). Usage: step4e.py SEED n L --Ks 4,16,64,256 --d 16
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--Ks', default='4,16,64,256')
ap.add_argument('--d', type=int, default=16)
ap.add_argument('--r', type=int, default=32)
ap.add_argument('--log2train', type=int, default=15)
ap.add_argument('--log2fresh', type=int, default=14)
ap.add_argument('--pops', type=int, default=200)
ap.add_argument('--M_pop', type=int, default=64)
ap.add_argument('--lam_pop', type=float, default=1.0)
ap.add_argument('--steps', type=int, default=800)
ap.add_argument('--lr', type=float, default=1e-2)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
KS = [int(k) for k in args.Ks.split(',')]
d = min(args.d, n); r = min(args.r, n)
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4e_n{n}_L{L}_s{seed}_d{d}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
PASS = 2.0 * n * n * L
DT = torch.float64
rng = np.random.RandomState(seed)


@torch.no_grad()
def fwd(X):
    h = torch.from_numpy(np.asarray(X, dtype=np.float32))
    for l in range(L):
        h = torch.relu(h @ W[l].T)
    return h.double().numpy()


def vjp0(X, V):
    h = torch.from_numpy(np.asarray(X, dtype=np.float32)); masks = []
    for l in range(L):
        z = h @ W[l].T; masks.append(z > 0); h = torch.relu(z)
    g = torch.from_numpy(np.asarray(V, dtype=np.float32))
    for l in range(L - 1, -1, -1):
        g = (g * masks[l]) @ W[l]
    return g.double().numpy()


NT = 1 << args.log2train
Xtr = rng.standard_normal((NT, n)); Ftr = fwd(Xtr)
Xho = rng.standard_normal((NT // 4, n)); Fho = fwd(Xho)
G0 = vjp0(Xtr[:NT // 4], rng.standard_normal((NT // 4, n)))
ev, U = np.linalg.eigh(G0.T @ G0 / len(G0)); Pi0 = U[:, ::-1][:, :d]          # downstream-read input directions
cL = Ftr.mean(0); _, _, Vt = np.linalg.svd(Ftr - cL, full_matrices=False); PiL = Vt[:r].T
proj_y = lambda F: (F - cL) @ PiL
# populations for the population-mean loss
prs = np.random.RandomState(seed + 5)
pops = []
for b in range(args.pops):
    s = [0.03, 0.1, 0.3, 0.6, 0.9][b % 5]
    mu = math.sqrt(1 - s * s) * prs.standard_normal(n)
    X = mu + s * prs.standard_normal((args.M_pop, n))
    pops.append((mu @ Pi0, mu, s, proj_y(fwd(X)).mean(0)))
paths = NT + NT // 4 + args.pops * args.M_pop + (NT // 4) * 2           # train, held-out, populations, VJPs (2 passes)
# truth
S1 = np.zeros(n); S2 = np.zeros(n); gT = np.random.RandomState(4242); NTr = 1 << 20
for _ in range(NTr // 65536):
    f = fwd(gT.standard_normal((65536, n))); S1 += f.sum(0); S2 += (f * f).sum(0)
mu_true = S1 / NTr; V_true = float((S2 / NTr - mu_true ** 2).sum())
VF = float(Fho.var(0).sum())
print(f'[{time.time() - t0:.0f}s] {NT} training paths, {args.pops} populations, truth 2^20', flush=True)


class Bumps(torch.nn.Module):
    def __init__(self, K, Utr, Ytr, Xtr):
        super().__init__()
        km = KMeans(n_clusters=K, n_init=1, max_iter=50, random_state=seed).fit(Utr) if K > 1 else None
        cent = km.cluster_centers_ if K > 1 else Utr.mean(0, keepdims=True)
        lab = km.labels_ if K > 1 else np.zeros(len(Utr), dtype=int)
        Bs = []
        for k in range(K):
            Ck = np.cov(Utr[lab == k].T) if (lab == k).sum() > d else np.eye(d)
            Bs.append(np.linalg.cholesky(np.linalg.inv(Ck + 1e-2 * np.eye(d))))
        Xa = np.c_[Xtr, np.ones(len(Xtr))]
        coef, *_ = np.linalg.lstsq(Xa, Ytr, rcond=None)
        P = lambda a: torch.nn.Parameter(torch.as_tensor(a, dtype=DT))
        self.A = P(coef[:-1].T); self.a0 = P(coef[-1])
        self.c = P(cent); self.B = P(np.stack(Bs))
        self.alpha = P(np.zeros((K, d, r))); self.dk = P(np.zeros((K, r)))

    def M(self):
        return self.B @ self.B.transpose(-1, -2) + 1e-4 * torch.eye(d, dtype=DT)

    def bumps(self, U):
        D = U[:, None, :] - self.c[None]
        return torch.exp(-0.5 * torch.einsum('nki,kij,nkj->nk', D, self.M(), D))

    def forward(self, X, U):
        bk = self.bumps(U)
        loc = torch.einsum('nd,kdr->nkr', U, self.alpha) + self.dk[None]
        return X @ self.A.T + self.a0 + torch.einsum('nk,nkr->nr', bk, loc)

    def mean_closed(self, m, mu_full, s):
        """E[g] for x ~ N(mu_full, s^2 I) (u = Pi0^T x ~ N(m, s^2 I_d))."""
        Mk = self.M(); I = torch.eye(d, dtype=DT)
        S = s * s * I
        Z = torch.linalg.det(I + S @ Mk) ** -0.5                       # (K,)
        Cinv = torch.linalg.inv(torch.linalg.inv(Mk) + S)
        dm = m - self.c
        Z = Z * torch.exp(-0.5 * torch.einsum('ki,kij,kj->k', dm, Cinv, dm))
        post = torch.linalg.solve(torch.linalg.inv(S + 1e-30 * I)[None] + Mk if s > 0 else Mk,
                                  ((torch.linalg.inv(S) @ m)[None] + torch.einsum('kij,kj->ki', Mk, self.c))[..., None])[..., 0]
        loc = torch.einsum('kd,kdr->kr', post, self.alpha) + self.dk
        return self.A @ mu_full + self.a0 + (Z[:, None] * loc).sum(0), Z, post


Utr = Xtr @ Pi0; Ytr = proj_y(Ftr); Uho = Xho @ Pi0; Yho = proj_y(Fho)
rest_ho = float((((Fho - cL) - Yho @ PiL.T) ** 2).sum(1).mean())
res = dict(n=n, L=L, seed=seed, d=d, r=r, NT=NT, pops=args.pops, M_pop=args.M_pop, V_true=V_true, rows=[])
Xt = torch.as_tensor(Xtr, dtype=DT); Ut = torch.as_tensor(Utr, dtype=DT); Yt = torch.as_tensor(Ytr, dtype=DT)
for K in KS:
    t1 = time.time()
    model = Bumps(K, Utr, Ytr, Xtr)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    gen = torch.Generator().manual_seed(seed)
    opt_flops = 0.0
    for step in range(args.steps):
        idx = torch.randint(0, NT, (2048,), generator=gen)
        pred = model(Xt[idx], Ut[idx])
        loss = ((pred - Yt[idx]) ** 2).sum(1).mean() / VF
        if args.lam_pop > 0:
            bsel = torch.randint(0, len(pops), (16,), generator=gen).tolist()
            lp = 0.0
            for b in bsel:
                m, mu, s, ym = pops[b]
                mg, _, _ = model.mean_closed(torch.as_tensor(m, dtype=DT), torch.as_tensor(mu, dtype=DT), s)
                lp = lp + ((mg - torch.as_tensor(ym, dtype=DT)) ** 2).sum() / VF
            loss = loss + args.lam_pop * lp / len(bsel)
        opt.zero_grad(); loss.backward(); opt.step()
        opt_flops += 3 * (2048 * (2 * n * r + K * (2 * d * d + 2 * d * r)) + 16 * K * (4 * d ** 3 + 2 * d * r))
    with torch.no_grad():
        ph = model(torch.as_tensor(Xho, dtype=DT), torch.as_tensor(Uho, dtype=DT)).numpy()
        leftover = float(((((Yho - ph) ** 2).sum(1)).mean() + rest_ho) / VF)
        # confidence per expert: responsibility-weighted held-out residual variance
        bk = model.bumps(torch.as_tensor(Uho, dtype=DT)).numpy()
        resp = bk / (bk.sum(1, keepdims=True) + 1e-300)
        r2 = ((Yho - ph) ** 2).sum(1)
        s2 = (resp * r2[:, None]).sum(0) / (resp.sum(0) + 1e-300)
        mg0, Z0, post0 = model.mean_closed(torch.zeros(d, dtype=DT), torch.zeros(n, dtype=DT), 1.0)
    Eg = cL + PiL @ mg0.numpy()
    e_model = float(((Eg - mu_true) ** 2).sum() / V_true)
    # correction: uniform and importance sampled, same number of fresh paths
    NF = 1 << args.log2fresh
    gf = np.random.RandomState(seed + 99)
    Xu = gf.standard_normal((NF, n)); Fu = fwd(Xu)
    with torch.no_grad():
        gu = cL + model(torch.as_tensor(Xu, dtype=DT), torch.as_tensor(Xu @ Pi0, dtype=DT)).numpy() @ PiL.T
    est_u = Eg + (Fu - gu).mean(0)
    e_unif = float(((est_u - mu_true) ** 2).sum() / V_true)
    # IS proposal in u: 0.5 N(0, I) + 0.5 sum_k w_k N(post_k, (I + M_k)^-1)
    with torch.no_grad():
        Mk = model.M().numpy()
    wk = Z0.numpy() * s2; wk = wk / wk.sum() if wk.sum() > 0 else np.full(K, 1 / K)
    covs = [np.linalg.inv(np.eye(d) + Mk[k]) for k in range(K)]
    comp = gf.choice(K + 1, size=NF, p=np.r_[0.5, 0.5 * wk])
    Ui = np.zeros((NF, d))
    Ui[comp == 0] = gf.standard_normal(((comp == 0).sum(), d))
    for k in range(K):
        sel = comp == k + 1
        if sel.any():
            Ui[sel] = post0.numpy()[k] + gf.standard_normal((sel.sum(), d)) @ np.linalg.cholesky(covs[k]).T
    # full x: u-part from the proposal, the orthogonal part from N(0, I)
    Xo = gf.standard_normal((NF, n)); Xo = Xo - (Xo @ Pi0) @ Pi0.T
    Xi = Xo + Ui @ Pi0.T
    def logN(Uv, m, C):
        Lc = np.linalg.cholesky(C); z = np.linalg.solve(Lc, (Uv - m).T)
        return -0.5 * (z * z).sum(0) - np.log(np.diag(Lc)).sum() - 0.5 * d * np.log(2 * np.pi)
    logp = logN(Ui, np.zeros(d), np.eye(d))
    lq = np.stack([np.log(0.5) + logp] + [np.log(0.5 * wk[k] + 1e-300) + logN(Ui, post0.numpy()[k], covs[k]) for k in range(K)])
    mx = lq.max(0); logq = mx + np.log(np.exp(lq - mx).sum(0))
    wts = np.exp(logp - logq)
    Fi = fwd(Xi)
    with torch.no_grad():
        gi = cL + model(torch.as_tensor(Xi, dtype=DT), torch.as_tensor(Ui, dtype=DT)).numpy() @ PiL.T
    est_is = Eg + (wts[:, None] * (Fi - gi)).mean(0)
    e_is = float(((est_is - mu_true) ** 2).sum() / V_true)
    # expected errors from the residual variances (uniform: Var(f-g)/N; IS: Var(w (f-g))/N)
    var_u = float(((Fu - gu) - (Fu - gu).mean(0)).var(0).sum() / V_true / NF)
    wr = wts[:, None] * (Fi - gi)
    var_is = float(wr.var(0).sum() / V_true / NF)
    cost_train = paths + opt_flops / PASS + K * (4 * d ** 3) / PASS
    cost = cost_train + 2 * NF                                         # uniform and IS each use NF fresh paths
    row = dict(K=K, leftover=leftover, estimand_model_only=e_model, estimand_uniform=e_unif, estimand_is=e_is,
               expected_uniform=var_u, expected_is=var_is, is_gain=var_u / max(var_is, 1e-300), cost_train=cost_train,
               cost_total_one_correction=cost_train + NF, mc_at_cost=1.0 / (cost_train + NF), secs=time.time() - t1)
    res['rows'].append(row)
    print(f"K={K}: leftover {leftover:.3f} | estimand: model-only {e_model:.2e}, + uniform correction {e_unif:.2e} "
          f"(expected {var_u:.2e}), + IS correction {e_is:.2e} (expected {var_is:.2e}); IS gain {row['is_gain']:.2f} | "
          f"cost {cost_train + NF:.3g} passes, MC at that cost {1 / (cost_train + NF):.2e} ({row['secs']:.0f}s)", flush=True)
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
