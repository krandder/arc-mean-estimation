"""A3 pre-PREREG tests: (1) the oracle single-layer-expert ceiling, (2) the integration and additivity tests.

Oracle experts (zero training cost): for each layer l -> l+1, K centres = K-means centres of pilot states in the
projected coordinates u_l; each expert's map is the exact local linearisation of layer l+1 at the pilot state nearest
its centre, h_{l+1} = D_k W_{l+1} h_l, written in the projections: A_k = Pi_{l+1}^T D_k W Pi_l,
b_k = Pi_{l+1}^T (D_k W c_l - c_{l+1}); gate k = N(centre_k, covariance of its K-means cell + ridge), prior = cell
fraction; residual covariance from held-out pilot pairs (A2). Chain only (s = 1). Propagation: lib/lmle.py (Monte
Carlo draws through the pointwise fused map, gPoE at each draw), N(0, I) and held-out shell populations
N(sqrt(1 - s^2) mu, s^2 I). Metrics: the estimand's nMSE against the truth; the held-out population-mean error at the
output (|m - m_true|^2 / V_L, V_L = output variance in the projection); the INTEGRATION discrepancy (propagation vs an
accurate Monte Carlo integral of the same model's pointwise predictor over the population, 2^14 draws) separated from
the model's APPROXIMATION error (that integral vs the true population mean); additivity F(pP + (1-p)Q) vs
pF(P) + (1-p)F(Q). Cost in passes: pilot paths, VJPs, linearisation flops, propagation flops.
MEASURED (exploratory, A3 pre-PREREG). Usage: step4c.py SEED n L --Ks 1,4,16,64,256 --ds 16,32,64
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import lmle  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--Ks', default='1,4,16,64,256')
ap.add_argument('--ds', default='16,32,64')
ap.add_argument('--log2pilot', type=int, default=14)
ap.add_argument('--draws', type=int, default=256)
ap.add_argument('--fusion', default='gpoe')
ap.add_argument('--centres', type=int, default=3)
ap.add_argument('--widths', default='0.03,0.3')
ap.add_argument('--M_eval', type=int, default=1 << 14)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
KS = [int(k) for k in args.Ks.split(',')]; DS = [min(int(x), n) for x in args.ds.split(',')]
WID = [float(w) for w in args.widths.split(',')]
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4c_n{n}_L{L}_s{seed}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
Wn = [w.double().numpy() for w in W]
PASS = 2.0 * n * n * L
DT = lmle.DT
rng = np.random.RandomState(seed)


@torch.no_grad()
def push(X):
    h = torch.from_numpy(np.asarray(X, dtype=np.float32))
    H = [np.asarray(X, dtype=np.float64)]
    for l in range(L):
        h = torch.relu(h @ W[l].T)
        H.append(h.double().numpy())
    return H


def vjp_all(X, V):
    h = torch.from_numpy(np.asarray(X, dtype=np.float32)); masks = []
    for l in range(L):
        z = h @ W[l].T; masks.append(z > 0); h = torch.relu(z)
    g = torch.from_numpy(np.asarray(V, dtype=np.float32)); gs = [None] * (L + 1); gs[L] = g.double().numpy()
    for l in range(L - 1, -1, -1):
        g = (g * masks[l]) @ W[l]; gs[l] = g.double().numpy()
    return gs


NP = 1 << args.log2pilot
pilot = rng.standard_normal((NP, n)); Hp = push(pilot)
gs = vjp_all(pilot[:NP // 2], rng.standard_normal((NP // 2, n)))
cost_base = NP + (NP // 2) * 2                                      # pilot paths + VJPs, in passes
# truth (accurate MC) of the estimand
NT = 1 << 20
S1 = np.zeros(n); S2 = np.zeros(n); gT = np.random.RandomState(4242)
for _ in range(NT // 65536):
    f = push(gT.standard_normal((65536, n)))[-1]; S1 += f.sum(0); S2 += (f * f).sum(0)
mu_true = S1 / NT; V_true = float((S2 / NT - mu_true ** 2).sum())
# held-out populations and their true output means (M_eval paths each) and the draws used for the model integral
prs = np.random.RandomState(seed + 7)
pops = []
for ci in range(args.centres):
    mu = prs.standard_normal(n)
    for s in WID:
        mean = math.sqrt(1 - s * s) * mu
        X = mean + s * prs.standard_normal((args.M_eval, n))
        pops.append(dict(s=s, mean=mean, X=X, fmean=push(X)[-1].mean(0)))
print(f'[{time.time() - t0:.0f}s] pilot {NP}, truth 2^20, {len(pops)} held-out populations', flush=True)
res = dict(n=n, L=L, seed=seed, Ks=KS, ds=DS, widths=WID, V_true=V_true, rows=[])
for d in DS:
    bases = []
    for l in range(L + 1):
        c = np.zeros(n) if l == 0 else Hp[l].mean(0)
        if l < L:
            G = gs[l].T @ gs[l] / len(gs[l]); ev, U = np.linalg.eigh(G); P = U[:, ::-1][:, :d]
        else:
            _, _, Vt = np.linalg.svd(Hp[L] - c, full_matrices=False); P = Vt[:d].T
        bases.append((c, P))
    coords = lambda l, H: (H - bases[l][0]) @ bases[l][1]
    VL = float(coords(L, Hp[L]).var(0).sum())
    frac_out = float(coords(L, Hp[L]).var(0).sum() / Hp[L].var(0).sum())
    for K in KS:
        t1 = time.time()
        model = lmle.LMLE(L, d, K, d, skips=(1,))
        lin_flops = 0.0
        half = NP // 2
        for l in range(L):
            U_l = coords(l, Hp[l][:half])
            if K == 1:
                lab = np.zeros(half, dtype=int); cent = U_l.mean(0, keepdims=True)
            else:
                km = KMeans(n_clusters=K, n_init=1, max_iter=50, random_state=seed).fit(U_l)
                lab, cent = km.labels_, km.cluster_centers_
            A, b, covs, pri = [], [], [], []
            for k in range(K):
                idx = np.where(lab == k)[0]
                j = idx[np.argmin(((U_l[idx] - cent[k]) ** 2).sum(1))] if len(idx) else 0
                hstate = Hp[l][j]
                Dk = (Wn[l] @ hstate > 0).astype(float)
                M = Dk[:, None] * Wn[l]                                 # exact local map of layer l+1
                A.append(bases[l + 1][1].T @ M @ bases[l][1])
                b.append(bases[l + 1][1].T @ (M @ bases[l][0] - bases[l + 1][0]))
                C = np.cov(U_l[idx].T) if len(idx) > d else np.cov(U_l.T)
                covs.append(C + 1e-3 * np.trace(C) / d * np.eye(d))
                pri.append(max(len(idx), 1) / half)
                lin_flops += 2 * n * n + 2 * d * n * n
            bank = model.banks[f'{l}_1']
            bank.init_oracle(cent, covs, np.array(pri) / sum(pri), A, b)
            bank.set_heldout_error(coords(l, Hp[l][half:]), coords(l + 1, Hp[l + 1][half:]))
        eps = {l: lmle.std_draws(args.draws, d, 3000 + l) for l in range(L + 1)}
        prop_flops = L * args.draws * K * d * d * 6
        # estimand
        with torch.no_grad():
            o, st = model.propagate(torch.zeros(d, dtype=DT), torch.eye(d, dtype=DT), eps, mode=args.fusion)
        est = bases[L][0] + bases[L][1] @ o[-1][0].numpy()
        e_est = float(((est - mu_true) ** 2).sum() / V_true)
        # populations: propagation vs model integral vs truth
        pe, integ, approx = [], [], []
        for p in pops:
            m0 = torch.as_tensor(p['mean'] @ bases[0][1], dtype=DT); S0 = torch.eye(d, dtype=DT) * p['s'] ** 2
            with torch.no_grad():
                op, _ = model.propagate(m0, S0, eps, mode=args.fusion)
                us, _ = model.point_chain(torch.as_tensor(coords(0, p['X'][:4096]), dtype=DT), mode=args.fusion)
            m_prop = op[-1][0].numpy()
            m_int = us[L].numpy().mean(0)                                   # integral of the pointwise predictor
            m_true = coords(L, p['fmean'][None])[0]
            pe.append((p['s'], float(((m_prop - m_true) ** 2).sum() / VL)))
            integ.append((p['s'], float(((m_prop - m_int) ** 2).sum() / VL)))
            approx.append((p['s'], float(((m_int - m_true) ** 2).sum() / VL)))
        # additivity: F(pP + (1-p)Q) vs pF(P) + (1-p)F(Q) for the first two populations of width 0.3
        P_, Q_ = [p for p in pops if p['s'] == WID[-1]][:2]
        mP = torch.as_tensor(P_['mean'] @ bases[0][1], dtype=DT); mQ = torch.as_tensor(Q_['mean'] @ bases[0][1], dtype=DT)
        S_ = torch.eye(d, dtype=DT) * WID[-1] ** 2
        with torch.no_grad():
            oP, _ = model.propagate(mP, S_, eps, mode=args.fusion, split_on=False)
            oQ, _ = model.propagate(mQ, S_, eps, mode=args.fusion, split_on=False)
            oM, _ = model.propagate([(0.3, mP, S_), (0.7, mQ, S_)], None, eps, mode=args.fusion, split_on=False)
        add_err = float(((oM[-1][0] - (0.3 * oP[-1][0] + 0.7 * oQ[-1][0])) ** 2).sum() / VL)
        cost = cost_base + (lin_flops + prop_flops) / PASS
        row = dict(d=d, K=K, estimand_nmse=e_est, estimand_bar=float(np.trace(o[-1][2].numpy()) / VL),
                   pop_err=pe, integration=integ, approximation=approx, additivity=add_err, cost=cost,
                   out_frac=frac_out, secs=time.time() - t1)
        res['rows'].append(row)
        agg = lambda lst, s: float(np.median([v for w, v in lst if w == s]))
        print(f"d={d} K={K}: estimand nMSE {e_est:.2e} | pop error (s={WID[0]}/{WID[-1]}) {agg(pe, WID[0]):.3f}/{agg(pe, WID[-1]):.3f}"
              f" = integration {agg(integ, WID[0]):.3f}/{agg(integ, WID[-1]):.3f} vs approximation {agg(approx, WID[0]):.3f}/{agg(approx, WID[-1]):.3f}"
              f" | additivity {add_err:.1e} | cost {cost:.0f} passes ({row['secs']:.0f}s)", flush=True)
        json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
