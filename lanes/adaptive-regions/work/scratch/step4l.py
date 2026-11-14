"""Step 4 per SPEC-learned-experts.md v1 + A1 + A2 (hashed 16:58:07Z): learned layered mixture of linear experts.

Pipeline (one net, one model size):
1. pilot N(0, I) paths; projections Pi_l = top-d eigenvectors of E[J_l^T J_l] (one VJP per path gives every layer;
   v ~ N(0, I) at the output), Pi_L = top-d principal axes of h_L, centres c_l (c_0 = 0);
2. (a) per-sample model: EM warm start of every bank (l, s), s in skips, on pilot pairs; held-out residual covariances
   R_err from a second pilot half (A2);
3. populations: training and held-out centres disjoint; widths sigma; empirical moments of u_l per layer from M paths;
4. (b) population model: (a) trained end to end on sum_b sum_l [|m - m_emp|^2 / V_l + lam_cov ||S - S_emp||^2 / V_l^2
   + lam_cal NLL(m_emp; m, E + S_emp / M)], Adam, curriculum on sigma;
5. metrics (spec section 5, A2): population-mean error per layer and width, (a) vs (b), held-out; interval coverage
   (68% / 95%, Mahalanobis with E + S_emp/M); the estimand m_L(N(0, I)) with and without N(0, I) in training against
   the truth; pointwise residual; cost in passes (all paths, VJPs, EM and training flops, propagation).
MEASURED. Usage: step4l.py SEED n L [--K 8] [--d 32] [--fusion gpoe] [--with_n01 1] ...
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
from scipy.stats import chi2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import lmle  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--K', type=int, default=8)
ap.add_argument('--d', type=int, default=32)
ap.add_argument('--r', type=int, default=8)
ap.add_argument('--skips', default='1,2,4,8')
ap.add_argument('--log2pilot', type=int, default=13)
ap.add_argument('--M', type=int, default=1024)
ap.add_argument('--centres_tr', type=int, default=8)
ap.add_argument('--centres_te', type=int, default=4)
ap.add_argument('--widths', default='0.03,0.1,0.3,1.0')
ap.add_argument('--pop_family', default='shell', help="shell: N(sqrt(1-s^2) mu, s^2 I); spec: N(mu, s^2 I)")
ap.add_argument('--with_n01', type=int, default=1)
ap.add_argument('--epochs', type=int, default=150)
ap.add_argument('--lr', type=float, default=3e-3)
ap.add_argument('--lam_cov', type=float, default=0.1)
ap.add_argument('--lam_cal', type=float, default=0.01)
ap.add_argument('--draws', type=int, default=256)
ap.add_argument('--fusion', default='gpoe')
ap.add_argument('--K_pop', type=int, default=64)
ap.add_argument('--truth_log2', type=int, default=20)
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed, K = args.n, args.L, args.seed, args.K
d = min(args.d, n)
SK = tuple(int(s) for s in args.skips.split(','))
WID = [float(w) for w in args.widths.split(',')]
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
tag = f'n{n}_L{L}_s{seed}_K{K}_d{d}_{args.fusion}_n01{args.with_n01}_p{args.log2pilot}'
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4l_{tag}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
PASS = 2.0 * n * n * L
DT = lmle.DT
rng = np.random.RandomState(seed)
flops = dict(paths=0.0, vjp=0.0, em=0.0, train=0.0, estimand=0.0)


@torch.no_grad()
def push(X):
    h = torch.from_numpy(np.asarray(X, dtype=np.float32))
    H = [np.asarray(X, dtype=np.float64)]
    for l in range(L):
        h = torch.relu(h @ W[l].T)
        H.append(h.double().numpy())
    return H


def vjp_all(X, V):
    """g_l = d(v . h_L)/d h_l for every l (one backward pass)."""
    h = torch.from_numpy(np.asarray(X, dtype=np.float32))
    masks = []
    for l in range(L):
        z = h @ W[l].T
        masks.append(z > 0)
        h = torch.relu(z)
    g = torch.from_numpy(np.asarray(V, dtype=np.float32))
    gs = [None] * (L + 1)
    gs[L] = g.double().numpy()
    for l in range(L - 1, -1, -1):
        g = (g * masks[l]) @ W[l]
        gs[l] = g.double().numpy()
    return gs


# 1. pilot, projections
NP = 1 << args.log2pilot
pilot = rng.standard_normal((NP, n))
Hp = push(pilot); flops['paths'] += NP * PASS
gs = vjp_all(pilot[:NP // 2], rng.standard_normal((NP // 2, n))); flops['vjp'] += (NP // 2) * 2 * PASS
bases = []
for l in range(L + 1):
    c = np.zeros(n) if l == 0 else Hp[l].mean(0)
    if l < L:
        G = gs[l].T @ gs[l] / len(gs[l])
        ev, U = np.linalg.eigh(G)
        P = U[:, ::-1][:, :d]
    else:
        _, _, Vt = np.linalg.svd(Hp[L] - c, full_matrices=False)
        P = Vt[:d].T
    bases.append((c, P))
coords = lambda l, H: (H - bases[l][0]) @ bases[l][1]
V_l = [float(coords(l, Hp[l]).var(0).sum()) for l in range(L + 1)]
# truth for the estimand
try:
    tr = ar.au.load_arc_truth(seed, n, L)
    mu_true = tr['mean'][-1] if tr['mean'].ndim == 2 else tr['mean']; V_true = float((tr['var'][-1] if tr['var'].ndim == 2 else tr['var']).sum())
except Exception:
    try:
        dd = np.load(f'/home/agent/workspaces/mats/work/arc-update/runs/truth_n{n}_L{L}_s{seed}.npz')
        NN = float(dd['N']); m_ = (dd['S1A'] + dd['S1B']) / NN; v_ = (dd['S2A'] + dd['S2B']) / NN - m_ ** 2
        mu_true, V_true = m_[L - 1], float(v_[L - 1].sum())
    except Exception:
        S1 = np.zeros(n); S2 = np.zeros(n); NT = 1 << args.truth_log2
        g2 = np.random.RandomState(777)
        for _ in range(NT // 65536):
            f = push(g2.standard_normal((65536, n)))[-1]; S1 += f.sum(0); S2 += (f * f).sum(0)
        mu_true = S1 / NT; V_true = float((S2 / NT - mu_true ** 2).sum())

# 2. (a) EM warm start, held-out residual covariances
model_a = lmle.LMLE(L, d, K, args.r, skips=SK)
half = NP // 2
for key, bank in model_a.banks.items():
    l, s = map(int, key.split('_'))
    bank.init_em(coords(l, Hp[l][:half]), coords(l + s, Hp[l + s][:half]), seed=seed)
    bank.set_heldout_error(coords(l, Hp[l][half:]), coords(l + s, Hp[l + s][half:]))
    flops['em'] += bank.em_iter * half * K * (2 * d) ** 2 * 6
print(f'[{time.time() - t0:.0f}s] pilot {NP}, projections, EM for {len(model_a.banks)} banks', flush=True)


# 3. populations
def make_pops(n_centres, M, rs, include_n01):
    pops = []
    for ci in range(n_centres):
        mu = rs.standard_normal(n)
        for s in WID:
            if s >= 1.0 and args.pop_family == 'shell':
                continue                                         # the s = 1 shell population is N(0, I) itself
            mean = math.sqrt(max(1 - s * s, 0)) * mu if args.pop_family == 'shell' else mu
            X = mean + s * rs.standard_normal((M, n))
            H = push(X); flops['paths'] += M * PASS
            pops.append(dict(s=s, mean=mean, cov0=s * s,
                             ms=[coords(l, H[l]).mean(0) for l in range(1, L + 1)],
                             Ss=[np.cov(coords(l, H[l]).T) for l in range(1, L + 1)]))
    if include_n01:
        X = rs.standard_normal((M, n)); H = push(X); flops['paths'] += M * PASS
        pops.append(dict(s=1.0, mean=np.zeros(n), cov0=1.0, ms=[coords(l, H[l]).mean(0) for l in range(1, L + 1)],
                         Ss=[np.cov(coords(l, H[l]).T) for l in range(1, L + 1)]))
    return pops


tr_pops = make_pops(args.centres_tr, args.M, np.random.RandomState(seed + 1), args.with_n01)
te_pops = make_pops(args.centres_te, 2 * args.M, np.random.RandomState(seed + 2), False)
paths_te = len(te_pops) * 2 * args.M
flops['paths'] -= paths_te * PASS                               # held-out evaluation paths are not estimator cost
eps = {l: lmle.std_draws(args.draws, d, 1000 + l) for l in range(L + 1)}
print(f'[{time.time() - t0:.0f}s] {len(tr_pops)} training, {len(te_pops)} held-out populations', flush=True)


def u0_moments(p):
    m0 = torch.as_tensor(p['mean'] @ bases[0][1], dtype=DT)
    S0 = torch.eye(d, dtype=DT) * p['cov0']
    return m0, S0


def run_pops(model, pops, grad=False):
    res = []
    for p in pops:
        m0, S0 = u0_moments(p)
        if grad:
            o, st = model.propagate(m0, S0, eps, K_pop=args.K_pop, mode=args.fusion)
        else:
            with torch.no_grad():
                o, st = model.propagate(m0, S0, eps, K_pop=args.K_pop, mode=args.fusion)
        res.append((o, st))
    return res


def prop_flops(model):
    nb = sum(len(model.routes(t)) for t in range(1, L + 1))
    return nb * (args.draws * K * (d * d * 4) + K * d ** 3 * 3)


def metrics(model, pops, label):
    rs = run_pops(model, pops)
    per_layer = {s: [[] for _ in range(L)] for s in WID}
    cov68 = []; cov95 = []; bars = []
    for (o, st), p in zip(rs, pops):
        for l in range(L):
            e = float(((o[l][0].numpy() - p['ms'][l]) ** 2).sum() / V_l[l + 1])
            per_layer[p['s']][l].append(e)
        dlt = o[-1][0].numpy() - p['ms'][-1]
        Ctot = o[-1][2].numpy() + p['Ss'][-1] / (2 * args.M)
        z2 = float(dlt @ np.linalg.solve(Ctot + 1e-12 * np.eye(d), dlt))
        q = chi2.cdf(z2, d)
        cov68.append(q <= 0.68); cov95.append(q <= 0.95)
        bars.append((p['s'], float(np.trace(o[-1][2].numpy()) / V_l[L]), float((dlt ** 2).sum() / V_l[L])))
    summ = {str(s): [float(np.mean(v)) if v else None for v in per_layer[s]] for s in WID}
    out = dict(per_layer=summ, interval_cov68=float(np.mean(cov68)), interval_cov95=float(np.mean(cov95)),
               bar_vs_err=bars)
    print(f"{label}: output population-mean error by width " +
          ', '.join(f"{s}: {summ[str(s)][-1]:.3f}" for s in WID if summ[str(s)][-1] is not None) +
          f" | interval coverage 68% {out['interval_cov68']:.2f}, 95% {out['interval_cov95']:.2f}", flush=True)
    return out


def estimand(model):
    m0 = torch.zeros(d, dtype=DT); S0 = torch.eye(d, dtype=DT)
    with torch.no_grad():
        o, st = model.propagate(m0, S0, eps, K_pop=args.K_pop, mode=args.fusion)
    est = bases[L][0] + bases[L][1] @ o[-1][0].numpy()
    err = float(((est - mu_true) ** 2).sum() / V_true)
    bar = float(np.trace(bases[L][1] @ o[-1][2].numpy() @ bases[L][1].T) / V_true)
    comps = [(a, float(np.trace(E.numpy()) / V_l[L])) for a, _, E in st['components']]
    return err, bar, comps


def pointwise(model, M=2048):
    X = np.random.RandomState(seed + 9).standard_normal((M, n))
    f = push(X)[-1]
    with torch.no_grad():
        us, _ = model.point_chain(torch.as_tensor(coords(0, X), dtype=DT), mode=args.fusion)
    pred = bases[L][0] + us[L].numpy() @ bases[L][1].T
    return float(((f - pred) ** 2).sum(1).mean() / f.var(0).sum())


res = dict(args=vars(args), d=d, V_l=V_l, n_tr_pops=len(tr_pops), n_te_pops=len(te_pops))
res['a'] = metrics(model_a, te_pops, '(a) per-sample EM experts, held-out')
res['a']['estimand_nmse'], res['a']['estimand_bar'], res['a']['components'] = estimand(model_a)
res['a']['pointwise'] = pointwise(model_a)
print(f"(a) estimand N(0,I): nMSE {res['a']['estimand_nmse']:.2e}, error bar (nMSE units) {res['a']['estimand_bar']:.2e}; pointwise residual {res['a']['pointwise']:.3f}", flush=True)
flops['estimand'] += prop_flops(model_a)

# 4. (b) end-to-end on populations
import copy
model_b = copy.deepcopy(model_a)
opt = torch.optim.Adam(model_b.parameters(), lr=args.lr)
widths_tr = np.array([p['s'] for p in tr_pops])
for ep in range(args.epochs):
    stage = 0.1 if ep < args.epochs // 3 else (0.3 if ep < 2 * args.epochs // 3 else 1.01)
    sel = [i for i in range(len(tr_pops)) if widths_tr[i] <= stage]
    opt.zero_grad()
    loss = 0.0
    for i in sel:
        p = tr_pops[i]
        m0, S0 = u0_moments(p)
        o, _ = model_b.propagate(m0, S0, eps, K_pop=args.K_pop, mode=args.fusion)
        for l in range(L):
            m, S, E = o[l]
            me = torch.as_tensor(p['ms'][l], dtype=DT); Se = torch.as_tensor(p['Ss'][l], dtype=DT)
            dm = m - me
            loss = loss + (dm ** 2).sum() / V_l[l + 1] + args.lam_cov * ((S - Se) ** 2).sum() / V_l[l + 1] ** 2
            Ct = E + Se / args.M + 1e-9 * torch.eye(d, dtype=DT)
            loss = loss + args.lam_cal * 0.5 * (dm @ torch.linalg.solve(Ct, dm) + torch.logdet(Ct)) / d
    (loss / max(len(sel), 1)).backward()
    opt.step()
    flops['train'] += 3 * len(sel) * prop_flops(model_b)
    if ep % max(1, args.epochs // 6) == 0 or ep == args.epochs - 1:
        print(f'  epoch {ep} (sigma <= {stage}, {len(sel)} pops): loss {float(loss.detach()) / max(len(sel), 1):.4e} [{time.time() - t0:.0f}s]', flush=True)
res['b'] = metrics(model_b, te_pops, '(b) population-trained, held-out')
res['b']['estimand_nmse'], res['b']['estimand_bar'], res['b']['components'] = estimand(model_b)
res['b']['pointwise'] = pointwise(model_b)
flops['estimand'] += prop_flops(model_b)
print(f"(b) estimand N(0,I): nMSE {res['b']['estimand_nmse']:.2e}, error bar {res['b']['estimand_bar']:.2e}; pointwise residual {res['b']['pointwise']:.3f}", flush=True)
cost = sum(flops.values()) / PASS
res.update(flops=flops, cost_passes=cost, mu_true_source='truth', secs=time.time() - t0)
try:
    rj = json.load(open(f'/home/agent/workspaces/mats/work/arc-update/runs/rqmc_n{n}_L{L}_s{seed}.json'))
    xs = np.log([x['N'] for x in rj['rows']]); ys = np.log([x['mean_nmse'] for x in rj['rows']])
    lc = math.log(cost)
    res['rqmc_at_cost'] = float(np.exp(np.interp(lc, xs, ys))) if xs[0] <= lc <= xs[-1] else \
        float(np.exp(ys[-1] + (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) * (lc - xs[-1])))
except Exception:
    res['rqmc_at_cost'] = None
res['mc_at_cost'] = 1.0 / cost
print(f"cost {cost:.3g} passes ({ {k: round(v / PASS) for k, v in flops.items()} }); MC at that cost {1 / cost:.2e}; RQMC {res['rqmc_at_cost']}", flush=True)
json.dump(res, open(out, 'w'))
print('wrote', out, f'total {time.time() - t0:.0f}s')
