"""Per-layer relevance accounting (measurements) and the theory-v1 predictions it is compared with.

analyse_layer(fut, X_true, rng, P, r) measures, for the future map `fut` and samples of the true layer-l law:
  frame (m, Sigma, spectrum, radial variance, angle between independent points), V_l (true and Gaussian), total
  variance and memory share (sigma > 0), Gaussian-convention mean gap, degree-1 (Stein) shares and relevance spectrum
  (vector output and scalar readout r), gradient energy, Mehler noise-sensitivity curve, active-subspace residual
  curves (vector: Gaussian and true-law projection; scalar: Gaussian), PCA-basis residuals, the radial 1-d
  description, per-degree captured shares of the AS subspaces, exact-identity parts (frozen J at the mean).
"""
import math
import time

import numpy as np

import rel


def kgrid(n):
    ks = [0, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160, 192, 224, 256]
    return [k for k in ks if k <= n]


def _res_dict(res):
    return {str(k): [float(v[0]), float(v[1])] for k, v in res.items()}


def analyse_layer(fut, Xtrue, rng, P, r=None, rhos=(-0.5, 0.0, 0.25, 0.5, 0.8, 0.95), do_true_res=True,
                  do_parts=True):
    t0 = time.time()
    n = Xtrue.shape[1]
    nout = fut.Ws[-1].shape[0]
    if r is None:  # fixed random unit readout (seeded), the generic scalar observable
        r = np.random.default_rng(424242).standard_normal(nout)
        r = r / np.linalg.norm(r)
    Pc = Xtrue.shape[0]
    fr = rel.gaussian_frame(Xtrue[: Pc // 2])
    Xe = Xtrue[Pc // 2:]
    m = fr['m']
    e = m / np.linalg.norm(m)
    trS = float(np.trace(fr['C']))
    rad = float(e @ fr['C'] @ e)
    A, B = Xe[: len(Xe) // 2], Xe[len(Xe) // 2: 2 * (len(Xe) // 2)]
    nA, nB = np.linalg.norm(A, axis=1), np.linalg.norm(B, axis=1)
    ok = (nA > 0) & (nB > 0)
    cosab = np.einsum('pi,pi->p', A[ok], B[ok]) / nA[ok] / nB[ok]
    ev = fr['evals']
    out = dict(n=n, t=fut.t, sigma=fut.sigma, trSigma=trS, radial_var=rad, m2=float(m @ m),
               mean_cos=float(np.mean(cosab)), theta_pair=float(np.mean(np.arccos(np.clip(cosab, -1, 1)))),
               cloud_evals=ev.tolist(), cloud_PR=float(ev.sum() ** 2 / np.sum(ev ** 2)),
               meanQ=float(np.mean(np.sum(Xe ** 2, 1)) / n))
    # added 21:46Z (after the Part 1 hash; registered fields unchanged): spectrum of the angular block P_perp Sigma P_perp
    Pp = np.eye(n) - np.outer(e, e)
    out['cloud_evals_perp'] = np.sort(np.linalg.eigvalsh(Pp @ fr['C'] @ Pp))[::-1].tolist()
    Pv = min(P, len(A))
    q_true = rel.pair_sq(fut, A[:Pv], B[:Pv], rng, r=r)
    out['V_true'] = [float(0.5 * q_true[0].mean()), float(0.5 * q_true[0].std(ddof=1) / math.sqrt(Pv))]
    out['Vr_true'] = [float(0.5 * q_true[1].mean()), float(0.5 * q_true[1].std(ddof=1) / math.sqrt(Pv))]
    Xg1, Z1 = rel.gaussian_sample(fr, P, rng)
    Xg2, _ = rel.gaussian_sample(fr, P, rng)
    q_g = rel.pair_sq(fut, Xg1, Xg2, rng, r=r)
    out['V_gauss'] = [float(0.5 * q_g[0].mean()), float(0.5 * q_g[0].std(ddof=1) / math.sqrt(P))]
    out['Vr_gauss'] = [float(0.5 * q_g[1].mean()), float(0.5 * q_g[1].std(ddof=1) / math.sqrt(P))]
    if fut.sigma > 0:
        out['totvar_true'] = [float(x) for x in rel.total_var(fut, A[:Pv], B[:Pv], rng)]
    a_t = fut.forward(np.stack([Xe[:P]]), rng)[0]
    a_g = fut.forward(np.stack([Xg1]), rng)[0]
    out['mean_gap_nmse'] = float(np.sum((a_t.mean(0) - a_g.mean(0)) ** 2) / max(out['V_true'][0], 1e-300))
    out['Ea2_true'] = float(np.mean(np.sum(a_t ** 2, 1)))
    out['Ea_true_norm2'] = float(np.sum(a_t.mean(0) ** 2))
    # degree 1 (Stein / regression), vector and scalar, Gaussian and true law
    ag = fut.forward(np.stack([Xg1]), rng)[0]
    ag = ag - ag.mean(0)
    V1g, se1g, Bt = rel.ustat_sq(ag, Z1)
    agr = (ag @ r)[:, None]
    V1rg, se1rg, Btr = rel.ustat_sq(agr, Z1)
    Zt = (Xe[:P] - m) @ fr['Sm12']
    at = fut.forward(np.stack([Xe[:P]]), rng)[0]
    at = at - at.mean(0)
    V1t, se1t, _ = rel.ustat_sq(at, Zt)
    V1rt, se1rt, _ = rel.ustat_sq((at @ r)[:, None], Zt)
    out.update(V1_gauss=[V1g, se1g], V1_true=[V1t, se1t], V1r_gauss=[V1rg, se1rg], V1r_true=[V1rt, se1rt])
    w1, U1 = np.linalg.eigh(Bt.T @ Bt)
    out['R1_evals'] = w1[::-1][: min(96, n)].tolist()
    # gradient energy and Mehler curve (vector; Gaussian)
    out['J1_gauss'] = [float(x) for x in rel.gradient_energy(fut, fr, P, rng)]
    mc = rel.mehler_curve(fut, fr, list(rhos), P, rng)
    out['mehler_D'] = {str(k): [float(v[0]), float(v[1])] for k, v in mc.items()}
    # active subspaces: vector (random output cotangents) and scalar (cotangent r)
    C, w, U = rel.active_subspace(fut, fr, P, rng, q=4)
    out['AS_evals'] = w[: min(96, n)].tolist()
    out['AS_trace'] = float(w.sum())
    ks = kgrid(n)
    res = rel.subspace_residuals(fut, fr, U, ks, P, rng, true_X=(Xe[:P] if do_true_res else None))
    out['res_AS_gauss'] = _res_dict(res['gauss'])
    if do_true_res:
        out['res_AS_true'] = _res_dict(res['true'])
    # per-degree: degree-1 captured by the AS subspaces (unbiased U-statistic on projected coordinates)
    cap1 = {}
    ZU = Z1 @ U
    for k in ks:
        if k == 0:
            cap1['0'] = 0.0
            continue
        c, _, _ = rel.ustat_sq(ag, ZU[:, :k])
        cap1[str(k)] = float(c)
    out['cap1_AS'] = cap1
    # PCA basis (whitened eigenvectors of Sigma, descending)
    resp = rel.subspace_residuals(fut, fr, fr['evecs'], ks, P, rng)
    out['res_PCA_gauss'] = _res_dict(resp['gauss'])
    # degree-1 basis
    res1 = rel.subspace_residuals(fut, fr, U1[:, ::-1], ks, P, rng)
    out['res_R1_gauss'] = _res_dict(res1['gauss'])
    # scalar readout: its own AS basis (cotangent r)
    nsc = min(P, 4096)
    Xs, _ = rel.gaussian_sample(fr, nsc, rng)
    Rr = np.broadcast_to(r, (1, nsc, 1, nout)).copy()
    if fut.sigma > 0:
        _, u = fut.vjp(np.stack([Xs, Xs]), np.concatenate([Rr, Rr]), rng, share=[0, 1])
        uA, uB = u[0][:, 0, :] @ fr['S12'], u[1][:, 0, :] @ fr['S12']
        Cr = (uA.T @ uB + uB.T @ uA) / (2 * nsc)
    else:
        _, u = fut.vjp(np.stack([Xs]), Rr)
        uA = u[0][:, 0, :] @ fr['S12']
        Cr = uA.T @ uA / nsc
    wr, Ur = np.linalg.eigh(Cr)
    wr, Ur = wr[::-1], Ur[:, ::-1]
    out['ASr_evals'] = wr[: min(96, n)].tolist()
    # scalar residuals along the scalar AS basis
    Z = rng.standard_normal((P, n))
    Zp = rng.standard_normal((P, n))
    cz, czp = Z @ Ur, Zp @ Ur
    X0 = fr['m'] + Z @ fr['S12']
    rs = {}
    for k in ks:
        Xk = fr['m'] + (np.concatenate([cz[:, :k], czp[:, k:]], 1) @ Ur.T) @ fr['S12']
        _, qs = rel.pair_sq(fut, X0, Xk, rng, r=r)
        rs[str(k)] = [float(0.5 * qs.mean()), float(0.5 * qs.std(ddof=1) / math.sqrt(P))]
    out['res_ASr_gauss'] = rs
    # radial description: the linear feature e.X (whitened direction S12 e)
    wdir = fr['S12'] @ e
    wdir = wdir / np.linalg.norm(wdir)
    Q, _ = np.linalg.qr(np.concatenate([wdir[:, None], rng.standard_normal((n, n - 1))], 1))
    if Q[:, 0] @ wdir < 0:
        Q[:, 0] *= -1
    rr = rel.subspace_residuals(fut, fr, Q, [1], P, rng)
    out['res_radial_gauss'] = [float(x) for x in rr['gauss'][1]]
    if do_true_res:
        rrt = rel.subspace_residuals(fut, fr, Q, [0, 1], P, rng, true_X=Xe[:P])
        out['res_radial_true'] = [float(x) for x in rrt['true'][1]]
        out['res_mean_true'] = [float(x) for x in rrt['true'][0]]
        Ct, wt, Ut = rel.active_subspace(fut, fr, P, rng, X=Xe[:P], q=4)
        rt = rel.subspace_residuals(fut, fr, Ut, ks, P, rng, true_X=Xe[:P])
        out['res_ASt_true'] = _res_dict(rt['true'])
    # overlap of the top AS direction with the radial whitened direction
    out['AS1_radial_overlap'] = float((U[:, 0] @ wdir) ** 2)
    if do_parts:
        pt = rel.parts_shares(fut, Xe[:P], m, rng)
        out['parts_true'] = {k: (v.tolist() if isinstance(v, np.ndarray) else float(v)) for k, v in pt.items()}
    out['seconds'] = time.time() - t0
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Theory v1 helpers
# ----------------------------------------------------------------------------------------------------------------------

def kappa_c(c):
    """Arc-cosine kernel for complex arguments (principal branches)."""
    c = np.asarray(c, dtype=complex)
    return (np.sqrt(1.0 - c * c) + (math.pi - np.arccos(c)) * c) / math.pi


def degree_spectrum_kernel(c0, t, noise_Q=None, dmax=60, r0=0.85, N=512):
    """Hermite degree spectrum s_d (d = 1..dmax) of g on a thin cloud whose independent points have cosine c0, from the
    infinite-width kernel: K(rho) prop. to C_t(c(rho)) - C_t(c0), c(rho) = 1 - (1 - rho)(1 - c0), C_t the t-fold
    output-correlation map. Noiseless future: C_t = kappa^(t). With noise_Q (radius Q = |h|^2/(n sigma^2)) the hidden
    layers are the independent-noise map c' = Q kappa(c)/(Q + 1) (two copies with independent future noise, L0 model of
    the numerics lane) and the output layer is kappa. Taylor coefficients by FFT on |rho| = r0."""
    z = r0 * np.exp(2j * math.pi * np.arange(N) / N)
    c = 1.0 - (1.0 - z) * (1.0 - c0)
    for k in range(t):
        last = (k == t - 1)
        c = kappa_c(c)
        if noise_Q is not None and not last:
            c = noise_Q * c / (noise_Q + 1.0)
    coef = np.fft.fft(c) / N
    d = np.arange(N)
    coef = (coef / r0 ** d).real
    s = coef[1: dmax + 1]
    tot = None
    # total variance share normaliser: C_t(1) - C_t(c0), computed on the real line
    cr = np.array([1.0, c0], dtype=complex)
    for k in range(t):
        last = (k == t - 1)
        cr = kappa_c(cr)
        if noise_Q is not None and not last:
            cr = noise_Q * cr / (noise_Q + 1.0)
    tot = (cr[0] - cr[1]).real
    return s / tot, tot


def h_poly_capture(lam, dmax):
    """For a spectrum lam (descending), returns cap[d-1, k] = h_d(lam_1..lam_k) / h_d(lam_1..lam_n) for d = 1..dmax,
    k = 0..n (complete homogeneous symmetric polynomials; lam normalised by lam_1 to avoid overflow)."""
    lam = np.asarray(lam, float) / lam[0]
    n = len(lam)
    H = np.zeros((dmax + 1, n + 1))
    H[0, :] = 1.0
    for j in range(1, n + 1):
        H[1:, j] = H[1:, j - 1]
        for d in range(1, dmax + 1):
            H[d, j] = H[d, j - 1] + lam[j - 1] * H[d - 1, j]
    return H[1:, :] / H[1:, n:n + 1]


def generic_capture(lam, s, ks):
    """Haar-generic model: expected explained share of the top-k PCA subspace = sum_d s_d h_d(lam_<=k)/h_d(lam)."""
    cap = h_poly_capture(lam, len(s))
    return {k: float(np.sum(s * cap[:, k])) for k in ks}


def fc_spectrum(t, m, reps=4, rng=None):
    """Squared singular values (descending) of a product of t independent m x m Ginibre matrices with entry variance
    1/m (the half-width Fuss-Catalan model of the frozen future Jacobian), averaged over reps sorted spectra."""
    rng = np.random.default_rng(0) if rng is None else rng
    acc = np.zeros(m)
    for _ in range(reps):
        M = np.eye(m)
        for _ in range(t):
            M = (rng.standard_normal((m, m)) / math.sqrt(m)) @ M
            M /= np.linalg.norm(M)
        sv = np.sort(np.linalg.svd(M, compute_uv=False) ** 2)[::-1]
        acc += sv / sv.sum()
    return acc / reps


def free_product_capture(lam, back, reps=4, rng=None):
    """Degree-1 capture curve when the backward operator (eigenvalues `back`, length n, zero-padded) is Haar-rotated
    relative to the cloud (eigenvalues lam): eigenvalues of Lam^{1/2} O^T diag(back) O Lam^{1/2}, cumulative share."""
    rng = np.random.default_rng(1) if rng is None else rng
    n = len(lam)
    b = np.zeros(n)
    b[: len(back)] = back[:n]
    acc = np.zeros(n + 1)
    for _ in range(reps):
        O, _ = np.linalg.qr(rng.standard_normal((n, n)))
        M = (np.sqrt(lam)[:, None] * (O.T * b) @ O) * np.sqrt(lam)[None, :]
        w = np.sort(np.linalg.eigvalsh(M))[::-1]
        w = np.maximum(w, 0)
        acc += np.concatenate([[0.0], np.cumsum(w) / w.sum()])
    return acc / reps


def backward_spectrum(t, n, reps=3, rng=None):
    """Squared singular values (descending, normalised to sum 1) of the frozen future Jacobian model: a product of t
    Gaussian blocks n -> n/2 -> ... -> n/2 (half the units active per layer, entries N(0, 2/n)). Rank n/2."""
    rng = np.random.default_rng(3) if rng is None else rng
    h = n // 2
    acc = np.zeros(h)
    for _ in range(reps):
        M = rng.standard_normal((h, n)) * math.sqrt(2.0 / n)
        for _ in range(t - 1):
            M = (rng.standard_normal((h, h)) * math.sqrt(2.0 / n)) @ M
            M /= np.linalg.norm(M)
        sv = np.sort(np.linalg.svd(M, compute_uv=False) ** 2)[::-1]
        acc += sv / sv.sum()
    return acc / reps


def N_from_capture(cap, eps):
    """Smallest k with 1 - cap[k] <= eps (cap indexed by k = 0..n)."""
    for k, c in enumerate(cap):
        if 1 - c <= eps:
            return k
    return len(cap) - 1
