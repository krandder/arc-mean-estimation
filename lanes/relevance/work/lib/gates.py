"""Gate counts: how many downstream gates account for the degree >= 2 part of g_l (main's request, 21:40Z).

For a gate set G: g_G = the future map in which only the units in G switch (true relu); every other unit keeps the
gate it has on the mean point's trajectory (same future noise), i.e. acts linearly with its frozen gate D_k(m).
g_{all} = g, g_{empty} = the frozen-at-mean linear model. The residual nonlinear part of the difference,
V_{>=2}(g - g_G) = V(g - g_G) - V_1(g - g_G) (variance minus its Stein degree-1 part, Gaussian convention), measures the
nonlinear variance that the gates outside G carry (directly or by interaction).

Orderings (per noise realisation; units of all future layers pooled):
  importance I = |u|^2 s^2 psi(tau): u = frozen backward sensitivity column J^m_{k->L} e_i, s = cloud spread of the
  linearised preactivation (W_k J^m_{l->k-1}(X - m))_i, tau = |z_i(m)| / s, psi(tau) = E relu(Y - tau)^2;
  margin: tau ascending.
G(l, eps) = the smallest G on the grid with V_{>=2}(g - g_G) <= eps V_l.
"""
import math

import numpy as np
from scipy.stats import norm

import rel


def psi(tau):
    return (1 + tau ** 2) * norm.sf(tau) - tau * norm.pdf(tau)


def _reference(fut, m, X, xis):
    """m's trajectory (preacts, gates), linear spreads of the cloud's frozen propagation, backward column norms."""
    t = fut.t
    hm = m[None, :]
    dl = X - m
    zms, Dms, sds = [], [], []
    for k in range(t):
        zm = (hm @ fut.WT[k])[0]
        Dm = zm > 0
        dz = dl @ fut.WT[k]
        sds.append(np.sqrt(np.mean(dz ** 2, 0)) + 1e-300)
        zms.append(zm)
        Dms.append(Dm)
        dl = dz * Dm
        hm = np.maximum(zm, 0)[None, :]
        if k < t - 1 and fut.sigma > 0:
            hm = hm + fut.sigma * xis[k][None, :]
    # backward column norms |J^m_{k->L} e_i|^2 for units at every layer k (J_{L->L} = I)
    nout = fut.Ws[-1].shape[0]
    Jb = np.eye(nout)
    u2 = [None] * t
    for k in reversed(range(t)):
        u2[k] = np.sum(Jb ** 2, 0)  # column norms of J^m_{k->L} (maps layer-k post-activation to the output)
        Jb = (Jb * Dms[k][None, :]) @ fut.Ws[k]
    return zms, Dms, sds, u2


def mixed_forward(fut, X, Dms, masks, xis):
    """Forward pass in which units with mask = True switch (relu) and the others keep the frozen gate Dms[k]."""
    h = X
    for k in range(fut.t):
        z = h @ fut.WT[k]
        h = np.where(masks[k][None, :], np.maximum(z, 0.0), z * Dms[k][None, :])
        if k < fut.t - 1 and fut.sigma > 0:
            h = h + fut.sigma * xis[k][None, :]
    return h


def full_forward(fut, X, xis):
    h = X
    for k in range(fut.t):
        h = np.maximum(h @ fut.WT[k], 0.0)
        if k < fut.t - 1 and fut.sigma > 0:
            h = h + fut.sigma * xis[k][None, :]
    return h


def nonlinear_residual(d1, d2, Z, blocks=16):
    """Amendment 2A (gpt-6-astra round 2, T2). For two realisations d1, d2 (P x n_out; identical when sigma = 0) of a
    difference function on the same Gaussian inputs Z, estimate V = tr Cov of its noise average (cross-realisation
    covariance) and its first-chaos energy |E[d Z^T]|^2 by the CROSS-realisation U-statistic
      [<D1, D2>_F - sum_p (d1_p . d2_p) |Z_p|^2] / (P (P - 1)),  D_r = sum_p d_r,p Z_p^T,
    with each realisation centred by its own mean and the centring factor (1 - 2/P + 2/P^2) divided out (exact for
    Gaussian Z). The previous version averaged the two realisations first, which adds half their variance to the
    first-chaos term and biases the nonlinear residual downward. Returns (V_nl, V, V_1, jackknife SE of V_nl)."""
    P = Z.shape[0]
    c1, c2 = d1 - d1.mean(0), d2 - d2.mean(0)
    cf = 1 - 2.0 / P + 2.0 / P ** 2

    def stats(idx):
        a1, a2, z = c1[idx], c2[idx], Z[idx]
        m = len(idx)
        V = np.einsum('pi,pi->', a1, a2) / (m - 1)
        D1, D2 = a1.T @ z, a2.T @ z
        diag = np.einsum('pi,pi->p', a1, a2) * np.einsum('pi,pi->p', z, z)
        V1 = (np.sum(D1 * D2) - diag.sum()) / (m * (m - 1)) / cf
        return V - V1, V, V1

    allidx = np.arange(P)
    Vnl, V, V1 = stats(allidx)
    s = P // blocks
    jk = np.array([stats(np.setdiff1d(allidx, np.arange(b * s, (b + 1) * s)))[0] for b in range(blocks)])
    se = math.sqrt((blocks - 1) / blocks * np.sum((jk - jk.mean()) ** 2))
    return float(Vnl), float(V), float(V1), float(se)


def gate_count(fut, fr, P, rng, Ggrid=None, n_noise=2, orderings=('importance', 'margin')):
    """Returns dict with, per ordering, the curve G -> (V_>=2(g - g_G), V(g - g_G)) (Gaussian convention), the total
    number of future gates, the mean number of exact flips between cloud points and m, and V_l (for normalisation).
    sigma = 0 uses one realisation; sigma > 0 uses n_noise independent future-noise realisations, each shared by all
    P samples (masks and orderings defined per realisation), combined by cross-realisation products (unbiased for the
    noise-averaged difference)."""
    n = len(fr['m'])
    t = fut.t
    total = n * t
    if Ggrid is None:
        Ggrid = sorted(set([0] + [int(round(x)) for x in np.geomspace(1, total, 40)] + [total]))
    Z = rng.standard_normal((P, n))
    X = fr['m'] + Z @ fr['S12']
    # Amendment 2A (gpt-6-astra round 2, T2): gate spreads and importances from independent training inputs, so the
    # selected mixed map does not depend on the evaluation sample.
    Ztr = rng.standard_normal((P, n))
    Xtr = fr['m'] + Ztr @ fr['S12']
    nreal = 1 if fut.sigma == 0 else n_noise
    reals = []
    for r in range(nreal):
        xis = [rng.standard_normal(n) for _ in range(t - 1)] if fut.sigma > 0 else None
        zms, Dms, sds, u2 = _reference(fut, fr['m'], Xtr, xis)
        tau = [np.abs(zms[k]) / sds[k] for k in range(t)]
        imp = np.concatenate([u2[k] * sds[k] ** 2 * psi(tau[k]) for k in range(t)])
        mar = np.concatenate(tau)
        gfull = full_forward(fut, X, xis)
        reals.append(dict(xis=xis, Dms=Dms, imp=imp, mar=mar, gfull=gfull))
    out = dict(total_gates=total, Ggrid=Ggrid, P=P)
    # first-order (diagonal) prediction: sorted importances of the first realisation, cumulative from the top
    imp_sorted = np.sort(reals[0]['imp'])[::-1]
    cum = np.concatenate([[0.0], np.cumsum(imp_sorted)])
    out['imp_total'] = float(cum[-1])
    out['imp_tail'] = {str(G): float(cum[-1] - cum[min(G, total)]) for G in Ggrid}
    out['n_gates_tau_lt'] = {str(T): int(np.sum(reals[0]['mar'] < T)) for T in (0.5, 1, 2, 3)}
    # V_l (Gaussian) from the same samples: pairwise with shared realisation products
    for ordname in orderings:
        curve = {}
        for G in Ggrid:
            ds = []
            for rr in reals:
                key = -rr['imp'] if ordname == 'importance' else rr['mar']
                sel = np.zeros(total, bool)
                if G > 0:
                    sel[np.argsort(key, kind='stable')[:G]] = True
                masks = [sel[k * n:(k + 1) * n] for k in range(t)]
                gG = mixed_forward(fut, X, rr['Dms'], masks, rr['xis'])
                ds.append(rr['gfull'] - gG)
            if nreal == 1:
                d1 = d2 = ds[0]
            else:
                d1, d2 = ds[0], ds[1]
            Vnl, Vd, V1d, se = nonlinear_residual(d1, d2, Z)
            curve[str(G)] = [Vnl, Vd, V1d, se]
        out[ordname] = curve
    # exact flips between cloud points and m (first realisation), per sample, all future layers
    rr = reals[0]
    hx, hm = X, fr['m'][None, :]
    fl = 0.0
    for k in range(t):
        zx, zm = hx @ fut.WT[k], hm @ fut.WT[k]
        fl += np.mean(np.sum((zx > 0) != (zm > 0), 1))
        hx, hm = np.maximum(zx, 0), np.maximum(zm, 0)
        if k < t - 1 and fut.sigma > 0:
            hx, hm = hx + fut.sigma * rr['xis'][k][None, :], hm + fut.sigma * rr['xis'][k][None, :]
    out['mean_flips_vs_m'] = float(fl)
    return out


def nonlinear_part_counts(fut, fr, P, rng, ks, q=4):
    """N_{>=2}: residual of the degree >= 2 part along (a) the active subspace of the nonlinear part
    g - B~ Z (gradient grad g Sigma^{1/2} - B~), (b) the ordinary active subspace. Residual_{>=2}(P_k) =
    residual(P_k) - (V_1 - degree-1 captured by P_k) (Hermite chaoses are preserved by conditioning on P_k Z).
    Returns dict basis -> {k: [res_total, res_deg1, res_>=2]}, plus V_1 and B~."""
    n = len(fr['m'])
    nout = fut.Ws[-1].shape[0]
    Zs = rng.standard_normal((P, n))
    Xs = fr['m'] + Zs @ fr['S12']
    a = fut.forward(np.stack([Xs]), rng)[0]
    a = a - a.mean(0)
    V1, se1, Bt = rel.ustat_sq(a, Zs)
    R = rng.standard_normal((1, P, q, nout))
    if fut.sigma > 0:
        _, u = fut.vjp(np.stack([Xs, Xs]), np.concatenate([R, R]), rng, share=[0, 1])
        uA = u[0] @ fr['S12'] - np.einsum('pqo,oj->pqj', R[0], Bt)
        uB = u[1] @ fr['S12'] - np.einsum('pqo,oj->pqj', R[0], Bt)
        C = (np.einsum('pqi,pqj->ij', uA, uB) + np.einsum('pqi,pqj->ij', uB, uA)) / (2 * P * q)
    else:
        _, u = fut.vjp(np.stack([Xs]), R)
        uA = u[0] @ fr['S12'] - np.einsum('pqo,oj->pqj', R[0], Bt)
        C = np.einsum('pqi,pqj->ij', uA, uA) / (P * q)
    w, U = np.linalg.eigh(C)
    Unl = U[:, ::-1]
    out = dict(V1=[V1, se1], nlAS_evals=w[::-1][: min(96, n)].tolist())
    Z2 = rng.standard_normal((P, n))
    X2 = fr['m'] + Z2 @ fr['S12']
    a2 = fut.forward(np.stack([X2]), rng)[0]
    a2 = a2 - a2.mean(0)
    res = rel.subspace_residuals(fut, fr, Unl, ks, P, rng)['gauss']
    curve = {}
    ZU = Z2 @ Unl
    for k in ks:
        # Amendment 2A: the degree-1 complement |B~ (I - P_k)|^2 estimated directly on the holdout (coordinates
        # k..n of the basis), with its jackknife SE; zero at k = n by construction.
        if k >= n:
            c1, s1 = 0.0, 0.0
        else:
            c1, s1, _ = rel.ustat_sq(a2, ZU[:, k:])
        r_tot, s_tot = res[k]
        curve[str(k)] = [float(r_tot), float(c1), float(r_tot - c1), float(math.hypot(s_tot, s1))]
    out['nlAS'] = curve
    return out


def n1_split(fut, fr, P, rng, ks):
    """Unbiased degree-1 counts: the degree-1 relevance basis U1 (eigenvectors of B~^T B~) is estimated on one half
    and its captured degree-1 share is measured on the other half by the U-statistic (no eigenvalue-noise inflation).
    Returns dict k -> [V_1 - captured_1(k)] (absolute) and V_1."""
    n = len(fr['m'])
    ZA = rng.standard_normal((P, n))
    XA = fr['m'] + ZA @ fr['S12']
    aA = fut.forward(np.stack([XA]), rng)[0]
    aA = aA - aA.mean(0)
    _, _, BA = rel.ustat_sq(aA, ZA)
    w, U = np.linalg.eigh(BA.T @ BA)
    U1 = U[:, ::-1]
    ZB = rng.standard_normal((P, n))
    XB = fr['m'] + ZB @ fr['S12']
    aB = fut.forward(np.stack([XB]), rng)[0]
    aB = aB - aB.mean(0)
    V1, se, _ = rel.ustat_sq(aB, ZB)
    ZU = ZB @ U1
    out = {}
    for k in ks:
        cap = 0.0 if k == 0 else rel.ustat_sq(aB, ZU[:, :k])[0]
        out[str(k)] = float(V1 - cap)
    return dict(V1=[float(V1), float(se)], res1=out)
