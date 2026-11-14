"""Hybrid (c): a future-built control variate c(h_l) whose mean comes from a closure, with RQMC on the residual.

Estimator: est = E_Q[c] + mean_RQMC( h_L(x) - c(h_l(x)) ), Q = the closure's layer-l model.
Per layer l and surrogate, measured on independent true samples:
  eta  = tr Var(h_L - c(h_l)) / V                       (residual variance share; fit and evaluation sets disjoint)
  beta = |E_Q[c] - E_P[c]|^2 / V for Q = exact Gaussian recursion ('eg') and ARC K = 2 'simple' ('k2'); the true layer
         mean (truth file) and true second moments (2^17 samples) give E_P[c]. At l = 1 the Gaussian recursion's
         moments are exact, so beta_eg(1) is pure numerical/sampling error.
  RQMC on the residual: R = 8 scrambled-Sobol replicates at N = 2^8, 2^10, 2^12, 2^14, mean nMSE of the residual mean
         against its true value (the residual's true mean is Y - E_P[c]); G_R = (eta / N) / that, and the paired plain
         RQMC on h_L with the same scrambles gives G.
Surrogates (all linear in h_l unless stated; m = the true layer mean, used only to centre):
  jac      c = Jbar_l (h - m), Jbar_l = E[J] of g_l over 128 true samples (basis VJPs): the backward pass
  jacmf    c = Jmf_l (h - m), Jmf_l = prod_{j > l} W_j^T-ordered with gate probabilities Phi(m_j / s_j) of the exact
           Gaussian recursion (mean-field, fully deductive, ~n passes)
  reg      c = B (h - m), B = Cov(h_L, h_l) Cov(h_l)^+ fitted on 2^15 pilot samples (sampling-based setup)
  regq<k>  reg plus all quadratic monomials of the top-k whitened futnl features of g_l (fitted jointly)
Costs (pass units, 1 pass = 2 n^2 L flops), recorded: closure to layer l, backward/fit setup, per-sample a = 1 +
cost(c) / pass.
usage: run_hyb.py N L SEED [--layers 1,2,4,8,16,24] [--tag T] -> runs/hyb_n{N}_L{L}_s{SEED}{T}.json"""
import argparse, json, os, sys, time
import numpy as np
import torch
from scipy.special import ndtr
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
sys.path.insert(0, '/home/agent/workspaces/mats/work/bits-bounds/lib')
import fa  # noqa: E402
import closure as CL  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('n', type=int); ap.add_argument('L', type=int); ap.add_argument('seed', type=int)
ap.add_argument('--layers', default='1,2,4,8,16,24'); ap.add_argument('--tag', default='')
ap.add_argument('--log2fit', type=int, default=15); ap.add_argument('--log2ev', type=int, default=15)
ap.add_argument('--qk', type=int, default=16); ap.add_argument('--rqmc', default='8,10,12,14')
ap.add_argument('--R', type=int, default=8)
args = ap.parse_args()
n, L, seed = args.n, args.L, args.seed
layers = [int(x) for x in args.layers.split(',') if int(x) < L]
RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
out = os.path.join(RUNS, f'hyb_n{n}_L{L}_s{seed}{args.tag}.json')
net = fa.load_net(n, L, seed)
W, Y, V = net['W'], net['Y'], net['V']
PASS = 2.0 * n * n * L
t0 = time.time()
res = dict(n=n, L=L, seed=seed, V=V, args=vars(args), layers={})

# closures: exact Gaussian recursion states (and its cost), ARC K = 2 'simple' states
Wn = [w.double().numpy() for w in W]
eg = {}; m = np.zeros(n); S = np.eye(n)
for l in range(1, L + 1):
    m, S = CL.relu_moments(Wn[l - 1] @ m, Wn[l - 1] @ S @ Wn[l - 1].T, 48)
    eg[l] = (m.copy(), S.copy())
eg_cost_per_layer = (4.0 * n ** 3 + n * n * 48 * 28) / PASS
k2 = fa.au.arc_kprop(W, 2, kind='simple', keep_states=tuple(layers))
k2_cost = k2['flops'] / PASS


def jac_mf(l):
    """Mean-field averaged Jacobian of g_l (n_out x n): prod over j = L..l+1 of diag(p_j) W_j, p_j = P(z_j > 0) under
    the exact Gaussian recursion's pre-activation law at layer j."""
    J = np.eye(n)
    for j in range(L, l, -1):
        mprev, Sprev = eg[j - 1] if j - 1 >= 1 else (np.zeros(n), np.eye(n))
        mu = Wn[j - 1] @ mprev
        s = np.sqrt(np.maximum(np.einsum('ij,jk,ik->i', Wn[j - 1], Sprev, Wn[j - 1]), 1e-300))
        p = ndtr(mu / s)
        J = J @ (p[:, None] * Wn[j - 1])
    return J


@torch.no_grad()
def samples(Nn, sd):
    gen = torch.Generator().manual_seed(int(sd))
    x = torch.randn(Nn, n, generator=gen)
    _, keep = fa.au.forward(W, x, l0=0, l1=L, keep=set(layers) | {L})
    return keep


fit = samples(1 << args.log2fit, 61_000_000 + seed)
ev = samples(1 << args.log2ev, 62_000_000 + seed)
fL, eL = fit[L].numpy(), ev[L].numpy()
ms = [int(x) for x in args.rqmc.split(',')]
SURR = {}          # (l, name) -> dict(cfun, cP)
for l in layers:
    tl = time.time()
    mu = net['mean'][l - 1]
    Xl = fa.true_samples(W, l, 1 << 16, seed=63_000_000 + seed * 100 + l).double().numpy()
    D = Xl - mu[None, :]
    Sl = D.T @ D / (D.shape[0] - 1)
    row = dict(l=l, surrogates={}, eg_cost=eg_cost_per_layer * l, k2_cost=k2_cost * l / L)
    hf, he = fit[l].numpy(), ev[l].numpy()
    Jb = fa.jbar(W, l, torch.from_numpy(Xl[:128]).float())
    Jmf = jac_mf(l)
    Df = hf - mu[None, :]
    Cxx = Df.T @ Df / len(Df); Cfx = (fL - fL.mean(0)).T @ Df / len(Df)
    Breg = Cfx @ np.linalg.pinv(Cxx, rcond=1e-10)
    Bv, Vv = fa.vjp_rows(W, l, torch.from_numpy(Xl[:1 << 12]).float(), seed=64_000_000 + seed * 100 + l)
    Bn = Bv - Vv @ Jb
    Rnl = Bn.T @ Bn / len(Bn)
    A = fa.features('futnl', args.qk, Sl, Rnl)
    Ca = A.T @ Sl @ A; ev_, U_ = np.linalg.eigh(0.5 * (Ca + Ca.T))
    A = A @ (U_ / np.sqrt(np.clip(ev_, 1e-300, None))) @ U_.T
    iu = np.triu_indices(args.qk)

    def qfeat(h, A=A, mu=mu, iu=iu):
        a = (h - mu[None, :]) @ A
        return (a[:, :, None] * a[:, None, :])[:, iu[0], iu[1]]
    Qf = qfeat(hf); Qm = Qf.mean(0)
    Xf = np.concatenate([Df, Qf - Qm], 1)
    Bq = ((fL - fL.mean(0)).T @ Xf / len(Xf)) @ np.linalg.pinv(Xf.T @ Xf / len(Xf), rcond=1e-10)
    Qtrue = qfeat(Xl).mean(0)
    del Xl, D
    for name, B in (('jac', Jb), ('jacmf', Jmf), ('reg', Breg), (f'regq{args.qk}', Bq)):
        quad = name.startswith('regq')
        if quad:
            Bl, Bqq = B[:, :n], B[:, n:]
            cfun = (lambda h, Bl=Bl, Bqq=Bqq, mu=mu, qfeat=qfeat, Qm=Qm:
                    (h - mu[None, :]) @ Bl.T + (qfeat(h) - Qm) @ Bqq.T)
        else:
            Bl, Bqq = B, None
            cfun = lambda h, B=B, mu=mu: (h - mu[None, :]) @ B.T
        r = eL - cfun(he)
        eta = float(r.var(0).sum() / V)
        cP = Bqq @ (Qtrue - Qm) if quad else np.zeros(n)
        betas = {}
        for qn, (mq, Sq) in (('eg', eg[l]), ('k2', k2['states'][l])):
            cQ = (mq - mu) @ Bl.T
            if quad:
                am = (mq - mu) @ A
                EQ = A.T @ Sq @ A + np.outer(am, am)
                cQ = cQ + Bqq @ (EQ[iu[0], iu[1]] - Qm)
            betas[qn] = float(((cQ - cP) ** 2).sum() / V)
        a_cost = 1.0 + ((2.0 * n * n + 2.0 * n * len(iu[0]) + 2.0 * n * args.qk) if quad else 2.0 * n * n) / PASS
        setup = {'jac': 128 * n * 3.0 * (L - l) / L,
                 'jacmf': (L - l) * 2.0 * n ** 3 / PASS + eg_cost_per_layer * L,
                 'reg': float(1 << args.log2fit),
                 f'regq{args.qk}': float(1 << args.log2fit) + 4096 * 3.0 * (L - l) / L + 128 * n * 3.0 * (L - l) / L}[name]
        row['surrogates'][name] = dict(eta=eta, beta=betas, a=a_cost, setup_passes=setup, rqmc={})
        SURR[(l, name)] = dict(cfun=cfun, cP=cP)
        print(f'l={l} {name}: eta {eta:.3f} beta_eg {betas["eg"]:.2e} beta_k2 {betas["k2"]:.2e} '
              f'({time.time() - t0:.0f}s)', flush=True)
    row['secs'] = time.time() - tl
    res['layers'][str(l)] = row
    json.dump(res, open(out, 'w'))

# RQMC on the residuals (the same scrambled points for every surrogate and for plain h_L)
from scipy.stats import qmc
from scipy.special import ndtri
plain = {}
for mm in ms:
    Nn = 1 << mm
    acc = {key: [] for key in SURR}; ep = []
    for r in range(args.R):
        eng = qmc.Sobol(d=n, scramble=True, seed=int(seed) * 1000 + 17 * mm + r)
        u = np.clip(eng.random(Nn), 1e-12, 1 - 1e-12)
        x = torch.from_numpy(ndtri(u)).float()
        _, keep = fa.au.forward(W, x, l0=0, l1=L, keep=set(layers) | {L})
        hL = keep[L].numpy()
        ep.append(float(((hL.mean(0) - Y) ** 2).sum() / V))
        for (l, name), d in SURR.items():
            resid = (hL - d['cfun'](keep[l].numpy())).mean(0)
            acc[(l, name)].append(float(((resid - (Y - d['cP'])) ** 2).sum() / V))
    plain[mm] = float(np.mean(ep))
    for (l, name), v in acc.items():
        res['layers'][str(l)]['surrogates'][name]['rqmc'][str(mm)] = float(np.mean(v))
    print(f'RQMC N=2^{mm}: plain {plain[mm]:.2e}; ' + ' '.join(f'{l}/{name} {np.mean(v):.2e}' for (l, name), v in acc.items())
          + f' ({time.time() - t0:.0f}s)', flush=True)
    res['rqmc_plain'] = {str(k): v for k, v in plain.items()}
    json.dump(res, open(out, 'w'))
res['secs'] = time.time() - t0
json.dump(res, open(out, 'w'))
print('done', out, f'{res["secs"]:.0f}s', flush=True)
