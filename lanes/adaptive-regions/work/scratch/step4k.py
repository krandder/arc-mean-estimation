"""A4 isotropic-bump experts with more advice and STRONGER hold-out shapes (Kelvin via main ~19:20Z), 32x4.

Advice (free): 2^20 N(0, I) training paths + 2,000 training shell populations N(sqrt(1 - s^2) mu, s^2 I) x 256 paths;
the model g(x) = A x + a0 + sum_k exp(-lambda_k/2 |u - c_k|^2) (alpha_k^T u + d_k), u = Pi_0^T x (downstream-read input
projection), fitted by pointwise MSE + the shell population-mean loss (closed form).
Held-out estimands (shapes the training never resembled, plus the shells): shells (s = 0.1/0.3/0.6/0.9, new centres);
anisotropic Gaussians N(sqrt(1 - s^2) mu, Sigma), Sigma = Q diag(sig2) Q^T, condition numbers 10 and 100, tr Sigma =
n s^2 (s = 0.3, 0.9); shifted N(0.5 mu, 0.6^2 I); tilted N(0, I + 3 v v^T); mixtures of 2 and 3 shell Gaussians;
N(0, I) (reported, flagged: the training shells cover it).
Closed form for a Gaussian component N(mu, Sigma): u ~ N(m, S), S = Pi_0^T Sigma Pi_0 = Q diag(s_j) Q^T:
E[bump_k] = prod_j (1 + s_j lambda_k)^{-1/2} exp(-1/2 sum_j (Q^T(m - c_k))_j^2 / (1/lambda_k + s_j)),
E[bump_k u] = E[bump_k] (m + Q diag(s_j / (s_j + 1/lambda_k)) Q^T (c_k - m)). Estimation cost = eigendecomposition + K
rotations of centres (d^2 each) + O(K d r). MC and RQMC on each held-out population at equal estimation compute.
MEASURED (exploratory). Usage: step4k.py SEED n L --Ks 64,256,1024,4096
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
from scipy.stats import qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
from sklearn.cluster import MiniBatchKMeans  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--Ks', default='64,256,1024,4096')
ap.add_argument('--d', type=int, default=32)
ap.add_argument('--r', type=int, default=32)
ap.add_argument('--log2train', type=int, default=20)
ap.add_argument('--pops', type=int, default=2000)
ap.add_argument('--M_pop', type=int, default=256)
ap.add_argument('--lam_pop', type=float, default=1.0)
ap.add_argument('--steps', type=int, default=1200)
ap.add_argument('--lr', type=float, default=5e-3)
ap.add_argument('--batch', type=int, default=2048)
ap.add_argument('--te_centres', type=int, default=3)
ap.add_argument('--equal_steps', action='store_true', help='same number of steps at every K (no big-K cap)')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
KS = [int(k) for k in args.Ks.split(',')]
d = min(args.d, n); r = min(args.r, n)
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4k_n{n}_L{L}_s{seed}_d{d}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
PASS = 2.0 * n * n * L
DT = torch.float64
rng = np.random.RandomState(seed)


@torch.no_grad()
def fwd(X, chunk=1 << 16):
    outs = []
    for i in range(0, len(X), chunk):
        h = torch.from_numpy(np.asarray(X[i:i + chunk], dtype=np.float32))
        for l in range(L):
            h = torch.relu(h @ W[l].T)
        outs.append(h.double().numpy())
    return np.concatenate(outs)


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
NV = min(NT, 1 << 15); G0 = vjp0(Xtr[:NV], rng.standard_normal((NV, n)))
ev, U = np.linalg.eigh(G0.T @ G0 / len(G0)); Pi0 = np.ascontiguousarray(U[:, ::-1][:, :d])
cL = Ftr.mean(0); _, _, Vt = np.linalg.svd(Ftr[:1 << 17] - cL, full_matrices=False); PiL = np.ascontiguousarray(Vt[:r].T)
VF = float(Ftr.var(0).sum())
proj_y = lambda F: (F - cL) @ PiL
prs = np.random.RandomState(seed + 5)
tr_pops = []
for b in range(args.pops):
    s = [0.03, 0.1, 0.3, 0.6, 0.9][b % 5]
    mu = math.sqrt(1 - s * s) * prs.standard_normal(n)
    X = mu + s * prs.standard_normal((args.M_pop, n))
    tr_pops.append(dict(comps=[(1.0, mu, s * s * np.eye(n))], ym=proj_y(fwd(X)).mean(0)))
print(f'[{time.time() - t0:.0f}s] advice: {NT} paths + {args.pops} shell populations', flush=True)

# held-out shapes
hrs = np.random.RandomState(seed + 77)


def rand_cov(kappa, s):
    Q, _ = np.linalg.qr(hrs.standard_normal((n, n)))
    sig = np.exp(np.linspace(0, -math.log(kappa), n)); sig = sig / sig.sum() * n * s * s
    return (Q * sig) @ Q.T


te = []
for ci in range(args.te_centres):
    mu = hrs.standard_normal(n)
    for s in (0.1, 0.3, 0.6, 0.9):
        te.append(dict(kind=f'shell s={s}', comps=[(1.0, math.sqrt(1 - s * s) * mu, s * s * np.eye(n))]))
    for kappa in (10, 100):
        for s in (0.3, 0.9):
            te.append(dict(kind=f'aniso k={kappa} s={s}', comps=[(1.0, math.sqrt(1 - s * s) * mu, rand_cov(kappa, s))]))
    te.append(dict(kind='shifted', comps=[(1.0, 0.5 * mu, 0.36 * np.eye(n))]))
    v = hrs.standard_normal(n); v /= np.linalg.norm(v)
    te.append(dict(kind='tilted', comps=[(1.0, np.zeros(n), np.eye(n) + 3 * np.outer(v, v))]))
    for nm in (2, 3):
        w = hrs.dirichlet(np.ones(nm))
        cs = []
        for j in range(nm):
            s = [0.3, 0.6][j % 2]
            cs.append((float(w[j]), math.sqrt(1 - s * s) * hrs.standard_normal(n), s * s * np.eye(n)))
        te.append(dict(kind=f'mixture {nm}', comps=cs))
te.append(dict(kind='N(0,I) [not truly held out]', comps=[(1.0, np.zeros(n), np.eye(n))]))


def sample_pop(p, N, rs):
    w = np.array([c[0] for c in p['comps']])
    cnt = rs.multinomial(N, w / w.sum())
    xs = []
    for (wc, mu, Sig), k in zip(p['comps'], cnt):
        if k:
            Lc = np.linalg.cholesky(Sig + 1e-12 * np.eye(n))
            xs.append(mu + rs.standard_normal((k, n)) @ Lc.T)
    return np.concatenate(xs)


for p in te:
    F = fwd(sample_pop(p, 1 << 18, hrs))
    p['m'] = F.mean(0); p['trcov'] = float(F.var(0).sum())
    rq = {}
    for Nb in (16, 64, 256, 1024):
        errs = []
        for rep in range(8):
            eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1000 + rep + 31 * Nb)
            z = ndtri(np.clip(eng.random(Nb), 1e-12, 1 - 1e-12))
            # stratified allocation over mixture components, inverse-normal per component
            w = np.array([c[0] for c in p['comps']]); cnt = np.floor(Nb * w / w.sum()).astype(int); cnt[0] += Nb - cnt.sum()
            xs = []; i0 = 0
            for (wc, mu, Sig), k in zip(p['comps'], cnt):
                Lc = np.linalg.cholesky(Sig + 1e-12 * np.eye(n)); xs.append(mu + z[i0:i0 + k] @ Lc.T); i0 += k
            Fq = fwd(np.concatenate(xs))
            est = sum(wc / w.sum() * Fq[sum(cnt[:j]):sum(cnt[:j + 1])].mean(0) for j, (wc, _, _) in enumerate(p['comps']) if cnt[j] > 0)
            errs.append(float(((est - p['m']) ** 2).sum() / VF))
        rq[Nb] = float(np.mean(errs))
    p['rqmc'] = rq
print(f'[{time.time() - t0:.0f}s] {len(te)} held-out populations with truths and RQMC', flush=True)


class IsoBumps(torch.nn.Module):
    def __init__(self, K, Utr, Ytr, Xtr):
        super().__init__()
        km = MiniBatchKMeans(n_clusters=K, n_init=1, random_state=seed, batch_size=4096).fit(Utr[:1 << 17])
        cent = km.cluster_centers_
        nf = min(len(Xtr), 1 << 17); coef, *_ = np.linalg.lstsq(np.c_[Xtr[:nf], np.ones(nf)], Ytr[:nf], rcond=None)
        P = lambda a: torch.nn.Parameter(torch.as_tensor(a, dtype=DT))
        self.A = P(coef[:-1].T); self.a0 = P(coef[-1]); self.c = P(cent)
        spread = np.median(((Utr[:4096, None, :] - cent[None]) ** 2).sum(-1).min(1)) if K > 1 else d
        self.loglam = P(np.full(K, math.log(1.0 / max(spread, 1e-6))))
        self.alpha = P(np.zeros((K, d, r))); self.dk = P(np.zeros((K, r)))

    def forward(self, X, U):
        D2 = (U * U).sum(1)[:, None] - 2 * U @ self.c.T + (self.c * self.c).sum(1)[None]
        bk = torch.exp(-0.5 * torch.exp(self.loglam)[None] * D2.clamp_min(0))
        loc = torch.einsum('nd,kdr->nkr', U, self.alpha) + self.dk[None]
        return X @ self.A.T + self.a0 + torch.einsum('nk,nkr->nr', bk, loc)

    def mean_component(self, mu, Sig):
        m = torch.as_tensor(mu @ Pi0, dtype=DT)
        S = Pi0.T @ Sig @ Pi0
        sj, Q = np.linalg.eigh(0.5 * (S + S.T)); sj = np.clip(sj, 0, None)
        sj = torch.as_tensor(sj, dtype=DT); Q = torch.as_tensor(Q, dtype=DT)
        lam = torch.exp(self.loglam)
        dc = (self.c - m) @ Q                                                     # (K, d) in eigencoords
        Z = torch.exp(-0.5 * torch.log1p(sj[None] * lam[:, None]).sum(1)
                      - 0.5 * (dc ** 2 / (1 / lam[:, None] + sj[None])).sum(1))
        post = m + (dc * (sj[None] / (sj[None] + 1 / lam[:, None]))) @ Q.T
        loc = torch.einsum('kd,kdr->kr', post, self.alpha) + self.dk
        return self.A @ torch.as_tensor(mu, dtype=DT) + self.a0 + (Z[:, None] * loc).sum(0)

    def mean_pop(self, comps):
        w = sum(c[0] for c in comps)
        return sum(c[0] / w * self.mean_component(c[1], c[2]) for c in comps)


Utr = Xtr @ Pi0; Ytr = proj_y(Ftr)
Xt = torch.as_tensor(Xtr, dtype=DT); Ut = torch.as_tensor(Utr, dtype=DT); Yt = torch.as_tensor(Ytr, dtype=DT)
res = dict(n=n, L=L, seed=seed, d=d, r=r, NT=NT, pops=args.pops, VF=VF, rows=[],
           te=[dict(kind=p['kind'], trcov_rel=p['trcov'] / VF, rqmc=p['rqmc']) for p in te])
for K in KS:
    t1 = time.time()
    model = IsoBumps(K, Utr, Ytr, Xtr)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    gen = torch.Generator().manual_seed(seed)
    steps = args.steps if (K <= 256 or args.equal_steps) else max(300, args.steps * 256 // K)
    for step in range(steps):
        idx = torch.randint(0, NT, (args.batch,), generator=gen)
        loss = ((model(Xt[idx], Ut[idx]) - Yt[idx]) ** 2).sum(1).mean() / VF
        lp = 0.0
        for b in torch.randint(0, len(tr_pops), (16,), generator=gen).tolist():
            pp = tr_pops[b]
            lp = lp + ((model.mean_pop(pp['comps']) - torch.as_tensor(pp['ym'], dtype=DT)) ** 2).sum() / VF
        loss = loss + args.lam_pop * lp / 16
        opt.zero_grad(); loss.backward(); opt.step()
    est_flops = d ** 3 * 10 + K * (2 * d * d + 2 * d * r + 12 * d) + 2 * n * r          # per Gaussian component
    with torch.no_grad():
        Xho = np.random.RandomState(seed + 3).standard_normal((1 << 13, n)); Fho = fwd(Xho)
        ph = model(torch.as_tensor(Xho, dtype=DT), torch.as_tensor(Xho @ Pi0, dtype=DT)).numpy()
        leftover = float(((proj_y(Fho) - ph) ** 2).sum(1).mean() + (((Fho - cL) - proj_y(Fho) @ PiL.T) ** 2).sum(1).mean()) / VF
        rows = []
        for p in te:
            est = cL + PiL @ model.mean_pop(p['comps']).numpy()
            e = float(((est - p['m']) ** 2).sum() / VF)
            cost = est_flops * len(p['comps']) / PASS
            rows.append(dict(kind=p['kind'], err=e, cost=cost, mc_at_cost=p['trcov'] / VF / cost))
    res['rows'].append(dict(K=K, steps=steps, leftover=leftover, n_params=sum(q.numel() for q in model.parameters()),
                            pops=rows, secs=time.time() - t1))
    kinds = sorted(set(x['kind'] for x in rows), key=lambda k: [x['kind'] for x in rows].index(k))
    for kd in kinds:
        rr = [x for x in rows if x['kind'] == kd]
        print(f"K={K} {kd:26s}: model-only {np.median([x['err'] for x in rr]):.2e} at {rr[0]['cost']:.3g} passes "
              f"(MC there {np.median([x['mc_at_cost'] for x in rr]):.2e})", flush=True)
    print(f'K={K}: leftover {leftover:.3f}, steps {steps}, params {res["rows"][-1]["n_params"]} ({time.time() - t1:.0f}s)', flush=True)
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
