"""Amendment A5 (Kelvin's architecture): sampling-trained, deductively propagated layered experts with targeted
corrections. 32x4 first.

Representation: lib/lmle.py LMLE (chain s = 1; Gaussian gates in the downstream-read coordinates u_l; affine experts;
held-out residual covariances), propagated DEDUCTIVELY (Monte Carlo over the model's own Gaussian components, no net
evaluations) as expert-indexed components; the input population is split into its input-gate parts, each propagated
as its own chain, so every part has an output mean and a propagated error covariance E (A2).
Training (advice, free; sampling allowed), on training populations N(sqrt(1 - s^2) mu, s^2 I) (held-out centres are
disjoint): (a) downstream-weighted conditional fit on real state pairs (residual weighted by the read-direction
eigenvalues); (b) reparametrised samples of the model's layer-l mixture, reconstructed to full states and pushed
through the REAL layers l+1..L, must reproduce the population's true output mean; the deductive internal means must
match the real layer means; the deductive output mean must match the truth; calibration NLL of the output mean
under E (+ sampling noise).
Estimation on held-out populations (and N(0, I), not trained on): deductive estimate; targeted corrections: the parts
with the largest a_k^2 tr E_k get n_k proportional to a_k sqrt(tr E_k) inputs drawn from N(part) with exact weights
p(x) g_k(x) / q_k(x), replacing their deductive contribution (unbiased for corrected parts). Errors against 2^18-path
truths; estimation-time compute (propagation flops + correction passes + gate evaluations) against MC and RQMC on
the same population. MEASURED (exploratory). Usage: step5.py SEED n L --K 16 --steps 400
"""
import argparse, copy, json, math, os, sys, time
import numpy as np
import torch
from scipy.stats import chi2, qmc
from scipy.special import ndtri
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lmle  # noqa: E402

DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.set_default_device(DEV)


def weights_np(seed, n, L):
    """Same stream as arc-noisy anet.make_weights (numpy RandomState(1_000_003 + 7919 seed), N(0, 2/n))."""
    rs = np.random.RandomState(1_000_003 + 7919 * seed)
    return [rs.standard_normal((n, n)) * math.sqrt(2.0 / n) for _ in range(L)]

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--K', type=int, default=16)
ap.add_argument('--d', type=int, default=32)
ap.add_argument('--pops', type=int, default=300)
ap.add_argument('--M', type=int, default=256)
ap.add_argument('--steps', type=int, default=400)
ap.add_argument('--batch_pops', type=int, default=8)
ap.add_argument('--R_push', type=int, default=64)
ap.add_argument('--lr', type=float, default=3e-3)
ap.add_argument('--lam_a', type=float, default=1.0)
ap.add_argument('--lam_b', type=float, default=1.0)
ap.add_argument('--lam_int', type=float, default=1.0)
ap.add_argument('--lam_cal', type=float, default=0.01)
ap.add_argument('--draws', type=int, default=256)
ap.add_argument('--fusion', default='poe')
ap.add_argument('--te_centres', type=int, default=4)
ap.add_argument('--te_widths', default='0.1,0.3,0.6,0.9')
ap.add_argument('--budgets', default='0,16,64,256,1024')
ap.add_argument('--em', default='sklearn', help="sklearn | torch (chunked GPU EM for 1M+ advice paths)")
ap.add_argument('--train_parts', type=int, default=0, help='0 = all parts in the training deduce')
ap.add_argument('--train_draws', type=int, default=0, help='0 = all draws in the training deduce')
ap.add_argument('--out', default=None)
args = ap.parse_args()
n, L, seed, K = args.n, args.L, args.seed, args.K
d = min(args.d, n)
BUD = [int(b) for b in args.budgets.split(',')]
TEW = [float(w) for w in args.te_widths.split(',')]
torch.set_num_threads(int(os.environ.get('AR_THREADS', '4')))
out = args.out or os.path.join('/root/runs' if os.path.isdir('/root/runs') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runs_local'), f'step5_n{n}_L{L}_s{seed}_K{K}_d{d}_{args.fusion}.json')
t0 = time.time()
W64c = [torch.from_numpy(w) for w in weights_np(seed, n, L)]          # CPU copies for the numpy-side passes
W64 = [w.to(DEV) for w in W64c]                                          # device copies for differentiable pushes
PASS = 2.0 * n * n * L
DT = lmle.DT
rng = np.random.RandomState(seed)


@torch.no_grad()
def push_np(X):
    h = torch.from_numpy(np.asarray(X, dtype=np.float64))
    H = [h.numpy()]
    for l in range(L):
        h = torch.relu(h @ W64c[l].T); H.append(h.numpy())
    return H


def push_torch(h, l0):
    """Differentiable push of states h (layer l0) through the real layers l0+1..L."""
    for l in range(l0, L):
        h = torch.relu(h @ W64[l].T)
    return h


# ---------------- advice data: training populations
prs = np.random.RandomState(seed + 5)
tr = []
for b in range(args.pops):
    s = [0.03, 0.1, 0.3, 0.6, 0.9][b % 5]
    mu = math.sqrt(1 - s * s) * prs.standard_normal(n)
    X = mu + s * prs.standard_normal((args.M, n))
    tr.append(dict(s=s, mu=mu, X=X, H=push_np(X)))
allH = [np.concatenate([p['H'][l] for p in tr]) for l in range(L + 1)]
# downstream-read projections from VJPs on the training states
Xs = allH[0][:8192]
h = torch.from_numpy(Xs); masks = []
for l in range(L):
    z = h @ W64c[l].T; masks.append(z > 0); h = torch.relu(z)
g = torch.from_numpy(prs.standard_normal((len(Xs), n)))
gs = [None] * (L + 1); gs[L] = g.numpy()
for l in range(L - 1, -1, -1):
    g = (g * masks[l]) @ W64c[l]; gs[l] = g.numpy()
bases, eigs = [], []
for l in range(L + 1):
    c = np.zeros(n) if l == 0 else allH[l].mean(0)
    if l < L:
        ev, U = np.linalg.eigh(gs[l].T @ gs[l] / len(gs[l])); P = np.ascontiguousarray(U[:, ::-1][:, :d]); e_ = np.ascontiguousarray(ev[::-1][:d])
    else:
        _, sv, Vt = np.linalg.svd(allH[L] - c, full_matrices=False); P = Vt[:d].T; e_ = np.ones(d)
    bases.append((c, P)); eigs.append(np.maximum(e_, 1e-12))
coords = lambda l, H: (H - bases[l][0]) @ bases[l][1]
V_l = [float(coords(l, allH[l]).var(0).sum()) for l in range(L + 1)]
VF = float(allH[L].var(0).sum())
for p in tr:
    p['mL'] = p['H'][L].mean(0)
    p['ml'] = [coords(l, p['H'][l]).mean(0) for l in range(L + 1)]
    # review fix (astra #10): sampling covariance of the M-path empirical output mean (the calibration target)
    p['Csamp'] = torch.as_tensor(np.cov(coords(L, p['H'][L]).T) / len(p['H'][L]), dtype=DT)
print(f'[{time.time() - t0:.0f}s] advice: {args.pops} populations x {args.M} paths', flush=True)

# ---------------- model, EM warm start (= per-sample model) with held-out residuals
model = lmle.LMLE(L, d, K, d, skips=(1,))
half = len(allH[0]) // 2
for l in range(L):
    bank = model.banks[f'{l}_1']
    if args.em == 'torch':
        bank.init_em_torch(coords(l, allH[l][:half]), coords(l + 1, allH[l + 1][:half]), seed=seed)
    else:
        bank.init_em(coords(l, allH[l][:half]), coords(l + 1, allH[l + 1][:half]), seed=seed)
    if args.fusion != 'poe':          # R_err is not used by plain PoE (Kelvin: variances only from the fused NLL)
        bank.set_heldout_error(coords(l, allH[l][half:]), coords(l + 1, allH[l + 1][half:]))
    print(f'  EM layer {l} done [{time.time() - t0:.0f}s]', flush=True)
model_a = copy.deepcopy(model)
eps = {l: lmle.std_draws(args.draws, d, 5000 + l) for l in range(L + 1)}


def input_parts(model, mu, s):
    """Split the input population N(mu, s^2 I) (u_0 = Pi_0^T x) into the layer-0 experts' gate parts (no net)."""
    m = torch.as_tensor(mu @ bases[0][1], dtype=DT); S = torch.eye(d, dtype=DT) * s * s
    bank = model.banks['0_1']
    Ls = torch.linalg.cholesky(S)
    Z = m + lmle.std_draws(4096, d, 77) @ Ls.T
    G = torch.exp(bank.log_gates(Z))
    w = G.mean(0); om = G / (G.sum(0, keepdim=True) + 1e-300)
    mk = om.T @ Z
    Dk = Z[None] - mk[:, None]
    Sk = (om.T[:, :, None] * Dk).transpose(1, 2) @ Dk + 1e-9 * torch.eye(d, dtype=DT)
    return w, mk, Sk


def deduce(model, mu, s, per_part=True, sample_parts=0, R=0):
    """Deductive propagation of the input parts (batched); returns parts [(mass, out mean u_L, E_L, per-layer
    [(mean, cov)])], the population's output mean (u_L), per-layer population means, kept part indices, the parts.
    sample_parts > 0 (training only, for memory at large K): draw that many parts with probability proportional to
    their mass, each carrying mass total / sample_parts, an unbiased estimate of the full mixture; R > 0 uses the
    first R of the standardised draws per layer."""
    w, mk, Sk = input_parts(model, mu, s)
    w = torch.nan_to_num(w, nan=0.0)
    keep = torch.where(w > 1e-12)[0]          # review fix (astra #8): keep every part with mass (was 1e-4)
    if len(keep) == 0:
        keep = torch.argmax(w)[None]
    a = w[keep]
    if sample_parts and len(keep) > sample_parts:
        pick = torch.multinomial((a / a.sum()).detach(), sample_parts, replacement=True)
        keep = keep[pick]
        a = (w[keep] / w[keep].detach()) * (w[keep[:0]].sum() + a.sum().detach()) / sample_parts   # value total/S, grad via w
    ep = eps if not R else {l: v[:R] for l, v in eps.items()}
    outs = model.propagate_parts(mk[keep], Sk[keep], ep, mode=args.fusion)
    tot = a.sum()
    parts = [(a[i], outs[-1][0][i], outs[-1][2][i], [(o[0][i], o[1][i]) for o in outs]) for i in range(len(keep))]
    layer_means = [(a[:, None] * o[0]).sum(0) / tot for o in outs]
    out_u = layer_means[-1]
    return parts, out_u, layer_means, keep.tolist(), (w, mk, Sk)


def recon(l, U):
    return torch.as_tensor(bases[l][0], dtype=DT) + U @ torch.as_tensor(bases[l][1].T, dtype=DT)


# ---------------- (b)-style end-to-end training (advice)
opt = torch.optim.Adam(model.parameters(), lr=args.lr)
gen = np.random.RandomState(seed + 11)
pairs_l = [(torch.as_tensor(coords(l, allH[l]), dtype=DT), torch.as_tensor(coords(l + 1, allH[l + 1]), dtype=DT)) for l in range(L)]
wts = [torch.as_tensor(np.sqrt(eigs[l + 1] / eigs[l + 1].sum()), dtype=DT) for l in range(L)]
train_flops = 0.0
for step in range(args.steps):
    opt.zero_grad()
    loss = 0.0
    # (a) downstream-weighted conditional fit on real pairs (fused pointwise prediction)
    idx = torch.as_tensor(gen.randint(0, len(allH[0]), 1024))
    for l in range(L):
        U_l, U_n = pairs_l[l]
        pred, Unc, _ = model.pointwise(model.banks[f'{l}_1'], U_l[idx], args.fusion)
        if args.fusion == 'poe':
            # calibration NLL of the FUSED prediction against real states, downstream-weighted per coordinate;
            # this is what trains the experts' input-dependent diagonal variances (plain PoE, no normalisation)
            var = torch.diagonal(Unc, dim1=-2, dim2=-1)
            nll = ((U_n[idx] - pred) ** 2 / var + torch.log(var)) * (wts[l] ** 2) * d
            loss = loss + args.lam_a * nll.sum(1).mean() / d
        else:
            loss = loss + args.lam_a * (((U_n[idx] - pred) * wts[l]) ** 2).sum(1).mean() / V_l[l + 1]
    # (b) population terms
    for b in gen.randint(0, len(tr), args.batch_pops):
        p = tr[b]
        parts, out_u, layer_means, keep, (w, mk, Sk) = deduce(model, p['mu'], p['s'], sample_parts=args.train_parts, R=args.train_draws)
        mL_true = torch.as_tensor(coords(L, p['mL'][None])[0], dtype=DT)
        dm = out_u - mL_true
        loss = loss + (dm ** 2).sum() / V_l[L]
        for l in range(L):
            loss = loss + args.lam_int * ((layer_means[l] - torch.as_tensor(p['ml'][l + 1], dtype=DT)) ** 2).sum() / V_l[l + 1]
        # samples of the model's layer-l mixture pushed through the real layers (l = 1 .. L-1)
        for l in range(1, L):
            # rebuild the layer-l mixture from the parts' chains: propagate again to layer l is costly; use the
            # per-part means at layer l with the part's propagated spread approximated by the layer's EM residual scale
            As = torch.stack([pp[0] for pp in parts]); As = As / As.sum()
            Zs = []
            for pp in parts:                                                    # reparametrised draws per part
                Mpl, Spl = pp[3][l - 1]
                Lc = torch.linalg.cholesky(Spl + 1e-9 * torch.eye(d, dtype=DT))
                Zs.append(Mpl + eps[l][:args.R_push] @ Lc.T)
            Z = torch.stack(Zs)                                                 # (P, R, d)
            Hs = recon(l, Z.reshape(-1, d))
            F = push_torch(Hs, l).reshape(len(parts), -1, n).mean(1)
            Fm = (As[:, None] * F).sum(0)
            loss = loss + args.lam_b * (((Fm - torch.as_tensor(p['mL'], dtype=DT)) ** 2).sum() / VF) / (L - 1)
        Ec = parts[0][2]
        Ct = sum(pp[0] / sum(q[0] for q in parts) * pp[2] for pp in parts) + p['Csamp'] + 1e-9 * torch.eye(d, dtype=DT)
        loss = loss + args.lam_cal * 0.5 * (dm @ torch.linalg.solve(Ct, dm) + torch.logdet(Ct)) / d
    if not torch.isfinite(loss):                         # skip a non-finite step (seen at K = 256 on the L4)
        opt.zero_grad(); continue
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 100.0)
    opt.step()
    if step % max(1, args.steps // 8) == 0 or step == args.steps - 1:
        print(f'  step {step}: loss {float(loss.detach()):.4e} [{time.time() - t0:.0f}s]', flush=True)

# ---------------- evaluation on held-out populations (deductive + targeted corrections)
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
        f = push_np(p['mu'] + p['s'] * hrs.standard_normal((65536, n)))[-1]; S1 += f.sum(0); S2 += (f * f).sum(0)
    p['m'] = S1 / NTr; p['trcov'] = float((S2 / NTr - p['m'] ** 2).sum())
prop_flops = L * args.draws * K * (6 * d * d) + L * K * d ** 3 * 4


def evaluate(mdl, label):
    rows = []
    fr = np.random.RandomState(seed + 999)
    for p in te:
        with torch.no_grad():
            parts, out_u, _, keep, (w, mk, Sk) = deduce(mdl, p['mu'], p['s'])
        est_ded = bases[L][0] + bases[L][1] @ out_u.detach().cpu().numpy()
        e_ded = float(((est_ded - p['m']) ** 2).sum() / VF)
        tot = float(sum(pp[0] for pp in parts))
        Eu = sum(float(pp[0]) / tot * pp[2].detach().cpu().numpy() for pp in parts)
        dlt = (est_ded - p['m']) @ bases[L][1]
        z2 = float(dlt @ np.linalg.solve(Eu + 1e-12 * np.eye(d), dlt))
        q = chi2.cdf(z2, d)
        n_parts = len(parts)
        cost_ded = (prop_flops * n_parts) / PASS
        # targeted corrections
        contrib = np.array([float(pp[0]) ** 2 * float(torch.trace(pp[2])) for pp in parts])
        alloc_w = np.array([float(pp[0]) * math.sqrt(float(torch.trace(pp[2]))) for pp in parts])
        corr = []
        for Nc in BUD:
            if Nc == 0:
                continue
            nk = np.floor(Nc * alloc_w / alloc_w.sum()).astype(int)
            est_u = out_u.detach().cpu().numpy() * tot
            est_full = np.zeros(n) + bases[L][0] * 0
            parts_est = []
            for i, (pp, kk) in enumerate(zip(parts, keep)):
                a = float(pp[0]); m_part = bases[L][0] + bases[L][1] @ pp[1].detach().cpu().numpy()
                if nk[i] >= 2:
                    # draw x from q_k: u-part N(mk, Sk), orthogonal part from the population (exact weights)
                    mkk = mk[kk].detach().cpu().numpy(); Skk = Sk[kk].detach().cpu().numpy()
                    Lc = np.linalg.cholesky(Skk + 1e-12 * np.eye(d))
                    m_pop = p['mu'] @ bases[0][1]
                    # review fix (astra #9): defensive mixture q = 0.5 N(mk, Sk) + 0.5 population, bounded weights
                    from_pop = fr.random_sample(nk[i]) < 0.5
                    Uq = np.where(from_pop[:, None], m_pop + p['s'] * fr.standard_normal((nk[i], d)),
                                  mkk + fr.standard_normal((nk[i], d)) @ Lc.T)
                    Xo = p['mu'] + p['s'] * fr.standard_normal((nk[i], n))
                    Xo = Xo - (Xo @ bases[0][1]) @ bases[0][1].T
                    Xq = Xo + Uq @ bases[0][1].T
                    lp = -0.5 * (((Uq - m_pop) / p['s']) ** 2).sum(1) - d * math.log(p['s'])
                    zq = np.linalg.solve(Lc, (Uq - mkk).T)
                    lg_ = -0.5 * (zq * zq).sum(0) - np.log(np.diag(Lc)).sum()
                    lq = np.logaddexp(np.log(0.5) + lg_, np.log(0.5) + lp)
                    with torch.no_grad():
                        gk = torch.exp(mdl.banks['0_1'].log_gates(torch.as_tensor(Uq, dtype=DT)))[:, kk].detach().cpu().numpy()
                    wq = np.exp(lp - lq) * gk
                    Fq = push_np(Xq)[-1]
                    parts_est.append((wq[:, None] * Fq).mean(0))
                else:
                    parts_est.append(a * m_part)
            est_c = np.sum(parts_est, 0) / 1.0
            e_c = float(((est_c - p['m']) ** 2).sum() / VF)
            cost = cost_ded + Nc * (1 + K * 2 * d * d / PASS)
            corr.append(dict(N=Nc, err=e_c, cost=cost, mc_at_cost=p['trcov'] / cost / VF))
        # RQMC on the population at the same N budgets
        rq = {}
        for Nb in [b for b in BUD if b > 0]:
            errs = []
            for rep in range(8):
                eng = qmc.Sobol(d=n, scramble=True, seed=seed * 1000 + rep + 31 * Nb)
                u = np.clip(eng.random(Nb), 1e-12, 1 - 1e-12)
                errs.append(float(((push_np(p['mu'] + p['s'] * ndtri(u))[-1].mean(0) - p['m']) ** 2).sum() / VF))
            rq[Nb] = float(np.mean(errs))
        rows.append(dict(s=p['s'], e_ded=e_ded, cost_ded=cost_ded, mc_at_ded_cost=p['trcov'] / max(cost_ded, 1e-9) / VF,
                         pop_var_rel=p['trcov'] / VF, z2=z2, in68=bool(q <= 0.68), in95=bool(q <= 0.95), n_parts=n_parts,
                         corr=corr, rqmc=rq))
    for s in sorted(set(r['s'] for r in rows)):
        rr = [r for r in rows if r['s'] == s]
        print(f"{label} s={s}: deductive {np.median([r['e_ded'] for r in rr]):.2e} at {rr[0]['cost_ded']:.3g} passes (MC there "
              f"{np.median([r['mc_at_ded_cost'] for r in rr]):.2e}); corrected N={BUD[-1]} {np.median([r['corr'][-1]['err'] for r in rr]):.2e}"
              f" (MC at equal cost {np.median([r['corr'][-1]['mc_at_cost'] for r in rr]):.2e}, RQMC N={BUD[-1]} {np.median([r['rqmc'][BUD[-1]] for r in rr]):.2e})", flush=True)
    cov68 = float(np.mean([r['in68'] for r in rows])); cov95 = float(np.mean([r['in95'] for r in rows]))
    print(f'{label}: interval coverage 68% {cov68:.2f}, 95% {cov95:.2f}', flush=True)
    return dict(rows=rows, cov68=cov68, cov95=cov95)


res = dict(args=vars(args), d=d, VF=VF, V_l=V_l)
res['a'] = evaluate(model_a, '(a) per-sample EM')
res['b'] = evaluate(model, '(b) trained (A5)')
res['n_params'] = sum(p_.numel() for p_ in model.parameters())
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'), default=float)
print('wrote', out, f'total {time.time() - t0:.0f}s')
