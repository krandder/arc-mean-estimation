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
