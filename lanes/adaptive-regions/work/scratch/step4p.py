"""Step 4, population-level training (Kelvin's choices via main): (a) per-sample EM experts vs (b) the same experts
trained end to end on population moments, with gPoE fusion (lib/popmoe.py).

Populations: N(sqrt(1 - s^2) x_c, s^2 I) for centres x_c ~ N(0, I) and widths s (s = 1 is N(0, I)); training centres and
held-out centres are disjoint. Truth moments per layer: M sampled paths per population, mean and covariance in the
low-rank coordinates u_l = P_l^T (h_l - c_l) (top-d axes of a pilot N(0, I) cloud; u_0 = x).
(a) EM: per layer, a K-component joint GMM on (u_l, u_{l+1}) from the pilot paths (lib/gmoe.py) -> experts.
(b) the same experts after Adam on the population loss sum_b sum_l |m - m_emp|^2 / V_l + lam ||S - S_emp||_F^2 / V_l^2,
    curriculum: s <= 0.15 first, then s <= 0.5, then all.
Reports, for (a) and (b), on held-out populations: per-layer normalised mean error by width; the pointwise input-end
leftover Var(f - f_hat)/Var f (f_hat from tiny populations N(x, 0.01^2 I) at held-out inputs x); the N(0, I) output-mean
error against the truth; the gPoE vs mixture fusion; cost (all sampled paths + training flops) and RQMC at that cost.
MEASURED (exploratory, dev). Usage: step4p.py SEED n L [--K 4] [--d 32]
"""
import argparse, json, math, os, sys, time
import numpy as np
import torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import ar  # noqa: E402
import gmoe  # noqa: E402
import popmoe  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--K', type=int, default=4)
ap.add_argument('--d', type=int, default=32)
ap.add_argument('--log2pilot', type=int, default=13)
ap.add_argument('--M', type=int, default=1024)
ap.add_argument('--centres_tr', type=int, default=8)
ap.add_argument('--centres_te', type=int, default=4)
ap.add_argument('--widths', default='0.05,0.15,0.3,0.5,0.8,1.0')
ap.add_argument('--epochs', type=int, default=300)
ap.add_argument('--lr', type=float, default=3e-3)
ap.add_argument('--lam_cov', type=float, default=0.1)
ap.add_argument('--fusion', default='gpoe')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed, K = args.n, args.L, args.seed, args.K
d = min(args.d, n)
WID = [float(w) for w in args.widths.split(',')]
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs', f'step4p_n{n}_L{L}_s{seed}_K{K}.json')
t0 = time.time()
W = ar.weights(seed, n, L)
PASS = 2.0 * n * n * L
rng = np.random.RandomState(seed)


@torch.no_grad()
def push(X):
    """All states h_1..h_L for inputs X (numpy (M, n)) -> list of numpy arrays."""
    h = torch.from_numpy(X.astype(np.float32))
    H = []
    for l in range(L):
        h = torch.relu(h @ W[l].T)
        H.append(h.double().numpy())
    return H


pilot = rng.standard_normal((1 << args.log2pilot, n))
Hp = push(pilot)
bases = [(np.zeros(n), np.eye(n))]
for l in range(L):
    c = Hp[l].mean(0)
    _, sv, Vt = np.linalg.svd(Hp[l] - c, full_matrices=False)
    bases.append((c, Vt[:d].T))
V_l = [float(n)] + [float(((Hp[l] - bases[l + 1][0]) @ bases[l + 1][1]).var(0).sum()) for l in range(L)]
dims = [n] + [d] * L
coords = lambda l, H: (H - bases[l][0]) @ bases[l][1]
# truth
try:
    tr = ar.au.load_arc_truth(seed, n, L)
    mu_true = tr['mean'][-1] if tr['mean'].ndim == 2 else tr['mean']
    V_true = float((tr['var'][-1] if tr['var'].ndim == 2 else tr['var']).sum())
except Exception:
    dd = np.load(f'/home/agent/workspaces/mats/work/arc-update/runs/truth_n{n}_L{L}_s{seed}.npz')
    NN = float(dd['N']); m_ = (dd['S1A'] + dd['S1B']) / NN; v_ = (dd['S2A'] + dd['S2B']) / NN - m_ ** 2
    mu_true, V_true = m_[L - 1], float(v_[L - 1].sum())

# (a) EM experts per layer from the pilot paths
init = []
em_flops = 0.0
for l in range(L):
    U = pilot if l == 0 else coords(l, Hp[l - 1])
    Vv = coords(l + 1, Hp[l])
    mdl = gmoe.LayerMoE(K, seed=seed, max_iter=100).fit(U, Vv)
    em_flops += mdl.gm.n_iter_ * U.shape[0] * K * (U.shape[1] + d) ** 2 * 6
    G = np.stack([np.diag(mdl.Suu[k]) for k in range(K)])
    if l == 0:
        G = np.repeat(G.mean(1, keepdims=True), n, 1)                     # isotropic gates at the input
    init.append(dict(pi=mdl.pi, g=mdl.mu_u, G=G, B=mdl.B, b=mdl.b, R=mdl.R))
print(f'pilot {len(pilot)} paths + EM in {time.time() - t0:.0f}s', flush=True)


def populations(n_centres, M, rs):
    pops = []
    for ci in range(n_centres):
        xc = rs.standard_normal(n)
        for s in WID:
            if s >= 1.0 and ci > 0:
                continue
            mean = math.sqrt(max(1 - s * s, 0)) * xc
            X = mean + s * rs.standard_normal((M, n))
            H = push(X)
            ms = [coords(l + 1, H[l]).mean(0) for l in range(L)]
            Ss = [np.cov(coords(l + 1, H[l]).T) for l in range(L)]
            pops.append(dict(s=s, mean=mean, ms=ms, Ss=Ss, fmean=H[-1].mean(0)))
    return pops


tr_pops = populations(args.centres_tr, args.M, np.random.RandomState(seed + 1))
te_pops = populations(args.centres_te, 2 * args.M, np.random.RandomState(seed + 2))
n_samples_train = len(pilot) + len(tr_pops) * args.M
print(f'{len(tr_pops)} training populations, {len(te_pops)} held-out; {time.time() - t0:.0f}s', flush=True)


def to_t(pops):
    m0 = torch.tensor(np.stack([p['mean'] for p in pops]), dtype=popmoe.DT)
    S0 = torch.stack([torch.eye(n, dtype=popmoe.DT) * p['s'] ** 2 + 1e-9 * torch.eye(n, dtype=popmoe.DT) for p in pops])
    ms = [torch.tensor(np.stack([p['ms'][l] for p in pops]), dtype=popmoe.DT) for l in range(L)]
    Ss = [torch.tensor(np.stack([p['Ss'][l] for p in pops]), dtype=popmoe.DT) for l in range(L)]
    return m0, S0, ms, Ss


def evaluate(model, pops, fusion):
    m0, S0, ms_e, Ss_e = to_t(pops)
    with torch.no_grad():
        ms, Ss, _ = model(m0, S0, fusion)
    per_layer = []
    for l in range(L):
        err = ((ms[l] - ms_e[l]) ** 2).sum(1).numpy() / V_l[l + 1]
        per_layer.append({str(s): float(np.mean([e for e, p in zip(err, pops) if p['s'] == s])) for s in WID})
    # N(0, I) output mean (the s = 1 population) against the truth, in full output space
    i1 = [i for i, p in enumerate(pops) if p['s'] >= 1.0][0]
    est = bases[L][0] + bases[L][1] @ ms[-1][i1].numpy()
    e_true = float(((est - mu_true) ** 2).sum() / V_true)
    return per_layer, e_true


def pointwise_leftover(model, fusion, M=1024):
    rs = np.random.RandomState(seed + 3)
    X = rs.standard_normal((M, n))
    f = push(X)[-1]
    y = coords(L, f)
    m0 = torch.tensor(X, dtype=popmoe.DT)
    S0 = torch.eye(n, dtype=popmoe.DT)[None].repeat(M, 1, 1) * 1e-4
    with torch.no_grad():
        ms, _, _ = model(m0, S0, fusion)
    pred = ms[-1].numpy()
    VF = float(f.var(0).sum())
    out_sub = float(((f - bases[L][0]) - y @ bases[L][1].T).var(0).sum())
    return float((((y - pred) ** 2).sum(1).mean() + out_sub) / VF)


res = dict(n=n, L=L, seed=seed, K=K, d=d, widths=WID, n_samples_train=n_samples_train, fusion=args.fusion)
model_a = popmoe.PopMoE(dims, K, init=init)
for fus in ('gpoe', 'mix'):
    pl, et = evaluate(model_a, te_pops, fus)
    res[f'a_{fus}'] = dict(per_layer=pl, nmse_N01=et, pointwise_leftover=pointwise_leftover(model_a, fus))
    print(f"(a) EM experts, {fus}: held-out output mean error by width {pl[-1]}; N(0,I) nMSE {et:.2e}; pointwise "
          f"input-end leftover {res[f'a_{fus}']['pointwise_leftover']:.3f}", flush=True)
# (b) end-to-end on populations
model_b = popmoe.PopMoE(dims, K, init=init)
opt = torch.optim.Adam(model_b.parameters(), lr=args.lr)
m0, S0, ms_e, Ss_e = to_t(tr_pops)
widths_t = np.array([p['s'] for p in tr_pops])
tr_flops = 0.0
hist = []
for ep in range(args.epochs):
    stage = 0.15 if ep < args.epochs // 3 else (0.5 if ep < 2 * args.epochs // 3 else 1.01)
    sel = torch.from_numpy(np.where(widths_t <= stage)[0])
    opt.zero_grad()
    ms, Ss, _ = model_b(m0[sel], S0[sel], args.fusion)
    loss = 0.0
    for l in range(L):
        loss = loss + ((ms[l] - ms_e[l][sel]) ** 2).sum(1).mean() / V_l[l + 1] \
            + args.lam_cov * ((Ss[l] - Ss_e[l][sel]) ** 2).sum((1, 2)).mean() / V_l[l + 1] ** 2
    loss.backward()
    opt.step()
    tr_flops += 3 * len(sel) * sum(K * (dims[l] ** 2 * dims[l + 1] * 4 + dims[l + 1] ** 3 * 4) for l in range(L))
    if ep % max(1, args.epochs // 10) == 0 or ep == args.epochs - 1:
        hist.append((ep, float(loss.detach())))
        print(f"  epoch {ep} stage {stage}: loss {float(loss.detach()):.4e}", flush=True)
for fus in ('gpoe', 'mix'):
    pl, et = evaluate(model_b, te_pops, fus)
    res[f'b_{fus}'] = dict(per_layer=pl, nmse_N01=et, pointwise_leftover=pointwise_leftover(model_b, fus))
    print(f"(b) trained on populations, {fus}: held-out output mean error by width {pl[-1]}; N(0,I) nMSE {et:.2e}; "
          f"pointwise input-end leftover {res[f'b_{fus}']['pointwise_leftover']:.3f}", flush=True)
cost = n_samples_train + (em_flops + tr_flops) / PASS
res.update(loss_hist=hist, cost_passes=cost, em_flops=em_flops, train_flops=tr_flops, mc_nmse_at_cost=1.0 / cost,
           V_l=V_l, secs=time.time() - t0)
try:
    rj = json.load(open(f'/home/agent/workspaces/mats/work/arc-update/runs/rqmc_n{n}_L{L}_s{seed}.json'))
    xs = np.log([x['N'] for x in rj['rows']]); ys = np.log([x['mean_nmse'] for x in rj['rows']])
    res['rqmc_nmse_at_cost'] = float(np.exp(np.interp(math.log(cost), xs, ys))) if math.log(cost) <= xs[-1] else \
        float(np.exp(ys[-1] + (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) * (math.log(cost) - xs[-1])))
except Exception:
    res['rqmc_nmse_at_cost'] = None
print(f"cost {cost:.0f} passes (samples {n_samples_train}); MC at that cost {1 / cost:.2e}; RQMC {res['rqmc_nmse_at_cost']}", flush=True)
json.dump(res, open(out, 'w'))
print('wrote', out, 'total', time.time() - t0)
