# Bits-bounds theory v2 (merged with the co-prover; v1 is frozen in coprover/FORMAL_v1_as_written.md)

Lane bits-bounds, 1 November 2026. v1 written 21:07-21:18Z by Claude (frozen, sha dbdcb7f7); v2 written 21:45Z-
after reading gpt-6-astra's round-1 answer and while round 2 ran; the round-2 audit is applied throughout and logged in
section 12; the fresh-session GPT-6 review (review/review_gpt6.md, 16 findings) is applied as v2.1 (list in section 13). Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, MEASURED, HEURISTIC, CONJECTURE. Provenance: [C] Claude,
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
   H = 1/2) above. Where the variance is made (6.6): the frozen log-radius difference of two inputs is a martingale
   whose increments depend on the current angle only (PROVEN, every width); in mean field the share made after layer l
   is ~8.3/(l + 9), width-free [IB]. Cell bits N_l(eps) ~ max(0, (d_l/p) log2(D_l(1)/eps^2)) (HEURISTIC; a
   high-resolution law whose dimension grows with resolution for an exponential spectrum [r4-A]; registered test:
   it separates many-bit from zero-bit cuts, 77/77, but resolved counts only within a factor ~2, 5/13 within 2 bits).
6. Lower bounds (section 7). (a) Forward-only cell sweeps: log2 M >= R_rho(eps^2 V) (rate-distortion); averaged over
   futures, the forward-only/two-sided separation in cell count is unbounded as D -> 0 (PROVEN in the class under
   angular source hypotheses) [C, corrected by r2-A]. (b) Stratified upper bound for merges: M past-chosen references with
   exact cell statistics have future-averaged error sum_k P_k^2 E|Rbar_k|^2 + cross terms <= max_k P_k D + cross terms
   (PROVEN identity and upper bound; MEASURED per-net bias ~ D/M in the rough regime) [C]. This is an upper bound, not a
   lower bound: residual means can cancel. (c) Point-evaluation bounds: linear point rules (all merges) have
   future-averaged error equal to a kernel discrepancy under the exact finite-width kernel, whose cubic singularity is
   proven (PROVEN identity); the rate error^2 >= c M^{-1-3/d} is a CONJECTURE until a kernel-quadrature theorem with
   checked spectral hypotheses is applied; adaptive point methods error^2 >= c M^{-1-2H/d} under a Gaussian surrogate
   (G), which does not describe adaptive queries to actual finite-width nets [C]. (d) Query access with unknown common
   bias: Theta(min(2^N, eps^{-2})) [A]. (e) Cost of a specified dense closure implementation: n^{K-1} passes for order
   K, so at fixed eps that implementation is dearer than MC once n^{K-1} > eps^{-2}; this is not a lower bound for
   the closure class [C].
7. Upper bounds (section 8). Multi-reference merge samplers: two-level gains over the one-reference sampler only at
   L >= n (MEASURED, E3); full multilevel with several reference trajectories (F1, Amendment 1). Deterministic merged
   estimates have bias ~ D(M)/M but need the cell statistics, a depth-l problem (the forward bits).
8. Hash (section 9). True (with stated scope): for point-evaluation methods, beyond the future's linearity scale the
   future is rough on a cloud whose covariance has ~n/l effective directions, and under (G) the deterministic
   advantage is at most M^{2H/d} (PROVEN UNDER (G)); at ARC's 256 x 32 our k-means construction with 256 cells does
   not reach eps^2 = 0.1 at the cuts l = 8, 16, 24 (MEASURED). False: "k*-collapse makes a hash" (the count is d_l ~ n/l and rho_l, not k*); "the final layers are
   hard" (they are the easiest: N -> 0); "a hash is hard to average" (a random hash with a known ensemble mean is easy
   [C+A]; it is hard only with an unknown common bias and point access [A]); "nothing beats sampling" (the multilevel
   sampler beats plain MC; whether anything beats the best multilevel sampler is open).
9. Bottleneck (section 11): averaging methods (closures), and adaptive point methods on actual nets, evade every
   bound above; a lower bound for them at L = alpha n is C4 = a restricted C0*. For the cleanest closure, the exact
   single-Gaussian recursion: an unconditional 1/n floor for one Gaussianisation step; a full annealed 1/n floor at
   fixed alpha and large n (so a bounded annealed gain at its own cost) PROVEN UNDER a one-layer radius hypothesis
   (H_R) [r3-A]; MEASURED: its median gain over MC at its matrix-product cost is 3.26 at 128 x 128 and 0.87, 1.02 at
   192 x 192, 256 x 256 (registered Amendments 3-4; moderate evidence that the gain has peaked).

## 1. Setting and notation
Width n, depth L, W_l iid N(0, 2/n), no bias, x ~ N(0, I_n); h_l = relu(W_l h_{l-1}); a = h_L. Cut at layer l:
cloud P_l = law of h_l(x); future g_l = T_L o ... o T_{l+1}, T_j(h) = relu(W_j h); mu = E_{P_l} g_l; g_l positively
1-homogeneous, piecewise linear; J_l(h) the frozen-gate matrix of h's trajectory, so g_l(h) = J_l(h) h; L' = L - l.
kappa(t) = (sqrt(1 - t^2) + (pi - arccos t) t)/pi. Unit inputs: A(U) = h_L(U), V_ang = tr Var_U A; radius exact by
homogeneity (mu = m_n E A, m_n = E|x|) [A 5.1].
Criteria (review finding 9). Four different quantities appear and are kept apart: (i) the per-net normalised error
|est - mu|^2 / V(W); (ii) its median over nets; (iii) the annealed ratio E_W |est - mu|^2 / E_W V(W); (iv) absolute
annealed distortions such as E_{W>l} D_l(Q), compared with a deterministic budget D. The measurements use unit inputs and
V_ang; for Gaussian inputs V = m_n^2 V_ang + (n - m_n^2) E|A(U)|^2, and radius-exact MC has per-sample variance
m_n^2 V_ang. The rate-distortion statements use a fixed budget D, not a future-dependent V.

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
Definition 4.1 (MPS) [C, corrected after review]. State: a finite signed combination nu_l of finitely described
measures (Dirac masses, Gaussians, cone-restricted Gaussians); update nu_l = C_l(T_l # nu_{l-1}) with a closure C_l
(identity when exact; splits and merges are closures); estimate = mean of nu_L. Forward-only if C_l depends on W_{<=l}
only. Particle methods, the multilevel sampler (its merge delta_h -> delta_{|h| c/|c|} is a closure), Gaussian closures
and mixtures, branch-and-bound and cone enumeration are MPS. A truncated cumulant list is not a measure and does not by
itself define a push-forward; cumulant propagation is an MPS only through a specified measure-valued reconstruction
(for example a Gaussian or Edgeworth-type density), and the results below are not applied to it otherwise.
Theorem 4.2 (telescoping; PROVEN UNDER integrability of every pairing) [C]. est - mu = <nu_0 - gamma, g_0> +
sum_l <nu_l - T_l # nu_{l-1}, g_l>.
Lemma 4.3 (Euler residual; PROVEN for a nonzero reference whose trajectory avoids gate boundaries, or with a fixed
boundary convention) [C; R's exact pathwise identity 4.2 is the same fact]. g_l(h) - [g_l(c) + J_l(c)
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
Theorem 5.1 (one future layer, exact at every width; PROVEN for nonzero h, c) [C]. E_W |relu(W h) - D(c) W h|^2 =
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
Proposition 5.3 (exact finite-width annealed chain; PROVEN; the cubic coefficient below for n >= 2, fixed finite t,
phi -> 0) [C]. Given the Gram matrix G of (h, c, v), the next
layer's rows are independent of the past, so the triples (w.h, w.c, w.v) are iid N(0, (2/n) G) over units and
(h', c', v') = (relu(z_h), relu(z_c), 1{z_c > 0} z_v): an exact Markov chain in the 3 x 3 Gram matrix, O(n) per layer
(the gram-chain lane's argument with a tangent-type replica). Checked against nets with random futures (medians within
15%). Finite-width cubic coefficient (PROVEN, r2-A): E|h_t - v_t|^2 = (4/(3 pi)) S_{n,t} phi^3 + o(phi^3) for unit
initial vectors, S_{n,t} = sum_{j<t} (1 - 2^{1-n})^j, so there is no positive t/n correction (only exponentially small
rank-collapse terms). CORRECTION to v1/v2-draft: lib/chain3.py reports E[|h_t - v_t|^2 / |h_t|^2] (normalised by the
output norm, with floors), a different observable; its 1.7-3.3x excess over the mean field at n = 64-128 is an
inverse-norm effect (regularised expansion 1 + (5t + 1)/n [r2-A]; the unregularised ratio has no finite expectation
because h_t = 0 with v_t != 0 has positive probability). Astra's chain with the scale kept gives raw/MF = 0.988, 0.979,
1.001 at n = 64, 128, 1024 (L' = 16, phi = 0.01). The registered P2 compares like with like in normalisation (nets and chain both
output-normalised), but the chain is not an exact benchmark at the smallest angles: its Cholesky jitter leaves a
residual of about 1.6e-12 at phi = 0 (n = 32, t = 16; review finding 8), and the output floors act after different
rescalings in the chain and in the nets; part of P2's miss is therefore numerical, not only the inverse-norm effect.
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
6.4 Measured cell bits (k-means references from the past; the merge type per cell, frozen or radial, is chosen with
the future on the fit split, so "best" is two-sided in that choice; the bit counts interpolate log-linearly between grid
values of M and take the better of the two M = 1 merges on the test split; results/posthoc.md section 3; medians over
nets; all statements are for this construction and these cuts).
- ARC's 256 x 32: more than 8 bits (256 cells do not reach eps^2 = 0.1) at l = 8, 16, 24; 6.8 bits at l = 28.
- L = n/2 (64 x 32, 128 x 64, 256 x 128): > 8 bits at l = L/4; at L/2, 3.4 bits (128 x 64) and 2.1 bits (256 x 128) at
  eps^2 = 0.1, > 8 bits at eps^2 = 0.03.
- L = n (32, 64, 128, 256): at L/2, > 8, > 8, 6.1, 0.8 bits at eps^2 = 0.01 (falling with width); at 3L/4 and 7L/8,
  0 bits at eps^2 = 0.1 and at most 4 bits at eps^2 = 0.01 (32 x 32: 4.0 and 1.7).
- L = 4n (32 x 128): 0-5 bits everywhere.
- One radial merge at absolute layer l leaves (3-9)/l of the variance (e.g. 0.047 at l = 64 of 256 x 256, 0.074 at
  l = 64 of 128 x 128, 0.32 at l = 16 of 64 x 64): the residual depends mainly on the absolute depth.
- Decay of D_best(M) with M for this construction: exponent gamma 0.01-0.2 in the rough regime, 0.3-1.5 in the smooth
  one; 3/gamma is about twice PR in the smooth regime (results/posthoc.md section 2). PR is a covariance participation
  ratio, not the source dimension d of section 7, and the exponent of a suboptimal construction does not bound the
  optimal exponent in either direction.
6.5 Depth regimes (HEURISTIC from 6.2-6.4). At L = alpha n and l = lambda L: PR ~ 1/(alpha lambda) + 1.4 and
rho ~ 3.8 (1 - lambda)/lambda, both independent of n: the bits that matter at a fixed relative depth do not grow with
width. But the variance is created in the first O(1) layers (input-bits lane: C_L = 5.5, 7.2, 8.6 of C_inf = 10.65 at
L = 8, 16, 32), where d ~ n/l is large and the remaining future is long and rough (rho ~ 3.8 L/l). Bits are few where
variance is not made, and many where it is.

6.6 The bits at layer l as one formula (v2.2, written 23:12-23:21Z on 1 November; the variance profile is the
input-bits lane's [IB], outbox/input-bits-2026-10-31.md section 2.2; the combination with the cloud dimension and the
cell exponent is new here).
(v2.3, 23:41-23:47Z: rewritten after co-prover round 4, coprover/astra_r4_answer.md; PROVENANCE round 4 lists what
changed.)
(a) PROVEN [C, repaired by r4-A], every width. For unit inputs u, u' with layer-j states at angle theta_j and layer
gains G(h) = |relu(W h)|/|h|, the law of the pair (G(h), G(h')) under a fresh He layer depends on the angle only and
is exchangeable. Freeze the log ratio Z_j = log|h_j(u)| - log|h_j(u')| at its value before the first death (zero
increments afterwards). Then Z is a martingale with conditional increment variance v_n(theta_j) (a function of the
angle only), and Var Z_L = sum_{j<L} E[1{no death before j} v_n(theta_j)] exactly; Z_L equals the unfrozen log
ratio except with probability <= 2 L 2^{-n}. (Conditioning on survival to the final depth instead keeps zero drift
but makes the increment variance depend on the remaining depth [r4-A].) Large n at fixed angle:
v_n = b(theta)/n + O(n^-2), b(theta) = 3 - 2 k2(cos theta), k2(r) = E[z_+^2 z'_+^2] (unit Gaussians, correlation r);
b = 2 theta^2 - (2/3) theta^4 + ... (iterated limit) [C; = [IB]'s (1/2)(5 - B)].
(b) MEAN FIELD [IB, C, r4-A] (deterministic angles cos theta_{j+1} = kappa(cos theta_j), theta_0 = pi/2; the leading
order as n -> inf at fixed depth). The quantity is the variance across inputs of log|h_L(u)|, averaged over weights:
n E_W Var_u log|h_L| -> B_L/2, B_L = sum_{j<L} b(theta_j); B_inf/2 = 10.65 ([IB]: C_inf = 10.65). The share made after
layer l, F_l = (B_inf - B_l)/B_inf, is 0.486, 0.325, 0.197, 0.111, 0.060, 0.031 at l = 8, 16, 32, 64, 128, 256:
about 8.3/(l + 9), asymptotically 8.34/l, independent of width. (v2.2 quoted 10.63, 0.058, 0.029 from a sum truncated
at 4096 layers and the approximation 5.5/(l + 5.5); both corrected.) Extending these to L ~ n needs uniform
finite-width control. Two further approximations, labelled HEURISTIC: the output variance of unit inputs,
V_ang/E|A|^2 ~ 1 - c_L exp(-B_L/(2n)) (log-normal radii), and the normalised one-reference radial distortion
D_R(1) ~ [S_l(phi) + 2(1 - cos psi_L(phi))]/(V_ang/E|A|^2), with phi the reference angle, S_l(phi) the pair's future
sum of b/n and psi_L its output angle. The exact kernel form is rho_{n,t}(phi) = 2(1 - K_{n,t}(cos phi)), a function
of (phi, n, t) [r4-A]. Strict mean field has no linear term (rho ~ phi^2/(1 + z)^2, z = t phi/(3 pi)); the finite-width
radial part adds ~(6 pi/n) phi z/(1 + z), justified in the window 1/phi << t << n [A r2, r4-A], and dominates the
angular part only when t^2 phi/n >> 1. D_R(1) is a normalised one-reference distortion, not literally the future's
variance share: it depends on the reference policy (the scorer uses the RMS angle to the k-means centre, while the
merge uses a member as reference).
(c) MEASURED (POST HOC on the registered E1 nets; results/variance_made.md, results/bits5_posthoc_old.json; both
reproduced by r4-A): V_ang/E|A|^2 from (b) against the 64 nets: configuration medians 0.78-1.06 of the prediction
(0.96-1.06 at n >= 128), per-net ratios within [2/3, 1.5] on 94%. D_R(1) predicted from the measured M = 1 spread:
median measured/predicted 0.95 (10-90%: 0.24, 2.2) over 256 cells; configuration medians 0.57-1.24 except 256 x 256
(0.38). l D_R(1) ranges 0.21-8.6 over the L >= n configurations and cuts, so "(3-9)/l" holds only at the rough cuts.
Decay exponents of the k-means construction over M = 4..256 (empirical, not source dimensions): gamma_R x PR has
median 0.72 (10-90%: 0.29, 1.24) over the 117 cells with theta_median L'/2 > 2 (of which only 55 have L' phi > 3 pi at
M = 1), 1.03 in the 77 cells with 0.5 <= theta_median L'/2 <= 2, and gamma_F x PR/3 = 0.57 in the 62 cells below 0.5.
(d) The formula (HEURISTIC; registered test PREREG Amendment 5). For forward-only cell methods,
    N_l(eps) ~ max(0, (d_l/p) log2(D_l(1)/eps^2)),
with d_l an effective dimension of the layer-l cloud (fitted: ~1.4 PR_l over M = 4..256, PR_l ~ 1.04 n/l + 1.38),
D_l(1) the normalised one-reference distortion of (b), and p the local exponent of the distortion in the cell radius
(~1 in the rough window for radial merges, 2 for radial merges at small angles, 3 for frozen merges). It is a
high-resolution law: under two-sided source regularity and two-sided power distortion it holds up to constants
(r4-A); for a cloud with an exponential (Lyapunov) spectrum, lambda_k ~ exp(-2 beta (k - 1)), beta = l/n, the
dimension itself grows with the resolution, d_sb(r) ~ log(sigma/r)/beta, and optimal quantisation with distance loss
has log(D(M)/sigma) = -sqrt(2 beta log M)(1 + o(1)) [r4-A, PROVEN UNDER the Gaussian model]: the bits grow like
(n/(2l)) ln^2(D_l(1)/eps^2)/ln 2, i.e. quadratically in the log of the precision; at D_l(1)/eps^2 ~ 10 this is within
~15% of (n/l) log2(D_l(1)/eps^2). Agreement with the measured cell bits (rough cells, eps^2 in {0.1, 0.03, 0.01}):
registered (Amendment 5) 82 of 90 pairs, which decomposes into 63/63 pairs where both exceed 8 bits, 14/14 zero-bit
pairs, and 5/13 resolved nonzero counts (there the formula over-predicts by a median factor 1.8); post hoc on the old
nets 249/251, 36/36 and 23/64 [decomposition by r4-A, checked]. So the formula separates the cuts that need many
bits from those that need none, but does not predict the intermediate counts to better than a factor ~2.
(e) PROVEN UNDER a linear minorant and a small-ball hypothesis [C; checked by r4-A as an abstract theorem]. Let the
future-averaged radial-merge distortion of a state h assigned to reference c be |h|^2 rho(phi(h, c)) (it depends on
the radius and the angle only, Prop 4.4), and suppose rho(phi) >= a min(phi, phi_0). Let the radius-weighted
angular law of the cloud satisfy P_w(phi(h, c) <= r) <= K (r/theta)^d for every direction c and every r <= theta,
with theta <= phi_0 and K M >= 1. Then any M past-chosen references with any assignment have
D(M) >= a E|h|^2 (d/(d+1)) theta (K M)^{-1/d}, so reaching
D(M) <= eps^2 V needs log2 M >= d log2( a (E|h|^2/V) (d/(d+1)) theta / eps^2 ) - log2 K. Proof: for any references,
P_w(min_k phi(h, c_k) <= r) <= M K (r/theta)^d, so E_w min_k phi >= int_0^{r*} (1 - M K (r/theta)^d) dr =
(d/(d+1)) r*, r* = theta (M K)^{-1/d}; multiply by a E|h|^2. References and assignments must be measurable from the
past (future-selected assignments break the reduction to a fixed future-averaged distortion). The theorem bounds the
future-averaged pointwise distortion, not the error of an estimated mean. Its hypotheses FAIL globally for the nets
[r4-A]: (i) rho_{n,t}(phi) <= 2(1 - cos phi) <= phi^2 and rho = phi^2 + o(phi^2) at fixed n, t, so no positive linear
minorant holds at small angles; a minorant ~(6 pi/n) phi can hold only on a window of cell radii (see (b)); (ii) the
layer-l angular law has atoms (an input cone with a single active first-layer neuron maps to a coordinate ray, which
keeps positive mass if it survives), so a global small-ball bound fails; it can hold only for a bulk part, with the
exceptional mass accounted for. So (e) is a theorem about an idealised source, and the bits formula (d) is not yet a
lower bound for nets; the measured exponents are an empirical comparison, not an achievability result.
(f) Reading for the hash argument. In the rough window a forward-only cell method with exact cell statistics needs
~2^{N_l(eps)} cells to reach a pointwise distortion eps^2: a table exponential in the cloud's Lyapunov dimension
d_l ~ n/l (and growing faster than any fixed power of 1/eps for an exponential spectrum), which is Kelvin's hash
picture made quantitative, with d_l in place of k*. Comparing 2^{N_l} with eps^{-2} is an idealised enumeration
comparison only: it is not a necessary condition for beating sampling, since a mean estimator can cancel errors,
stratify and sample the residual, and every method's setup must be charged [r4-A]; no separation from the
shared-trajectory multilevel sampler (ideal work O(eps^-2 log^2 L) against O(L eps^-2) for plain sampling) follows.
(g) Cross-lane check (POST HOC, one net; report section 3.6; results/compare_bitacc.json, compare_bitacc_wf.json).
On the bit-accounting lane's ARC net (st.W_layer seed 4000), their learned local codes need 230, 104, 34-52 bits at
l = 4, 8, 16 and settle at the output's own ~19 bits for l >= 24 (nMSE 0.1). The formula with d = PR gives 224, 112,
45; Gaussian water-filling on the measured angular spectrum with a distortion quadratic in the angle gives 276, 157,
56 and 31-22 at l >= 24 (within 1.6x everywhere); with a distortion linear in the angle down to the target, 3-7x
more. The radial merge is a code (cell index plus radius) and a subclass of their local codes; frozen merges keep
the state and are not codes, which is why the smooth layers differ (their output floor).

## 7. Lower bounds
Theorem 7.1 (forward-only cell sweeps; PROVEN) [C]. For any M-cell quantiser computed from W_{<=l} (randomised
independently of W_{>l} allowed: condition on the public randomness), E_{W>l} D_l(Q) >= D_rho(log2 M), the
distortion-rate function of P_l under rho_{L'}(h, c) = E_{W>l} |g_l(h) - m(h; c)|^2; so N_cell^fwd(l, eps) >=
R_rho(eps^2 V). Proof: I(X; X^) <= H(X^) <= log2 M.
Corollary 7.2 (angular version; PROVEN UNDER: the radius-weighted angular law P~ below has a compact regular
d-dimensional support and finite differential entropy, and f_t(theta) >= a min(theta, theta_0)^3) [C, corrected by
r2-A]. The homogeneous distortion has the form
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
Theorem 7.4 (stratified upper bound for merges; PROVEN identity and upper bound) [C]. Past-chosen cells C_k, references c_k and merge
rule, exact cell statistics: the merged estimate's error is e = sum_k P_k Rbar_k, Rbar_k = E[R | C_k], R = A - m, and
over the random future E|e|^2 = sum_k P_k^2 E|Rbar_k|^2 + sum_{k != k'} P_k P_k' E[Rbar_k . Rbar_k'], with
E|Rbar_k|^2 <= D_k (Jensen) and, for the radial merge, E[R(h; c) . R(h'; c')] = |h||h'| times the mixed second
difference kappa(h^.h'^) - kappa(h^.c'^) - kappa(c^.h'^) + kappa(c^.c'^). With equal-mass cells and negligible cross
terms E|e|^2 <= D/M, the error of a stratified sampler with one draw per stratum. This is an upper bound: residual
means can cancel, so it does not say that references cannot do better (that would need a lower bound; Thm 7.5 is the
attempt). MEASURED (POST HOC): per-net bias_best/(D_best/M) has median 0.82 [10-90%: 0.18, 3.8] in the rough regime
(453 cells) and 1.54 [0.27, 8.2] in the smooth regime (315 cells), where a systematic (curvature) part appears: the
measured bias behaves like the stratified figure, in size.
Theorem 7.5 (point-evaluation lower bounds) [C].
(a) Linear point rules, no Gaussian assumption (PROVEN for the identity; the rate is a CONJECTURE until a
kernel-quadrature lower bound is applied with checked hypotheses: equivalence of the kernel's native space on the
source with a Sobolev space of smoothness 3/2 + d/2, a regular source geometry, and the allowed derivative orders;
review finding 2). A rule that uses the future only through its values and finitely many
derivatives at M points chosen from the past, combined with past-chosen weights (every merge estimator of section 5 is
such a rule: radial merges use g(c_k), frozen merges J(c_k)), has future-averaged squared error equal to the squared
kernel discrepancy between P_l and the rule under the exact finite-width back kernel K_{n,L'} (Prop 4.4; only second
moments of the future enter). The angular part of K_{n,L'} has the cubic singularity
k_{n,t}(cos phi) = 1 - phi^2/2 + (S_{n,t}/(3 pi)) phi^3 + o(phi^3), S_{n,t} = sum_{j<t}(1 - 2^{1-n})^j [A r2, (2.4)-(2.5)].
For a source with a density bounded above and below on a d-dimensional regular set, the best M-point rule for a kernel
with such a singularity would have squared error >= c(d) A M^{-1-3/d} (kernel quadrature for Sobolev-type kernels of
smoothness 3/2 + d/2; recalled; a cubic diagonal expansion alone does not supply the needed coercivity). So reference/merge methods gain at most M^{3/d}
over MC from the cubic part alone; a rough (H = 1/2) part of size ~1/n in the kernel, as section 6.3 suggests, would
lower the exponent to 1/d.
(b) Adaptive or nonlinear point methods (PROVEN UNDER (G)). (G): on the cloud's support the future minus its known
mean is a centred Gaussian field whose covariance has an isotropic singular part A |h - h'|^{2H}, the support is
d-dimensional and P_l has a density bounded above and below. Then every algorithm that uses the future only through M
adaptively chosen evaluations of values and finitely many derivatives has average error^2 >= c(d, H) A M^{-1-2H/d}
(average-case IBC for Gaussian measures: adaption does not help and linear rules are optimal; Wasilkowski 1986,
Traub-Wasilkowski-Wozniakowski 1988, Ritter 2000; recalled, hypotheses not checked line by line). (G) is false at
finite width with L' ~ n; (b) is for the surrogate and does not cover adaptive queries to actual finite-width nets, so
closures are not the only class left uncovered (review finding 2).
Bits: log2 M >= [log2(A/(eps^2 V)) - O(1)]/(1 + 2H/d), against log2(1/eps^2) for MC; the deterministic advantage
exponent is 2H/d (3/d smooth, 1/d rough). As eps -> 0 at a fixed net, d -> n - 1 and the exponent tends to 3/(n-1),
the unrestricted lane's partition-cubature exponent [A of that lane].
Proposition 7.6 (query access, unknown common bias; PROVEN) [A]. A table of K values accessible by value queries,
eps <= 1/2: E(mu_hat - mu)^2 <= eps^2 V for every table needs m >= K/[2(1 + eps^2 K)] >= (1/4) min(K, eps^{-2}) queries
(Beta prior on the common bias); sampling without replacement with ceil(K/[1 + eps^2(K - 1)]) queries suffices.
Proposition 7.7 (hybrids: the mean version of the linear-feature separation; PROVEN UNDER q << mu, matching feature
marginals and finite second moments) [C]. For features P with the true law of P X and a surrogate conditional law q of
the complement, est - truth = E_mu[r (dq/dmu - 1)], r = g - E_mu[g | P X], so |est - truth| <= sqrt(E r^2)
sqrt(chi^2(q || mu)) (per coordinate; for vector output the sharp constant uses lambda_max(E r r^T) [A r2]). A two-sided P with residual eps V suppresses the forward model's error
by sqrt(eps V); a past-measurable P captures relevance only in proportion to the cloud variance it captures [R, A 5.4].
Proposition 7.8 (cost of a specified dense closure implementation; cost accounting, not a lower bound) [C, corrected
after review]. The dense implementations used here and by ARC update an n x n covariance with matrix products, n
single-input passes per layer with schoolbook products (n^{omega - 2} with fast ones), and an order-K tensor version
~n^{K-1}. At fixed eps MC needs eps^{-2} passes, so whenever n^{K-1} > eps^{-2} those implementations are dearer than MC
whatever their accuracy. This does not bound the closure class: maintaining a matrix does not by itself require a
matrix product per layer, and other implementations may be cheaper. With measured fixed-order floors (K = 2: about 0.12/n nMSE in the
stationary regime; gains over MC at its own cost 2-8x at widths 32-128, about 1 at 1024), fixed-order closures are
constant-factor methods at their own cost. For depth growing with width at fixed eps, only sweeps with O(n^2 polylog)
work per layer can beat sampling by a growing factor.

## 8. Upper bounds and the comparison with the multilevel sampler
8.1 Two-level merge samplers (registered E3). Level 1 = merge at prefix depth r (cost r/L), level 2 = A - G. All ratios
are ideal propagation-only comparisons: setup, the fit split's prefixes, clustering and reference assignment are not
charged (review finding 6). Headline numbers minimise configuration medians over r (registered P9 minimises per net
first: 0.74 instead of 0.81 at 128 x 128). The one-reference radial sampler of (K5) has ideal ratio 1.06 at ARC's
256 x 32 (no gain), 0.99, 0.80, 0.81, 0.46 at L = n (n = 32, 64, 128, 256) and 0.64 at L = 4n (best prefix depth;
medians); with 256 forward-only references the
residual falls, but level 1 then carries the full variance: 0.73, 0.69, 0.66, 0.42 at L = n, 0.32 at L = 4n (gains
over the one-reference sampler of 1.1-1.4x and 2x), and 2.0-2.2, worse than MC, at 256 x 32; at L = n/2 also worse
than or level with MC.
8.2 Full multilevel with several reference trajectories (registered Amendment 1, F1, on 52 nets: 44 of the evaluation
nets plus 8 new 64 x 256 nets; ideal propagation-only gains over radius-exact MC; best nonempty subset of dyadic levels
chosen on the same split, so optimistic, and plain MC (the empty subset) is not among the options; medians over nets). One random reference
trajectory (the unrestricted lane's sampler): 1.21, 1.41, 1.58, 2.43 at L = n for n = 32, 64, 128, 256 (growing with n,
as its n/log^2 n law predicts); 2.16 and 3.92 at L = 4n (n = 32, 64); 0.99 at ARC's 256 x 32. M reference trajectories
shared by all levels (k-means at the deepest level): best over M = 4-256 is 1.43, 1.46, 1.58, 2.48 at L = n (a gain
over one reference of 1.18, 1.03, 1.0, 1.02: shrinking to nothing as n grows), 3.36 and 5.50 at L = 4n (1.55x and
1.40x), and 0.49-0.65 at ARC's 256 x 32 (worse). In these runs several references helped only where the cloud is
low-dimensional (L >= 4n), and their extra gain did not grow with n at the sizes tested.
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
no piecewise-linear structure, kink or non-uniform input law is used (the values need only be iid with finite variance;
K >= 2; distinct queries; the comparator is T-sample MC with replacement under the annealed criterion). The gain is
largest at small budgets (K at T = 1, since one query of a K-state table gains a factor K over one MC sample) and is at
least 4(K - 1)/K over all budgets; enumeration (T = K) is exact. Separately, a minimax table theorem (Prop 7.6) [A]:
with an unknown common bias and value queries the same table needs Theta(min(2^N, eps^{-2})) queries. So "hash" must
say which model it means.
What survives, precisely.
- S1 (PROVEN UNDER (G) for the bound; MEASURED for the construction). For point-evaluation methods (sampling,
  references, cells, branch-and-bound centres), beyond the future's linearity scale the future is a rough field on a
  cloud whose covariance has ~n/l effective directions; merges with exact cell statistics behave, in measured size, like
  stratified sampling (Thm 7.4 is an upper bound); under (G) the deterministic advantage is at most M^{2H/d} (Thm 7.5).
  At ARC's 256 x 32 our k-means construction with 256 cells does not reach eps^2 = 0.1 at the cuts l = 8, 16, 24.
- S2 (PROVEN in the cell class). Forward-only computations cannot see the future's frame [A 5.4, R Thm 1, K7]; for cells
  this costs an unbounded number of bits as eps -> 0 (Thm 7.3).
What fails, precisely.
- F1. The count is not exp(k*): the past contributes d_l ~ n/l directions, the future the ratio rho_l ~ 3.8 L'/l and
  the exponent H; k* (the future's rank) does not enter the cell count.
- F2. The final layers are the easiest: N_cell -> 0 as l -> L (measured at 7L/8 for L >= n: 0 bits at eps^2 = 0.1, at
  most 1.7 bits at eps^2 = 0.01).
- F3. Hash => hard to average fails for random hashes (Prop 9.1); averaging methods (closures) integrate kinks
  analytically and evade N; their obstacles are a fixed-order bias (K3) and the cost of the dense implementations (Prop 7.8).
- F4. "Nothing beats sampling" fails for plain MC (the multilevel sampler); whether anything beats the best multilevel
  sampler by a growing factor is open (C0*).

## 10. What the four families pay, in one table (HEURISTIC summary of sections 5-9)
| family | pays for | bound or measurement |
|---|---|---|
| MC / RQMC / designs | per-sample variance | designs: gain <= M^{2H/d} (Thm 7.5), ~4x in mean field at depth ~ width (K6) |
| multilevel shared trajectory | per-level residual variances D_r ~ 1/r + n/L^2 | n/log^2 n at L = alpha n (K5, A 3.3) |
| cells, enumeration, branch-and-bound | 2^{N_cell} cells plus cell statistics | Thm 7.1-7.4; N_cell > 8 bits at ARC's 256 x 32 |
| closures, cumulant propagation | non-Gaussianity tested by the future; n^{K-1} passes | bias floor at fixed K (K3); Prop 7.8; exact single-Gaussian recursion: annealed error >= c E V/n for large n under (H_R); median gain 3.26 at n = 128, about 1 at 192-256 (section 11, C4) |

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
which with C_ML <= O(n + n^q log^2 n) closes "no polynomial advantage" for that class.
C4 for the exact single-Gaussian recursion (lib/closure.py: exact Gaussian ReLU moments, moment matching at every
layer, 2n passes at matrix-product cost; round 3, coprover/astra_r3_answer.md, checks logs/check_r3.log):
- PROVEN [r3-A]. (i) E|m_L - mu|^2 = sum_l D_l + 2 sum_{l<k} C_lk exactly, each term a Gaussianisation defect tested
  against the exact future's kernel; the cross terms have no sign. (ii) The future kernel has a radius component
  (a_n^{2(t-1)}/pi)|h||h'|, a_n = E sqrt((2/n) sum (Z_i)_+^2) = 1 - 5/(8n) + O(n^-2), which survives a suffix of
  depth alpha n with the factor e^{-5 alpha/4}. (iii) The first Gaussianisation raises the mean radius by
  E rho_1 = 9/(16 sqrt n) + o(n^-1/2): it discards the third and fourth cumulants of relu(W x), although the first two
  moments are exact. (iv) Unconditional one-defect theorem: Gaussianising once after layer 1 and integrating the true
  suffix exactly gives liminf n E|mu~ - mu|^2 >= (81/(256 pi)) e^{-5 alpha/4} (0.054 at alpha = 1/2, 0.029 at 1).
- PROVEN UNDER (H_R) [r3-A]. (H_R): E_W R(G(T_W # N(m, S))) >= a_n R(N(m, S)) for every m, S, where R is the mean
  radius and G moment matching: Gaussianisation does not lower the mean radius on average over a fresh He layer (the
  pointwise version is false, example (23)). Under (H_R) every later radius defect is >= 0 on average and, at fixed
  alpha and for all large enough n, E_W|m_L - mu|^2 >= c(alpha) E_W V / n, c(alpha) = 81 e^{-5 alpha/4}/(512 pi
  C_V), C_V = 1 + 2 sum_j (1 - c_j) = 13.481, so c = 2.0e-3 at alpha = 1/2 and 1.1e-3 at alpha = 1. At the
  recursion's own cost (2n passes) MC has nMSE 1/(2n), so the recursion's annealed gain over MC (E_W of the squared
  error against E_W V; not a median or per-net gain) is at most 1/(2 c(alpha)), about 470 at alpha = 1: bounded,
  not growing. If (H_R) fails, a faster decline needs later negative radius defects that cancel the first to leading
  order (necessary, not sufficient).
- CHECKED NUMERICALLY [C]: n(1 - a_n) -> 5/8; (E|H|^4 - E|G|^4)/n -> 9/2; sqrt(n) E rho_1 = 0.536, 0.556, 0.561 at
  n = 16, 64, 256 (-> 0.5625); the counterexample's size; the constants (C_V by a stable recurrence for 1 - c_j,
  whose tail constant reaches 9 pi^2/2; review 2, finding 6).
- MEASURED (registered Amendments 3 and 4; results/closure_scores.json, results/closure4_scores.json; POST HOC
  statistics in results/posthoc_closure.md; 76 nets, 48 of them the E1-E3 weight instances, Gaussian inputs).
  Median gain over MC at the matrix-product cost, L = n: 0.38, 0.28, 0.63, 3.26, 0.87, 1.02 at n = 16, 32, 64, 128,
  192, 256 (8 nets to n = 128, 4 beyond); L = n/2: 2.28, 0.59, 0.80, 0.89, 0.40 at n = 16-256. At alpha = 1, B1
  (median nMSE slope -2.05 over 16-128) and B2 (gain growth 8.6x from n = 16 to 128) missed; both hit at
  alpha = 1/2; B3 and B4 (n = 192, 256) hit. POST HOC: the per-net nMSE (geometric mean over nets) falls like
  n^{-1.97 +- 0.35} over n = 16-128 at L = n; over 128-256 the slope is +0.5 +- 1.3 (geometric means 1.5e-3,
  3.6e-3, 1.8e-3 at n = 128, 192, 256), and the n = 192 and 256 means sit 1.9 and 1.7 SE above the extrapolated
  n^{-2} trend. H_peak (the gain peaked near n = 128) is favoured on moderate evidence, not established. Per-net
  gains scatter over two decades (0.15-46 at n >= 128). The squared error is the cross-product (a - mu1).(a - mu2),
  an unbiased numerator: it removes the upward bias of reference sampling, not its noise (relative SE 0.36 and 0.14
  on the two nets with the smallest errors, review 2). Numerics: Phi2 with 48 and 128 quadrature nodes agree to
  1e-14 (relative) on those two nets (results/quadrature_check.jsonl); review 2 found correlations up to 0.999906
  and negative covariance eigenvalues of at most 1.2e-16 (relative) at 256 x 256, seed 103: no material
  instability, though not every numerical cause is excluded. The annealed ratio n E[err^2]/E[V] is 0.21-1.25
  (0.2-1.0 at L = n), two to three decades above the conditional floor, so the floor bounds the gain without saying
  where growth stops; these finite-width values test neither the asymptotic theorem nor (H_R). At the estimated
  implementation cost (an operation count for Phi2 by 48-node quadrature, about 2005 + 2n passes) the configuration
  medians are below 0.4 at every width (single nets reach 5.3).
- Reading: the cleanest averaging method gained at most about 3x up to n = 256 at L = n, and under (H_R) its annealed
  gain is bounded by a constant for large n. C4 for corrected closures (higher order, mixtures, splits) remains open.
C5 (two-sided count). log2 #(future linear regions met by the cloud) ~ d_l log2((n/pi) L' theta_l / d_l). New.

## 12. Measured scorecard and round-2 audit
Registered predictions (PREREG.md; results/prereg_scores.json, results/ml_scores.json, results/gain_scores.json):
| prediction | outcome |
|---|---|
| P1 cubic exponent of the frozen residual in [2.4, 3.6] on >= 80% of cells | missed narrowly: 79% of 169; median slope 2.91 (10-90%: 2.19-3.43) |
| P2 nets' cubic coefficient within [1/3, 3] of the chain's | missed: 47%; the chain's output-normalised mean is inflated at small width (inverse-norm effect, Prop 5.3): net/chain medians 0.06, 0.35, 0.52, 0.77 at n = 32-256, while the nets' coefficients 0.84, 0.68, 0.51, 0.46 approach the mean-field 0.424 as n grows |
| P3 frozen better below L' phi = 0.5, radial better above 5 | hit: 84% of 105 |
| P4 D_F(1) > D_R(1) at L/4 (>= 90%); D_F(16) < D_R(16) at 7L/8 (>= 80%) | missed narrowly on the first clause (89%); second 100% |
| P5 decay exponents in the registered bands | missed: 17 groups pass, 10 fail; ARC's 256 x 32 and L = n/2 at L/4 decay even more slowly (gamma ~ 0.00-0.07), L = 4n faster (0.5-1.6) |
| P6 two-sided cells <= 0.8 x forward-only at M = 64 on >= 60% | missed: 56%; median ratio 0.77 (10-90%: 0.54-0.99) |
| P7 bias <= D/10 for M >= 16 where resolved | hit: 95% of 730 |
| P8 mean-propagation error decreases from L/4 to 7L/8 (>= 80%); <= 0.05 at 7L/8 (>= 75%) | as worded (endpoint decrease) hit: 64 of 64, second clause 100%; the hashed scorer used a stricter reading (non-increasing over all four cuts), under which it is missed (39 of 64, 61%; deep values sit near the 4096-sample noise floor). Disclosed in review finding 7 |
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

## 13. Fresh-session review (GPT-6, review/review_gpt6.md; verdict "major revision", 16 findings) and what changed
1. Thm 7.4 overstated: now an identity plus an upper bound; the "no better than stratified sampling" reading removed.
2. Thm 7.5's rate not established: the rate is now a CONJECTURE pending a kernel-quadrature theorem with checked
   hypotheses; noted that (G) does not cover adaptive queries to actual nets.
3. Prop 7.8 is the cost of a specified implementation, not a class lower bound: restated.
4. D_best is not forward-only (its merge type is chosen with the future); two-sided assignment uses the test outputs
   (a representation oracle): labels changed in 6.4, the scorecard and the report; forward-only statements use F, R,
   rule.
5. Universal claims restricted to the tested construction, cuts, sizes and precision range.
6. E3/F1 ratios labelled ideal propagation-only (setup, prefixes, clustering, assignment uncharged).
7. P8 reported under both readings; under the registered wording it is a hit (main score 3 hits, 8 misses).
8. The chain is not an exact benchmark at the smallest angles (jitter floor ~1.6e-12): P2's interpretation softened.
9. Criteria and the radius conversion stated in section 1.
10. Cumulant truncations are not measures: Def 4.1 restricted.
11. k-means could return labels from before the last centre update: fixed in lib/bb.py after the registered runs
    (kmeans_dirs now recomputes the assignment before returning); the registered results used the hashed version; the
    reviewer's replay shows the size of the effect (one two-sided D_best changes from 0.0422 to 0.0436).
12. F1's "best subset" excluded the empty subset (plain MC): now "best nonempty hierarchy".
13. Hash prose made precise (model, K >= 2, comparator, the gain K at T = 1, the minimax table theorem separate).
14. Cell-bit tables disclosed as interpolated and as using the future-chosen merge type and the test split for M = 1.
15. Several summaries corrected (configuration medians against per-net minima in E3; F1 counts 44 + 8; P5 17/10; bias
    counts 453/315).
16. Hypotheses added (integrability for Thm 4.2; nonzero references and a boundary convention for Lemma 4.3 and Thm 5.1;
    n >= 2, fixed t, phi -> 0 for Prop 5.3; q << mu and matching marginals for Prop 7.7, with the sign est - truth =
    +E[r (dq/dmu - 1)]; Cor 7.2's hypotheses on the radius-weighted angular law).
Also from the review: the main scorer was hashed at 21:34:30Z, after the first outputs existed (the queue started
21:32:31Z) and before I first read any output (21:38Z, via scratch/tables.py); timestamps alone cannot verify the latter.

## 14. Second fresh-session review (GPT-6, review/review2_gpt6.raw; verdict "major revision", 14 findings)
On the closure test, round 3 and the application of the first review; it reproduced every registered score and
quoted statistic. Changes, here and in the report: the closure's peak stated as moderate evidence (post hoc z = 1.9,
1.7 against the extrapolated n^-2 trend) rather than established; "at fixed alpha, large n", "annealed" and "under
(H_R)" carried into every statement of the floor; the cross-product described as an unbiased numerator with its
noise; numerical claims narrowed to the convergence checks made; "actual cost" replaced by "estimated implementation
cost"; C_V recomputed by a stable recurrence (13.481; the value survives, the tail constant is 9 pi^2/2); the closure
population (76 nets, 48 shared with E1-E3) and round 3's chronology (launched before Amendment 3's runs) corrected;
Thm 7.4's equal-mass and cross-term conditions restored in the report; the uncovered classes named (adaptive point
methods on actual nets; corrected closures) and future-selected merges excluded from Thm 7.5(a); the jitter caveat
beside P2; the hash gain as at least 4(K-1)/K (K at T = 1); Prop 7.7's sign in the report; both E3 aggregation
orders reported; applied fixes separated from disclosure-only answers (the k-means fix was not followed by
regenerated results). PREREG Amendment 3 and the hashed scratch/run_closure.py say the cross-product removes "the
samplers' noise"; it removes their upward bias.
