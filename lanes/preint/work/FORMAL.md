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

---
# Additions after the v1 freeze (each dated; v1 above is unchanged, hash in notes/formal_hashes.txt)

## E1 (14:14Z, main's request; before reading the co-prover's round-1 answer). F9: beyond linear rules
(a) PROVEN (by citation; abstracts checked 2 Nov, full texts not read). For a linear functional of a random element
of a separable Banach space with a Gaussian measure, and information made of N continuous linear functionals (point
values or line + radius integrals of f qualify): the optimal algorithm is linear (Traub, Wasilkowski, Wozniakowski,
"Average case optimality for linear problems", Theor. Comput. Sci. 29 (1984) 1-25); adaptive choice of the N
functionals does not help (Wasilkowski, Wozniakowski, "Can adaption help on the average?", Numer. Math. 44 (1984)
169-190, proved for orthogonally invariant measures, which include Gaussian measures and scale mixtures of them);
adaptively varying the number of evaluations can help, but optimal information stays close to nonadaptive fixed
cardinality (Wasilkowski, "Information of varying cardinality", J. Complexity 2 (1986) 204-228; elliptically
contoured measures: Wasilkowski, J. Complexity 5 (1989) 363-368). From memory, not checked: varying cardinality does not
help when the minimal error is convex in N (Plaskota, J. Complexity 9 (1993) 458-470, treats the non-convex case).
(b) Consequence (PROVEN UNDER the Gaussian surrogate prior G: f Gaussian with the nets' mean m(x) = c|x| and
covariance C = K - m m^T). Subtracting the known mean changes only the degree-0 coefficient (a_0 -> a_0 - |c|^2), so
F7(e) holds with that a_0 for every algorithm, adaptive or not, linear or not, that uses N point values or N line
integrals (fixed cardinality). The same holds for a scale mixture of G (orthogonal invariance), which covers a
net-to-net lognormal scale (Hanin-Nica: Var log |h_L|^2 ~ 5 L / n for ReLU).
(c) The true prior is not G, and the gap is not a small correction. The random-net law is supported on the
(n^2 L)-dimensional family {f_W}: each evaluation returns n numbers, so about n L generic evaluations (8,192 at
256 x 32) determine W information-theoretically (up to the net's symmetries), after which the mean is a function of
the data. So no information-based lower bound for nonlinear algorithms can hold beyond N ~ n L under the true prior;
past that point every separation must be computational (the white-box problem). Below it, non-Gaussian features
(rectified outputs: about half the units are zero at a given input; x-dependent norm fluctuations) could in principle
be exploited by a nonlinear estimator; no such estimator is known here. For rules linear in the sampled values
(MC, RQMC, lattices, designs, PI with a fixed or random u) F7 is exact without any Gaussian assumption.
(d) MEASURED (smoke test, 32 nets at 32 x 4; full runs at 64 x 8, 128 x 16, 256 x 32 queued, scratch/nongauss.py):
excess kurtosis over nets of unit outputs at a fixed input 4.7 (rectification), of pre-activations 0.8, of the one-point
error 3.7 (3.8 after dividing by each net's own RMS); Var log |h_L|^2 = 0.54 against 5 L / n = 0.625.

## E2 (14:39Z, after reading the co-prover's round 1, coprover/astra_r1_answer.md; model line gpt-6-astra checked)
Agreements found independently (v1 frozen 14:00:39Z; answer read from 14:38Z): F1 (identity and normalisation);
F4 (C^{1,1} under transversality, monotonicity unnecessary, fold argument); F3's one crossing per unit per half circle
in the wide limit; F5's Poisson-model spectrum |xi|^{-(d+3)} and the half-derivative gain in that model; F7's MMD
identity and zonal kernel; the degree-2 rank obstruction (astra's (13) is F7(d) with j = 1).
Corrections and additions from astra [A] (each re-derived by me where marked [checked]):
(a) F4 sharpened [A]: D^2 g(y) = sum_j v_j (P a_j)(P a_j)^T p(t_j(y)) / |a_j . u| on the facets crossed (P = I - u u^T,
    v_j a_j^T the Jacobian jump across facet j): a closed formula for the Hessian; C^{1,1} is sharp
    (f(a, t) = (a + |t|)_+ gives a jump of g''). For a FIXED transversal fan, D^2 g is piecewise smooth with finitely
    many interfaces, so g, G in H^{5/2-} (f in H^{3/2-}). [checked: the formula is the u-integral of the facet
    measure D^2 f = sum_j v_j a_j a_j^T H^{d-1}|F_j.]
(b) F5 corrected [A]: for a fixed net (finite fan) the constructive randomised rates are N^{-1-3/(d-1)} for
    radius-exact sampling on S^{d-1} and N^{-1-5/(d-2)} after line + radius (quadratic interpolation per cell), not
    my N^{-1-4/(d-2)}; my 4/(d-2) is the rate of the orientation-averaged Poisson model (half a derivative), which is
    the better description while cells hold many kinks (pre-asymptotic). Scrambled Sobol is only proven o(1/N) on
    either integrand. Crossover with these exponents: q - p = (2d+1)/((d-1)(d-2)) ~ 2/d, B* ~ c^{d/2}.
(c) F3 made exact at finite width [A, PROVEN; checked]: for a fixed arc independent of the weights, the expected
    number of new sign changes at layer l (all n units) is n q_n^{l-1}, q_n = 1 - (n+1)/2^n = P(at least two active
    units). Step: with a = preactivation, b = transverse derivative (independent standard Gaussians), K active units,
    the angular speed ratio is chi_{K-1}/chi_K, of conditional mean E chi_{K-1} E chi_K^{-1} = 1 for K >= 2 and 0 for
    K <= 1. So E V_l = 3 + n sum_{j<l} q_n^j and the expected cost of a full exact line is
    3 + (n/L) sum_{j=0}^{L-2} (L-1-j) q_n^j passes (about 3,971 at 256 x 32, 205 at 8 x 256). My v1 F3(b) is the same
    Kac-Rice step conditional on the past; (c) of v1 (HEURISTIC wide-limit) is replaced by this exact expectation. The
    measured ratios 0.76-1.39 are sample means of a heavy-tailed product (few lines, one net per size).
(d) F7(g) relabelled [A]: the NNGP kernel is not a safe proxy for the finite-width kernel along L = alpha n: at
    finite width b_0 <= m_n^2 / n, so 1 - b_0 >= 1/(2n) + O(n^-2), while the GP composition has 1 - b_0 = O(n^-2)
    (9 pi^2 / (2 t^2)); in that joint limit the GP even gives a counterexample to absolute-MSE barriers
    (radius-exact MC risk O(1/(d N))). So F7(g)'s numbers are an NNGP illustration only; the theorem F7(e) stands,
    and its numbers must come from the finite-width (per-net or weight-averaged) degree energies (runs/deg_*.json).
(e) A proxy-free finite-width barrier [A, PROVEN; checked the three inequalities]: the finite-width power-series
    coefficients satisfy b_j >= 0, b_0 >= 1/pi, b_2 >= b_0/(2n) (the first layer's radial Hermite feature
    (|Z|^2 - n)/sqrt(2n) carries E F / sqrt(2n)), b_0 <= m_n^2/n. With the rank-r degree-2 bound this gives, for every
    network-independent scalar-weight rule (signed weights allowed), absolute ensemble MSE >= 1/(4 pi^2 N) for N <= n/2
    point queries and >= 1/(8 pi^2 N) for N <= n/4 line + radius queries, at every depth. So no width-uniform exponent
    above 1 holds over budget windows reaching N ~ n. Normalised version under sup_n E tr Var f < infinity
    (not proved). F7(e) extends the window to N ~ N(d, j) but needs the even energy above degree 2j, which is the
    unproven H_even at finite width.
(f) Signed weights at high degree: astra's high-degree bound (17) uses positive weights; F7(d) (rank lemma with the
    degree-j harmonic feature map) does not need positivity: (tr A)^2 <= rank(A) ||A||_F^2 holds for real symmetric A
    of any signature. To be audited in round 2.
(g) Positive route [A, PROVEN UNDER an approximation-versus-cost hypothesis]: a white-box surrogate p_q with exact
    integral at cost q^a and residual trVar(f - p_q) <= C q^-b, uniformly in width, gives MSE T^{-1-b/a} by
    construction + independent correction samples. Concrete test proposed by astra: an exact first-layer squared-norm
    control S(U) = |relu(W_1 U)|^2 with E S = ||W_1||_F^2 / (2d), linearised inside the multilevel sampler's first
    level. A single fixed control changes only the constant; an exponent needs a family with the uniform law.

## E3 (14:48Z) Per-net version of F7, test-kernel leakage, and the measured non-Gaussianity
(a) Per-net theorem (PROVEN [C]): for a fixed net W and any N-point rule composed with an independent Haar-random
    rotation Q of the inputs (any rule can be randomised this way), E_Q |E f - nu_Q(f)|^2 equals the discrepancy under
    the net's own zonal kernel kappa_W(rho) = sum_k ||f_k||^2 P_k(rho), where ||f_k||^2 is the energy of the degree-k
    angular component of xhat -> f_W(xhat) (Fubini over Q; E_Q f(Qx) . f(Qy) depends only on |x|, |y|, <xhat, yhat>).
    So F7(e) holds per net with a_k = ||f_k||^2. Degree 1 and 2 energies and the odd/even split are measurable
    (scratch/degrees.py); individual degrees >= 4 are not (4th-order tensors or very noisy U-statistics).
(b) NUMERICAL: the test kernels P_j^2 concentrate on degree 2j: pi^{(2)}_4 = 0.891, 0.942, 0.970, 0.985 and
    pi^{(3)}_6 = 0.787, 0.879, 0.935, 0.966 at d = 32, 64, 128, 256 (the rest on lower even degrees). Using the
    measured lump "even degrees >= 4" as if it sat at degree 4 (alpha_2 = lump) is therefore accurate to a few
    percent at d >= 128 but needs per-degree dominance to be rigorous: it is HEURISTIC. Rigorous per net with
    measured quantities: degree 2 only, N(1/N - 1/d) (useful for N < d).
(c) MEASURED (scratch/nongauss.py, post hoc; fresh nets 10000+, K = 96-512 per size): excess kurtosis over nets of
    a unit's pre-activation at a fixed input 1.8-2.4 (close to the lognormal scale mixture 3(e^{Var log} - 1) with
    Var log |h_L|^2 = 0.67-0.73 against Hanin-Nica's 5L/n = 0.625); of unit outputs 6.9-9.1 (half the units are zero
    at a given input); of the one-point error divided by each net's own RMS 5.7-8.8 (n = 32-256, L = n/8). So the
    random-net prior is far from Gaussian at L/n = 1/8, mostly through rectification, not only through a scale
    mixture (which orthogonal invariance would cover). E1's extension to nonlinear and adaptive algorithms therefore
    applies only to the Gaussian surrogate; for the true prior the linear-rule theorem (F7, E3a) is what holds.

## E4 (14:57Z) H_even measured on actual nets (post hoc; scratch/degrees.py v2, results/degree_table.md)
Per-net angular energies as shares of the angular variance (2^14 directions per net; degree 1 and 2 by split-half
products of centred moment tensors, unbiased; odd and even parts from antipodal pairs): even degrees >= 4 carry
0.08-0.09 (n = 32, L = 4), 0.11-0.17 (64, 8), 0.17-0.26 (128, 16), 0.25-0.27 (256, 32); odd degrees >= 3 carry
0.12-0.31 over the same range; degrees 1-2 fall from 0.79 to 0.43. The NNGP proxy (F7(g)) has the right order for the
even share at n = 128-256 but the wrong low degrees (it gives degree-1 shares 0.11-0.19 against 0.21-0.36 measured).
With E3(a)-(b): a rotation-randomised N-point rule at 256 x 32 has N x nMSE >~ 0.24-0.26 for N << N(256, 2) = 32,895
(HEURISTIC through the leakage step). Over n = 32-256 the even share above degree 2 rises with width, as H_even needs;
no proof that it stays bounded below as n -> infinity.
A first version of the estimator (uncentred moments, v1) gave deg2 = 0.45 and -0.12 on the two 256 x 32 nets (noise:
the output mean is ~6x its angular spread); v2 removes that noise (logs/deviations.txt).

## E5 (15:17Z) Co-prover round 2 audit (coprover/astra_r2_answer.md; model line gpt-6-astra; read-only, xhigh)
Confirmed (PROVEN, with the stated qualifications): F1; F2 (exact in real arithmetic; the pass count is matvec-
equivalent; crossings are sorted, so it is not a wall-clock bound; window mode is unbiased, not exact); F3 and E2(c)
(new strict sign changes; the half-circle specialisation n q_n^{l-1}; for an arc of length |A|: (n |A| / pi) q_n^{l-1};
not valid unchanged for a network-chosen u such as PI_as); F4 with two corrections: W^{2,inf}_loc (not global; the
function grows linearly) and F4(v)'s "has a kink" is too strong (a parallel facet can leave a kink or cancel, e.g.
f(y, t) = clip(t, -|y|, |y|)); E2(a)-(b); F7(a)-(c) for network-independent scalar-weight rules; F7(d) and E2(f) for
signed weights (no eigenvalue sign assumption); the line rank bound, refined to r_j <= 1 + N j when all lines share u;
F7(e)'s LP and the minimisation over s; the degree-energy formulas of scratch/degrees.py.
Corrections:
(a) F7(f) as stated is WRONG [A, counterexample]: for d >= 11 a signed rule on 3d - 2 nodes integrates every degree-4
    harmonic exactly, so "even energy above degree 2j" alone does not force c/N; the LP needs individual degrees
    (alpha_2 = min(a_2 / pi_2, a_4 / pi_4)). Repaired for the actual finite-width ENSEMBLE [A, PROVEN UNDER the
    hypothesis]: using the nonnegative power-series coefficients b_l, tensor features x^{tensor j} (which also extend
    astra's (17) to signed weights) and r = min{j : N(d, j) >= 2N}, for N <= d^p:
    E_W ||error||^2 / Vbar >= (c/2 - O(1/d) - O(1/N)) / N whenever m^2 sum_{j >= r} a_{2j} >= c Vbar
    (point rules; a ratio of ensemble expectations, not per-net nMSE or medians).
(b) E3(b)'s lump-based per-net barrier (even >= 4 treated as degree 4) is not a certificate: a per-net bound needs
    a_4 (and a_6 near N = N(d, 2)) individually with uncertainty, e.g. a_k = N(d, k) E[F(U) . F(V) P_k(U . V)] on
    independent pairs. Not done (the U-statistic is too noisy at d >= 64 with our budgets).
(c) E1(b) needs scalar outputs or separable output covariance [A, counterexample with matrix output weights]: the
    nets' output covariance is exchangeable (common mode plus unit-specific), not separable, so the all-algorithm
    extension holds channel by channel (common mode and differential modes, each with its own scalar kernel), not with
    the trace kernel directly. The Gaussian results themselves are proved directly [A]: the conditional mean is affine;
    with adaptive linear functionals the posterior covariance depends only on the realised functionals, so adaption
    cannot beat the best nonadaptive design; scale mixtures inherit this for fixed cardinality; with an expected (not
    capped) cardinality budget, varying cardinality helps at most down to the convex envelope of e_N^2.
(d) E1(c)'s identifiability claim is WITHDRAWN [A, counterexample]: finitely many evaluations can miss an arbitrarily
    narrow activation cone (an open family of nets agrees at every sampled point and has different integrals; a
    width-3, two-layer construction), dead units remove local equations, and rescalings reduce the count. So neither
    "about nL evaluations identify W" nor "information bounds for nonlinear algorithms end at N ~ nL" follows. What
    remains true: the all-algorithm bound is proved only for Gaussian (or scale-mixture) surrogates; for the true prior
    nonlinear and adaptive algorithms are not covered either way.
(e) E3(c)'s diagnostic remark is wrong [A]: dividing by a net's own RMS does not give a pure Gaussian scale mixture zero
    excess kurtosis (it leaves sign(Z), excess kurtosis -2). The kurtosis numbers are descriptive only; log |h|^2 is
    clipped at nets with a dead output (zero norm has positive probability at finite width).
(f) Matched-N comparisons (posthoc_matched.py): the "line worth" column is a variance ratio r(N) at matched N, not an
    equivalent number of points (that is N r^{1/alpha}); and the two slopes were fitted over different actual ranges
    (PI from its own lower endpoint, the reference from whatever points exist above it). Fixed in v2 of the script
    (intersection of ranges; both quantities reported).
(g) Positive route (E2(g)) confirmed, with the caveat that if evaluating the residual costs q^gamma the exponent is
    1 + (b - gamma)/a; squared-hinge controls (astra's round-1 first-layer control and sums of them) cannot touch even
    degrees >= 4 (floor sum_{k >= 4 even} a_k). Candidate family [A, HEURISTIC]: biased Gaussian ridge controls
    a + B x + sum_r v_r (a_r . x - t_r)_+ with normals from first-layer rows and sampled gate normals, fitted, each with
    an analytic Gaussian integral; cheapest falsification: a nested-dictionary residual test across the ladder with
    held-out residual variance and all construction, fitting and evaluation charged. No evidence yet for a
    width-uniform b > 0.

## E6 (15:56Z) Changes after the review's round 1 (review/review_r1_answer.md; responses in review/RESPONSE.md)
- F3 is the cost of this algorithm (retained vertices), not a lower bound for exact line integration: inherited
  vertices can become redundant downstream, and pruning was not tried.
- E2(b)'s exponents are upper bounds for an interpolation-plus-residual cubature, not rates of scrambled Sobol, and a
  lower measured slope is not by itself evidence of a pre-asymptotic regime. c^{d/2} is conditional on power-law models
  with comparable prefactors.
- F7's statements are kept in their exact scope: network-independent nodes, directions and scalar weights; the
  proxy-free bound is in absolute squared error for N <= n/2 points or n/4 lines; the ensemble corollary is for point
  rules and is a ratio of ensemble expectations; line rules have the LP certificate with r_j = N (j + 1) only.
- E3/E4's per-net "barrier" is a heuristic (aggregate treated as degree 4) that would apply only to Haar-randomised
  rules; the claim of a ~4x ceiling on what designs can gain is withdrawn.
- The window estimator's one-point tail term gives an eventual C_eps / N floor (negligible at eps = 1e-8 over the
  budgets run).
