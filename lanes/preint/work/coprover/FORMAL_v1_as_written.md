# preint FORMAL v1 (written 13:50-14:10Z, 2 Nov 2026, before reading the co-prover's round-1 answer)

Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, HEURISTIC, CONJECTURE. Notation: f(x) = h_L(x) in R^n,
h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n) (n x n, no biases), x ~ mu = N(0, I_d), d = n; m = E|x|; u a unit vector,
yhat uniform on the unit sphere S(u-perp); e(psi) = cos psi yhat + sin psi u; k = d - 1.

## F1. Line + radius identity (PROVEN)
E[f(x) | yhat] = int_R f(yhat + s u) w(s) ds = (k / sqrt(2 pi)) int_{-pi/2}^{pi/2} f(e(psi)) cos^{k-1}(psi) dpsi,
w(s) = (k / sqrt(2 pi)) (1 + s^2)^{-(k+2)/2}, int w = E chi_k.
Proof. x = y + t u with y ~ N(0, I on u-perp), t ~ N(0, 1) independent; y = rho yhat, rho ~ chi_k independent of yhat.
Homogeneity: f(rho yhat + t u) = rho f(yhat + (t/rho) u). Substituting t = s rho (dt = rho ds):
E[f | yhat] = int f(yhat + s u) [int_0^inf rho^2 phi(s rho) chi_k(rho) drho] ds, and the bracket equals
(k/sqrt(2 pi))(1 + s^2)^{-(k+2)/2} by int_0^inf rho^{k+1} e^{-a rho^2/2} drho = 2^{k/2} Gamma(k/2 + 1) a^{-(k+2)/2}.
The angle form follows from s = tan psi, f(yhat + s u) = f(e(psi)) / cos psi, ds = dpsi / cos^2 psi. []
So the radius is integrated together with the line at no extra cost; this conditions on less than the classic
pre-integration E[f | y] and so never has larger variance (tower property).

## F2. Exact algorithm and its cost (PROVEN)
On the half-plane H = {a yhat + b u : a >= 0} every z^{(l)} = W_l h_{l-1} is continuous, piecewise linear, positively
homogeneous. Induction: if h_{l-1} is linear on each cone spanned by consecutive vertices v_i, v_{i+1} (angle < pi),
z^{(l)} is linear there, unit j changes sign inside iff z_j(v_i) z_j(v_{i+1}) < 0, at the chord point
(1-lam) v_i + lam v_{i+1}, lam = z_j(v_i) / (z_j(v_i) - z_j(v_{i+1})), where z^{(l)} is the same interpolation of the
two vertex vectors; after inserting these points relu(z^{(l)}) is linear on every sub-cone. f(yhat + s u) is affine
in s between consecutive vertices (s = b/a), and on the end pieces it is affine with slopes f(+u), -f(-u). The
integral is a finite sum of closed forms (Student-t cdf with k + 1 degrees of freedom; elementary antiderivative
-(1/sqrt(2 pi))(1 + s^2)^{-k/2} of s w(s)). Cost: sum_l V_{l-1} matvecs (V_l = vertices after layer l) plus O(n) per
segment and per new vertex; in passes about mean_l V_{l-1}. (Implementation lib/line.py; tests/test_line.py.)

## F3. How many vertices (cost law)
(a) PROVEN. Layer 1: z_j(e(psi)) = A_j cos(psi - theta_j), which has exactly one zero in (-pi/2, pi/2) unless
theta_j = 0 mod pi (probability 0). So V_1 = 3 + n on the half circle, almost surely.
(b) PROVEN (Kac-Rice, conditional on the past). Given h_{l-1} on the arc, each unit's pre-activation
z(psi) = w . h_{l-1}(e(psi)), w ~ N(0, (2/n) I) independent of the past, is a centred Gaussian process with covariance
(2/n) <h(psi), h(psi')>, smooth on each piece between vertices (zeros at the finitely many vertices have probability
0). Kac-Rice gives E[#zeros on an arc A | past] = (1/pi) int_A |h ^ h'| / |h|^2 dpsi = Lambda_{l-1}(A) / pi, where
Lambda_{l-1}(A) is the length of the curve psi -> h_{l-1}(e(psi)) / |h_{l-1}(e(psi))| on the unit sphere
(arcs where h_{l-1} = 0 contribute no sign changes). Hence
    E[V_l - V_{l-1} | past] = n Lambda_{l-1}(A) / pi,   Lambda_0(half circle) = pi, Lambda_0(window |psi| <= psi0) = 2 psi0.
(c) HEURISTIC (wide limit). The ReLU correlation map has derivative 1 at rho = 1, so infinitesimal angles are preserved
in the wide limit and Lambda_l ~ Lambda_0: V_L ~ 3 + n L on the half circle, 3 + n L (2 psi0 / pi) on a window.
MEASURED (results/pieces.md, 12 nets n = 8..256, L <= 64): ratio to 3 + n l between 0.76 and 1.39; 256 x 32: 6,686
(0.82). Narrow-deep 8 x 256: the curve collapses (synchronisation, Lambda -> 0), V saturates at 103-172.
(d) Consequences. An exact full line costs about n L / 2 passes. The weight cos^{d-2} psi has width about
1/sqrt(d-2); a window holding all but eps of it has psi0 ~ z_eps / sqrt(d - 2), so a windowed line costs about
(z_eps / pi) L sqrt(n) passes (z = 5.7 for eps = 1e-8: 929 predicted, 752 measured at 256 x 32).

## F4. Smoothness of the pre-integrated function (PROVEN for piecewise-linear f; sketch at the level of steps)
Let f be continuous, linear on each cone of a finite complete polyhedral fan, u a unit vector not parallel to any
facet (n_sigma . u != 0 for every facet normal n_sigma). g(y) = int f(y + t u) phi(t) dt on u-perp (the same holds
for int f(y + s u) w(s) ds, k >= 2). Then:
(i) g is real-analytic on each open cell of u-perp minus A_u, A_u = the projection along u of the codimension-2
faces: there the sequence of facets crossed by the line is constant and every crossing t_sigma(y) =
-(n_sigma . y - 0)/(n_sigma . u) is affine in y, and f is affine in (y, t) between crossings.
(ii) g is C^1 everywhere: grad g(y) = int grad f(y + t u) phi(t) dt (f Lipschitz, dominated convergence; grad f is
locally constant off the facets and each line meets the facets in finitely many t), continuous in y by dominated
convergence (pointwise convergence fails only at the finitely many crossing t of the limit line).
(iii) grad g is Lipschitz: |grad g(y) - grad g(y')| <= |y - y'| sum_sigma phi_max |[grad f]_sigma| |n_sigma| / |n_sigma . u|
(each crossing moves by at most |n_sigma||y - y'| / |n_sigma . u|, and the integrand differs only between the old and
new crossing; crossings that appear or vanish at A_u do so with zero length). So g in C^{1,1} = W^{2,inf}, and the
Hessian generically jumps across A_u.
(iv) No monotonicity is needed. Gilbert-Kuo-Sloan's failure mode is a fold: two crossings merging. For a smooth fold
the gap between them grows like sqrt(dist) and leaves a fractional singularity; for a piecewise-linear fold (a line
crossing two facets that meet at a ridge) the gap grows linearly in the distance to the projected ridge, the tent
between the crossings has height O(gap), so its contribution is O(dist^2): C^{1,1} survives.
(v) If u is parallel to a facet, g has a kink (gradient jump) on that facet's projection. The constant in (iii)
grows like sum over facets of 1/|cos angle(n_sigma, u)|: large for deep nets (many facets, some nearly parallel).

## F5. Rates for a fixed net (HEURISTIC)
Random-kink model: f a sum of kinks J_i (nu_i . x - b_i)_+ with Poisson offsets and isotropic normals. Each kink's
spectrum is |omega|^{-4} along nu_i; averaging over orientations gives |f^(xi)|^2 ~ |xi|^{-(d+3)}, so f in H^{3/2-}.
After pre-integration along u a kink with c = nu . u becomes a kink smoothed over width |c|, spectrum
omega^{-4} e^{-c^2 omega^2}; c has a bounded density at 0, so the orientation average is omega^{-5} along each normal,
|g^(xi)|^2 ~ |xi|^{-(d+3)} on R^{d-1}: g in H^{2-}. Optimal randomized rules on H^s in D dims reach MSE N^{-1-2s/D}
(Bakhvalov, Novak). Radius-exact sampling works on S^{d-1} (D = d-1), PI on S^{d-2} (D = d-2):
    RQMC-RB / optimal:  N^{-1 - 3/(d-1)};   PI / optimal:  N^{-1 - 4/(d-2)},
an exponent gain (d+2)/((d-1)(d-2)) ~ 1/d. With per-line cost c_L (F3) and constants K_PI, K_RQ, the crossover is
C* = (K_PI c_L^{alpha'} / K_RQ)^{1/(alpha' - alpha)}: about (const)^{d}. For d = 8 (narrow-deep, 7 angles; PI
on 6) the asymptotic exponents are 1.43 and 1.67. Scrambled nets need not attain these isotropic rates (known bounds
for jumps are weaker: N^{-1-1/(2d-1)}); the pre-asymptotic regime (cells containing many kinks) is not covered.

## F6. What one line is worth (HEURISTIC, zonal-kernel model)
With the weight-averaged angular kernel kappa (F7), Var(line) / Var(point) ~ E[kappa~(cos(psi - psi'))] / kappa~(1),
psi, psi' independent draws from the line weight (width ~1/sqrt(d-2)), kappa~ = kappa - a_0. For mean degree D << d:
vr ~ 1 - D / (d - 2). MEASURED: vr = 0.87 (random u) and 0.69 (active-subspace u) at 32 x 4; 0.55 at 8 x 256. So at
large d a line is worth about one point while costing (z/pi) L sqrt(n) passes (F3d).

## F7. Wide-net limit: a lower bound for every rule linear in f (PROVEN; numbers NUMERICAL under the NNGP proxy)
(a) Weight-averaged kernel. K(x, x') := E_W f(x) . f(x') = |x||x'| kappa(<xhat, xhat'>) at every finite width. Proof:
W_1 Q has the law of W_1 for orthogonal Q, so K(Qx, Qx') = K(x, x'); homogeneity. kappa is positive definite on
S^{d-1}, so kappa = sum_k a_k P_k with a_k >= 0 (Schoenberg; P_k normalised Gegenbauer, P_k(1) = 1).
(b) For a rule nu (signed measure: N weighted points, or N weighted line + radius measures), fixed or randomised
independently of W: E_W |E_mu f - nu(f)|^2 = int int K d(mu - nu) d(mu - nu) (expand; Fubini).
(c) Expansion. With v_i = c_i |x_i| (points), s = sum_i v_i and Q_k = sum_{i,i'} v_i v_i' P_k(<xhat_i, xhat_i'>) >= 0:
    E_W MSE = a_0 (m - s)^2 + sum_{k >= 1} a_k Q_k
(for k >= 1, int |x| P_k(<xhat, z>) dmu(x) = 0 for every unit z).
(d) Rank lemma. For j >= 1 let Y_1..Y_{N_j} be an orthonormal basis of degree-j harmonics (N_j = dim), phi(z) the
vector of their values, so phi(z) . phi(z') = N_j P_j(<z, z'>). A = sum_i v_i phi(xhat_i) phi(xhat_i)^T has rank <= N,
tr A = N_j s and ||A||_F^2 = N_j^2 sum v_i v_i' P_j^2(rho_ii'); (tr A)^2 <= rank(A) ||A||_F^2 gives
    sum_{i,i'} v_i v_i' P_j(rho_ii')^2 >= s^2 / N.
P_j^2 = sum_k pi^{(j)}_k P_k with pi^{(j)} >= 0 (product of positive definite kernels), sum_k pi_k = 1, pi_0 = 1/N_j,
supported on even k <= 2j. Hence sum_{k>=1} pi^{(j)}_k Q_k >= s^2 (1/N - 1/N_j).
(e) Theorem. If alpha_j >= 0 satisfy sum_j alpha_j pi^{(j)}_k <= a_k for all k >= 1, then with
B = sum_j alpha_j (1/N - 1/N_j)_+:   E_W MSE >= min_s [a_0 (m - s)^2 + B s^2] = m^2 a_0 B / (a_0 + B).
For N line + radius functionals the same holds with 1/N replaced by 1/(N (j + 1)): a degree-j harmonic restricted
to a great circle spans at most j + 1 functions, so each line's matrix has rank <= j + 1.
(f) Corollary (PROVEN UNDER H_even(p, c): the even-degree energy of kappa in degrees 2j with N_j >= 2N carries at
least a fraction c of E_W tr Var f for all n in the family). Then E_W nMSE >= (c/2 - o(1)) / N for every N-point
rule: no rule linear in point values beats MC by more than the factor 2/c in that range, and none has a power-law
exponent above 1 that holds as n grows with N <= n^p. Odd degrees are not covered (antipodal pairs integrate them
exactly), and the bound says nothing for N >> N_j (fixed width, very large N), where exponents above 1 are possible.
(g) NUMERICAL (scratch/kernel_bound.py, results/kernel_bound.json; NNGP kernel kappa_L as a proxy for the finite-width
kappa, test kernels j <= 15-19, degrees <= KMAX = 160): lower bound on N x nMSE for N = 2^6 .. 2^22 points:
    32 x 4: 0.10 .. 0.01;  64 x 8: 0.19 .. 0.04;  128 x 16: 0.34 .. 0.13;  256 x 32: 0.34 .. 0.18;
    256 x 64: 0.24 .. 0.15;  512 x 64: 0.25 .. 0.17;  1024 x 128: 0.15 .. 0.10.
Measured RQMC plateaus (arc-update) are above these (32 x 4: 0.19; 256 x 32: 0.48-0.51), as they must be. Angular
degree-1 share of the NNGP kernel at 256 x 32 is 0.11 (0.10 of the total variance), while the relevance lane measured
a Hermite degree-1 share of 0.22 on actual nets: the NNGP proxy is off by about 2x in the low degrees at L/n = 1/8, so
the bound's numbers are HEURISTIC for the actual nets; the theorem (e) itself is exact for whatever kappa is.

## F8. What this says about the asymptote (HEURISTIC summary of F3-F7)
- Fixed width, N -> infinity: exponents above 1 exist (F5), and pre-integration raises them by about 1/d; the
  crossover against RQMC needs compute exponential in d. At d = 8 the gain is real but the constant is ~10^2.
- Width growing with depth along L = alpha n: the weight-averaged error of every point rule (and every line rule) is
  at least c / N for N up to poly(n) (F7), because most of the variance sits in even angular degrees whose harmonic
  spaces have dimension n^j / j!; mean degree grows like L. So sampling-side methods linear in f have asymptote 1 in
  that regime; pre-integration only adds cost (F3, F6). Escaping needs information that is not a linear functional of
  f on few points or lines: white-box use of the weights (deduction, the exact tail of nd-exact), or estimators that
  are non-linear in f.

## Open after v1
- A per-net (not weight-averaged) version for rotation-randomised rules: the same theorem with kappa = the net's own
  zonal average; it needs per-net degree energies, which are hard to measure beyond degree 2.
- The finite-width kappa's degree distribution (the NNGP proxy misses the low degrees by ~2x).
- Whether scrambled nets attain the F5 isotropic rates on kinks.
