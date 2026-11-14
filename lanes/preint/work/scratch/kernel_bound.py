"""Gegenbauer energies of the deep ReLU kernel in dimension d and the rank lower bound for N-point (or N-line) rules.

kappa_L = L-fold composition of the normalised arc-cosine map k(r) = (sqrt(1 - r^2) + (pi - arccos r) r) / pi
(infinite-width NNGP of a He-ReLU net; the finite-width weight-averaged kernel differs by O(L/n): HEURISTIC proxy).
Power series kappa_L(r) = sum_m b_m r^m (series composition, truncated at degree M; the truncated mass is reported).
r^m = sum_{k = m, m-2, ...} c^{(d)}_{m,k} P_k(r) with P_k = C^{(alpha)}_k / C^{(alpha)}_k(1), alpha = (d-2)/2 (all
c >= 0, sum_k c_{m,k} = 1); a_k = sum_m b_m c_{m,k}: the energy of degree k (kappa = sum_k a_k P_k).
pi^{(j)}: Gegenbauer coefficients of P_j^2 (probability distribution on even k <= 2j, pi_0 = 1/N(d,j)).
Bound (FORMAL F7): for any N-point rule with real weights, under the weight average, s = sum_i c_i |x_i|,
  sum_{k>=1} pi^{(j)}_k Q_k >= s^2 (1/N - 1/N(d,j)),   Q_k = sum_{i,i'} v_i v_i' P_k(<xhat_i, xhat_i'>) >= 0,
so for alpha >= 0 with sum_j alpha_j pi^{(j)}_k <= a_k (k >= 1): E MSE >= m^2 a0 B / (a0 + B), B = sum_j alpha_j
(1/N - 1/N(d,j))_+ (m = E|x|). N line + radius integrals: 1/N -> 1/(N (j + 1)). LP for alpha solved per N.
Usage: kernel_bound.py OUT.json"""
import json
import math
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.special import gammaln

M = 1200          # power-series truncation degree
KMAX = 160        # Gegenbauer degrees kept
JMAX = 40         # test kernels P_j^2, j <= JMAX


def arccos_series(M):
    """Power series of k(r) = (sqrt(1-r^2) + (pi - arccos r) r) / pi = 1/pi + r/2 + (r arcsin r + sqrt(1-r^2) - 1)/pi."""
    c = np.zeros(M + 1)
    c[0] = 1.0 / math.pi
    c[1] = 0.5
    # r arcsin r = sum_j a_j r^{2j+2}, a_j = (2j)! / (4^j (j!)^2 (2j+1)); sqrt(1-r^2) - 1 = -sum_{j>=1} e_j r^{2j},
    # e_j = (2j)! / (4^j (j!)^2 (2j - 1))
    for j in range(0, M // 2 + 1):
        lc = gammaln(2 * j + 1) - j * math.log(4) - 2 * gammaln(j + 1)
        if 2 * j + 2 <= M:
            c[2 * j + 2] += math.exp(lc) / (2 * j + 1) / math.pi
        if j >= 1 and 2 * j <= M:
            c[2 * j] -= math.exp(lc) / (2 * j - 1) / math.pi
    return c


def compose(outer, inner, M):
    """Coefficients of outer(inner(r)) truncated at degree M (inner has no constant-free assumption)."""
    res = np.zeros(M + 1)
    powk = np.zeros(M + 1)
    powk[0] = 1.0
    for k in range(len(outer)):
        if abs(outer[k]) > 0:
            res += outer[k] * powk
        powk = np.convolve(powk, inner)[:M + 1]
        if not np.any(powk > 1e-300):
            break
    return res


def kernel_series(L, M):
    k1 = arccos_series(M)
    cur = k1.copy()
    for _ in range(L - 1):
        cur = compose(k1, cur, M)
    return cur


def log_C1(k, alpha):
    """log C_k^{(alpha)}(1) = log Gamma(k + 2 alpha) - log k! - log Gamma(2 alpha)."""
    return gammaln(k + 2 * alpha) - gammaln(k + 1) - gammaln(2 * alpha)


def mono_to_gegen(d, M, KMAX):
    """c[m, k]: r^m = sum_k c[m, k] P_k(r) (normalised Gegenbauer in dimension d), k <= KMAX."""
    alpha = (d - 2) / 2.0
    c = np.zeros((M + 1, KMAX + 1))
    for m in range(M + 1):
        for j in range(0, m // 2 + 1):
            k = m - 2 * j
            if k > KMAX:
                continue
            lv = (gammaln(m + 1) - m * math.log(2) + math.log(k + alpha) + gammaln(alpha) - gammaln(j + 1)
                  - gammaln(m - j + alpha + 1) + log_C1(k, alpha))
            c[m, k] = math.exp(lv)
    return c


def gegen_poly_coeffs(d, jmax):
    """Power-basis coefficients of P_j (normalised) for j <= jmax via P_{k+1} = (2(k+alpha) r P_k - k P_{k-1})/(2 alpha + k)."""
    alpha = (d - 2) / 2.0
    P = [np.array([1.0]), np.array([0.0, 1.0])]
    for k in range(1, jmax):
        a = np.zeros(k + 2)
        a[1:] += 2 * (k + alpha) * P[k]
        a[:k] -= k * P[k - 1]
        P.append(a / (2 * alpha + k))
    return P


def Ndk(d, k):
    if k == 0:
        return 1.0
    return math.exp(math.log(2 * k + d - 2) - math.log(k) + gammaln(k + d - 2) - gammaln(d - 1) - gammaln(k))


def main():
    outp = sys.argv[1]
    res = {}
    for (n, L) in [(32, 4), (64, 8), (128, 16), (256, 32), (64, 64), (256, 64), (512, 64), (1024, 128)]:
        d = n
        b = kernel_series(L, M)
        trunc = 1.0 - b.sum()
        C = mono_to_gegen(d, M, KMAX)
        a = b @ C                                       # energies a_k, k <= KMAX
        lost = 1.0 - a.sum()                            # mass at degree > KMAX or beyond M
        m2 = 2.0 * math.exp(2 * (gammaln((d + 1) / 2.0) - gammaln(d / 2.0)))
        vr = d - m2
        ang = a[1:].sum() + lost                        # angular variance (lost mass counted as angular)
        trvar = d * ang + vr * a[0]
        Pj = gegen_poly_coeffs(d, JMAX)
        PI = np.zeros((JMAX + 1, KMAX + 1))
        Nd = np.array([Ndk(d, j) for j in range(JMAX + 1)])
        valid = np.zeros(JMAX + 1, dtype=bool)
        for j in range(1, JMAX + 1):
            sq = np.convolve(Pj[j], Pj[j])
            PI[j] = sq @ C[:sq.size]
            # keep only test kernels whose expansion is numerically sound: sums to 1, no negative mass, pi_0 = 1/N(d,j)
            valid[j] = (abs(PI[j].sum() - 1.0) < 1e-8 and PI[j].min() > -1e-10
                        and abs(PI[j][0] * Nd[j] - 1.0) < 1e-6 if 1.0 / Nd[j] > 1e-250 else
                        abs(PI[j].sum() - 1.0) < 1e-8 and PI[j].min() > -1e-10)
        PI = np.maximum(PI, 0.0)
        PI[~valid] = 0.0
        rec = dict(n=n, L=L, series_trunc_mass=float(trunc), mass_beyond_KMAX=float(lost), a0=float(a[0]),
                   ang_var=float(ang), radial_share=float(vr * a[0] / trvar),
                   a=[float(v) for v in a[:41]],
                   mean_degree=float(((np.arange(KMAX + 1) * a)[1:].sum() + lost * KMAX) / ang),
                   even_share=float(a[2::2].sum() / ang), odd_share=float(a[1::2].sum() / ang),
                   share_deg1=float(a[1] / ang), share_deg2=float(a[2] / ang),
                   pi_check=[float(PI[j].sum()) for j in (1, 5, 10, 20, JMAX)],
                   pi0_vs_1overN=[float(PI[j][0] * Nd[j]) for j in (1, 5, 10, 20, JMAX)],
                   valid_j_max=int(np.nonzero(valid)[0].max()), n_valid=int(valid.sum()), bounds={})
        for lines in (False, True):
            for logN in range(6, 23, 2):
                Nn = 2.0 ** logN
                gain = np.array([max(0.0, 1.0 / (Nn * ((j + 1) if lines else 1)) - 1.0 / Nd[j]) if valid[j] else 0.0
                                 for j in range(1, JMAX + 1)])
                A = PI[1:, 1:].T                        # constraints k = 1..KMAX
                r = linprog(-gain, A_ub=A, b_ub=a[1:], bounds=[(0, None)] * JMAX, method='highs')
                B = -r.fun if r.success else float('nan')
                mse_lb = m2 * a[0] * B / (a[0] + B) if B > 0 else 0.0
                rec['bounds'][('lines' if lines else 'points') + '_2^%d' % logN] = dict(
                    B=float(B), N_times_nmse_lb=float(Nn * mse_lb / trvar))
        res['%dx%d' % (n, L)] = rec
        print('n %4d L %3d a0 %.4f ang %.2e mean_deg %.1f even %.2f deg1 %.3f deg2 %.3f radial %.3f lost %.1e |' % (
            n, L, rec['a0'], ang, rec['mean_degree'], rec['even_share'], rec['share_deg1'], rec['share_deg2'],
            rec['radial_share'], lost), 'valid j<=%d (%d)' % (rec['valid_j_max'], rec['n_valid']),
            ' '.join('%s:%.2f' % (k.replace('points_', 'P').replace('lines_', 'Ln'), v['N_times_nmse_lb'])
                     for k, v in rec['bounds'].items() if k.startswith('points')), flush=True)
    json.dump(res, open(outp, 'w'), indent=1)


if __name__ == '__main__':
    main()
