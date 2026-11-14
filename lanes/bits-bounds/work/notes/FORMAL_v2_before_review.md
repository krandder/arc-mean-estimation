# Bits-bounds theory v2 (merged with the co-prover; v1 is frozen in coprover/FORMAL_v1_as_written.md)

Lane bits-bounds, 1 November 2026. v1 written 21:07-21:18Z by Claude (frozen, sha dbdcb7f7); v2 written 21:45Z-
after reading gpt-6-astra's round-1 answer and while round 2 ran; the audit items from round 2 are applied in section
12. Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, MEASURED, HEURISTIC, CONJECTURE. Provenance: [C] Claude,
[A] astra (round 1 unless marked r2), [C+A] both independently, [R] the relevance lane (work/relevance/FORMAL.md),
(K1)-(K11) earlier lanes as listed in coprover/STATEMENT_r1.md. MEASURED items cite the registered runs (PREREG.md,
results/prereg_scores.json); post-hoc analyses are marked POST HOC.

## 0. Claims in one screen

1. Model (section 2). Layer sweeps: p passes, M bits of persistent memory (everything kept counts), public
   randomness, charged work. All four families sit in it [C+A].
2. Information bounds are capped (section 3). Every information lower bound on an unrestricted state is at most the
   weights' description length (n^2 L log(1/eps) bits) [C+A]; the exact forward-only quantity is the quantisation
   error of the mean-query function T(A) [A]; a worst-case INDEX family separates forward-only (Omega(d) bits) from
   future-aware (O(log d) bits) [A]. Per-sample (trajectory) information is the same at every layer of a noiseless
   net [C+A]. So "the bits that matter at layer l" can only bound a representational or access-restricted class, or
   time.
3. Exact identities (section 4). Telescoping defect identity for measure-propagation sweeps [C]; Euler residual
   g(h) - J(c) h = (J(h) - J(c)) h, a sum of frozen-propagated flip vectors [C; R independently].
4. Residual laws (section 5). One layer, exact at every width: frozen (linearised) residual (2|h|^2/pi)(phi - sin phi
   cos phi) ~ (4/(3 pi)) |h|^2 phi^3; radial 2|h|^2(1 - kappa(cos phi)) [C]. L' = t layers, mean field: closed form
   [r2-A], frozen (4t/(3 pi)) phi^3 - (t(t-1)/pi^2) phi^4 + ..., in the scaling limit x = t phi/(3 pi)
   frozen phi^2 [1 + (1+x)^{-2} - 2 (1+x)^{-3}] against radial phi^2/(1+x)^2, crossing at t phi = 3 pi (2^{1/3} - 1)
   = 2.45 [C, closed forms r2-A]. At finite width the raw cubic coefficient is (4/(3 pi)) sum_{j<t} (1 - 2^{1-n})^j,
   i.e. no t/n enhancement [r2-A]. MEASURED on 64 nets: P1-P3.
5. The bits that matter (section 6). Adopted N = the relevance lane's linear-feature count [R]; for the mean only the
   nonlinear part counts (N_>=2) [C+A]. Past: cloud size 3 pi/l and dimension PR = 1.04 n/l + 1.38 (MEASURED, POST
   HOC, R^2 = 0.96; the n/l term is the rank-conditioned Lyapunov count). Future: linearity scale ~2.45/L'; ratio
   rho_l = cloud size / linearity scale ~ 3.8 L'/l; smooth (cubic, H = 3/2) below, rough (merging; gains vary,
   H = 1/2) above. Cell bits N_cell ~ d_l log2 rho_l + (d_l / 2H) log2(1/eps^2) (HEURISTIC; measured profiles in 6.4).
6. Lower bounds (section 7). (a) Forward-only cell sweeps: log2 M >= R_rho(eps^2 V) (rate-distortion); averaged over
   futures, the forward-only/two-sided separation in cell count is unbounded as D -> 0 (PROVEN in the class under
   angular source hypotheses) [C, corrected by r2-A]. (b) References are samples: M past-chosen references with exact
   cell statistics have the future-averaged error of a stratified sampler with one draw per stratum, sum_k P_k^2 D_k +
   cross terms (PROVEN identity; MEASURED bias ~ D/M in the rough regime) [C]. (c) Point-evaluation lower bounds:
   linear point rules (all merges) have future-averaged error equal to a kernel discrepancy under the exact finite-width
   kernel, whose cubic singularity is proven, so error^2 >= c M^{-1-3/d} for a regular d-dimensional source; adaptive
   point methods error^2 >= c M^{-1-2H/d} under a Gaussian surrogate (G) [C]. (d) Query access with unknown common bias:
   Theta(min(2^N, eps^{-2})) [A]. (e) Cost floor: an order-K closure costs n^{K-1} passes, so at fixed eps it loses
   to MC once n^{K-1} > eps^{-2} [C].
7. Upper bounds (section 8). Multi-reference merge samplers: two-level gains over the one-reference sampler only at
   L >= n (MEASURED, E3); full multilevel with several reference trajectories (F1, Amendment 1). Deterministic merged
   estimates have bias ~ D(M)/M but need the cell statistics, a depth-l problem (the forward bits).
8. Hash (section 9). True: for point-evaluation methods, beyond the future's linearity scale the future is rough on a
   cloud of dimension ~n/l, references are samples in disguise, and the deterministic advantage is at most
   M^{2H/d} (PROVEN UNDER (G)); at ARC's 256 x 32 no cell method reaches eps^2 = 0.1 with 256 cells at l <= 24
   (MEASURED). False: "k*-collapse makes a hash" (the count is d_l ~ n/l and rho_l, not k*); "the final layers are
   hard" (they are the easiest: N -> 0); "a hash is hard to average" (a random hash with a known ensemble mean is easy
   [C+A]; it is hard only with an unknown common bias and point access [A]); "nothing beats sampling" (the multilevel
   sampler beats plain MC; whether anything beats the best multilevel sampler is open).
9. Bottleneck (section 11): averaging methods (closures) evade every bound above; a lower bound for them at
   L = alpha n is C4 = a restricted C0*.

## 1. Setting and notation
Width n, depth L, W_l iid N(0, 2/n), no bias, x ~ N(0, I_n); h_l = relu(W_l h_{l-1}); a = h_L. Cut at layer l:
cloud P_l = law of h_l(x); future g_l = T_L o ... o T_{l+1}, T_j(h) = relu(W_j h); mu = E_{P_l} g_l; g_l positively
1-homogeneous, piecewise linear; J_l(h) the frozen-gate matrix of h's trajectory, so g_l(h) = J_l(h) h; L' = L - l.
kappa(t) = (sqrt(1 - t^2) + (pi - arccos t) t)/pi. Unit inputs: A(U) = h_L(U), V_ang = tr Var_U A; radius exact by
homogeneity (mu = m_n E A, m_n = E|x|) [A 5.1].

## 2. The model
Definition 2.1 (layer sweep) [C+A]. p passes, each visiting all layers forward or backward; M bits of persistent memory
between layer visits (particles, cumulants, mixture components, cached weights, cell descriptions and accumulators
all count; retaining part of a weight block after leaving its layer uses memory); a public random tape independent of
the weights; all computation charged (unit: one n x n matrix-vector product, "mv"); output in R^n. Statements about M
reals need a stated precision. "Two-sided" = some backward pass precedes the forward pass that produces the estimate.
Proposition 2.2 (membership; PROVEN by inspection) [C+A]. MC / RQMC / designs: 1 pass, N n numbers, N mv per layer.
Multilevel shared-trajectory sampler (K5): 1 pass (the reference is one more particle; each merged sample keeps one
norm; the reference's norms give the suffix products at the end), O(n + L + n sum_j N_j) numbers [astra uses two passes
or cached weights; one pass suffices as described]. Cumulant propagation of order K (K3): 1 pass, binom(n+K, K) numbers,
n^{O(K)} work per layer [A]. Gaussian closure with S split components: 1 pass, O(S n^2) numbers, O(S n^3) work per
layer; two-sided if the split choice uses a backward relevance summary. Branch-and-bound over input cones: breadth
first, 1 pass per refinement round, O(B n^2 L) numbers for B cells [A]. Exact cone enumeration: 1 pass, one cell per
cone with mass.

## 3. Information bounds and their cap
Theorem 3.1 (streaming to communication; PROVEN, standard) [C+A]. At each cut the state crosses at most 2p - 1 times,
so M >= CC^dist_{2p-1}(eps)/(2p - 1).
Corollary 3.2 (PROVEN from (K2)). One forward pass: M >= (n(n+1)/2) log2(1/eps) - O(1); p passes:
M >= (n log2(1/eps) - O(1))/(2p - 1) (genuine ensemble, fixed (n, l >= 3, L'), eps -> 0).
Proposition 3.3 (the cap; PROVEN) [C+A]. Storing the prefix weights to operator-norm accuracy eta = min{1, delta /
(sqrt(n) l C^{L-1})} costs n^2 l ceil(log2(3 + B n/eta)) bits when every |W| <= B, C = B + 1 [A], and suffices
information-theoretically. Hence no information bound on an unrestricted state exceeds a polynomial in n; a bound of the
form 2^{N} with N a count of the input's bits holds only for a representational class or as a time bound (a
super-linear time lower bound for an explicit distributional problem, out of reach (K6)).
Theorem 3.4 (exact forward-only characterisation; PROVEN) [A]. With T(A) = integral f_B dP_A the mean-query function in
H = L^2(pi; R^n), every forward-only algorithm whose cut state has b bits has annealed error >= D_{2^b}(T(A)) (the
2^b-point quantisation error of the random element T(A)), and a quantiser attaining it gives a b-bit one-way estimator
with unrestricted computation. Uniform version by packing and covering in sup_B |integral f_B d(P - Q)|.
Proposition 3.5 (worst-case INDEX separation; PROVEN) [A]. W_1 = diag(1 + u), u in {0,1}^d, suffix selecting coordinate
j into the first output: constant precision needs > 0.188 d forward-only bits but O(log d) bits after a future-reading
pass. Worst case, not the He ensemble.
Proposition 3.6 (trajectory information is layer-free; PROVEN) [C+A]. For a noiseless net the information about the
output carried by h_l is that of the output itself at every l (Y = g_l(H_l)); with H ~ N(m, C) and an affine future,
the rate is the water-filling over the eigenvalues of C^{1/2} A^T A C^{1/2} [A], yet the mean needs no trajectory bits
(E Y = A m) [A]. So trajectory bits do not bound mean estimation.

## 4. Measure-propagation sweeps and exact identities
Definition 4.1 (MPS) [C]. State: a finite signed combination nu_l of finitely described components (Dirac masses,
Gaussians, cone-restricted Gaussians, or quasi-measures given by truncated cumulants); update nu_l = C_l(T_l # nu_{l-1})
with a closure C_l (identity when exact; splits and merges are closures); estimate = mean of nu_L. Forward-only if C_l
depends on W_{<=l} only. All families of Prop 2.2 are MPS; the multilevel sampler's merge delta_h -> delta_{|h| c/|c|}
is a closure.
Theorem 4.2 (telescoping; PROVEN) [C]. est - mu = <nu_0 - gamma, g_0> + sum_l <nu_l - T_l # nu_{l-1}, g_l>.
Lemma 4.3 (Euler residual; PROVEN) [C; R's exact pathwise identity 4.2 is the same fact]. g_l(h) - [g_l(c) + J_l(c)
(h - c)] = (J_l(h) - J_l(c)) h = sum_{j>l} J_{j->L}(c) r_j, r_j = (D_j(h) - D_j(c)) W_j h_{j-1}, supported on the units
whose gates differ between the two trajectories. Tested exactly (tests/test_bb.py).
Proposition 4.4 (forward-only defects are kernel discrepancies; PROVEN) [C+A]. For a closure independent of W_{>l},
E_{W>l} |<nu - nu', g_l>|^2 = MMD^2 under k(h, h') = |h||h'| kappa_{n,L'}(cos angle(h, h')); in particular
E_B |g_B(h) - g_B(h')|^2 = (|h| - |h'|)^2 + 2|h||h'| [1 - kappa_{n,L'}(cos angle)] [A 5.2]. Also E_B J_B(h)^T J_B(h) = I
for every fixed h != 0 [A 5.3], while the typical |J u|^2 decays: annealed quadratic criteria are carried by rare
expansions.

## 5. Merges and their residual laws
Two merges of a state h into a reference c (both cost one future evaluation per reference when only the mean is
needed, because E[J(c) h 1_cell] = J(c) E[h 1_cell]): frozen m_F(h; c) = J_l(c) h; radial m_R(h; c) = (|h|/|c|) g_l(c).
Theorem 5.1 (one future layer, exact at every width; PROVEN) [C]. E_W |relu(W h) - D(c) W h|^2 =
(2|h|^2/pi)(phi - sin phi cos phi) = (4/(3 pi))|h|^2 phi^3 (1 + O(phi^2)); E_W #(disagreeing gates) = n phi/pi;
E_W |relu(W h) - (|h|/|c|) relu(W c)|^2 = 2|h|^2 (1 - kappa(cos phi)) = |h|^2 (phi^2 - (2/(3 pi)) phi^3 + O(phi^4)).
Checked by Monte Carlo over W (tests/test_bb.py, within 4 SE).
Theorem 5.2 (mean field; PROVEN UNDER the infinite-width limit at fixed L') [C]. The pair (h, c) at equal norms keeps
its norms; cos phi_{j+1} = kappa(cos phi_j); the frozen vector v keeps |v| and v.c; psi_j = angle(h_j, v_j) follows the
recursion of lib/meanfield.py. Frozen residual -> 2(1 - cos psi_{L'}); radial -> 2(1 - cos phi_{L'}).
Closed form (PROVEN UNDER the same limit) [r2-A; checked by Claude to 7 digits]: with s = cos phi, r_j = cos phi_j,
P_t = prod_{j<t} (1 - phi_j/pi), the frozen cosine is q_t = s r_t + (1 - s^2) P_t (equivalently s C_t(s) + (1 - s^2)
C_t'(s), C_t = kappa^{o t}). Hence, at fixed t, D_F = (4t/(3 pi)) phi^3 - (t(t-1)/pi^2) phi^4 + O_t(phi^5); in the
scaling limit phi -> 0 with x = t phi/(3 pi) fixed, D_F = phi^2 [1 + (1+x)^{-2} - 2(1+x)^{-3}] and D_R = phi^2/(1+x)^2,
so the frozen merge is better iff t phi < 3 pi (2^{1/3} - 1) = 2.4497 (2.384 at t = 16 from the exact recursion). For
fixed phi and t -> infinity, D_F -> 2(1 - cos phi), and 1/phi_t - 1/phi - t/(3 pi) grows logarithmically, so the
reciprocal-angle law holds only in the scaling regime [r2-A].
NUMERICAL: frozen/(L' phi^3) = 0.4244 = 4/(3 pi) at L' = 1 and 0.41-0.47 for L' phi small (L' = 4-48).
Proposition 5.3 (exact finite-width annealed chain; PROVEN) [C]. Given the Gram matrix G of (h, c, v), the next
layer's rows are independent of the past, so the triples (w.h, w.c, w.v) are iid N(0, (2/n) G) over units and
(h', c', v') = (relu(z_h), relu(z_c), 1{z_c > 0} z_v): an exact Markov chain in the 3 x 3 Gram matrix, O(n) per layer
(the gram-chain lane's argument with a tangent-type replica). Checked against nets with random futures (medians within
15%). Finite-width cubic coefficient (PROVEN, r2-A): E|h_t - v_t|^2 = (4/(3 pi)) S_{n,t} phi^3 + o(phi^3) for unit
initial vectors, S_{n,t} = sum_{j<t} (1 - 2^{1-n})^j, so there is no positive t/n correction (only exponentially small
rank-collapse terms). CORRECTION to v1/v2-draft: lib/chain3.py reports E[|h_t - v_t|^2 / |h_t|^2] (normalised by the
output norm, with floors), a different observable; its 1.7-3.3x excess over the mean field at n = 64-128 is an
inverse-norm effect (regularised expansion 1 + (5t + 1)/n [r2-A]; the unregularised ratio has no finite expectation
because h_t = 0 with v_t != 0 has positive probability). Astra's chain with the scale kept gives raw/MF = 0.988, 0.979,
1.001 at n = 64, 128, 1024 (L' = 16, phi = 0.01). The registered P2 compares like with like (nets and chain both
output-normalised).
MEASURED (registered P1-P3; results/prereg_scores.json): see section 12 scorecard.

## 6. The bits that matter at layer l
6.1 Definitions. N(l, eps) = the relevance lane's count [R]: the least k such that some k linear features P h_l leave
residual E|g_l(X) - E[g_l(X) | P X]|^2 <= eps V_l (Gaussian convention); forward-only counterpart = the cloud's PCA
count (by [R] Theorem 1 / Cor 1b and [A 5.4], past-measurable features capture relevance in proportion to the cloud
variance they capture). For the mean only the nonlinear part counts: an affine future is integrated exactly from the
mean [C+A], so the relevant count is N_>=2, the features needed for the degree >= 2 part. Cell bits N_cell(l, eps)
= log2 of the least number of cells (references) such that merging each state with its cell's reference (frozen,
radial, or the better per cell) leaves residual <= eps^2 V [C].
6.2 The past (MEASURED, POST HOC). Angular cloud size ~3 pi/l (K8). Dimension: PR = 1.04 (n/l) + 1.38 over 256
(net, layer) points of all nine configurations (64 nets), R^2 = 0.961 (results/posthoc.md). HEURISTIC derivation of the n/l term:
a variance profile lambda_k ~ exp(-2(k-1) l/n), the rank-conditioned Lyapunov contraction (K8, K10), gives
PR = coth(l/n) ~ n/l + l/(3n); the eigenvalue log-slopes match -2 l/n for l/n <~ 0.2 and flatten to -0.4..-0.6 deeper
(the offset ~1.3 is not explained). So Kelvin's "Lyapunov covariances" set the past's count: about n/l directions.
They do not pick out directions for the future: given the past, the future's frame is Haar relative to the cloud's
axes [R Thm 1; A 5.4].
6.3 The future. Linearity scale phi_lin ~ 2.45/L' (Thm 5.2 crossover). Ratio rho_l = theta_l / phi_lin ~ 3.8 L'/l.
Smooth regime (rho < 1, l >~ 0.8 L): residual cubic in the cell size, Hölder exponent H = 3/2. Rough regime (rho > 1):
the future merges directions and states differ mostly through gains. PROVEN UNDER log regularisation and the iterated
limits (width first, then small angle) [r2-A]: one layer's squared-gain covariance gives 5 - B(cos theta) = 4 theta^2 -
(4/3) theta^4 + ..., the per-layer log-gain differences are orthogonal martingale differences, and
Var log(|g(h)|/|g(c)|) ~ (6 pi/n) phi x/(1+x): linear in phi (c = 6 pi) when t phi >> 1, a rough field with
H = 1/2. In the window 1/phi << t << n the radial residual is ~ (3 pi/t)^2 + (6 pi/n) phi (PROVEN UNDER uniform moment
control) [r2-A]: remaining angle plus gains; gains dominate only when phi >> n/t^2.
6.4 Measured cell bits (forward-only references; results/posthoc.md section 3; medians over nets).
- ARC's 256 x 32: more than 8 bits (256 cells do not reach eps^2 = 0.1) at l = 8, 16, 24; 6.8 bits at l = 28.
- L = n/2 (64 x 32, 128 x 64, 256 x 128): > 8 bits at l = L/4; at L/2, 3.4 bits (128 x 64) and 2.1 bits (256 x 128) at
  eps^2 = 0.1, > 8 bits at eps^2 = 0.03.
- L = n (32, 64, 128, 256): at L/2, > 8, > 8, 6.1, 0.8 bits at eps^2 = 0.01 (falling with width); 0-4 bits at 3L/4
  and 7L/8.
- L = 4n (32 x 128): 0-5 bits everywhere.
- One radial merge at absolute layer l leaves (3-9)/l of the variance (e.g. 0.047 at l = 64 of 256 x 256, 0.074 at
  l = 64 of 128 x 128, 0.32 at l = 16 of 64 x 64): the residual depends mainly on the absolute depth.
- Decay of D_best(M) with M: exponent gamma 0.01-0.2 in the rough regime, 0.3-1.5 in the smooth one; 3/gamma is about
  twice PR in the smooth regime (results/posthoc.md section 2).
6.5 Depth regimes (HEURISTIC from 6.2-6.4). At L = alpha n and l = lambda L: PR ~ 1/(alpha lambda) + 1.4 and
rho ~ 3.8 (1 - lambda)/lambda, both independent of n: the bits that matter at a fixed relative depth do not grow with
width. But the variance is created in the first O(1) layers (input-bits lane: C_L = 5.5, 7.2, 8.6 of C_inf = 10.65 at
L = 8, 16, 32), where d ~ n/l is large and the remaining future is long and rough (rho ~ 3.8 L/l). Bits are few where
variance is not made, and many where it is.

## 7. Lower bounds
Theorem 7.1 (forward-only cell sweeps; PROVEN) [C]. For any M-cell quantiser computed from W_{<=l} (randomised
independently of W_{>l} allowed: condition on the public randomness), E_{W>l} D_l(Q) >= D_rho(log2 M), the
distortion-rate function of P_l under rho_{L'}(h, c) = E_{W>l} |g_l(h) - m(h; c)|^2; so N_cell^fwd(l, eps) >=
R_rho(eps^2 V). Proof: I(X; X^) <= H(X^) <= log2 M.
Corollary 7.2 (angular version; PROVEN UNDER a compact regular d-dimensional angular support with finite differential
entropy and f_t(theta) >= a min(theta, theta_0)^3) [C, corrected by r2-A]. The homogeneous distortion has the form
rho(H, c) = R^2 f_t(angle(U, c)) (H = R U), so for a fixed codebook the assignment depends on U only and the problem is
angular quantisation under the radius-weighted law P~(du) = E[R^2 | U = u] P_U(du)/E R^2; then
log2 M >= (d/3) log2(E R^2/D) + O(1), d an actual source dimension (not the covariance participation ratio). v1's
Euclidean version was wrong: h = 2c has zero residual.
Theorem 7.3 (forward-only / two-sided separation in the cell class, averaged over futures; PROVEN UNDER the
hypotheses of Cor 7.2) [C, corrected by r2-A]. Fix a prefix and average over iid He suffixes. Every future-blind
M-reference policy has expected frozen distortion bounded below as in Cor 7.2, so its cell count diverges as D -> 0,
while a future-adaptive policy can use the at most 2^{n t} future gate regions and has zero frozen residual. The
separation in representation cell count is unbounded at high precision (also after averaging over prefixes on any
positive-probability set with uniform source bounds). v1 stated it for a fixed net, which is wrong: for one fixed net
a "past-measurable" policy may be the constant codebook that happens to be optimal. Two caveats [r2-A]: this is a
representation statement, not a mean-estimation separation (cancellations in E[g - m_Q], and exact conditional means
make every partition mean-exact), and constructing and integrating the future's regions is not free.
Theorem 7.4 (references are samples; PROVEN identity and bound) [C]. Past-chosen cells C_k, references c_k and merge
rule, exact cell statistics: the merged estimate's error is e = sum_k P_k Rbar_k, Rbar_k = E[R | C_k], R = A - m, and
over the random future E|e|^2 = sum_k P_k^2 E|Rbar_k|^2 + sum_{k != k'} P_k P_k' E[Rbar_k . Rbar_k'], with
E|Rbar_k|^2 <= D_k (Jensen) and, for the radial merge, E[R(h; c) . R(h'; c')] = |h||h'| times the mixed second
difference kappa(h^.h'^) - kappa(h^.c'^) - kappa(c^.h'^) + kappa(c^.c'^). With equal-mass cells and negligible cross
terms E|e|^2 <= D/M: M deterministic references average the within-cell (rough) part no better than a stratified
sampler with one draw per stratum. MEASURED (POST HOC): per-net bias_best/(D_best/M) has median 0.80 [10-90%: 0.17,
3.6] in the rough regime (414 cells) and 1.43 [0.23, 8.2] in the smooth regime (282 cells), where a systematic
(curvature) part appears.
Theorem 7.5 (point-evaluation lower bounds) [C].
(a) Linear point rules, no Gaussian assumption (PROVEN for the identity; the rate PROVEN UNDER source regularity and a
recalled kernel-quadrature lower bound). A rule that uses the future only through its values and finitely many
derivatives at M points chosen from the past, combined with past-chosen weights (every merge estimator of section 5 is
such a rule: radial merges use g(c_k), frozen merges J(c_k)), has future-averaged squared error equal to the squared
kernel discrepancy between P_l and the rule under the exact finite-width back kernel K_{n,L'} (Prop 4.4; only second
moments of the future enter). The angular part of K_{n,L'} has the cubic singularity
k_{n,t}(cos phi) = 1 - phi^2/2 + (S_{n,t}/(3 pi)) phi^3 + o(phi^3), S_{n,t} = sum_{j<t}(1 - 2^{1-n})^j [A r2, (2.4)-(2.5)].
For a source with a density bounded above and below on a d-dimensional regular set, the best M-point rule for a kernel
with such a singularity has squared error >= c(d) A M^{-1-3/d} (kernel quadrature for Sobolev-type kernels of
smoothness 3/2 + d/2; recalled, hypotheses not checked line by line). So reference/merge methods gain at most M^{3/d}
over MC from the cubic part alone; a rough (H = 1/2) part of size ~1/n in the kernel, as section 6.3 suggests, would
lower the exponent to 1/d.
(b) Adaptive or nonlinear point methods (PROVEN UNDER (G)). (G): on the cloud's support the future minus its known
mean is a centred Gaussian field whose covariance has an isotropic singular part A |h - h'|^{2H}, the support is
d-dimensional and P_l has a density bounded above and below. Then every algorithm that uses the future only through M
adaptively chosen evaluations of values and finitely many derivatives has average error^2 >= c(d, H) A M^{-1-2H/d}
(average-case IBC for Gaussian measures: adaption does not help and linear rules are optimal; Wasilkowski 1986,
Traub-Wasilkowski-Wozniakowski 1988, Ritter 2000; recalled, hypotheses not checked line by line). (G) is false at
finite width with L' ~ n; (b) is for the surrogate.
Bits: log2 M >= [log2(A/(eps^2 V)) - O(1)]/(1 + 2H/d), against log2(1/eps^2) for MC; the deterministic advantage
exponent is 2H/d (3/d smooth, 1/d rough). As eps -> 0 at a fixed net, d -> n - 1 and the exponent tends to 3/(n-1),
the unrestricted lane's partition-cubature exponent [A of that lane].
Proposition 7.6 (query access, unknown common bias; PROVEN) [A]. A table of K values accessible by value queries,
eps <= 1/2: E(mu_hat - mu)^2 <= eps^2 V for every table needs m >= K/[2(1 + eps^2 K)] >= (1/4) min(K, eps^{-2}) queries
(Beta prior on the common bias); sampling without replacement with ceil(K/[1 + eps^2(K - 1)]) queries suffices.
Proposition 7.7 (hybrids: the mean version of the linear-feature separation; PROVEN) [C]. For features P with the true
law of P X and a surrogate conditional law q of the complement, error = -E_mu[r (dq/dmu - 1)], r = g - E_mu[g | P X],
so |error| <= sqrt(E r^2) sqrt(chi^2(q || mu)). A two-sided P with residual eps V suppresses the forward model's error
by sqrt(eps V); a past-measurable P captures relevance only in proportion to the cloud variance it captures [R, A 5.4].
Proposition 7.8 (cost floor of state-heavy deduction; PROVEN, cost accounting) [C]. Keeping and updating an n x n matrix
per layer costs at least one matrix product per layer (n^{omega - 2} single-input passes; n with schoolbook); an
order-K closure costs ~n^{K-1} passes. At fixed eps MC needs eps^{-2} passes, so whenever n^{K-1} > eps^{-2} the
closure is dearer than MC whatever its accuracy. With measured fixed-order floors (K = 2: about 0.12/n nMSE in the
stationary regime; gains over MC at its own cost 2-8x at widths 32-128, about 1 at 1024), fixed-order closures are
constant-factor methods at their own cost. For depth growing with width at fixed eps, only sweeps with O(n^2 polylog)
work per layer can beat sampling by a growing factor.

## 8. Upper bounds and the comparison with the multilevel sampler
8.1 Two-level merge samplers (registered E3). Level 1 = merge at prefix depth r (cost r/L), level 2 = A - G. The
one-reference radial sampler of (K5) has ideal ratio 1.06 at ARC's 256 x 32 (no gain), 0.99, 0.80, 0.81, 0.46 at
L = n (n = 32, 64, 128, 256) and 0.64 at L = 4n (best prefix depth; medians); with 256 forward-only references the
residual falls, but level 1 then carries the full variance: 0.73, 0.69, 0.66, 0.42 at L = n, 0.32 at L = 4n (gains
over the one-reference sampler of 1.1-1.4x and 2x), and 2.0-2.2, worse than MC, at 256 x 32; at L = n/2 also worse
than or level with MC.
8.2 Full multilevel with several reference trajectories (registered Amendment 1, F1; ideal gains over radius-exact MC,
best subset of dyadic levels chosen on the same split, so optimistic; medians over nets). One random reference
trajectory (the unrestricted lane's sampler): 1.21, 1.41, 1.58, 2.43 at L = n for n = 32, 64, 128, 256 (growing with n,
as its n/log^2 n law predicts); 2.16 and 3.92 at L = 4n (n = 32, 64); 0.99 at ARC's 256 x 32. M reference trajectories
shared by all levels (k-means at the deepest level): best over M = 4-256 is 1.43, 1.46, 1.58, 2.48 at L = n (a gain
over one reference of 1.18, 1.03, 1.0, 1.02: shrinking to nothing as n grows), 3.36 and 5.50 at L = 4n (1.55x and
1.40x), and 0.49-0.65 at ARC's 256 x 32 (worse). Several references help only where the cloud is low-dimensional
(L >= 4n) and never by a factor that grows with n.
8.3 Deterministic merged estimates. With exact cell statistics the merged estimate's error is ~D(M)/M (Thm 7.4), e.g.
bias_best 6e-5 at 128 x 128, l = 64, M = 256; but the cell statistics E[h_l 1_{C_k}] are a depth-l problem with a
discontinuous readout. Cost: 2^{N_cell} future evaluations plus that forward problem. With a computable baseline and
cost C(M) ~ a M + b eps^{-2} M^{-p}, the optimum is C ~ eps^{-2/(p+1)}: idealised gains eps^{-6/(d+3)} (smooth, p = 3/d)
and eps^{-2/(d+1)} (rough, p = 1/d) over eps^{-2} [r2-A]: powers of the precision, not of the width, and small when d
is large.
8.3a Certificate for forward-only closures (PROVEN UNDER integrability) [r2-A]: by Thm 4.2, Prop 4.4 and Minkowski,
sqrt(E|mu^ - mu|^2) <= sqrt(E MMD^2_{K_L}(nu_0 - gamma)) + sum_l sqrt(E MMD^2_{K_{L-l}}(nu_l - T_l # nu_{l-1})), a valid
aggregate upper bound that does not assume the layer defects are orthogonal.
8.4 Multilevel regimes [A 3.3, PROVEN UNDER H_ML]: no growing gain certified for L < sqrt(n); L/(log^2 L + n/L) for
sqrt(n) < L < n; n/log^2 n at L = alpha n; L/log^2 L for L >> n if H_ML holds.
8.5 Where a deterministic method could beat sampling polynomially (HEURISTIC). It would need few bits where the variance
is made. At L = alpha n the variance is made in the first O(1) layers, where N_cell ~ (n/l) log2(3.8 L/l): no cell
method; a closure over those layers is accurate (l/n small) but must then carry the cloud through a rough future of
length ~L (accumulated non-Gaussianity ~L/n = alpha); the multilevel sampler pays only per-level variances. A
polynomial gain over it would need an averaging method whose error at L = alpha n falls faster than its cost grows
(C4).

## 9. Kelvin's hash argument, revisited
Proposition 9.1 (a random hash with a known ensemble mean is easy to average; PROVEN) [C+A, corrected by r2-A]. Model:
K = 2^N equally likely relevant states; the table values H(b) are iid across b over the ensemble (random weights) with
KNOWN mean m and variance s^2; the criterion is ARC's averaged one. Then the expected within-instance variance is
s^2 (1 - 1/K); after T distinct value queries the Bayes estimator is partial enumeration (observed values plus m for the
rest), with risk (K - T) s^2/K^2, against (K - 1) s^2/(K T) for T-sample MC with replacement: a gain K(K - 1)/(T(K - T)),
at least 4(K - 1)/K, so about 4 (exactly 2 at K = 2, T = 1; v1's "at least 4" was wrong), and 1/x over sampling without
replacement with the plain average (x = T/K). The zero-query prediction m already has normalised error 1/(K - 1)
[A 4.b]. The gain comes from the ensemble prior (iid values with a known mean), not from structure in the function:
the table is a uniformly random function, and no piecewise-linear structure, kink or non-uniform input law is used. With an unknown common bias and value queries the same table needs Theta(min(2^N, eps^{-2})) queries
(Prop 7.6) [A]: a hash is hard exactly when its bias is unknown and the access is by points.
What survives, precisely.
- S1 (PROVEN UNDER (G); MEASURED). For point-evaluation methods (sampling, references, cells, branch-and-bound centres),
  beyond the future's linearity scale the future is a rough field on a cloud of dimension ~n/l; references are samples
  in disguise (Thm 7.4); the deterministic advantage is at most M^{2H/d} (Thm 7.5). At ARC's 256 x 32 no forward-only
  cell set of 256 reaches eps^2 = 0.1 at l <= 24.
- S2 (PROVEN in the cell class). Forward-only computations cannot see the future's frame [A 5.4, R Thm 1, K7]; for cells
  this costs an unbounded number of bits as eps -> 0 (Thm 7.3).
What fails, precisely.
- F1. The count is not exp(k*): the past contributes d_l ~ n/l directions, the future the ratio rho_l ~ 3.8 L'/l and
  the exponent H; k* (the future's rank) does not enter the cell count.
- F2. The final layers are the easiest: N_cell -> 0 as l -> L (measured 0 bits at 7L/8 for L >= n).
- F3. Hash => hard to average fails for random hashes (Prop 9.1); averaging methods (closures) integrate kinks
  analytically and evade N; their obstacle is a fixed-order bias (K3) and the cost floor (Prop 7.8).
- F4. "Nothing beats sampling" fails for plain MC (the multilevel sampler); whether anything beats the best multilevel
  sampler by a growing factor is open (C0*).

## 10. What the four families pay, in one table (HEURISTIC summary of sections 5-9)
| family | pays for | bound or measurement |
|---|---|---|
| MC / RQMC / designs | per-sample variance | designs: gain <= M^{2H/d} (Thm 7.5), ~4x in mean field at depth ~ width (K6) |
| multilevel shared trajectory | per-level residual variances D_r ~ 1/r + n/L^2 | n/log^2 n at L = alpha n (K5, A 3.3) |
| cells, enumeration, branch-and-bound | 2^{N_cell} cells plus cell statistics | Thm 7.1-7.4; N_cell > 8 bits at ARC's 256 x 32 |
| closures, cumulant propagation | non-Gaussianity tested by the future; n^{K-1} passes | bias floor at fixed K (K3); Prop 7.8 |

## 11. Conjecture ledger and bottleneck
C1 (cubic law at finite width): RESOLVED by r2-A. The raw annealed residual has coefficient (4/(3 pi)) S_{n,t}, with no
t/n enhancement; the excess seen in v1's chain numbers was the output-norm normalisation (Prop 5.3).
C2 (decay with references). D_l(M) ~ M^{-3/d} smooth, ~M^{-1/d} rough. PROVEN UNDER a regular d-dimensional source and
comparable variograms (covering upper bound, small-ball lower bound) [r2-A]; which d applies to the nets is not proved:
MEASURED 3/gamma ~ 2 PR in the smooth regime and 1/gamma ~ 1.5-3 PR in the rough one (POST HOC). At a fixed net the
power law cannot hold for all M (future-adaptive frozen cells eventually become exactly linear) [r2-A].
C3 (rough gains): PROVEN in the iterated limit with c = 6 pi (section 6.3) [r2-A]; the extension to t = alpha n needs
additional estimates. MEASURED (registered Amendment 2, results/gain_scores.json): in the rough bins (L' phi >= 3) the
median ratio of the measured second moment of the log-gain difference to (6 pi/n) phi x/(1+x) is 1.02, 1.77, 0.50 at
n = 64, 128, 256 (every width inside the registered band [1/3, 3]; the registered stability clause, < 2x change from
n = 64 to 256, fails narrowly at 2.04x); per-net ratios range 0.4-5.4 but are roughly flat across phi within a net;
POST HOC log-log slope against phi x/(1+x) 0.94, 0.88, 0.75 (median) against the predicted 1. So the law's shape holds
and its constant holds to within a factor of 2-3 at L' = 3L/4 and L/2, with large net-to-net scatter.
C4 (BOTTLENECK; = C0* restricted to sweeps; astra's C_comp). At L = alpha n and eps = n^{-gamma}, every uniform
polynomial-memory, constant-pass sweep reaching the annealed criterion costs at least n^{-o(1)} times the best
shared-trajectory multilevel sampler. Every bound above covers point-evaluation and cell classes; averaging methods
(closures) are the gap. A K-only bias floor cannot hold for a class that contains polynomial Gaussian mixtures
(degenerate components are particles, so such mixtures contain MC) [r2-A]. A sufficient exponent-level target for a
specified uniform closure class [r2-A]: C_closure(n, eps = n^{-q/2}) >= n^{max(1, q) - o(1)} for every fixed q > 0,
which with C_ML <= O(n + n^q log^2 n) closes "no polynomial advantage" for that class. For the single-Gaussian
recursion a positive annealed floor at L = alpha n is plausible (CONJECTURE). Cheapest test: closure biases at widths
16-128 and fixed L/n, bias estimated without the reference sampler's noise by E[(a - mu1).(a - mu2)] = |a - mu|^2 with
two independent unbiased estimates mu1, mu2 [r2-A].
C5 (two-sided count). log2 #(future linear regions met by the cloud) ~ d_l log2((n/pi) L' theta_l / d_l). New.

## 12. Measured scorecard and round-2 audit
Registered predictions (PREREG.md; results/prereg_scores.json, results/ml_scores.json, results/gain_scores.json):
| prediction | outcome |
|---|---|
| P1 cubic exponent of the frozen residual in [2.4, 3.6] on >= 80% of cells | missed narrowly: 79% of 169; median slope 2.91 (10-90%: 2.19-3.43) |
| P2 nets' cubic coefficient within [1/3, 3] of the chain's | missed: 47%; the chain's output-normalised mean is inflated at small width (inverse-norm effect, Prop 5.3): net/chain medians 0.06, 0.35, 0.52, 0.77 at n = 32-256, while the nets' coefficients 0.84, 0.68, 0.51, 0.46 approach the mean-field 0.424 as n grows |
| P3 frozen better below L' phi = 0.5, radial better above 5 | hit: 84% of 105 |
| P4 D_F(1) > D_R(1) at L/4 (>= 90%); D_F(16) < D_R(16) at 7L/8 (>= 80%) | missed narrowly on the first clause (89%); second 100% |
| P5 decay exponents in the registered bands | missed: 17 of 27 groups; ARC's 256 x 32 and L = n/2 at L/4 decay even more slowly (gamma ~ 0.00-0.07), L = 4n faster (0.5-1.6) |
| P6 two-sided cells <= 0.8 x forward-only at M = 64 on >= 60% | missed: 56%; median ratio 0.77 (10-90%: 0.54-0.99) |
| P7 bias <= D/10 for M >= 16 where resolved | hit: 95% of 730 |
| P8 mean-propagation error monotone in l (>= 80%); <= 0.05 at 7L/8 (>= 75%) | missed on monotonicity (61%; deep values sit near the 4096-sample noise floor); second clause 100% |
| P9 one-reference two-level sampler in [0.5, 1.2]; multi-reference below it on >= 70%; gain <= 1.7x on >= 80%; no growth 64 -> 256 | missed on "below it" (50%: multi-reference loses at L <= n/2); other clauses hit (91%, 97%, growth 0.91x) |
| P10 eigenvalue log-slope in [-0.7, -0.15] (>= 90%); PR decreasing in l (>= 80%) | missed narrowly on the first clause (85%; ARC l = 8 flatter, L = 4n deep layers steeper); second 95% |
| P11 at L = n: > 8 bits at L/2 for eps^2 = 0.01 (>= 75%); <= 6 bits at 7L/8 (>= 75%) | missed on the first clause (43%): the bits at L/2 fall with width (> 8, > 8, 6.1, 0.8 bits at n = 32-256); second 100% |
| A1 one-reference multilevel gains in the bands | hit in all seven configurations |
| A2 its gain grows by 1.0-2.0x from n = 32 to 256 at L = n | missed narrowly: 2.01x |
| A3 several reference trajectories do not beat one (>= 75%) | missed: 65% (they beat it by > 1.25x on 35% of nets, at L >= 4n and small n); full dyadic versions worse on 75% |
| G1 rough-gain law within [1/3, 3] at each width, stable within 2x | missed narrowly on stability (2.04x); in band at every width (1.02, 1.77, 0.50) |
Reading: the theory's qualitative claims held (cubic exponent on average, the crossover, references are samples,
merges helping only in the smooth regime, constant-factor multi-reference gains); the misses are quantitative bands set
too narrow, the P2 normalisation problem, and one wrong expectation (P11: the bits at a fixed relative depth fall with
width, because the residual after layer l is about (3-9)/l whatever the width).
Round-2 audit: applied throughout (sections 5-11); verdicts and new results are logged in coprover/PROVENANCE.md.
