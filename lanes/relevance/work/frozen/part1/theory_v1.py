"""Theory v1 prediction rules (FORMAL.md v1, frozen 21:17:35Z). Frozen with PREREG Part 1: do not edit; later versions
go to theory_v2.py.

Inputs per analysed layer (from accounting.analyse_layer): the measured forward quantities only (cloud spectrum, cosine
between independent cloud points c_0, radial variance, mean point norm, E|X|^2, radius Q, n, t, sigma). Outputs:
predicted Hermite shares s_d, mean degree D, and N(l, eps) for the vector output and the scalar readout.
"""
import math

import numpy as np

import accounting as acc


def J2(theta):
    return 3 * np.sin(theta) * np.cos(theta) + (math.pi - theta) * (1 + 2 * np.cos(theta) ** 2)


def Bfun(c):
    """Per-layer squared-gain covariance coefficient: Cov(A(u), A(u')) = B(c)/n, B(1) = 5, B(0) = 0."""
    c = np.asarray(c, dtype=complex)
    th = np.arccos(c)
    return (2 / math.pi) * (3 * np.sin(th) * np.cos(th) + (math.pi - th) * (1 + 2 * np.cos(th) ** 2)) - 1


def channel_kernels(c0, t, n, sigma, Q=None, N=512, r0=0.85, dmax=60):
    """Taylor coefficients (d = 1..dmax) of the direction and amplitude kernels (units of |a|^2), and their totals.
    Direction: C_t(c(rho)) - C_t(c0) (noiseless kappa^(t), or the L0 independent-noise map when sigma > 0).
    Amplitude (sigma = 0 only): (1/(4n)) sum_{j=0}^{t-1} [B(c_j(rho)) - B(c_j(c0))]."""
    z = r0 * np.exp(2j * math.pi * np.arange(N) / N)
    pts = np.concatenate([1.0 - (1.0 - z) * (1.0 - c0), [1.0 + 0j, c0 + 0j]])
    c = pts.astype(complex)
    amp = np.zeros_like(c)
    for k in range(t):
        if sigma == 0:
            amp = amp + Bfun(c) / (4.0 * n)
        c = acc.kappa_c(c)
        if sigma > 0 and k < t - 1:
            c = Q * c / (Q + 1.0)
    d = np.arange(N)
    cd = (np.fft.fft(c[:N]) / N / r0 ** d).real
    ca = (np.fft.fft(amp[:N]) / N / r0 ** d).real
    Vdir = (c[N] - c[N + 1]).real
    Vamp = (amp[N] - amp[N + 1]).real if sigma == 0 else 0.0
    return cd[1:dmax + 1], ca[1:dmax + 1], Vdir, Vamp


def predict_layer(o, dmax=60):
    n, t, sigma = o['n'], o['t'], o['sigma']
    c0 = o['mean_cos']
    EX2 = o['m2'] + o['trSigma']
    Q = o.get('meanQ') if sigma > 0 else None
    sd, sa, Vdir, Vamp = channel_kernels(c0, t, n, sigma, Q=Q, dmax=dmax)
    rel_rad = o['radial_var'] / EX2
    if sigma > 0:
        rel_rad *= math.exp(-5.0 * t / n)
    V = Vdir + Vamp + rel_rad
    s = (sd + sa) / V
    s1_split = dict(dir=float(sd[0] / V), amp=float(sa[0] / V), rad=float(rel_rad / V))
    s = s.copy()
    s[0] += rel_rad / V
    D = float(np.sum(np.arange(1, dmax + 1) * s))
    return dict(s=s, s1=float(s[0]), D=D, V_rel=float(V), Vdir=float(Vdir), Vamp=float(Vamp), Vrad=float(rel_rad),
                s1_split=s1_split)


def predict_N(o, eps_list=(0.1, 0.01, 0.001), dmax=60, rng_seed=5):
    """Rule 4c (vector) and 4d (scalar). Radial and amplitude degree-1 parts are taken as captured by the top two
    directions; the direction channel's degree 1 by the free product of the cloud spectrum with the half-width backward
    spectrum; degrees >= 2 by the generic capture of the cloud spectrum."""
    pr = predict_layer(o, dmax=dmax)
    n, t = o['n'], o['t']
    lam = np.maximum(np.array(o['cloud_evals'], float), 1e-300)
    lam = lam / lam[0]
    cap = acc.h_poly_capture(lam, dmax)  # (dmax, n+1)
    S = acc.backward_spectrum(t, n, rng=np.random.default_rng(rng_seed))
    fp = acc.free_product_capture(lam, S, rng=np.random.default_rng(rng_seed + 1))
    s = pr['s']
    s1_dir = pr['s1_split']['dir']
    s1_other = s[0] - s1_dir
    ks = np.arange(n + 1)
    res_vec = s1_dir * (1 - fp) + s1_other * (ks < 2) + np.sum(s[1:, None] * (1 - cap[1:, :]), axis=0)
    res_sc = s[0] * (ks < 1) + np.sum(s[1:, None] * (1 - cap[1:, :]), axis=0)
    out = dict(pred=pr, N_vec={}, N_sc={})
    for e in eps_list:
        out['N_vec'][str(e)] = int(np.argmax(res_vec <= e)) if np.any(res_vec <= e) else n
        out['N_sc'][str(e)] = int(np.argmax(res_sc <= e)) if np.any(res_sc <= e) else n
    out['res_vec'] = res_vec.tolist()
    out['res_sc'] = res_sc.tolist()
    return out


def N1_free_product(o, eps_list=(0.1, 0.01), rng_seed=5):
    n, t = o['n'], o['t']
    lam = np.maximum(np.array(o['cloud_evals'], float), 1e-300)
    S = acc.backward_spectrum(t, n, rng=np.random.default_rng(rng_seed))
    fp = acc.free_product_capture(lam, S, rng=np.random.default_rng(rng_seed + 1))
    pca = np.concatenate([[0], np.cumsum(lam) / lam.sum()])
    return {str(e): dict(fp=acc.N_from_capture(fp, e), pca=acc.N_from_capture(pca, e)) for e in eps_list}
