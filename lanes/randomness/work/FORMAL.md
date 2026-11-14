# randomness lane: FORMAL v1 (my own theory, written before reading gpt-6-astra's round-1 answer)

Labels: PROVEN, PROVEN UNDER <hypothesis>, HEURISTIC, CONJECTURE. Provenance: [C] this lane (me), [prior: lane] an
earlier lane's report. Frozen by sha256 in notes/formal_hashes.txt before astra's answer is read; later additions are
appended as E1, E2, ... and never edit this version.

## 0. Setting and notation
x ~ gamma_n = N(0, I_n); f_W(x) = h_L(x) in R^n, h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n), no bias. Positive
homogeneity: f(x) = |x| g(u), u = x/|x|. G := m_n g (m_n = E|x|), mu(W) = E_u G(u) = E_x f(x).
Harmonic decomposition on S^{n-1} (componentwise for the n outputs): G = sum_{d>=0} G_d, G_d in H_d (degree-d spherical
harmonics); E_d(W) := E_u |G_d(u)|^2 (summed over outputs); Lambda(W) := sum_{d>=1} E_d(W) = V_sph(W), the per-point
variance of radius-exact (RB) MC; lambda_d := E_W E_d(W). P_d = P_d^{(n)}: the Gegenbauer polynomial of degree d for
S^{n-1}, normalised P_d(1) = 1 (P_2(t) = (n t^2 - 1)/(n - 1)).
A linear rule (design) D = {(c_i, u_i)}_{i<=m} on the sphere, sum c_i = 1, estimates mu by I_D(G) = sum_i c_i G(u_i);
plain designs on R^n estimate by sum_i c_i f(x_i). Aliasing: A_d(D) := sum_{i,j} c_i c_j P_d(u_i . u_j) (>= 0 because
P_d is positive definite on the sphere, Schoenberg).

## 1. Exact risk of designs (black-box)
**T1 (per-net risk of a Haar-randomised design; PROVEN [C]).** For any base design D_0 and Q Haar on O(n),
  E_Q |I_{Q D_0}(G) - mu|^2 = sum_{d>=1} E_d(W) A_d(D_0).
Proof. Put G~ = G - mu. For a in H_d, b in H_{d'}, the function (u, v) -> E_Q[a(Qu) b(Qv)] is invariant under
(u, v) -> (Ou, Ov), hence a function of u . v; as a bilinear pairing H_d x H_{d'} -> functions of t it intertwines the
O(n) actions, so by Schur's lemma it vanishes for d != d' and equals <a, b> P_d(u . v) for d = d' (Funk-Hecke; the
constant is fixed at u = v). Summing over outputs, E_Q <G~(Qu), G~(Qv)> = sum_{d>=1} E_d P_d(u . v) (d = 0 removed by
centring). Expand |sum_i c_i G~(Q u_i)|^2. QED.
Corollaries (PROVEN): iid uniform points: A_d = 1/m (d >= 1); antipodal sets (u and -u, equal weights): A_d = 0 for
odd d and A_d(D) = A_d(D_+) for even d, where D_+ is one point of each pair (so even degrees pay as if there were m/2
points); spherical t-designs: A_d = 0 for 1 <= d <= t; a union of R independently Haar-rotated copies of D_0: A_d/R
in expectation. An orthonormal basis has A_2 = 0 and A_d = (1 + (n - 1) P_d(0))/n otherwise; the regular simplex
(n + 1 points) is a 2-design; the cross-polytope (+-e_i) an antipodal 3-design; the 129 mutually unbiased bases of
R^256 from the Z4-Kerdock code with antipodes an antipodal 5-design (66,048 points); the same bases without antipodes
kill degrees 2 and 4 only.
Measurement consequence: the rotation variances of these designs on one net give the partial sums E_1, E_2,
sum_{odd}, sum_{even >= 4}, sum_{even >= 6} (relative to Lambda) without any truth and without high-variance
U-statistics.

**T2 (averaging over the ensemble; PROVEN [C], also [prior: unrestricted 3.5]).** W_1 -> W_1 Q preserves the law of the
net, so for a FIXED design D (chosen without looking at W) E_W |I_D(G_W) - mu(W)|^2 = sum_{d>=1} lambda_d A_d(D): a
fixed design and its Haar-randomised version have the same average risk.

**T3 (determinism and obliviousness are free on average; PROVEN [C], elementary).** For every m there is a fixed
m-point design with E_W risk <= E_W Lambda / m (average T2 over iid uniform designs: E A_d = 1/m, so some realisation is
at most the mean). Hence an oblivious estimator with zero random bits matches radius-exact MC on average at every
budget; with the white-box weight-derived seeds of [prior: unrestricted 3.1] it matches it exactly and unbiasedly. In
the average-case model, "random bits" is not a resource.

**T4 (black-box ceiling; PROVEN [C], restating [prior: unrestricted 3.5, astra] in this notation).** For nonnegative
weights and even d, A_d(D) >= sum_i c_i^2 + (min_{[-1,1]} P_d) (1 - sum_i c_i^2) >= 1/m - |min P_d| (sum c_i^2 >= 1/m by
Cauchy-Schwarz; the off-diagonal sum has weight 1 - sum c_i^2 and each term >= min P_d). So, with
d*(m) := min{even d : |min_{[-1,1]} P_d^{(n)}| <= 1/(2m)},
  E_W risk(D) >= (1/(2m)) sum_{even d >= d*(m)} lambda_d,   gain over RB-MC <= 2 Lambda_bar / Lambda_bar_{even >= d*(m)}.
Per net (Haar-randomised designs) the same with E_d(W). For antipodal positive designs the even part costs twice:
gain <= Lambda / (2 Lambda_{even >= d*(m/2)}) up to the same o(1). NUMERICAL (exact Gegenbauer minima on a 2e6-point
grid): at n = 256, |min P_4| = 9.05e-5, |min P_6| = 5.8e-6, |min P_8| = 6.2e-7, so d* = 4 for m <= 5.5e3, d* = 6 for
m <= 8.6e4 (this covers the Kerdock design, 66,048 points, and ARC's budget, 6.5e4 passes), d* = 8 for m <= 8.1e5.
Every design affordable at ARC's budget pays the full even tail from degree 6 on.

**T5 (seed length on average; PROVEN [C] from T3-T4).** Let s*(eps) be the least log2 m such that some fixed m-point
design has E_W risk <= eps^2 E_W V. Then
  log2(Lambda_bar_{even >= d*} / (2 eps^2 E V)) <= s*(eps) <= log2(Lambda_bar / (eps^2 E V)) + 1,
so s*(eps) = 2 log2(1/eps) + O(1), where the O(1) is at most log2 of the ceiling ratio. Correction to the hypothesis
under test: high noise sensitivity (a heavy spectral tail) does not force LONG seeds; seeds of MC length always suffice
on average. It forbids SHORT ones: no design beats MC by more than the inverse even-tail share. "Long seeds"
(superpolynomial in 1/eps, or exponential in n) can only arise for worst-case classes (section 4).

## 2. Noise sensitivity, the spectrum, and Gaussian surface area
**T6 (noise sensitivity pins the design tails; PROVEN [C]).** Let NS(rho) := E |G(u) - G(v)|^2 / (2 Lambda), u uniform,
v uniform on {v : u . v = rho}. By T1's kernel identity, NS(rho) = sum_{d>=1} e_d (1 - P_d(rho)), e_d = E_d / Lambda.
Write a_d = 1 - P_d(rho) in [0, 2] and tau_t := sum_{d>t} e_d. Then
  tau_t <= NS(rho) / min_{d>t} a_d,      tau_t >= (NS(rho) - max_{d<=t} a_d) / (max_{d>t} a_d - max_{d<=t} a_d)
(whenever the denominators are positive). For fixed d and n -> infinity, P_d(rho) -> rho^d, giving
tau_t in [(NS - 1 + rho^t) / rho^t, NS / (1 - rho^{t+1})] in the large-n form (there sup_{d>t} a_d = 1). So the share of the
angular variance that a t-design cannot touch is pinned, two-sidedly, by the noise sensitivity at rho ~ 1 - 1/t. The
coordinator's "noise sensitivity governs the seed" is correct in this precise, average-case form, with the direction of
T5. NS curves and design variances are two independent measurements of the same spectrum (checked in section 5).

**T7 (Gaussian surface area of the gate partition).** (a) PROVEN: a first-layer zero set {w . x = 0} is a hyperplane
through the origin with Gaussian surface area 1/sqrt(2 pi); the layer-1 partition has GSA n/sqrt(2 pi). (b) HEURISTIC
(mean field): for l >= 2, GSA({z_{l,i} = 0}) = E[delta(z_{l,i}(x)) |grad z_{l,i}(x)|] (coarea); the neuron-averaged
density of z_{l,i}(x) at 0 is that of a variance-2 mixture, 1/sqrt(4 pi), whatever the split between the neuron's mean
over inputs and its fluctuation, and |grad z| concentrates at sqrt 2 (E |grad z|^2 = (2/n) E ||J_{l-1}||_F^2 = 2 at
He initialisation), so each layer's partition has GSA ~ n/sqrt(2 pi) and the whole gate partition ~ n L / sqrt(2 pi)
(~3,300 at 256 x 32). (c) PROVEN (standard): for a.e.-transversal surfaces, P(gate of (x, y) differs) =
2 sqrt(delta/pi) GSA (1 + o(1)) for rho = 1 - delta Gaussian pairs, so the probability that ANY gate changes is ~1 once
delta >> 1/GSA^2 ~ 1e-7. The gate pattern is extremely noise-sensitive.

**T8 (boundary mass is not what limits designs on the output; HEURISTIC with a PROVEN identity).** For piecewise-linear
f, E|grad f(x) - grad f(y)|^2 / 2 = sum_k k (1 - rho^{k-1}) W_k (W_k = Hermite energy at degree k; PROVEN, since
grad lowers the degree by one and multiplies the energy by k) and, for small delta, it is ~2 sqrt(delta/pi) times the
surface integral of the squared gradient jump |J|^2 over the kink set (HEURISTIC, transversality). Hence the Hermite
tail beyond K is ~ (int_S |J|^2 dgamma_S) / (3 sqrt(pi) K^{3/2}) as K -> infinity. When one neuron (l, i) flips, the output
gradient jumps by (d f / d h_{l,i}) grad z_{l,i}, of squared size ~ 1 x 2 summed over outputs (a column of the
downstream Jacobian has E norm^2 ~ 1 at He initialisation; |grad z|^2 ~ 2), small against E ||grad f||_F^2 ~ n. So
int_S |J|^2 ~ 2 GSA ~ 0.8 n L, and the gradient decorrelates (sqrt(delta/pi) 0.8 n L ~ n/2) only at delta ~ 1.6/L^2:
the k^{-5/2} tail law governs degrees K >~ L^2/1.6 (hundreds at L = 32), far above any affordable design strength
(<= 5). Every non-linear harmonic of a piecewise-linear f is made by its kinks (a linear f has degree 1 only), so
"boundary mass" is the source of the whole non-linear spectrum; but how it distributes over degrees 2-5, which is what
designs can touch, is a large-scale property of many weak kinks, not their count. What limits
designs is the mesoscopic spectrum (degrees 3 to ~50, mean Hermite degree n / E V ~ 20 [prior: input-bits]), produced
by composition depth, not by boundary mass. Correction to the hypothesis: the gate partition is noise-sensitive in the
extreme (GSA ~ nL), the output is not (Lipschitz, NS(delta) ~ 20 delta for small delta).

## 3. White-box designs
**T9 (what alignment changes; PROVEN [C] for the identity, HEURISTIC for the gain).** Write W_1 = P Q (polar
decomposition: P = (W_1 W_1^T)^{1/2}, Q orthogonal). Because the law of W_1 is right-rotation invariant, Q is Haar and
independent of (P, W_2..W_L). A black-box design D evaluates F(P Q x) for fixed x: Q randomises it (T2). The polar-aligned
design evaluates F(P s) for s in D (x = Q^T s): it uses D in the net's canonical frame, where the risk averaged over the
ensemble is a discrepancy in the kernel K_can(s, s') = E <F(P s), F(P s')>, invariant only under simultaneous
coordinate permutations (relu commutes with permutations, not with rotations or sign flips). In this frame each
first-layer pre-activation z_i = sum_j P_ij s_j has a diagonal share P_ii^2 / (P^2)_ii -> (E sigma)^2 / E sigma^2 =
(8 / (3 pi))^2 ~ 0.72 (quarter-circle law of the singular values of W_1 / sqrt 2), so first-layer gates are nearly
coordinate-wise functions of s, and Sobol's well-stratified low-dimensional projections stratify them. HEURISTIC: this
raises the low-order ANOVA share of the integrand in s-coordinates and helps coordinate-aligned point sets (Sobol,
lattices), not rotation-invariant designs (t-designs). Randomisation that keeps the alignment and restores
unbiasedness: scrambling in s-coordinates (LMS + digital shift: about n b^2 / 2 + n b random bits for b digits), or a
random signed permutation of a design in the canonical frame (n log2 n + n bits) for permutation-symmetric designs;
neither makes the estimator unbiased over the sphere for a fixed net unless the design's s-law is exactly Gaussian
(scrambled nets: yes per coordinate marginally; signed permutations of a fixed set: no). With zero bits (deterministic
aligned Sobol) the estimate is a fixed function of the net.
Caution (PROVEN example): aligning a design that contains the standard basis puts points e_i at inputs whose first
layer is concentrated on one neuron (z = P e_i), atypical inputs; a few hundred such points in a 66,048-point Kerdock
set are harmless, a design made of them is not.

**T10 (first-layer controls are degree <= 2; HEURISTIC, measured on dev).** Features with closed-form Gaussian means
(z_i, |z_i|, relu(z_i), z_i^2, z_i |z_i|, |h_1|^2) span, after projection onto the sphere, mostly harmonic degrees 1
and 2 plus a weak high-degree tail of |z_i|; dev net 100 (256 x 32): held-out R^2 0.39 for (z, |z|), of which the odd
part is the linear term (R^2 0.49 of the odd variance) and the even part is z^2-like (0.25 of the even variance;
|z| adds 0.02). Designs that kill degrees 1-2 already remove all of it: first-layer controls are redundant with a
2-design. The multilevel prefix-norm controls leave 0.90-0.96 of the variance at L = n/8 (dev), gain ~1.

## 4. Worst case (what the PRG literature is about)
**T11 (worst-case fooling is a different problem; PROVEN in the weak form, CONJECTURE in the strong form).** For the
class of all bias-free width-n depth-L ReLU nets, a fixed design D can be defeated: the class contains positively
homogeneous piecewise-linear functions vanishing on the m directions of D while |E f| >= c sd(f) (e.g. a polyhedral
gauge minus narrow cones around the design directions, realisable once the width and depth suffice for the polyhedron);
so worst-case fooling at constant normalised error needs m growing with the class's capacity (CONJECTURE: exp(Omega(n))
for L >= 3 and width n). Deterministic worst-case estimation is as hard as derandomising threshold circuits [prior:
hardness lane, IKW-type consequences]. Known PRGs cover depth-1 structure only: halfspaces, PTFs, intersections and
functions of k halfspaces (the first-layer gate cell is an intersection of n origin halfspaces). None of this bears on
ARC's average-case problem, where T3 makes determinism free.

## 5. The trade-off that survives, and what the measurements test
- Random bits R: irrelevant to precision on average (T3). What an estimator's own randomness still buys is a
  self-certified error bar: with r independent (or pairwise independent) randomisations of a design one gets an
  unbiased estimate and an unbiased variance estimate. Pairwise-independent random shifts cost 2 n b bits for any r;
  a Haar rotation n(n - 1)/2 angles. A fixed design gives no error estimate on a given net.
- So the trade-off is compute vs precision, and "structure" enters as the spectrum share a design kills at a given m
  (T1, T4) or, white-box, as a better frame (T9). The black-box ceiling at m <= ~5e5 points and n = 256 is
  2 Lambda / Lambda_{even >= 6} (non-antipodal) and Lambda / (2 Lambda_{even >= 6}) per antipodal design (T4); dev
  (2 nets): Lambda_{even >= 6} / Lambda = 0.13-0.20, so antipodal Kerdock gains 2.6-4.0 over MC and no positive design
  of that size can gain more than ~5-8 (T4 with these numbers; CONJECTURE that a non-antipodal 5-design of affordable
  size would get near it).
- Predictions to test (registered in PREREG.md): spectrum partial sums from designs; consistency of T6 between NS
  curves and design variances; GSA per layer ~ n/sqrt(2 pi); white-box polar alignment helps Sobol RQMC at 256 x 32;
  the best structured combination at 256 x 32 and its gain.

## E1. Additions after reading gpt-6-astra round 1 (~14:10Z; coprover/PROVENANCE.md)
E1.1 (T4, cleaner form; PROVEN [A]). With k(t) = E_W <g(u), g(v)> = sum_r b_r t^r (b_r >= 0, sum b_r = 1, by a Hermite
expansion after the first layer) and M_r(Q) = int u^{(x)r} dQ, the ensemble risk of any rule is
m_n^2 sum_r b_r ||M_r(Q) - M_r(sigma)||_F^2; for even r = 2s and positive weights the off-diagonal terms
(u_i . u_j)^{2s} are nonnegative, so risk >= (m_n^2 / (2N)) sum_{s: tau_2s <= 1/(2N)} b_2s, tau_2s = E (U . V)^{2s} =
(2s - 1)!! / (n (n + 2) ... (n + 2s - 2)). At n = 256: tau_4 = 4.5e-5, tau_6 = 8.7e-7, tau_8 = 2.3e-8, so at N = 2^16
(1/(2N) = 7.6e-6) every power from degree 6 on is paid in full; my Gegenbauer version (T4) gives the same thresholds.
E1.2 (T7, now PROVEN [A], annealed, exact). E Per_gamma{z_{l,i} > 0} = (1 - 2^-n)^{l-1} / sqrt(2 pi), dead-region
interfaces included (the literal zero set of a deep pre-activation contains open dead cones; the gate-set perimeter is
the right object); summed over the net ~ n L / sqrt(2 pi). P(gate history through l changes) ~
(sqrt 2 n / pi)(sum_{j<l} beta_n^j) sqrt(delta), beta_n = 1 - (n + 1) 2^-n (fixed n, l; delta to 0).
E1.3 (T8, now PROVEN [A] for a fixed map with transversal facets). F(delta) := V NS(delta) = D delta -
(2 J_kink / (3 sqrt pi)) delta^{3/2} + o(delta^{3/2}), D = sum_k k H_k, J_kink = sum over facets of the Gaussian
surface integral of ||[J_f]||_F^2; Hermite tail sum_{k>t} H_k = O(J_kink t^{-3/2}). Annealed: E sum_k k H_k = n
exactly, so NS_ann(delta) <= (n / E V) delta with equality as delta goes to 0. Unused gates carry no jump: gate
counts do not price output effects.
E1.4 (correction to how T6 is used; [A]). Gaussian Hermite degree and spherical harmonic degree differ: the homogeneous
extension of a degree-d harmonic occupies Hermite degrees d, d + 2, ..., so sum_{d>t} E_d <= (m_n^2 / n) T_H(t) one way
only. T6 is stated with spherical pairs (exact Funk-Hecke) and stands; the Gaussian ("gauss") NS curves of noise.py
are Hermite statements and bound spherical tails only from above.
E1.5 (new [A]). (a) Bounded independence fails in the worst case: a 127-wise independent law on R^256 (Gaussian
magnitudes, sign parity constraint on 128 coordinates) and a width-256 positively homogeneous ReLU net whose mean it
gets wrong by a factor 2 (PROVEN). (b) Smoothness tail: sum_d d(d + n - 2) a_d = m_n^2 (n - 1), so
sum_{d>t} a_d <= m_n^2 (n - 1) / ((t + 1)(t + n - 1)) (PROVEN; informative only for t of order 30 or more at n = 256).
(c) Kerdock aliasing for even d: B_d = 1/(Kn) + ((n - 1)/(Kn)) P_d(0) + ((K - 1)/K) P_d(n^{-1/2}), K = n/2 + 1
(B_2 = B_4 = 0). (d) In the infinite-width kernel model, degrees 1-2 carry O(1/L) of the angular variance and the
even tail half of it (so the ~4x ceiling is a mean-field statement); finite width is different (ladder: degrees <= 2
carry 0.4-0.75). (e) CONJECTURE [A]: Kerdock blocks give N E err^2 / V in [0.33, 0.50] on fresh 256 x 32 nets.

## E2. Audit and additions after gpt-6-astra round 2 (read ~14:50Z; coprover/astra_r2_answer.md)
E2.1 Audit of v1 (accepted). T1-T3, T6 (identity and inequalities; "pins" overstated: the lower bound can be zero) and
T9 (identity) correct. T4 correct per degree; the tail form must sum every qualifying degree; for antipodal sets the
stronger ceiling A/(2 tail) needs M |min P_d| = o(1), otherwise A/tail; power and Gegenbauer coefficients are not
interchangeable (t^r = sum_d c_{r,d} P_d with c_{r,d} >= 0). T5 WRONG as a fixed-n, eps -> 0 statement: the tail in its
lower bound depends on m and vanishes as m grows; it holds at polynomial budgets (E2.3) and log2 m is a support-index
length, not runtime randomness. T7 first layer correct; later zero sets contain open dead regions (round 1); the
small-noise asymptotic does not by itself give near-one disagreement (the measurement does). T8 constants corrected:
(1/2) E||J(X) - J(Y)||_F^2 ~ (J_kink / sqrt pi) sqrt(delta) and sum_{k>K} H_k ~ (J_kink / (3 pi)) K^{-3/2}; my 0.8 nL and
the crossover K ~ L^2 remain HEURISTIC. T10 wrong as exact redundancy (|z_i|, relu(z_i), z_i |z_i|, |h_1|^2 have higher
harmonics); the measured near-redundancy stands as HEURISTIC. T11 needs an explicit capacity hypothesis; "known PRGs
cover depth-1 structure only" and "none bears on the average-case problem" are too strong (a valid worst-case PRG with
the right normalisation would also give an average-case bound). The spectral proxies in ladder_table.py carry small
systematic aliasing errors (e.g. |e2_hat - e2| <= 3/(n + 1) x even>=4 share), negligible against replicate noise.
E2.2 (exponents at fixed width; PROVEN [A]). For positive weight-independent rules, sum_{r > D, r even} b_r ~ C D^{-3/2}
(kink tail of the downstream map of first-layer pre-activations) and tau_d ~ C_n d^{-(n-1)/2} give
risk >= c N^{-1 - 3/(n-1)} for large N, so p <= 1 + 3/(n - 1) (1.0118 at n = 256); stratifying the sphere into N
equal cells attains N^{-1 - 2/(n-1)} (1.0078 at n = 256). So "exponent exactly 1" is false at fixed n, but the black-box
exponent lies in [1 + 2/(n-1), 1 + 3/(n-1)]: indistinguishable from 1 at n = 256. A fitted slope over 2^8..2^18 is not
constrained by these asymptotic bounds. Unions of R rotated copies of a FIXED design have exponent exactly 1.
Thresholds at n = 256 (power form): even degrees >= 4 counted for N <= 11,008, >= 6 for N <= 572,416.
E2.3 (the finite-width mechanism; PROVEN [A]). For unit inputs at inner product t, with norms r_j, r'_j and cosine c_j
of the layer-j states: 1 - k_j(t) = [1 - B_j(t)] + T_j(t), B_j = E[r_j r'_j] (norm mismatch), T_j = B_j - k_j
(direction mismatch). Bounds: 0 <= 1 - a_n(c) <= (2/n)(1 - c) per layer for the norm factor; T_j <= 9 pi^2/(2 j^2);
B_j - B_{j+1} <= (2/n) T_j. Hence V_L <= n - m_n^2 + (m_n^2/n)(2 + 3 sqrt2 pi) + 9 pi^2 m_n^2/(2 L^2) = O(1 + n/L^2)
uniformly, and as n, L -> infinity with L/sqrt n -> infinity, n (1 - k_{n,L}(t)) -> S(t) = sum_{j>=0} eta(K_j(t)),
eta(c) = 3/2 - E[Z_+^2 Z'_+^2], K_j = kappa^{(j)}; E V -> S(0) + 1/2 with S(0) = 10.6505 (numerical evaluation of the
proven series). The finite-width variance is made by persistent differences in ACTIVATION NORMS accumulated over the
first layers (each O(1/n), summing to O(1)); taking width to infinity first removes exactly this term, which is why
the mean-field picture (degrees 1-2 share O(1/L)) does not describe finite width.
E2.4 (limits of the spectrum and of design gains; PROVEN formulas [A], values numerical). lambda_d -> A_d (the power
coefficients of A(t) = S(0) - S(t)); limiting shares: degree 1 0.2906, degree 2 0.2080, odd 0.5704, even 0.4296,
even >= 4 0.2215, even >= 6 0.1661; S(-1) = S(0) + 3/2 (parity). Gains over plain MC tend to (S(0) + 1/2)/(S(0) - A_1 -
A_2) = 2.09 (simplex), (S(0) + 1/2)/(S(0) - 3/2 - 2 A_2) = 2.36 (cross-polytope), (S(0) + 1/2)/(S(0) - 3/2 - 2 A_2 - 2 A_4)
= 3.15 (Kerdock, along dimensions with complete real MUBs). No positive oblivious rule has a gain diverging with n at
budgets N <= C n^p: liminf N R_N >= sum_{even r >= d} A_r > 0 for even d > 2p: Theta(1/N) in the joint wide/deep limit.
Measured at 256 x 32 (medians, 5 nets): odd 0.56, even 0.43, degrees <= 2 0.47, even >= 4 0.22, even >= 6 0.17;
simplex 1.93, cross-polytope 2.39, Kerdock 3.04. The theory accounts for the measured spectrum.
E2.5 (degree 1 = mean Jacobian; PROVEN [A]). E_1(W) = (m_n^2/n) ||E_X J_f(X)||_F^2.
E2.6 (the noise slope; PROVEN [A]). NS'_ann(0) = n / E V -> n/11.15 along L = alpha n, i.e. ~0.72 L at L = n/8: my
"1 + L/2" description of the per-layer slope is not the asymptotic law. CONJECTURE [A]: at 512 x 64, degrees <= 2 share
0.45-0.60, odd 0.55-0.59, simplex gain 1.8-2.6, cross-polytope 2.0-2.8, ensemble noise slope 35-45.
E2.7 (white-box; [A]). Signed permutations of a Kerdock set keep its flat coordinate pattern: for f = relu, the aligned
antipodal MUB rule estimates 1/2 where the Gaussian mean is 1/sqrt(2 pi) (PROVEN): the bias comes from the flat
majority of the design, not from a few axis points. W-dependent frames escape the oblivious bound; scrambling with
jointly uniform points keeps them unbiased; for fixed n they give o(1/N) under standard scrambling hypotheses with no
dimension-uniform rate. CONJECTURE: polar or SVD alignment alone will not change the exponent at L = alpha n.
E2.8 (open question, [A]). Whether a cheap weight-dependent construction can predict and integrate the persistent
scalar norm fluctuations well enough that the residual angular variance tends to zero, with all costs counted.
Cancelling degrees 1-2 explains a constant gain; exploiting the full norm profile is the plausible route past the
proven oblivious ceiling. [C] note: this is the multilevel prefix-norm idea; with the norm variance made at rate ~1/j^2
per layer j, a prefix of r layers leaves ~1/r of it (consistent with the measured best-prefix residual ~0.9 at r = 1),
and dyadic levels give a gain ~ L / (2 c log^2 L), below 1 at L = 32 and above it only for L of order several hundred
(HEURISTIC).
