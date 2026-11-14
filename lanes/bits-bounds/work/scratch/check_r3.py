"""Numerical checks of co-prover round 3 (coprover/astra_r3_answer.md); output logs/check_r3.log.
(a) a_n = E sqrt((2/n) sum (Z_i)_+^2) = 1 - 5/(8n) + O(n^-2): exact sum over K ~ Binomial(n, 1/2) chi-square laws.
(c) E|H|^4 - E|G|^4 = (9/2) n + O(1) at the first layer (H = relu(W X), G its moment-matched Gaussian given W), from
    per-W exact formulas (arc-cosine kernels of degree 1 and 2; Gaussian fourth moments), averaged over W draws.
(d) E rho_1 = E|G| - E|H| = 9/(16 sqrt n) + o(n^-1/2): E|H| = a_n E|X| exactly; E[|G| | W] by the Laplace identity
    E sqrt(Z) = (1/(2 sqrt pi)) int_0^inf (1 - E exp(-t Z)) t^(-3/2) dt (exact for Gaussians), averaged over W with the
    control variate sqrt(q(W)), q = E|H|^2 given W, whose mean is known exactly.
(e) Cov(Z_+, Z'_+) at correlation 1/2: exact 0.1453439474 against the linear (K = 2 'simple') term 1/8.
(f) Counterexample to the pointwise radius hypothesis: E|G_M| - E|H_M| ~ -1/(2 sqrt(2 pi) M^2).
(g) The constants: C_V = 1 + 2 sum_j (1 - c_j), c_{j+1} = kappa(c_j), c_0 = 0; c(alpha) = 81 e^{-5 alpha/4} /
    (512 pi C_V); the one-defect constant (81 / (256 pi)) e^{-5 alpha/4}.
Also a Monte Carlo cross-check of the Laplace quadrature at n = 16."""
import math
import numpy as np
from scipy.special import gammaln, ndtr
from scipy import integrate

rng = np.random.default_rng(20261101 + 3)
out = []


def p(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


def k1(r):
    r = np.clip(r, -1.0, 1.0)
    th = np.arccos(r)
    return (np.sin(th) + (math.pi - th) * np.cos(th)) / (2 * math.pi)


def k2(r):
    r = np.clip(r, -1.0, 1.0)
    th = np.arccos(r)
    return (3 * np.sin(th) * np.cos(th) + (math.pi - th) * (1 + 2 * np.cos(th) ** 2)) / (2 * math.pi)


def a_exact(n):
    K = np.arange(1, n + 1)
    logp = gammaln(n + 1) - gammaln(K + 1) - gammaln(n - K + 1) - n * math.log(2)
    ek = np.exp(logp + gammaln((K + 1) / 2) - gammaln(K / 2)) * 2 / math.sqrt(n)
    return float(ek.sum())


def mean_radius(n):
    return math.exp(0.5 * math.log(2.0) + gammaln((n + 1) / 2.0) - gammaln(n / 2.0))


def gauss_radius(m, S, umin=-60.0, umax=60.0, du=0.005):
    """E|G| for G ~ N(m, S) by the Laplace identity (trapezoid in u = log t)."""
    lam, V = np.linalg.eigh(0.5 * (S + S.T))
    lam = np.maximum(lam, 0.0)
    mt2 = (V.T @ m) ** 2
    u = np.arange(umin, umax + du, du)
    t = np.exp(u)
    tl = 2.0 * np.outer(t, lam)
    logM = -0.5 * np.log1p(tl).sum(axis=1) - t * (mt2[None, :] / (1.0 + tl)).sum(axis=1)
    f = -np.expm1(logM) * np.exp(-0.5 * u)
    return float(np.trapezoid(f, u) / (2 * math.sqrt(math.pi)))


def first_layer_moments(W):
    s = np.linalg.norm(W, axis=1)
    R = (W @ W.T) / np.outer(s, s)
    np.fill_diagonal(R, 1.0)
    m = s / math.sqrt(2 * math.pi)
    S = np.outer(s, s) * (k1(R) - 1 / (2 * math.pi))
    np.fill_diagonal(S, s * s * (0.5 - 1 / (2 * math.pi)))
    return s, R, m, S


p('(a) n, n(1 - a_n)  [-> 5/8 = 0.625]')
for n in [16, 64, 256, 1024, 4096]:
    p('   ', n, round(n * (1 - a_exact(n)), 5))

p('(Laplace quadrature vs Monte Carlo at n = 16, one W)')
n = 16
W = rng.standard_normal((n, n)) * math.sqrt(2 / n)
s, R, m, S = first_layer_moments(W)
lam, V = np.linalg.eigh(S)
G = m + (rng.standard_normal((400000, n)) * np.sqrt(np.maximum(lam, 0))) @ V.T
r = np.linalg.norm(G, axis=1)
p('    E|G| Laplace', round(gauss_radius(m, S), 6), ' MC', round(r.mean(), 6), '+-', round(r.std() / math.sqrt(len(r)), 6))

p('(c, d) n, draws, (E|H|^4 - n^2)/n [-> 7 + 10/n], (E|G|^4 - n^2)/n [-> 5/2 + O(1/n)], difference/n [-> 9/2],'
  ' sqrt(n) E rho_1 [-> 9/16 = 0.5625] +- SE')
for n, draws in [(16, 400), (64, 200), (256, 60)]:
    H4, G4, cv = [], [], []
    for _ in range(draws):
        W = rng.standard_normal((n, n)) * math.sqrt(2 / n)
        s, R, m, S = first_layer_moments(W)
        s2 = s * s
        H4.append(float(s2 @ k2(R) @ s2))
        q = float(s2.sum() / 2)
        G4.append(q * q + 2 * float(np.sum(S * S)) + 4 * float(m @ S @ m))
        cv.append(gauss_radius(m, S) - math.sqrt(q))
    H4, G4, cv = np.array(H4), np.array(G4), np.array(cv)
    Esq = math.exp(0.5 * math.log(2.0) + gammaln((n * n + 1) / 2.0) - gammaln(n * n / 2.0)) / math.sqrt(n)
    EG = cv.mean() + Esq
    EH = a_exact(n) * mean_radius(n)
    se = cv.std(ddof=1) / math.sqrt(draws)
    p('   ', n, draws, round((H4.mean() - n * n) / n, 3), round((G4.mean() - n * n) / n, 3),
      round((H4 - G4).mean() / n, 3), '+-', round((H4 - G4).std(ddof=1) / math.sqrt(draws) / n, 3),
      ' sqrt(n) E rho_1 =', round(math.sqrt(n) * (EG - EH), 4), '+-', round(math.sqrt(n) * se, 4))

p('(e) Cov(Z+, Z\'+) at r = 1/2: exact', round(float(k1(0.5) - 1 / (2 * math.pi)), 10), ' linear term r/4 =', 0.125)

p('(f) M, E|G_M| - E|H_M|, -1/(2 sqrt(2 pi) M^2)')
for M in [4.0, 8.0, 16.0, 32.0]:
    ph = lambda z: math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    EH = integrate.quad(lambda z: ph(z) * math.sqrt(max(M + z, 0) ** 2 + max(-z, 0) ** 2), -np.inf, -M,
                        epsabs=1e-14, epsrel=1e-13, limit=400)[0]
    EH += integrate.quad(lambda z: ph(z) * math.sqrt((M + z) ** 2 + z * z), -M, 0, epsabs=1e-14, epsrel=1e-13, limit=400)[0]
    EH += integrate.quad(lambda z: ph(z) * (M + z), 0, np.inf, epsabs=1e-14, epsrel=1e-13, limit=400)[0]
    PhM, phM = float(ndtr(M)), ph(M)
    m1 = M * PhM + phM
    m2 = 1 / math.sqrt(2 * math.pi)
    e11 = (M * M + 1) * PhM + M * phM
    e22 = 0.5
    e12 = integrate.quad(lambda z: (M + z) * (-z) * ph(z), -M, 0, epsabs=1e-15, epsrel=1e-13)[0]
    Sg = np.array([[e11 - m1 * m1, e12 - m1 * m2], [e12 - m1 * m2, e22 - m2 * m2]])
    EG = gauss_radius(np.array([m1, m2]), Sg, du=0.002)
    p('   ', M, '%.4e' % (EG - EH), '%.4e' % (-1 / (2 * math.sqrt(2 * math.pi) * M * M)))

# stable recurrence for d_j = 1 - c_j (review 2, finding 6): 1 - kappa(1 - d) = (pi d - sqrt(d (2 - d))
# + (1 - d) arccos(1 - d)) / pi with arccos(1 - d) = 2 arcsin(sqrt(d / 2)); tail sum_{j >= J} d_j ~ A/(J - 1/2),
# where d_j j^2 -> A = 9 pi^2/2.
d = 1.0
tot = 0.0
J = 4000000
for j in range(J):
    tot += d
    d = (math.pi * d - math.sqrt(d * (2 - d)) + (1 - d) * 2 * math.asin(math.sqrt(d / 2))) / math.pi
A = d * J * J
tot += A / (J - 0.5)
CV = 1 + 2 * tot
p('(g) C_V =', round(CV, 6), ' (tail constant (1 - c_j) j^2 at j = 4e6:', round(A, 3), '; 9 pi^2/2 =',
  round(9 * math.pi ** 2 / 2, 3), ')')
for alpha in [0.5, 1.0]:
    p('    alpha', alpha, ' c(alpha) =', '%.3e' % (81 * math.exp(-1.25 * alpha) / (512 * math.pi * CV)),
      ' one-defect constant (81/(256 pi)) e^{-5 alpha/4} =', round(81 * math.exp(-1.25 * alpha) / (256 * math.pi), 5))
open('logs/check_r3.log', 'w').write('\n'.join(out) + '\n')
