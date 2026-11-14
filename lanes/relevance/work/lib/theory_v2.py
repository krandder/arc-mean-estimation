"""Theory v2 prediction rules (FORMAL.md section "v2"; changes against v1 listed there).

Changes from v1 (theory_v1.py is kept frozen):
- D from the annealed gradient-energy identity: E_W tr(grad g Sigma grad g^T) = tr Sigma x E|a|^2 / E|X|^2 for the
  noiseless future (criticality preserves E|J v|^2), so D = (tr Sigma / E|X|^2) / (V_l / E|a|^2). v1 summed a truncated
  Taylor series of a heavy-tailed degree spectrum and was biased low.
- N lower bound (gpt-6-astra round 1): the first-chaos eigenvalue tail is a lower bound on the optimal residual of any
  k-dim projection, so N >= min{k : sum_{j>k} lambda_j(C_1) <= eps V}; eigenvalues debiased for sampling noise
  (E[B^T B]_hat = B^T B + (tr Var a / P) I).
- Stationary radial channel: rate variants 5/n (v1) and 5/(2n) + 1/Q (astra), both reported.
"""
import math

import numpy as np

import accounting as acc
import theory_v1 as v1


def predict_layer(o, dmax=60, radial_rate='v1'):
    n, t, sigma = o['n'], o['t'], o['sigma']
    c0 = o['mean_cos']
    EX2 = o['m2'] + o['trSigma']
    Q = o.get('meanQ') if sigma > 0 else None
    sd, sa, Vdir, Vamp = v1.channel_kernels(c0, t, n, sigma, Q=Q, dmax=dmax)
    rel_rad = o['radial_var'] / EX2
    if sigma > 0:
        rate = 5.0 / n if radial_rate == 'v1' else 5.0 / (2 * n) + 1.0 / Q
        rel_rad *= math.exp(-rate * t)
    V = Vdir + Vamp + rel_rad
    s = (sd + sa) / V
    s = s.copy()
    s1_split = dict(dir=float(sd[0] / V), amp=float(sa[0] / V), rad=float(rel_rad / V))
    s[0] += rel_rad / V
    D_identity = (o['trSigma'] / EX2) / V if sigma == 0 else None
    return dict(s=s, s1=float(s[0]), D=D_identity, V_rel=float(V), Vdir=float(Vdir), Vamp=float(Vamp),
                Vrad=float(rel_rad), s1_split=s1_split)


def first_chaos_lower_bound(o, P, eps_list=(0.1, 0.01, 0.001)):
    """Debiased first-chaos tail lower bound on N (NUMERICAL: relies on the debiasing of the sampled eigenvalues)."""
    V = o['V_gauss'][0]
    noise = (o['totvar_true'][0] if o['sigma'] > 0 else V) / P
    lam = np.maximum(np.array(o['R1_evals']) - noise, 0)
    V1 = o['V1_gauss'][0]
    beyond = max(V1 - lam.sum(), 0.0)
    tails = [lam[k:].sum() + beyond for k in range(len(lam))] + [beyond]
    out = {}
    for e in eps_list:
        out[str(e)] = next((k for k, tl in enumerate(tails) if tl <= e * V), len(tails) - 1)
    return out


def predict_N(o, lam_perp=None, eps_list=(0.1, 0.01, 0.001), dmax=60, rng_seed=5, radial_rate='v1'):
    """v2 rule. The radial and amplitude degree-1 parts point along the same output direction (the mean output), so
    together they occupy one input direction (captured at k >= 1). The direction channel's degree-1 part is captured by
    the free product of the ANGULAR cloud spectrum (eigenvalues of P_perp Sigma P_perp; v1 wrongly used the full
    spectrum, whose top eigenvalue is the radius) with the half-width backward spectrum, using the remaining k - 1
    directions. Degrees >= 2 are captured by the generic rule on the angular spectrum. Scalar readout: degree 1 takes
    one direction, degrees >= 2 the generic rule."""
    pr = predict_layer(o, dmax=dmax, radial_rate=radial_rate)
    n, t = o['n'], o['t']
    lp = o.get('cloud_evals_perp') if lam_perp is None else lam_perp
    lam = np.maximum(np.array(lp, float), 0.0)
    lam = lam[lam > lam[0] * 1e-10]
    lamn = lam / lam[0]
    nn = len(lam)
    cap = acc.h_poly_capture(lamn, dmax)  # (dmax, nn+1)
    S = acc.backward_spectrum(t, n, rng=np.random.default_rng(rng_seed))
    fp = acc.free_product_capture(np.concatenate([lam, np.zeros(n - nn)]) if nn < n else lam, S,
                                  rng=np.random.default_rng(rng_seed + 1))
    s = pr['s']
    s1_dir = pr['s1_split']['dir']
    s1_rest = s[0] - s1_dir
    ks = np.arange(n + 1)
    capd = np.concatenate([cap, np.repeat(cap[:, -1:], n + 1 - cap.shape[1], axis=1)], 1) if cap.shape[1] < n + 1 else cap
    fpk = np.array([fp[max(k - 1, 0)] if k >= 1 else 0.0 for k in ks])
    nonlin = np.sum(s[1:, None] * (1 - capd[1:, :n + 1]), axis=0)
    res_vec = s1_rest * (ks < 1) + s1_dir * (1 - fpk) + nonlin
    res_sc = s[0] * (ks < 1) + nonlin
    out = dict(pred=pr, N_vec={}, N_sc={}, res_vec=res_vec.tolist(), res_sc=res_sc.tolist())
    for e in eps_list:
        out['N_vec'][str(e)] = int(np.argmax(res_vec <= e)) if np.any(res_vec <= e) else n
        out['N_sc'][str(e)] = int(np.argmax(res_sc <= e)) if np.any(res_sc <= e) else n
    return out
