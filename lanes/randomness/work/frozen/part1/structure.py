"""Variance removed by each structure, for one net: radius-exact designs of increasing strength (Haar-randomised),
antipodal pairs, scrambled Sobol in black-box and gate-aligned (white-box) bases, prefix-norm (multilevel) controls,
and deterministic designs against the truth.

For a Haar-randomised design D of m points, the replicate variance Var_Q(est) (trace over outputs) is the design's risk
on this net, exactly sum_{d>=1} E_d(W) A_d(D) (Funk-Hecke), where E_d(W) is the harmonic energy of m_n g at degree d
(FORMAL T1). Output: per design, risk x m / V ("variance per point relative to plain MC", the inverse gain over MC at
equal points), with the replicate standard error, plus the harmonic partial sums it implies.

Usage: structure.py seed n L [--quick] [--out PATH]
"""
import argparse
import json
import math
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
import rnd  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('seed', type=int); ap.add_argument('n', type=int); ap.add_argument('L', type=int)
ap.add_argument('--quick', action='store_true')
ap.add_argument('--out', default=None)
ap.add_argument('--skip', default='')
a = ap.parse_args()
skip = set(a.skip.split(',')) if a.skip else set()
t0 = time.time()
n, L = a.n, a.L
net = rnd.Net(a.seed, n, L)
mn = net.mn
truth = rnd.load_truth(a.seed, n, L)
rng = np.random.default_rng([777, a.seed, n, L])
res = dict(seed=a.seed, n=n, L=L, mn=mn, truth_N=(truth['N'] if truth else None))
passes = 0


def log(msg):
    print(f'[{time.time() - t0:7.1f}s] n={n} L={L} seed={a.seed} {msg}', flush=True)


# ---- base statistics from one large iid sample (plain and radius-exact)
P = 1 << (12 if a.quick else 14)
X = rng.standard_normal((P, n))
F = net.outs(X)
passes += P
r = np.linalg.norm(X, axis=1)
G = F / r[:, None]                                         # g(u)
V_plain = float(np.sum(F.var(0, ddof=1)))
V_rb = float(mn ** 2 * np.sum(G.var(0, ddof=1)))          # per-point risk of radius-exact MC
V = truth['V'] if truth else V_plain
res.update(V=V, V_plain_sample=V_plain, V_rb=V_rb, rho_rb=V_rb / V)
Gm = G.mean(0)
res['mean_norm2_over_V'] = float(mn ** 2 * np.sum(Gm ** 2) / V)
# antipodal pairs on the same directions: g(-u)
Gneg = net.outs(-X) / r[:, None]
passes += P
pair = 0.5 * (G + Gneg)
V_even = float(mn ** 2 * np.sum(pair.var(0, ddof=1)))     # per pair: sum over even degrees of E_d
V_odd = float(mn ** 2 * np.sum((0.5 * (G - Gneg)).var(0, ddof=1)))
res.update(V_even=V_even, V_odd=V_odd)
log(f'V={V:.4g} V_rb/V={V_rb / V:.4f} even/rb={V_even / V_rb:.3f} odd/rb={V_odd / V_rb:.3f} '
    f'|mu|^2/V={res["mean_norm2_over_V"]:.2f}')

# ---- multilevel prefix-norm controls (shared reference trajectory), from the same sample
q = rng.standard_normal(n); q /= np.linalg.norm(q)
nus = []; hq = q.copy()
for l in range(L):
    z = np.maximum(net.W64[l].numpy() @ hq, 0.0)
    nus.append(np.linalg.norm(z)); hq = z / nus[-1]
qL = hq
suffix = np.ones(L + 1)
for rr in range(L - 1, -1, -1):
    suffix[rr] = suffix[rr + 1] * nus[rr]
U = X / r[:, None]
h = U.copy(); norms = {0: np.ones(P)}
import torch
with torch.no_grad():
    ht = torch.as_tensor(U).float()
    for l in range(L):
        ht = torch.relu(ht @ net.Wt[l])
        norms[l + 1] = ht.double().norm(dim=1).numpy()
Y = mn * G
ml = {}
for rr in sorted(set(r_ for r_ in [1, 2, 4, 8, max(1, L // 4), max(1, L // 2), max(1, 3 * L // 4), L - 1] if r_ < L)):
    Gr = mn * (suffix[rr] * norms[rr])[:, None] * qL[None, :]
    V1 = float(np.sum(Gr.var(0, ddof=1)))
    V2 = float(np.sum((Y - Gr).var(0, ddof=1)))
    C1 = rr / L
    risk2 = (math.sqrt(V1 * C1) + math.sqrt(V2 * 1.0)) ** 2  # optimal two-level allocation, per unit budget
    ml[rr] = dict(V1_over_Vrb=V1 / V_rb, resid_share=V2 / V_rb, gain_vs_rb=V_rb / risk2, gain_vs_mc=V / risk2)
res['multilevel'] = ml
best = max(ml.items(), key=lambda kv: kv[1]['gain_vs_rb'])
log(f'multilevel best r={best[0]} gain_vs_rb={best[1]["gain_vs_rb"]:.3f} resid_share={best[1]["resid_share"]:.3f}')
passes += P


# ---- Haar-randomised designs: replicate variance x m / V
def rand_design(name, base_fn, R):
    ests = []
    m = None
    for rep in range(R):
        Q = rnd.haar(n, rng)
        Ub = base_fn()
        m = Ub.shape[0]
        ests.append(rnd.rb_estimate(net, rnd.rotate(Ub, Q)))
    ests = np.array(ests)
    var = float(np.sum(ests.var(0, ddof=1)))
    # standard error of the trace variance by the delta method on per-replicate squared deviations
    dev2 = np.sum((ests - ests.mean(0)) ** 2, axis=1) * R / (R - 1)
    se = float(dev2.std(ddof=1) / math.sqrt(R))
    out = dict(m=m, R=R, risk=var, risk_se=se, inv_gain_mc=var * m / V, inv_gain_mc_se=se * m / V,
               inv_gain_rb=var * m / V_rb)
    if truth is not None:
        out['nmse_mean'] = float(np.mean(np.sum((ests - truth['mean']) ** 2, axis=1)) / V)
    res.setdefault('designs', {})[name] = out
    log(f'{name}: m={m} R={R} m*risk/V={out["inv_gain_mc"]:.4f} (+-{out["inv_gain_mc_se"]:.4f}) '
        f'gain_vs_mc={1 / max(out["inv_gain_mc"], 1e-12):.3f}')
    return R * m


Rs = 16 if a.quick else 64
if 'onb' not in skip:
    passes += rand_design('onb', lambda: np.eye(n), Rs)
if 'simplex' not in skip:
    S0 = rnd.simplex_base(n)
    passes += rand_design('simplex', lambda: S0, Rs)
if 'cross' not in skip:
    C0 = rnd.cross_base(n)
    passes += rand_design('cross', lambda: C0, Rs)
if n in (256,) and 'kerdock' not in skip:
    Kv = rnd.kerdock_bases(n).reshape(-1, n)
    Rk = 4 if a.quick else 12
    ests_k, ests_m = [], []
    for rep in range(Rk):
        Q = rnd.haar(n, rng)
        Ur = rnd.rotate(Kv, Q)
        Fp = net.outs(Ur); Fm = net.outs(-Ur)
        passes += 2 * Ur.shape[0]
        ests_k.append(mn * (Fp.sum(0) + Fm.sum(0)) / (2 * Ur.shape[0]))
        s = rng.choice([True, False], size=Ur.shape[0])
        ests_m.append(mn * (Fp[s].sum(0) + Fm[~s].sum(0)) / Ur.shape[0])
    for name, E, m in (('kerdock', np.array(ests_k), 2 * Kv.shape[0]), ('mub', np.array(ests_m), Kv.shape[0])):
        var = float(np.sum(E.var(0, ddof=1)))
        dev2 = np.sum((E - E.mean(0)) ** 2, axis=1) * Rk / (Rk - 1)
        se = float(dev2.std(ddof=1) / math.sqrt(Rk))
        out = dict(m=m, R=Rk, risk=var, risk_se=se, inv_gain_mc=var * m / V, inv_gain_mc_se=se * m / V,
                   inv_gain_rb=var * m / V_rb)
        if truth is not None:
            out['nmse_mean'] = float(np.mean(np.sum((E - truth['mean']) ** 2, axis=1)) / V)
        res.setdefault('designs', {})[name] = out
        log(f'{name}: m={m} R={Rk} m*risk/V={out["inv_gain_mc"]:.4f} (+-{out["inv_gain_mc_se"]:.4f})')

# ---- scrambled Sobol (RQMC) in black-box and gate-aligned bases, radius exact; and plain-Gaussian RQMC
W1 = net.W64[0].numpy()
bases = {'std': None, 'polar': rnd.basis_polar(W1), 'svd': rnd.basis_svd(W1)}
mlist = [10, 12] if a.quick else [10, 12, 14]
Rq = 8 if a.quick else 16
sob = {}
for bname, Qb in bases.items():
    for mlog in mlist:
        ests, ests_anti = [], []
        for rep in range(Rq):
            Pu = rnd.sobol_unit(mlog, n, scramble=True, seed=10_000 * a.seed + 100 * mlog + rep)
            Z = rnd.gauss_from_unit(Pu)
            Xs = Z if Qb is None else rnd.apply_basis(Z, Qb)
            Us = rnd.to_sphere(Xs)
            ests.append(rnd.rb_estimate(net, Us))
            passes += Us.shape[0]
        ests = np.array(ests)
        m = 1 << mlog
        var = float(np.sum(ests.var(0, ddof=1)))
        dev2 = np.sum((ests - ests.mean(0)) ** 2, axis=1) * Rq / (Rq - 1)
        se = float(dev2.std(ddof=1) / math.sqrt(Rq))
        key = f'rqmc_rb_{bname}_m{mlog}'
        sob[key] = dict(m=m, R=Rq, inv_gain_mc=var * m / V, inv_gain_mc_se=se * m / V, inv_gain_rb=var * m / V_rb)
        log(f'{key}: m*risk/V={var * m / V:.4f} (+-{se * m / V:.4f}) gain_vs_mc={V / (var * m):.3f}')
res['rqmc'] = sob

# ---- antipodal RQMC: Sobol (m/2 points) and their antipodes, black-box and polar bases
anti = {}
for bname in ('std', 'polar'):
    Qb = bases[bname]
    for mlog in ([12] if a.quick else [12, 14]):
        ests = []
        for rep in range(Rq):
            Pu = rnd.sobol_unit(mlog - 1, n, scramble=True, seed=20_000 * a.seed + 100 * mlog + rep)
            Z = rnd.gauss_from_unit(Pu)
            Xs = Z if Qb is None else rnd.apply_basis(Z, Qb)
            Us = rnd.to_sphere(Xs)
            ests.append(rnd.rb_estimate(net, np.concatenate([Us, -Us])))
            passes += 2 * Us.shape[0]
        ests = np.array(ests)
        m = 1 << mlog
        var = float(np.sum(ests.var(0, ddof=1)))
        dev2 = np.sum((ests - ests.mean(0)) ** 2, axis=1) * Rq / (Rq - 1)
        se = float(dev2.std(ddof=1) / math.sqrt(Rq))
        key = f'rqmc_anti_rb_{bname}_m{mlog}'
        anti[key] = dict(m=m, R=Rq, inv_gain_mc=var * m / V, inv_gain_mc_se=se * m / V, inv_gain_rb=var * m / V_rb)
        log(f'{key}: m*risk/V={var * m / V:.4f} (+-{se * m / V:.4f}) gain_vs_mc={V / (var * m):.3f}')
res['rqmc_anti'] = anti

# ---- Kerdock aligned with the polar frame of W_1, randomised by random signed permutations (white-box)
if n == 256 and 'kerdock' not in skip:
    Rk2 = 4 if a.quick else 12
    ests = []
    for rep in range(Rk2):
        perm = rng.permutation(n); sg = rng.choice([-1.0, 1.0], size=n)
        Ub = Kv[:, perm] * sg[None, :]
        Ux = rnd.apply_basis(Ub, bases['polar'])
        Fp = net.outs(Ux); Fm = net.outs(-Ux)
        passes += 2 * Ux.shape[0]
        ests.append(mn * (Fp.sum(0) + Fm.sum(0)) / (2 * Ux.shape[0]))
    E = np.array(ests); m = 2 * Kv.shape[0]
    var = float(np.sum(E.var(0, ddof=1)))
    dev2 = np.sum((E - E.mean(0)) ** 2, axis=1) * Rk2 / (Rk2 - 1)
    se = float(dev2.std(ddof=1) / math.sqrt(Rk2))
    out = dict(m=m, R=Rk2, risk=var, inv_gain_mc=var * m / V, inv_gain_mc_se=se * m / V, inv_gain_rb=var * m / V_rb)
    if truth is not None:
        out['nmse_mean'] = float(np.mean(np.sum((E - truth['mean']) ** 2, axis=1)) / V)
        out['nmse_mean_x_m'] = out['nmse_mean'] * m
    res['designs']['kerdock_polar_sp'] = out
    log(f'kerdock_polar_sp: m*risk/V={out["inv_gain_mc"]:.4f} (+-{out["inv_gain_mc_se"]:.4f}) '
        f'nmse*m={out.get("nmse_mean_x_m", float("nan")):.4f}')

# ---- deterministic designs against the truth (only meaningful when a noiseless truth exists)
if truth is not None:
    det = {}
    for mlog in ([10, 12] if a.quick else [10, 12, 14, 16]):
        Pu = rnd.sobol_unit(mlog, n, scramble=False)
        Us = rnd.to_sphere(rnd.gauss_from_unit(Pu))
        e = rnd.nmse(rnd.rb_estimate(net, Us), truth)
        passes += Us.shape[0]
        Us2 = rnd.to_sphere(rnd.apply_basis(rnd.gauss_from_unit(Pu), bases['polar']))
        e2 = rnd.nmse(rnd.rb_estimate(net, Us2), truth)
        passes += Us2.shape[0]
        det[f'sobol_det_m{mlog}'] = dict(m=1 << mlog, nmse=e, nmse_times_m=e * (1 << mlog), polar_nmse=e2,
                                         polar_nmse_times_m=e2 * (1 << mlog))
        log(f'sobol_det m=2^{mlog}: nmse*m={e * (1 << mlog):.4f} (polar {e2 * (1 << mlog):.4f})')
    res['deterministic'] = det
res['passes'] = passes
res['seconds'] = time.time() - t0
out = a.out or os.path.join(os.path.dirname(__file__), '..', 'runs', f'struct_n{n}_L{L}_s{a.seed}.json')
with open(out, 'w') as fh:
    json.dump(res, fh, indent=1)
log(f'done passes={passes} -> {out}')
