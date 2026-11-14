"""step4m = step4k (A4 isotropic bumps) + training to convergence + the HEADLINE comparison (Kelvin via main ~20:45Z).

Convergence: Adam with validation on held-out TRAINING populations and held-out training paths every eval_every steps;
lr x0.3 after `patience` evaluations without a 0.5% improvement, stop after 3 reductions (or max_steps). Doubling
check: continue the converged model for as many steps again and report the relative change of every error.
Headline: N(0, I) output-mean error of the model vs plain MC and RQMC with the SAME TOTAL number of input samples as
the advice (every advice path counts one), and vs the self-normalised importance-reweighted mean of exactly those
advice paths (target N(0, I), proposal = the advice mixture). Also: distinct gate patterns per layer.

Original step4k docstring:
A4 isotropic-bump experts with more advice and STRONGER hold-out shapes (Kelvin via main ~19:20Z), 32x4.

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
ap.add_argument('--max_steps', type=int, default=60000)
ap.add_argument('--eval_every', type=int, default=200)
ap.add_argument('--patience', type=int, default=3)
ap.add_argument('--log2truth', type=int, default=24)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
KS = [int(k) for k in args.Ks.split(',')]
d = min(args.d, n); r = min(args.r, n)
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4m_n{n}_L{L}_s{seed}_d{d}.json')
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
    FX = fwd(X)
    tr_pops.append(dict(comps=[(1.0, mu, s * s * np.eye(n))], ym=proj_y(FX).mean(0), X=X, F=FX, mu=mu, s=s))
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

# ---------------- headline baselines: N(0, I) with the advice's own sample count
N_ADV = NT + args.pops * args.M_pop
trs = np.random.RandomState(seed + 4242)
S1 = np.zeros(n); S2 = np.zeros(n); NTRU = 1 << args.log2truth
for i in range(NTRU >> 20 if NTRU >= (1 << 20) else 1):
    Fq = fwd(trs.standard_normal((min(NTRU, 1 << 20), n))); S1 += Fq.sum(0); S2 += (Fq * Fq).sum(0)
m0 = S1 / NTRU; tr0 = float((S2 / NTRU - m0 ** 2).sum())
truth_err = tr0 / NTRU / VF                                   # expected nMSE of the truth itself
mc_adv = tr0 / N_ADV / VF                                     # plain MC with N_ADV paths (expected nMSE)
rq_errs = []
N2 = 1 << int(math.floor(math.log2(N_ADV)))
for rep_ in range(4):
    eng = qmc.Sobol(d=n, scramble=True, seed=seed * 7919 + rep_)
    acc = np.zeros(n)
    for j in range(N2 >> 18 if N2 >= (1 << 18) else 1):
        z = ndtri(np.clip(eng.random(min(N2, 1 << 18)), 1e-12, 1 - 1e-12)); acc += fwd(z).sum(0)
    rq_errs.append(float(((acc / N2 - m0) ** 2).sum() / VF))
rqmc_adv = float(np.mean(rq_errs))
# self-normalised IS of exactly the advice paths, target N(0, I), proposal = advice mixture
def log_q(X):
    lq = [math.log(NT / N_ADV) - 0.5 * (X * X).sum(1)]
    for pp in tr_pops:
        lq.append(math.log(args.M_pop / N_ADV) - 0.5 * (((X - pp['mu']) / pp['s']) ** 2).sum(1) - n * math.log(pp['s']))
    return np.logaddexp.reduce(np.stack(lq), axis=0)
num = np.zeros(n); den = 0.0
for i in range(0, NT, 1 << 14):
    Xb = Xtr[i:i + (1 << 14)]; lw = -0.5 * (Xb * Xb).sum(1) - log_q(Xb); w_ = np.exp(lw)
    num += w_ @ Ftr[i:i + (1 << 14)]; den += w_.sum()
for pp in tr_pops:
    lw = -0.5 * (pp['X'] * pp['X']).sum(1) - log_q(pp['X']); w_ = np.exp(lw)
    num += w_ @ pp['F']; den += w_.sum()
is_adv = float(((num / den - m0) ** 2).sum() / VF)
plain_adv_nt = float(((Ftr.mean(0) - m0) ** 2).sum() / VF)    # mean of the N(0, I) advice paths alone
# distinct gate patterns per layer among N(0, I) paths
gp = []
with torch.no_grad():
    h = torch.from_numpy(np.asarray(Xtr, dtype=np.float32))
    for l in range(L):
        z = h @ W[l].T; h = torch.relu(z)
        bits = (z > 0).numpy()
        gp.append(int(len(np.unique(np.packbits(bits, axis=1), axis=0))))
print(f'[{time.time() - t0:.0f}s] headline baselines: advice paths {N_ADV}; N(0,I) MC {mc_adv:.2e}, RQMC (N={N2}) {rqmc_adv:.2e}, '
      f'IS of advice paths {is_adv:.2e}, mean of the {NT} N(0,I) advice paths {plain_adv_nt:.2e}, truth noise {truth_err:.1e}; '
      f'distinct gate patterns per layer (of {NT}) {gp}', flush=True)


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
NT_fit = NT - NT // 10; n_fit_pops = len(tr_pops) - len(tr_pops) // 10        # last 10% = validation
Xt = torch.as_tensor(Xtr, dtype=DT); Ut = torch.as_tensor(Utr, dtype=DT); Yt = torch.as_tensor(Ytr, dtype=DT)
res = dict(n=n, L=L, seed=seed, d=d, r=r, NT=NT, pops=args.pops, VF=VF, rows=[], N_adv=N_ADV, mc_adv=mc_adv, rqmc_adv=rqmc_adv,
           rqmc_adv_N=N2, is_adv=is_adv, mean_adv_nt=plain_adv_nt, truth_noise=truth_err, gate_patterns=gp,
           te=[dict(kind=p['kind'], trcov_rel=p['trcov'] / VF, rqmc=p['rqmc']) for p in te])
for K in KS:
    t1 = time.time()
    model = IsoBumps(K, Utr, Ytr, Xtr)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    gen = torch.Generator().manual_seed(seed)

    def train_steps(nsteps):
        for _ in range(nsteps):
            idx = torch.randint(0, NT_fit, (args.batch,), generator=gen)
            loss = ((model(Xt[idx], Ut[idx]) - Yt[idx]) ** 2).sum(1).mean() / VF
            lp = 0.0
            for b in torch.randint(0, n_fit_pops, (16,), generator=gen).tolist():
                pp = tr_pops[b]
                lp = lp + ((model.mean_pop(pp['comps']) - torch.as_tensor(pp['ym'], dtype=DT)) ** 2).sum() / VF
            loss = loss + args.lam_pop * lp / 16
            opt.zero_grad(); loss.backward(); opt.step()

    @torch.no_grad()
    def val_loss():
        ii = torch.arange(NT_fit, NT)
        lv = float(((model(Xt[ii], Ut[ii]) - Yt[ii]) ** 2).sum(1).mean() / VF)
        lpv = float(np.mean([float(((model.mean_pop(tr_pops[b]['comps']) - torch.as_tensor(tr_pops[b]['ym'], dtype=DT)) ** 2).sum() / VF)
                             for b in range(n_fit_pops, len(tr_pops))]))
        return lv + args.lam_pop * lpv

    best = float('inf'); bad = 0; red = 0; steps = 0; best_state = None
    while steps < args.max_steps:
        train_steps(args.eval_every); steps += args.eval_every
        v = val_loss()
        if v < best * (1 - 5e-3):
            best = v; bad = 0; best_state = {k_: t_.detach().clone() for k_, t_ in model.state_dict().items()}
        else:
            bad += 1
            if bad >= args.patience:
                red += 1; bad = 0
                if red > 3:
                    break
                for g_ in opt.param_groups:
                    g_['lr'] *= 0.3
    if best_state is not None:
        model.load_state_dict(best_state)
    lr_final = opt.param_groups[0]['lr']
    est_flops = d ** 3 * 10 + K * (2 * d * d + 2 * d * r + 12 * d) + 2 * n * r          # per Gaussian component

    @torch.no_grad()
    def headline():
        est0 = cL + PiL @ model.mean_pop([(1.0, np.zeros(n), np.eye(n))]).numpy()
        return float(((est0 - m0) ** 2).sum() / VF)
    h_conv = headline()
    rows_conv = [float(((cL + PiL @ model.mean_pop(p['comps']).detach().numpy() - p['m']) ** 2).sum() / VF) for p in te]
    # doubling check: as many steps again from the converged model at its final learning rate
    train_steps(steps)
    h_dbl = headline()
    rows_dbl = [float(((cL + PiL @ model.mean_pop(p['comps']).detach().numpy() - p['m']) ** 2).sum() / VF) for p in te]
    if best_state is not None:
        model.load_state_dict(best_state)
    dbl = dict(headline_conv=h_conv, headline_dbl=h_dbl, rel_change_headline=abs(h_dbl - h_conv) / max(h_conv, 1e-300),
               rel_change_heldout_median=float(np.median([abs(b_ - a_) / max(a_, 1e-300) for a_, b_ in zip(rows_conv, rows_dbl)])))
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
    res['rows'].append(dict(K=K, steps=steps, lr_final=lr_final, leftover=leftover, n_params=sum(q.numel() for q in model.parameters()),
                            pops=rows, secs=time.time() - t1, headline=h_conv, doubling=dbl))
    kinds = sorted(set(x['kind'] for x in rows), key=lambda k: [x['kind'] for x in rows].index(k))
    for kd in kinds:
        rr = [x for x in rows if x['kind'] == kd]
        print(f"K={K} {kd:26s}: model-only {np.median([x['err'] for x in rr]):.2e} at {rr[0]['cost']:.3g} passes "
              f"(MC there {np.median([x['mc_at_cost'] for x in rr]):.2e})", flush=True)
    print(f'K={K}: leftover {leftover:.3f}, converged at {steps} steps (lr {lr_final:.1e}), params {res["rows"][-1]["n_params"]} ({time.time() - t1:.0f}s)', flush=True)
    print(f'K={K} HEADLINE N(0,I): model {h_conv:.2e} vs MC {mc_adv:.2e}, RQMC {rqmc_adv:.2e}, IS-of-advice {is_adv:.2e} (same {N_ADV} paths); '
          f'doubling: headline {dbl["rel_change_headline"]:.1%}, held-out median {dbl["rel_change_heldout_median"]:.1%}', flush=True)
    json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
