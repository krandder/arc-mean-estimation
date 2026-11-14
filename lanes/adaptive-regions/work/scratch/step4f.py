"""A4 bump experts under the 'advice' accounting (Kelvin via main ~17:50Z): training is free advice (recorded, not
charged); only estimation-time compute is charged; scored estimands are HELD-OUT input populations
N(sqrt(1 - s^2) mu, s^2 I) (new centres) and N(0, I); advice size reported.

Model as scratch/step4e.py (global affine term on all inputs + K unnormalised Gaussian bumps with local affine maps in
the d-dim downstream-read input projection; exact Gaussian means). Training: pointwise MSE on training paths + a
population-mean loss over training populations (closed-form model means vs their empirical means).
For each held-out population P (and N(0, I)) and each estimation budget:
- model-only estimate E_P[g] (closed form); estimation cost = the closed-form mean's flops;
- control variate E_P[g] + mean over N fresh paths from P of (f - g); cost = closed form + N (pass + g evaluation).
Errors: |est - m_P|^2 / V_ref with m_P the population's true mean (2^18 paths) and V_ref the N(0, I) output variance;
MC on P at the same estimation-time flops has expected error tr Cov_P(f) / (N_eq V_ref). Also: the memorisation check
for N(0, I) (the model's estimate vs the plain average of the training paths). MEASURED (exploratory).
Usage: step4f.py SEED n L --Ks 16,64,256,1024 --d 32
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--Ks', default='16,64,256,1024')
ap.add_argument('--d', type=int, default=32)
ap.add_argument('--r', type=int, default=32)
ap.add_argument('--log2train', type=int, default=17)
ap.add_argument('--pops', type=int, default=400)
ap.add_argument('--M_pop', type=int, default=256)
ap.add_argument('--lam_pop', type=float, default=1.0)
ap.add_argument('--steps', type=int, default=3000)
ap.add_argument('--lr', type=float, default=5e-3)
ap.add_argument('--batch', type=int, default=4096)
ap.add_argument('--te_centres', type=int, default=6)
ap.add_argument('--te_widths', default='0.1,0.3,0.6,0.9')
ap.add_argument('--budgets', default='16,64,256,1024')
ap.add_argument('--bump', default='full', help='full: M_k = B B^T; iso: M_k = lambda_k I (O(d) closed form)')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
KS = [int(k) for k in args.Ks.split(',')]
d = min(args.d, n); r = min(args.r, n)
TEW = [float(w) for w in args.te_widths.split(',')]
BUD = [int(b) for b in args.budgets.split(',')]
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4f_n{n}_L{L}_s{seed}_d{d}_{args.bump}.json')
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


# advice data (free): training paths and training populations
NT = 1 << args.log2train
Xtr = rng.standard_normal((NT, n)); Ftr = fwd(Xtr)
G0 = vjp0(Xtr[:NT // 4], rng.standard_normal((NT // 4, n)))
ev, U = np.linalg.eigh(G0.T @ G0 / len(G0)); Pi0 = U[:, ::-1][:, :d]
cL = Ftr.mean(0); _, _, Vt = np.linalg.svd(Ftr - cL, full_matrices=False); PiL = Vt[:r].T
VF = float(Ftr.var(0).sum())
proj_y = lambda F: (F - cL) @ PiL
prs = np.random.RandomState(seed + 5)
tr_pops = []
for b in range(args.pops):
    s = [0.03, 0.1, 0.3, 0.6, 0.9][b % 5]
    mu = math.sqrt(1 - s * s) * prs.standard_normal(n)
    X = mu + s * prs.standard_normal((args.M_pop, n))
    tr_pops.append((mu @ Pi0, mu, s, proj_y(fwd(X)).mean(0)))
advice_paths = NT + NT // 4 * 2 + args.pops * args.M_pop
# held-out populations (new centres) and N(0, I): true means and covariance traces from 2^18 paths
hrs = np.random.RandomState(seed + 77)
te = []
for ci in range(args.te_centres):
    mu = hrs.standard_normal(n)
    for s in TEW:
        te.append(dict(s=s, mu=math.sqrt(1 - s * s) * mu))
te.append(dict(s=1.0, mu=np.zeros(n)))
for p in te:
    S1 = np.zeros(n); S2 = np.zeros(n); NTr = 1 << 18
    for _ in range(NTr // 65536):
        f = fwd(p['mu'] + p['s'] * hrs.standard_normal((65536, n))); S1 += f.sum(0); S2 += (f * f).sum(0)
    p['m'] = S1 / NTr; p['trcov'] = float((S2 / NTr - p['m'] ** 2).sum())
# RQMC on each held-out population (scrambled Sobol, inverse normal, 8 scrambles) at the budgets
from scipy.stats import qmc
from scipy.special import ndtri
for p in te:
    p['rqmc'] = {}
    for Nb in BUD:
        errs = []
        for rep in range(8):
            eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1000 + rep + 17 * Nb)
            u = np.clip(eng.random(Nb), 1e-12, 1 - 1e-12)
            est = fwd(p['mu'] + p['s'] * ndtri(u)).mean(0)
            errs.append(float(((est - p['m']) ** 2).sum()))
        p['rqmc'][Nb] = float(np.mean(errs))
print(f'[{time.time() - t0:.0f}s] advice: {NT} paths + {args.pops} populations; {len(te)} held-out populations', flush=True)


class Bumps(torch.nn.Module):
    def __init__(self, K, Utr, Ytr, Xtr):
        super().__init__()
        km = KMeans(n_clusters=K, n_init=1, max_iter=50, random_state=seed).fit(Utr[:min(len(Utr), 1 << 15)])
        cent = km.cluster_centers_; lab = km.predict(Utr)
        Bs = []
        for k in range(K):
            sel = Utr[lab == k]
            Ck = np.cov(sel.T) if len(sel) > d else np.eye(d)
            Bs.append(np.linalg.cholesky(np.linalg.inv(Ck + 1e-2 * np.eye(d))))
        coef, *_ = np.linalg.lstsq(np.c_[Xtr, np.ones(len(Xtr))], Ytr, rcond=None)
        P = lambda a: torch.nn.Parameter(torch.as_tensor(a, dtype=DT))
        self.A = P(coef[:-1].T); self.a0 = P(coef[-1])
        self.c = P(cent); self.B = P(np.stack(Bs))
        self.loglam = P(np.log(np.array([1.0 / max(np.trace(np.linalg.inv(b_ @ b_.T)) / d, 1e-6) for b_ in Bs])))
        self.alpha = P(np.zeros((K, d, r))); self.dk = P(np.zeros((K, r)))

    def M(self):
        if args.bump == 'iso':
            lam = torch.exp(self.loglam)
            return lam[:, None, None] * torch.eye(d, dtype=DT)
        return self.B @ self.B.transpose(-1, -2) + 1e-4 * torch.eye(d, dtype=DT)

    def forward(self, X, U):
        D = U[:, None, :] - self.c[None]
        if args.bump == 'iso':
            bk = torch.exp(-0.5 * torch.exp(self.loglam)[None] * (D * D).sum(-1))
        else:
            bk = torch.exp(-0.5 * (torch.einsum('nki,kij->nkj', D, self.M()) * D).sum(-1))
        loc = torch.einsum('nd,kdr->nkr', U, self.alpha) + self.dk[None]
        return X @ self.A.T + self.a0 + torch.einsum('nk,nkr->nr', bk, loc)

    def mean_closed(self, m, mu_full, s):
        if args.bump == 'iso':
            lam = torch.exp(self.loglam); s2 = s * s
            Z = (1 + s2 * lam) ** (-d / 2) * torch.exp(-0.5 * ((m - self.c) ** 2).sum(1) / (1 / lam + s2))
            post = (m[None] / s2 + lam[:, None] * self.c) / (1 / s2 + lam)[:, None]
            loc = torch.einsum('kd,kdr->kr', post, self.alpha) + self.dk
            return self.A @ mu_full + self.a0 + (Z[:, None] * loc).sum(0)
        Mk = self.M(); I = torch.eye(d, dtype=DT); s2 = s * s
        Z = torch.linalg.det(I + s2 * Mk) ** -0.5
        Cinv = torch.linalg.inv(torch.linalg.inv(Mk) + s2 * I)
        dm = m - self.c
        Z = Z * torch.exp(-0.5 * torch.einsum('ki,kij,kj->k', dm, Cinv, dm))
        post = torch.linalg.solve(I / s2 + Mk, ((m / s2)[None] + torch.einsum('kij,kj->ki', Mk, self.c))[..., None])[..., 0]
        loc = torch.einsum('kd,kdr->kr', post, self.alpha) + self.dk
        return self.A @ mu_full + self.a0 + (Z[:, None] * loc).sum(0)


Utr = Xtr @ Pi0; Ytr = proj_y(Ftr)
Xt = torch.as_tensor(Xtr, dtype=DT); Ut = torch.as_tensor(Utr, dtype=DT); Yt = torch.as_tensor(Ytr, dtype=DT)
res = dict(n=n, L=L, seed=seed, d=d, r=r, advice_paths=advice_paths, VF=VF, budgets=BUD, rows=[])
for K in KS:
    t1 = time.time()
    model = Bumps(K, Utr, Ytr, Xtr)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    gen = torch.Generator().manual_seed(seed)
    for step in range(args.steps):
        idx = torch.randint(0, NT, (args.batch,), generator=gen)
        loss = ((model(Xt[idx], Ut[idx]) - Yt[idx]) ** 2).sum(1).mean() / VF
        if args.lam_pop > 0:
            lp = 0.0
            for b in torch.randint(0, len(tr_pops), (16,), generator=gen).tolist():
                m, mu, s, ym = tr_pops[b]
                lp = lp + ((model.mean_closed(torch.as_tensor(m, dtype=DT), torch.as_tensor(mu, dtype=DT), s)
                            - torch.as_tensor(ym, dtype=DT)) ** 2).sum() / VF
            loss = loss + args.lam_pop * lp / 16
        opt.zero_grad(); loss.backward(); opt.step()
    n_params = sum(p.numel() for p in model.parameters())
    if args.bump == 'iso':
        flops_mean = K * (8 * d + 4 * d * r + 40) + 2 * n * r                    # O(d) closed form per bump
        flops_g = K * (4 * d + 2 * d * r + 20) + 2 * n * r
    else:
        flops_mean = K * (8 * d ** 3 + 4 * d * r) + 2 * n * r                    # closed-form mean, per population
        flops_g = K * (2 * d * d + 2 * d * r) + 2 * n * r                         # one evaluation of g
    Xho = np.random.RandomState(seed + 3).standard_normal((1 << 13, n)); Fho = fwd(Xho)
    with torch.no_grad():
        ph = model(torch.as_tensor(Xho, dtype=DT), torch.as_tensor(Xho @ Pi0, dtype=DT)).numpy()
    leftover = float(((proj_y(Fho) - ph) ** 2).sum(1).mean() + (((Fho - cL) - proj_y(Fho) @ PiL.T) ** 2).sum(1).mean()) / VF
    rows = []
    frs = np.random.RandomState(seed + 1000 + K)
    for p in te:
        with torch.no_grad():
            Eg = cL + PiL @ model.mean_closed(torch.as_tensor(p['mu'] @ Pi0, dtype=DT), torch.as_tensor(p['mu'], dtype=DT), p['s']).numpy()
        e_model = float(((Eg - p['m']) ** 2).sum() / VF)
        n_eq_model = flops_mean / PASS
        mc_at_model_cost = p['trcov'] / max(n_eq_model, 1e-12) / VF
        cv = []
        for Nc in BUD:
            X = p['mu'] + p['s'] * frs.standard_normal((Nc, n)); F = fwd(X)
            with torch.no_grad():
                g = cL + model(torch.as_tensor(X, dtype=DT), torch.as_tensor(X @ Pi0, dtype=DT)).numpy() @ PiL.T
            est = Eg + (F - g).mean(0)
            cost = (flops_mean + Nc * (PASS + flops_g)) / PASS
            cv.append(dict(N=Nc, err=float(((est - p['m']) ** 2).sum() / VF), cost=cost,
                           mc_at_cost=p['trcov'] / cost / VF, rqmc_at_N=p['rqmc'][Nc] / VF,
                           resid_var=float((F - g).var(0).sum() / VF) if Nc > 1 else None))
        rows.append(dict(s=p['s'], e_model=e_model, model_cost_passes=n_eq_model, mc_at_model_cost=mc_at_model_cost,
                         pop_var_rel=p['trcov'] / VF, cv=cv))
    mem = None
    with torch.no_grad():
        Eg0 = cL + PiL @ model.mean_closed(torch.zeros(d, dtype=DT), torch.zeros(n, dtype=DT), 1.0).numpy()
    mem = dict(model_vs_trainmean=float(((Eg0 - Ftr.mean(0)) ** 2).sum() / VF),
               trainmean_vs_truth=float(((Ftr.mean(0) - te[-1]['m']) ** 2).sum() / VF))
    res['rows'].append(dict(K=K, leftover=leftover, n_params=n_params, advice_bits_float64=64 * n_params,
                            flops_mean=flops_mean, flops_g=flops_g, pops=rows, memorisation=mem, secs=time.time() - t1))
    for s in sorted(set(p['s'] for p in te)):
        rr = [x for x in rows if x['s'] == s]
        em = np.median([x['e_model'] for x in rr]); mcm = np.median([x['mc_at_model_cost'] for x in rr])
        cvb = np.median([x['cv'][-1]['err'] for x in rr]); mcb = np.median([x['cv'][-1]['mc_at_cost'] for x in rr])
        rqb = np.median([x['cv'][-1]['rqmc_at_N'] for x in rr]); rq1 = np.median([x['cv'][0]['rqmc_at_N'] for x in rr])
        print(f"K={K} s={s}: model-only {em:.2e} at {rows[0]['model_cost_passes']:.3g} passes (MC there {mcm:.2e}; RQMC at N={BUD[0]} {rq1:.2e}) | "
              f"CV at N={BUD[-1]}: {cvb:.2e} (MC at equal cost {mcb:.2e}, RQMC with N={BUD[-1]} {rqb:.2e})", flush=True)
    print(f"K={K}: leftover {leftover:.3f}, params {n_params}, memorisation check {mem}, ({time.time() - t1:.0f}s)", flush=True)
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
