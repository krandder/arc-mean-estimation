# arc-update FORMAL v1 (written 04:41-04:54Z, 2 November 2026; frozen and hashed before reading the co-prover's answer)

Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, MEASURED, HEURISTIC, CONJECTURE. "[prior: lane]" marks results
from earlier lanes (outbox reports), with their labels.

## 0. What this document is for

ARC's goal: estimate mu(W) = E_x a_L for a random He-ReLU MLP "mechanistically", matching sampling (error eps^2 Var at
cost O(eps^-2) forward passes, all eps), at depths that grow with width; ARC's instance n = 256, L = 32. Information
bounds are closed (the weights are a short exact description) [prior: cut-rank-ext, bits-bounds]. Unrestricted
running-time lower bounds would be super-linear time lower bounds for an explicit problem [prior: unrestricted]. So a
theorem must live in a computational model. This document defines one that contains ARC's estimators and their natural
extensions, proves what can be proven in it, and isolates the hypotheses that the rest needs, each with a test.

## 1. Setting and the computational model

Nets: width n, depth L, h_0 = x ~ N(0, I_n), h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n), no bias, no noise; output
a = h_L. P_l = law of h_l. For a cut l, t = L - l, the future F_l = (W_{l+1}, ..., W_L) and g_l = g_{F_l}: R^n -> R^n,
g_l(h) = output given h_l = h. g_l is positively homogeneous and piecewise linear. Y = mu(W) = int g_l dP_l for every l.
Errors: E|est - Y|^2 (absolute), nMSE = |est - Y|^2 / V(W), V = tr Var_x a.

Definition 1 (layer-wise estimator). States S_0, ..., S_L with S_l = U_l(S_{l-1}, W_l, side information), output
est = R(S_L). It is forward-only at cut l if S_l is a function of W_1..W_l only (side information independent of F_l);
future-aware otherwise. Every layer-by-layer sweep (ARC's cumulant propagation, Gaussian closures, mixtures, particle
methods, layer-wise codes, breadth-first branch-and-bound) is forward-only at every cut.

Definition 2 (deduction-projection estimator; ARC's "expectation machine" form). A layer-wise estimator together with a
reconstruction S_l -> Q_l, Q_l a finite signed measure on R^n (or a linear functional on a class containing the
functions h -> phi(w . h) and all future maps g_l), with Q_0 = P_0 and est = int h dQ_L. Defects
Delta_l = Q_l - Phi_l Q_{l-1}, Phi_l = push-forward by h -> relu(W_l h).

Definition 3 (order-K moment closure). A deduction-projection estimator whose defects annihilate polynomials of degree
<= K: int p dDelta_l = 0 for deg p <= K ("exact deduction, moment-matching projection"). The family F_K of reachable
models: Gaussians (K = 2), truncated Gram-Charlier / Edgeworth signed measures built from cumulant tensors of orders
<= K (K >= 3), Gaussian mixtures with matched moments, etc. ARC's order-K cumulant propagation is of this form up to
(i) its truncation of the diagram sum (an additional defect) and (ii) its per-variant extras (power cumulants, the
extra trace for odd K, augmentation), which match some moments of order K + 1, K + 2. Its last step is exact for its
model: est_i = int relu(w_i . h) dQ_{L-1}(h), with Q_{L-1} the truncated Gram-Charlier measure of the method's final
cumulants (HEURISTIC identification, to be checked against the code: CHECK-1).

Definition 4 (resolving estimators). Estimators whose state at layer l represents P_l (or a projection) by M cells,
regions, particles or codes, each integrated or propagated exactly (cell/region merging, branch-and-bound, code-law
propagation, gate-pattern mixtures without moment matching). Covered by the bits-bounds lane's rate-distortion bounds.

Cost: one forward pass = 2 n^2 L flops. Comparators: plain MC (nMSE 1/N), radius-exact MC, RQMC (scrambled Sobol),
the Kerdock mutually-unbiased-bases design, the multilevel shared-trajectory sampler B* [prior: unrestricted].

## 2. Theorem A: the structure of forward-only deduction-projection estimators (all PROVEN)

A1 (telescoping) [prior: bits-bounds Thm 4.2]. est - Y = sum_{l=1}^{L} <g_l, Delta_l>, <g, Delta> = int g dDelta.

A2 (exact, orientation-free, Mehler-positive pricing). Let Delta be a past-measurable finite signed measure at layer l
with int |h| d|Delta| < infinity. Then
  E[ |<g_l, Delta>|^2 | W_1..W_l ] = sum_{d >= 0} b_d^{(n,t)} || M_d(Delta) ||_F^2,
  M_d(Delta) = int |h| (h/|h|)^{tensor d} dDelta(h) in Sym^d(R^n),
with b_d^{(n,t)} >= 0 and sum_d b_d^{(n,t)} = 1, at every finite width n and depth t.
Proof. k(h, h') := E_F[g(h) . g(h')]. Rotation invariance of W_{l+1} (iid Gaussian entries, independent of the past)
and positive homogeneity give k(h, h') = |h||h'| kappa(u . u'), u = h/|h|. For unit u, u' with u . u' = s, put
Z = sqrt(n/2) W_{l+1} u, Z' = sqrt(n/2) W_{l+1} u': standard Gaussian vectors with E[Z Z'^T] = s I. Write
g(u) = G(Z), G(z) = g_{l+1}(relu(sqrt(2/n) z)), G in L^2(gamma_n) (criticality gives E|G(Z)|^2 = 1). Mehler's
formula in L^2(gamma_n) with Hermite coefficients G^_alpha (vectors): E[G(Z) . G(Z')] = sum_alpha s^{|alpha|}
|G^_alpha|^2. Averaging over the remaining future, b_d = E sum_{|alpha| = d} |G^_alpha|^2 >= 0, and sum_d b_d =
kappa(1) = E|g(u)|^2 = 1 (exact criticality: E[|relu(Wh)|^2 | h] = |h|^2). Then k(h, h') = sum_d b_d <|h| u^{(d)},
|h'| u'^{(d)}>, and Fubini (absolute convergence: sum_d b_d int int |h||h'| |s|^d d|Delta| d|Delta| <= (int |h|
d|Delta|)^2) gives the formula. QED.
Values: one layer (t = 1): kappa_1(s) = (1/pi)(sqrt(1 - s^2) + (pi - arccos s) s) = 1/pi + s/2 + s^2/(2 pi)
+ s^4/(24 pi) + s^6/(80 pi) + ... (no odd terms beyond s^1). Infinite width, t layers: kappa_t = kappa_1 composed t
times, coefficients by composition (all >= 0). Deep futures: kappa_t(s) -> 1 for s < 1 with 1 - kappa_t(0) ~ 44.4/t^2
[prior: input-bits], so b_0 -> 1 (the radius feature) and the remaining ~44/t^2 of the weight sits at degrees d of
order t^2 (fine angular structure at resolution ~1/t). At finite width the radius feature decays like e^{-5t/(4n)}
[prior: bits-bounds r3] (HEURISTIC transfer to b_0^{(n,t)}).

A3 (what moment matching cancels). If Delta annihilates polynomials of degree <= K (K >= 1), then M_1(Delta) = 0, and
for every d != 1 the feature M_d(Delta) = int |h|^{1-d} h^{tensor d} dDelta is not a polynomial moment and is not
cancelled by the matching. In particular the radius feature M_0 = int |h| dDelta (weight b_0, which tends to 1 for deep
futures) and every d > K feature survive at every finite K. On a cloud concentrated at |h|^2 = q (1 + u),
u = O_P(n^{-1/2}): M_0(Delta) = sqrt(q) sum_{j >= 1} binom(1/2, j) int u^j dDelta, so moment matching of order K
cancels the j <= floor(K/2) terms and leaves the j = floor(K/2) + 1 term; for d > K, M_d(Delta) = q^{(1-d)/2}
int h^{tensor d} dDelta (1 + O(u)), the raw d-th moment defect. (PROVEN as identities; the sizes are HEURISTIC.)

A4 (random probes; why forward-only methods cannot compress the joint structure). Let T in Sym^r(R^n) be
past-measurable and w ~ N(0, sigma^2 I_n) independent. Then (Isserlis)
  E <w^{tensor r}, T>^2 = sigma^{2r} sum_{p=0}^{floor(r/2)} [C(r, 2p) (2p - 1)!!]^2 (r - 2p)! || tr^p T ||_F^2
(tr^p = p contracted index pairs; r = 3: 6||T||^2 + 9||tr T||^2; r = 4: 24||T||^2 + 72||tr T||^2 + 9||tr^2 T||^2).
All terms are >= 0, so for any past-measurable estimate T^ of T: E<w^{tensor r}, T - T^>^2 >= r! sigma^{2r}
||T - T^||_F^2, whatever T^ is (orientation-free). Consequence: the per-neuron cumulants of the next layer's
pre-activations, kappa_r(z_i) = <w_i^{tensor r}, kappa_r(h_l)> (multilinearity), are n independent Gaussian rank-one
probes of the full order-r cumulant tensor of the cloud. A forward-only representation of the cloud that keeps a
compressed T^ (low rank, sparse, factorised with truncation, top-k modes) errs on every probe by its full Frobenius
error. For a rank-k approximation (CP or multilinear), ||T - T^||_F^2 >= sum_{j > k} sigma_j^2(T_(1)) (Eckart-Young on
the mode-1 flattening T_(1), an n x n^{r-1} matrix, whose rank bounds every such approximation's rank). The flattening's
Gram matrix is estimable without forming T: for r = 3 and centred h, (T_(1) T_(1)^T)_{ab} = E[d_a d'_b (d . d')^2]
with d, d' independent centred copies (a U-statistic). PROVEN.

A5 (suffix-split bound; handles all cross-layer terms). Let the estimator be forward-only at cut l, with layer-l model
Q_l (past-measurable) and a suffix procedure A_t (any computation on Q_l and F_l). Let
e_t(Q) = E_F |A_t(Q, F) - int g_F dQ|^2 be its suffix error on input Q. Then, conditionally on the past,
  ( E_F |est - Y|^2 )^{1/2} >= || Q_l - P_l ||_{k_t} - e_t(Q_l)^{1/2},  ||Delta||_{k_t}^2 = sum_d b_d ||M_d(Delta)||^2.
Proof: est - Y = [A_t(Q_l, F) - int g dQ_l] + int g d(Q_l - P_l); Minkowski in L^2(F) and A2. QED.
Taking the infimum over the family: >= Gamma_F^{(t)}(P_l)^{1/2} - sup_{Q in F} e_t(Q)^{1/2}, with the
network-dependent "F-defect" Gamma_F^{(t)}(P_l) = inf_{Q in F} ||Q - P_l||_{k_t}^2.
Last-layer bottleneck (t = 1, exact last step, e_1 = 0): E_{W_L}|est - Y|^2 = ||Q_{L-1} - P_{L-1}||_{k_1}^2
>= Gamma_F^{(1)}(P_{L-1}) exactly; with the one-layer weights: >= (1/pi)(radius defect)^2 + (1/2)|mean defect|^2
+ (1/(2 pi))||M_2 defect||^2 + (1/(24 pi))||M_4 defect||^2 + ... . For every K = 2 closure (Gaussian last step,
ARC's K = 2 variants included) and, given CHECK-1, every order-K Gram-Charlier closure, this holds with no assumption on
how errors made at different layers combine.

A6 (per-net decomposition). For a fixed net (fixed future), est - Y = a_l + b_l with b_l = int g_l d(Q_l - P_l) (the
past model's defect tested by the actual future) and a_l = A_t(Q_l, F) - int g_l dQ_l (the suffix error). Both are
measurable when Q_l can be sampled (or reweighted): this attributes a method's error to cuts and measures cancellation
directly (test T-ATTR).

## 3. Theorem B: correlation growth makes forward compression impossible unless the structure factorises

B1 (PROVEN, A4). A forward-only method can save over the full order-r tensor only by the Frobenius energy it may drop;
the probes price every component equally.
B2 (HEURISTIC mechanism). Each relu layer creates order-r non-Gaussianity per neuron (a rank-one-like contribution per
active unit near its boundary); the linear step rotates the existing tensor by W^{tensor r}, an independent Haar-like
map; criticality keeps the contributions' norms of order one on average. So kappa_r(h_l) is approximately a sum over
layers j <= l of ~n rank-one terms in independent random orientations: its effective rank grows like (number of
contributing layers) x n until it saturates at the generic rank. ARC's factorised representation is exactly this sum
(its factor list grows by O(n) per layer, cost L^2 n^K); at L of order n its size reaches the dense size n^K/K!.
B3 (what "factorises" means, precisely). The order-r structure factorises at layer l if a past-measurable T^ of rank
k << n^{r-1} has ||kappa_r(h_l) - T^||_F^2 <= delta ||kappa_r(h_l)||_F^2 with delta small. By A4 this is the ONLY way a
forward-only method can carry it cheaply. Test T-RANK: the participation ratio of the flattening Gram and the
energy captured by its top-k directions, layer by layer, at 256 x 32. Prediction: no factorisation (top-8 capture < 50%
for l >= 4).

## 4. Theorem C: the price ladder of the cumulant hierarchy (arithmetic PROVEN; inputs MEASURED)

Let e_K be the error (nMSE) of the order-K method and c_K its cost in forward passes. Its gain over a sampler S is
G_K = e_S(c_K)/e_K; for MC e_S(c) = 1/c.
C1 (arithmetic). G_{K+1}/G_K = (e_K c_K)/(e_{K+1} c_{K+1}) (MC). Dense costs give c_{K+1}/c_K ~ n (basic), so raising
the order improves efficiency only if it divides the error by more than ~n. Under ARC's conjectured law e_K ~ a_K (L/n)^K
(used here only as a description of measured errors, H_LAD), each order divides the error by ~(n/L)(a_K/a_{K+1}) and
multiplies the cost by ~n: efficiency falls by ~L (a_{K+1}/a_K) per order. At 256 x 32 the measured K = 2 -> K = 3f step
divided the error by 6.4 for 108x the cost [prior: arc-noisy, sigma = 0.001]: a 17x loss of efficiency in one order.
C2 (consequence under H_LAD). The hierarchy can be competitive only at its lowest orders, whose errors are fixed
(deterministic) floors: e_2 ~ 1e-3 at 256 x 32. Every finer precision eps^2 < e_2 costs more than sampling by a factor
that grows geometrically in log(e_2/eps^2): roughly (L/a)^{log(e_2/eps^2)/log(n/L)} with a = a_{K+1}/a_K ~ 1.
C3 (along L = alpha n). PROVEN UNDER (H_R) [prior: bits-bounds r3]: the exact single-Gaussian recursion has bounded gain
over MC. MEASURED [prior: hardness, cut-rank]: ARC's K = 2 gain ~ n^{-0.59} at alpha = 1/8; factorised K = 3 gain
~ n^{-1.58} at fixed L/n. CONJECTURE C-LAD: for every fixed K, the order-K gain over MC is bounded at L = alpha n.
Test T-LAD: ARC's variants K = 1..4 along L = n/8 at n = 32, 64, 128, 256.

## 5. Theorem D: separation from the best sampler at depth proportional to width

PROVEN UNDER (H_R) and the multilevel cost hypotheses H_ML [prior: unrestricted 3.7; bits-bounds r3]: at L = alpha n the
multilevel shared-trajectory sampler's annealed gain over radius-exact MC is Omega(n / log^2 n), while the exact
single-Gaussian recursion's annealed gain over MC at its own cost is O(1). Hence the best sampler beats this closure by
a factor growing at least like n / log^2 n. Under C-LAD the same holds for every fixed-order closure. At 256 x 32
(alpha = 1/8) the asymptotic factor is ~1 (multilevel measured ~1.0); the comparator there is RQMC / Kerdock (2.4x MC).

## 6. Resolving estimators (Definition 4)

PROVEN in class [prior: bits-bounds Thm 7.1, Cor 7.2, Thm 7.3]: a forward-only cell sweep needs log2 M >= the
rate-distortion function of the cloud under the future-averaged merge distortion. MEASURED / HEURISTIC [prior]: at
256 x 32 the bits formula N_l ~ PR_l log2(D_l(1)/eps^2) gives 224, 112, 45 bits at l = 4, 8, 16 (eps^2 = 0.1), matching
learned local codes (230, 104, 34-52); 256 merge cells do not reach eps^2 = 0.1 at l = 8, 16, 24. So resolving the
cloud at 10% precision needs >= 2^45 cells at l = 16 against ~10 samples. Region census at width 8: 3e4-6e4 regions for
99% of the output mass at depth 8.

## 7. Future-aware layer-wise estimators

F1 (PROVEN) [prior: bit-accounting]. With unrestricted computation every layer needs only the output's own bits (the
encoder runs the future): there is no information obstruction for future-aware methods; their limit is computation.
F2 (PROVEN, reduction). For a future-aware deduction-projection estimator, the statistic the future needs from layer l
is int g_l dP_l = Y itself; a projection Pi_l chosen to preserve a set S_l of test functions leaves the error
sum_l <g_l - proj_{S_l} g_l, Delta_l>. Preserving the exact answer at each layer is the original problem at depth l.
F3 (MEASURED) [prior: relevance]. Linear test functions capturing 99% of the value function's variance at 256 x 32:
N(l, 0.01) = 256, 192, 128, 80, 48 at l = 0, 4, 8, 16, 24; nonlinear content: mean Hermite degree 21, 7.7, 4.1, 1.9,
1.3. A future-aware method that knows W_{l+1} needs only the n probes <w_i^{tensor r}, kappa_r(h_l)> (not the full
tensor), but each probe pulls back through W_l^T D_l to a probe of layer l - 1 and the pulled-back probes of all later
layers accumulate (L n directions per order); at tree level this costs ~L^2 n^3 per order (HEURISTIC), the cost of
ARC's factorised K = 3. Future-awareness changes which statistics are carried, not how many.

## 8. Kelvin's hypothesis: "whether the bits get scrambled when correctly compressed"

S1 (frames: scrambled; PROVEN). Given the past, the next layer acts on the cloud through an independent Gaussian
matrix (relevance Thm 1); its neurons read the cloud's joint order-r structure through n independent Gaussian rank-one
probes (A4); forward-measurable frames do no better than a random frame plus the state's direction (kstar-frames
Prop 2). Anything the past computes is seen by the future in a uniformly random orientation.
S2 (codes: not scrambled; MEASURED, phase-2 test pending) [prior: bit-accounting v1]. Consecutive layers' learned
local codes are related by near-linear threshold maps (96% of the predictable part); real-valued codes 74-98% linear.
S3 (codes: lossy and not nested; MEASURED) [prior: bit-accounting v1]. Each layer's code knows what the previous did not
(its encoder sees one more layer), and translating loses information.
S4 (correctly compressed = unrestricted: nothing moves; PROVEN) [prior: bit-accounting]. The minimal unrestricted code
at every layer is the output's own, so with correct compression nothing is scrambled and the compression is the
problem itself.
Reading: the version of the hypothesis that holds is S1 plus correlation growth (B2): the joint structure grows in
rank with depth and is read through random probes, so forward compression is impossible; not S2.

## 9. Steelman (best positive cases; to be quantified)

SP1 probe-augmented Gaussian closure (track the per-neuron 3rd and 4th cumulants of the pre-activations via
pulled-back probes at tree level, ~L x the K = 2 cost): the one-step oracle gain of 19-120x [prior: arc-noisy] is its
ceiling per layer; if it carried over fully at 256 x 32 it would land near parity with RQMC (HEURISTIC arithmetic).
SP2 exact Gaussian closure (fixing ARC's 'simple' off-diagonal update): bounded gain; measured <= ~3 at matrix cost.
SP3 hybrids with low-order ANOVA parts (control variates, RQMC): constant factors 1.3-3x; sampling, not deduction.
SP4 depth synchronisation / multilevel structure used deductively: needs L >> n; at 256 x 32 the future is rough at
every cut before ~0.8 L (rho_l > 1) [prior: bits-bounds].
SP5 factorised higher orders: B2 predicts no saving at L ~ n/8 (T-RANK).
SP6 advice: ARC's train-and-explain form limits advice to O(Time(sampling the weights)) for random nets.

## 10. Hypotheses ledger (each with its test)

| id | hypothesis | used by | test |
|---|---|---|---|
| CHECK-1 | ARC's final step equals int relu(w_i . h) dQ for a w-independent truncated Gram-Charlier Q | A5 for K >= 3 | read kprop_harmonic.py; numerical identity on a small net |
| H_R | Gaussianisation does not lower the mean radius on average over a fresh layer [prior] | C3, D | prior lane's diagnostic (not rerun here) |
| H_ML | layerwise schoolbook costs for the multilevel sampler [prior] | D | cost accounting |
| H_LAD | the order-K error ladder follows ~a_K (L/n)^K with a_{K+1}/a_K ~ 1 at fixed L | C1, C2 | T-LAD |
| B2 | the cumulant tensors' effective rank grows with depth (no factorisation) | B, SP5 | T-RANK |
| NC | no strong cancellation between past defect and suffix error | interpretation of A6 | T-ATTR |

---------------------------------------------------------------------------------------------------------------------
# FORMAL v2 additions (05:35Z onward; after reading astra round 1 and the dev runs; v1 above is frozen as
# coprover/FORMAL_v1_as_written.md)

## E1 (erratum to B2: "correlation growth" is refuted on the dev net)
Dev net 100 (256 x 32, N = 2^14): the participation ratio of the third cumulant's mode-1 flattening is 115, 68, 24,
6.6, 2.7, 1.5, 1.6, 1.2, 1.1 at l = 1, 2, 4, 8, 12, 16, 24, 28, 31, against the covariance's 164, 104, 55, 25, 13, 6.4,
5.1, 3.1, 2.9; the held-out top-32 multilinear capture is 0.07, 0.19, 0.51, 0.81, 0.94, 0.985 at l = 1..16. So the
order-3 structure does NOT grow in rank with depth: it is high-rank only in the first ~4-8 layers (where the output's
variance is made [prior: bits-bounds]) and collapses onto ~1 direction by l = 16. B2's mechanism (new rank-one terms in
random orientations accumulating) is wrong: the old terms are contracted with the cloud. Replacement:
B2' (MEASURED dev, registered as P9): PR3(l) <= PR_cov(l), PR3 >= 40 at l = 1 and <= 4 from l = 16; the forward
compression price (A4) is therefore large only in the early layers. B3's test stands.

## E2 (A5 is needed: forward-only access alone does not exclude cancellation) [astra r1 2.4, checked]
Q_1 = P_1 + eta, Q_2 = P_2 gives delta_1 = eta, delta_2 = -T_2 eta with cancelling contributions; both forward-only.
So no theorem can say "forward-only defects add up" without a restriction; A5 (Minkowski with the suffix error) and the
Gram criterion (lambda_min of the normalised defect Gram >= eta implies E|sum e_l|^2 >= eta sum E|e_l|^2) are the two
valid replacements. A6/T-ATTR measures the actual cancellation for ARC k2 and the exact Gaussian recursion.

## E3 (the price ladder, measured form; registered P1, P2, P5, P11, P12)
Dev (one net per width, L = n/8): best-variant gains over MC at own cost G_2 = 7.1, 5.9, 3.7, 4.1 and G_3 = 1.27,
0.85, 0.22, 0.063 at n = 32, 64, 128, 256; G_4 = 1.13, 0.11, 0.002 (n <= 128). Ratios G_3/G_2 = 0.18, 0.14, 0.06,
0.015 ~ 0.5/L. Per-order error reduction e_3/e_2 = 0.5, 0.37, 0.36, 0.52 (each order divides the error by only ~2-3,
not by ARC's conjectured n/L = 8), while the cost grows 30-120x. Best error over K <= 4 (K <= 3 at 256):
2.6e-5, 3.4e-5, 2.0e-4, 3.2e-4: the attainable precision WORSENS as width and depth grow together.
CONJECTURE (superasymptotic floor, HEURISTIC motivation: ARC's own statement that the diagram/Edgeworth series does not
converge at fixed n): at L = alpha n, min over fixed K of the order-K error does not tend to 0 as n grows (registered
finite-n version: P11).

## E4 (budget windows: what a deterministic floor implies; PROVEN arithmetic)
A deterministic estimator with error e and cost C beats a sampler with error curve s(N) exactly on the budget window
[C, s^{-1}(e)], which is nonempty iff its gain at own cost G = s(C)/e exceeds 1, and for s(N) = c/N its width is a
factor G. So "matching sampling for all eps" needs a family whose members have G >= const at every precision; a ladder
with G_{K+1}/G_K -> 0 cannot. At 256 x 32 the contest budget (6.5e4 passes) asks for nMSE ~6e-6 (Kerdock 0.40/N
[prior: arc-noisy]); the best affordable ARC variant (k3f, 4.9e4 passes) is at 2-3e-4.

## E5 (from astra r1, checked or labelled)
- E V bounds 0.4995 < E V < 20.14 at 256 x 32 (PROVEN [A]; not rechecked numerically here).
- Fixed-depth lower bound for ARC's basic K = 2 'simple' at L = 2: liminf n^2 R >= 0.110 (PROVEN [A]; read, not
  re-derived): ARC's n^{-K} scaling is tight at K = 2, L = 2 for that rule.
- Separation (astra eq. 12, PROVEN UNDER cost and multilevel-risk hypotheses): an order-K method with normalised error
  >= b n^{-p} at cost Theta(n^{K-1}) passes has gain over the multilevel sampler O(log^2 n n^{p-K}); a polynomial
  advantage needs p > K. With (H_R), the exact Gaussian recursion has p <= 1 < 2 = K: it loses to the multilevel sampler
  by a factor growing like n / log^2 n at L = alpha n. This is the precise form of FORMAL Theorem D.
- "Factorises" (astra): bounded elimination width of a supplied factor graph with charged construction gives
  O(T q^{w+1}); large high-order dependence alone does not contradict efficient factorisation (parity example).
- Kelvin's hypothesis, Formalisation A (astra): an exact code update exists iff H(Z_{l+1} | Z_l) = 0; Fano bounds the
  one-step error; cheap transitions do not imply cheap propagation of the code's law; a future-aware "correct
  compression" (quantise g_l(h)) makes the transition the identity at the cost of a suffix evaluation per encoding.
  Formalisation B: with a moment-summary interface, parity pairs defeat every summary-based estimator; an unknown-bias
  table under point queries has normalised risk ~1/(q + 2) (sampling-like).
- Positive (astra): (i) an analytic control for the first radial level of the multilevel sampler (bias O(1/n), setup
  O(n^3)); (ii) acceptance criterion for any control g with exact mean, residual share eta, evaluation cost a and setup
  B: it beats a 0.40/N comparator iff eta < (0.40/a)(1 - B/N); (iii) at FIXED weights, region integration has cost
  polylog(1/eps) (PROVEN [A]) and so eventually beats sampling as eps -> 0, with constants that the nd-exact lane
  measures as 1e16-1e18 certifiable cells at width 8.

## E6 (the price spectrum of a deep future; mean-degree column and asymptotics CORRECTED in E10.8; NUMERICAL, infinite width, scratch/kernel_spectrum.py,
## results/kernel_spectrum.json; exact b_0 = kappa_t(0), b_1 = kappa_t'(0), b_{>=2} = 1 - b_0 - b_1; FFT checks to 1e-4)
Weights of A2's features for a future of depth t (unit output energy):
| t | b_0 (radius M_0) | b_1 (mean M_1) | b_{>=2} (higher M_d) | median / 90% degree of the b_{>=2} mass | mean degree |
|---|---|---|---|---|---|
| 1 | 0.318 | 0.500 | 0.182 | 2 / 4 | 2.7 |
| 4 | 0.681 | 0.142 | 0.178 | 3 / 8 | 4.8 |
| 8 | 0.834 | 0.050 | 0.116 | 4 / 14 | 8.1 |
| 16 | 0.930 | 0.013 | 0.057 | 6 / 30 | 16.7 |
| 24 | 0.961 | 0.0055 | 0.034 | 8 / 51 | 28.0 |
| 31 | 0.973 | 0.0030 | 0.024 | 10 / 74 | 39.9 |
Reading (PROVEN identity A2 plus these numbers): for a deep future the mean of the cloud is almost free (b_1 ~ 1/t^2),
the radius feature carries nearly all the weight, and the rest is spread over radially normalised moments of degree up
to ~2.4 t (mean ~1.3 t). A defect in the cloud's higher structure at layer l = L - t is therefore read at degrees up to
~74 at l = 1 of ARC's 256 x 32, far beyond any finite cumulant order. (At finite width the radius weight decays like
e^{-5t/(4n)} [prior], 0.86 at t = 31, n = 256; HEURISTIC transfer.)

## E7 (errata and additions from gpt-6-astra round 2, 05:18-05:41Z, coprover/astra_r2_answer.md; read 05:42Z)
- A2: correct. The proof's "E_Z|G(Z)|^2 = 1" holds only averaged over the remaining future (E_{F', Z}|G|^2 = 1), which
  suffices for sum_d b_d = 1 exactly [A]. NEW (PROVEN [A]): b_0^{(n,t+1)} >= b_0^{(n,t)} >= 1/pi for every t >= 1 at every
  width (expected inner products of two independent first-layer states never decrease, since kappa_1(c) >= c). My v1
  sentence that the finite-width radius weight decays like e^{-5t/(4n)} is WITHDRAWN (that factor bounds the suffix mean,
  not b_0).
- A3: WRONG as worded [A]. Counterexample: Delta = sum_j (-1)^j C(K+1, j) delta_{(j+1)v} annihilates polynomials of
  degree <= K and has M_d(Delta) = 0 for every d (it is invisible to every positively homogeneous query). Correct
  statements: on a common sphere, order-K matching cancels every M_d with d <= K; tr M_d = M_{d-2} (the features are
  not independent); in general M_0 and M_d (d > K) are NOT forced to vanish, and the expansion (31) of astra's answer
  (finite Taylor order with an absolute remainder) replaces my relative-error expression.
- A4: identities correct; the bound is an expected-square bound over a fresh probe (uniform Frobenius lower bound;
  trace sectors get extra weight). It prices APPROXIMATION, not storage or computation: Sum_i e_i^{tensor r} has
  flattening PR n and an O(n) description [A]. "Forward methods cannot compress" (B1) is withdrawn as a computational
  claim; what remains is: any reconstruction with mode-1 flattening rank <= k errs on fresh probes by at least the
  flattening tail (PROVEN).
- A5: correct, and it needs no cross-layer assumption [A]. CHECK-1 CORRECTED [A, by code inspection]: ARC's K = 2
  'augment' is not Gaussian (it keeps a radial third-cumulant tensor and an isotropic fourth-cumulant tensor); with
  avg_metric = True no fixed signed measure reproduces the last-row map for K >= 3 or 'augment' (the corrections scale
  like ||w||^{-1}, ||w||^{-3}, not ||w||); ARC floors variances at 1e-10. So A5 applies exactly to ARC's K = 2 'simple'
  (up to the floor), to the exact Gaussian recursion, and to Gram-Charlier closures run with the exact metric.
  A5 by itself does not prove the bottleneck is large: on a positive ray every cloud has the same homogeneous queries as
  the point mass at its mean, so the Gaussian-family infimum can be zero [A].
- B1-B3: B2 is HEURISTIC and (E1) refuted on dev; B3's "only way" is wrong (sparse, implicit, symmetric or query-only
  representations are alternatives) [A].
- C2: ratio corrected (efficiency loss per order L a, not L/a) and the conclusion needs the ladder to hold uniformly
  over all orders used [A].
- F3: the relevance lane's N(l, eps) counts linear projections of the STATE with a nonlinear readout, not linear test
  functions; "future-awareness changes which statistics are carried, not how many" is WITHDRAWN (false without a
  representational restriction) [A].
- S1: correct conditional isotropy; it does not by itself establish computational scrambling. S3 is not a general
  theorem (a later code can retain information an earlier code discarded; trained-decoder errors are upper bounds) [A].
- NEW for ARC's actual K = 2 (PROVEN [A], read and checked at the level of the argument):
  (a) the 'simple' covariance rule has a valid Gaussian reconstruction (PSD); under (H_{R,s,tau}) (its radius defect
      has nonnegative fresh-layer mean, CONJECTURE) liminf n R_simple >= (c_s^2/(pi C_*)) e^{-5 alpha/4},
      c_s = 9/16 + 1/(4 pi^2), prefactor 0.0069; an explicit finite-n version evaluates to ~1.03e-5 at 256 x 32
      (decimal not interval-certified);
  (b) the unconditional one-replacement bound improves to liminf n R >= 81/(256 pi C_*) = 0.00636 with no depth
      attenuation (from b_0 >= 1/pi);
  (c) a hypothesis-free last-row certificate for any implementation: E_{W_L}|e_L|^2 >= n E_U[E_R f^2 - (E_R[R f])^2]
      with f(R, U) the algorithm's last-row output as a function of the row's norm and direction (the true output is
      homogeneous of degree one in R); for averaged-metric 'augment' it reduces to a positive-definite form in its third-
      and fourth-cumulant corrections (eq. 29 of the answer);
  (d) E_{W_L}|e_L|^2 >= (1/2)|m_{L-1} - mu_{L-1}|^2 for both K = 2 variants (odd part), exponentially weak when iterated.
- NEW, order K (PROVEN UNDER extensivity and remainder hypotheses [A]): conditional radial exponents p_rad =
  2 floor(K/2) - 1 (moments only), K - 1 ('simple', even K), K ('simple', odd K, exact extra trace), K + 1 ('augment',
  even K), K ('augment', odd K). With astra's (34), p_K <= K rules out a polynomial advantage over the multilevel
  sampler; the radial obstruction alone does NOT rule it out for augmented even K. No unique p_K for the full ARC
  algorithm follows (projection error, suffix propagation and accumulation are three separate gaps).
- Measurement corrections [A]: the participation-ratio numerator ((tr K1 + tr K2)/2)^2 is upward biased; tr K1 tr K2
  is unbiased for the squared trace (scored both ways); held-out capture ratios are ratios of unbiased numerators, not
  unbiased; fro2_direct is the same statistic as tr K3 (not an independent check); the split-half routines need chunks
  aligned with N/2 (true for every registered size: N and chunk are powers of two with N >= 2 chunk); PSD clipping in
  gauss_push changes the model (recorded clip fractions are <= 3e-16 on the dev nets).

## E8 (exploratory measurements bearing on the hypotheses; not registered)
- Radius-sign test of (H_R) and (H_{R,s,tau}) (scratch/hr_test.py, runs/hr_s200.json; states reached by ARC's K = 2
  'simple' recursion on eval net 200; 32 fresh layers per state, 2^15 samples): mean fresh-layer radius defect
  (Gaussian update minus true push-forward, absolute units, radius ~16-22):
  | state layer l | 0 | 1 | 2 | 4 | 8 | 16 | 24 |
  |---|---|---|---|---|---|---|---|
  | 'simple' | +0.036(1) | +0.020(2) | +0.015(2) | +0.0064(21) | +0.0020(24) | -0.0001(26) | -0.0038(32) |
  | exact | +0.035(2) | +0.021(2) | +0.015(2) | +0.0063(21) | +0.0067(31) | -0.0000(22) | -0.0016(32) |
  The l = 0 values match the proven asymptotics 9/(16 sqrt 256) = 0.0352 (exact) and c_s/sqrt 256 = 0.0367 ('simple').
  The defects are positive and decreasing through l = 4-8 and indistinguishable from zero at l = 16-24 at this resolution:
  no violation of either hypothesis on the states reached (consistent, not a proof).
- Radial part of the single-cut Gaussian defect (eval net 200, attribution runs, 2^19 pushes): replacing the oracle
  Gaussian's radius marginal by the true one reduces the defect from 1.4e-4, 3.4e-4, 4.5e-4 to 1.4e-5, 3.1e-5, 1.2e-5 at
  l = 1, 2, 4 (10-40x), but only 6.2e-5 -> 2.8e-5, 1.9e-4 -> 1.4e-4, 6.7e-5 -> 5.4e-5 at l = 8, 16, 24. So in the first
  layers the Gaussian defect the future sees is mostly the amplitude (radius) marginal, weighted by b_0 ~ 0.7-0.9 (E6);
  in the middle layers it is angular. (Post hoc; registered P8 covers only l = 8, 16, 24; other nets pending.)

## E9 (ARC's own law as an error-cost exponent; PROVEN arithmetic under the laws; registered P13-P14)
If the order-K error is e_K = c (L/n)^K (ARC's conjectured upper bound, used here as a description, constant c) and the
order-K cost is C_K = n^{K-1}/2 forward passes (basic: L n^{K+1} flops over 2 n^2 L per pass), then choosing the best
affordable order at budget C gives e(C) = c (L/n) (2C)^{-gamma}, gamma = log(n/L)/log n = 1 - log L/log n.
- Fixed L, n -> infinity: gamma -> 1, the sampling rate (ARC's theorem regime: "for any given depth ... at sufficiently
  large width").
- L = alpha n: gamma = log(1/alpha)/log n -> 0: the hierarchy's error improves with compute ever more slowly; at
  256 x 32, gamma = 0.375 against sampling's 1. Between orders the measured exponent on ARC's medians is
  ln(1.4e-3/2.2e-4)/ln(2.06e11/1.9e9) = 0.40 [prior: arc-noisy, sigma = 1e-3]; on our eval nets 0.52 (n = 32) and
  0.38 (n = 64) against 0.60 and 0.50 predicted (P13-P14 registered for n = 128, 256).
- Matching sampling at every eps needs gamma >= 1 (plus a constant); gamma < 1 whenever L > 1. So under ARC's own law
  the cumulant hierarchy cannot match sampling for all eps at any depth L > 1 at finite width, and at depth growing
  linearly with width its rate tends to zero. (Factorised variants change C_K by a factor ~L/n and do not change gamma's
  limit.) This is the cleanest one-line form of the negative for ARC's method class: it uses only ARC's own conjecture
  and cost law, and the measured exponents agree with it.
- Correction (E10.7, from astra r3): "floor" is the wrong word for E3/E9's conclusion. c_K >= c_* > 0 does not give
  inf_K c_K alpha^K > 0 (c_K = 1 is a counterexample). What does follow, under uniform-in-K laws e_K >= a c_* alpha^K
  and C_K >= d_* n^{K-1} over the orders used, is e_best(C) >= a c_* alpha (C/d_*)^{-gamma_n} with
  gamma_n = log(1/alpha)/log n (the gamma above): the hierarchy cannot match MC at all precisions even if its all-order
  floor is zero. ARC's upper-bound conjecture alone does not give this; it needs the law to be tight, uniformly.

## E10 (gpt-6-astra round 3, the radial closure and its ceiling; coprover/astra_r3_answer.md, exit 06:39Z, read 06:43Z)
Labels are astra's unless marked [checked]; equation numbers are the answer's.
1. An implementable radial closure (38)-(40): state Q(m, C, nu) = law of R G/|G|, G ~ N(m, C), R ~ nu independent;
   nu lognormal fitted to E|Y|^2 and Var|Y|^2 of the deduced next layer. Its update has O(J n^3) cost with J quadrature
   nodes for |G|^{-p} (Laplace transform plus Gaussian tilting); this is a fixed-accuracy cost, uniform accuracy in
   n, L, 1/eps is NOT proved. It is not an order-2 moment-matching projection (normalising changes mean and covariance).
   [PROVEN] In cost units: one node ~ ARC's K = 2 cost (393 passes at 256 x 32), so the 393-1200 range used in
   Amendment 2 corresponds to J = 1-3.
2. [PROVEN] The true radius marginal kills M_0 exactly (41). [PROVEN UNDER radial extensivity and Taylor-remainder
   control] The lognormal fit cancels the n^{-1/2} mean-radius defect of plain Gaussianisation (9/(16 sqrt n), E8's
   l = 0 row) and leaves O(n^{-3/2}) (42). This is why the early-layer lead in E8 exists.
3. [PROVEN UNDER H_shell (first-layer shell and coordinate-limit hypothesis); constants checked] Radius matching leaves
   the order-one coordinate skewness of the first layer, gamma_3 = kappa_3(sqrt2 Z_+) = a + 2 a^3 = 0.923, a = 1/sqrt pi
   [checked: E X = a, E X^2 = 1, E X^3 = 4a], so liminf n E|M_3(Q - P)|_F^2 >= gamma_3^2 (45), and
   liminf n E|M_d(Q - P)|_F^2 >= C(d, 3) gamma_3^2 a^{2d-6} (46). [PROVEN] Finite-width cubic price:
   b_3^{(n,t)} >= a_n^{2(t-2)} |Proj_3 rho_n|^2 / pi with |Proj_3 rho_n|^2 = 1/(3 pi n) + o(1/n) and
   a_n = E rho_n = 1 - 5/(8n) + o(1/n) [checked: Var rho_n^2 = 5/n; E[Z_+^2 He_3/sqrt6] = 1/sqrt(3 pi)], so
   b_3 >= (e^{-5 beta/4} + o(1))/(3 pi^2 n) at t = beta n (50); also b_2 >= a_n^{2t-2}/(2 pi n) (49). Together (51):
   the radius-corrected first-layer single-replacement error is >= e^{-5 beta/4} gamma_3^2/(3 pi^2) n^{-2}: p <= 2.
   At 256 x 32 this bound is 3.8e-7 in absolute units (1.8e-8 in nMSE units on net 200, V = 21.2), far below the
   measured 1.4e-5 nMSE at l = 1 (an exponent statement, not a useful number at this width). Transfer to the full recursion is a HYPOTHESIS (E2: a single-cut defect is not a lower
   bound when the suffix can cancel); under it, G_multilevel = O(log^2 n): no polynomial advantage.
4. [PROVEN] Amplitude propagation (52)-(53): R' = R A_W(U), U' = T_W(U) with A_W(u) = |relu(Wu)|,
   T_W(u) = relu(Wu)/A_W(u). The next radius law depends on the joint law of (R, U) through gate-dependent functions of
   U; a radius marginal plus finitely many covariances does not determine it. The exact object every positively
   homogeneous query needs is the radius-weighted direction measure nu_P(du) = E[R | U = u] P_U(du), and it propagates
   linearly: nu_{P'}(B) = int A_W(u) 1{T_W(u) in B} nu_P(du). (My reading, for section 8 and Kelvin's hypothesis: the
   correctly compressed state for the mean query is a compression of nu_P, and its update is a gain-weighted
   push-forward on the sphere: the same law-propagation problem, one dimension down. Splitting off the radius does not
   remove the angular problem; it isolates it.)
5. [PROVEN] Mid-layer angular error: D_ang = sum_{d>=2} b_d |int u^{tensor d} d(nu_Q - nu_P)|_F^2 (54). [PROVEN UNDER
   H_cap: directions in a cap of angular width 1/n, a limiting signed tangent profile sigma with zero mass, the kernel
   on the cap 1 - Psi_beta(z, z')/n^2, B = -iint Psi_beta d sigma d sigma > 0] D_ang = B/n + o(1/n) (55): a p = 1
   obstruction in the middle layers, worse than the first layer's p = 2. H_cap, in particular B > 0, is NOT established
   (CONJECTURE that the measured mid-layer residual is such a profile). astra's discriminating measurement, the width
   scaling of the radius-corrected single-cut defect at fixed l/n and t/n, is registered as Amendment 4 (P15-P16).
6. [PROVEN] E6's infinite-width spectrum cannot be transferred uniformly to t = beta n: its non-constant mass is
   O(t^{-2}) = O(n^{-2}) there, while (50) gives finite-width cubic mass Omega(1/n).
7. [PROVEN UNDER the stated laws] ARC's law (56)-(60): see the correction appended to E9. Fixed-K gain over MC is
   ~ n^{-(K-1)}/(d_K c_K alpha^K). [HEURISTIC] The measured constants at alpha = 1/8 give c_3/c_2 = 0.96-1.20 and
   c_4/c_3 = 2.0-4.4: consistent with a tight (L/n)^K ladder with growing constants, not proof of uniformity.
8. Audit of E1-E8 (accepted): E1 narrowed (a participation ratio alone does not determine tensor magnitude, trace-sector
   price, approximation cost or future relevance; "the compression price is large only in early layers" WITHDRAWN);
   E2 PROVEN; E3 kept as a dev record (best-gain variants need not be best-error variants); E4 PROVEN under its budget
   model; E5 "tight" -> "lower bound" (no matching upper bound is proved); E6 corrected (below); E7 retained; E8's
   before/after difference is not an orthogonal "radial share" (the transport changes every M_d, the mean included; at
   l = 31, where b_1 = 1/2, the radial-Gaussian defect 1.89e-5 exceeds the oracle Gaussian's 5.98e-6), the sign test
   covers the states reached by 'simple', not every state of the exact recursion, and the long-suffix weight at the
   early cuts is b_0 ~ 0.97 (t = 28-31), not 0.7-0.9 (my error).
   E6 correction [checked, results/kernel_spectrum.json]: sum_d d b_d = kappa_t'(1) = 1, so the mean degree of the
   b_{>=2} mass is exactly (1 - b_1)/(1 - b_0 - b_1): 2.75, 4.84, 8.22, 17.24, 29.28, 42.27 at t = 1, 4, 8, 16, 24, 31
   (the FFT column, truncated, gave 2.74, 4.80, 8.10, 16.74, 28.01, 39.92). Asymptotically 1 - b_0 ~ 9 pi^2/(2 t^2) and
   b_1 = Theta(t^{-3}) [checked: from kappa_1(rho) = rho + (2 sqrt2/(3 pi))(1 - rho)^{3/2} + ... near rho = 1], so the
   conditional mean degree eventually grows like 2 t^2/(9 pi^2): E6's "mean ~1.3 t" and "b_1 ~ 1/t^2" are finite-depth
   descriptions, not laws, and there is no degree cutoff.

## E11 (finite-width radius weight at 256; NUMERICAL, exploratory, not registered; scratch/finite_b0.py,
## results/finite_b0_n256.json; 4000 random futures x 64 orthogonal pairs, SE over futures)
b_0^{(n,t)} = K(0)/K(1) with K(rho) = E_future <g_t(u), g_t(v)> (A2's expansion is a power series in rho = u.v with
nonnegative coefficients, so b_0 is its value at rho = 0):
| t | 1 | 4 | 8 | 16 | 24 | 31 |
|---|---|---|---|---|---|---|
| n = 256 | 0.3183 | 0.6771 | 0.8235 | 0.9112 | 0.9378 | 0.9482 (SE 0.0002) |
| n = infinity (E6) | 0.3183 | 0.6810 | 0.8344 | 0.9295 | 0.9606 | 0.9734 |
At 256 x 32 the non-radial weight 1 - b_0 of a 31-layer future is 0.052, about twice the infinite-width 0.027, as
E10.6 says it must be (finite-width higher mass Omega(1/n) at t proportional to n). t = 1 gives 1/pi at every width.

## E12 (gpt-6-astra round 4 and the GPT-6 fresh-session review, both read 09:55-10:00Z; coprover/astra_r4_answer.md,
## review/review_gpt6.raw)
1. [PROVEN, astra r4 (R1)] For the radial recursion Q_l = Pi_rad Phi_l Q_{l-1} with an exact last step, est - Y = sum_l
   e_l with e_l = int g_l d(Q_l - Phi_l Q_{l-1}), the closure's OWN one-step defects, each priced by A2 with d >= 1 (the
   radius term vanishes because the projection keeps its own push-forward's radius law; the mean term need not). These
   are not the oracle single-cut defects; substituting those into the telescoping sum is wrong.
2. [PROVEN UNDER cap, remainder and local-discrepancy hypotheses (R2)-(R4)] A one-step defect is of order n^-1 if the
   priced tangent profile discrepancy is order one, n^-2 if it is order n^-1/2. [PROVEN UNDER sum_l D_l = Theta(L/n^2)
   and Gram bounds c I <= C <= C' I (R5)] the annealed error is Theta(L/n^2) = Theta(alpha/n): p_full = 1, consistent
   with the measured L/n^2 law of the radial recursion (section 4.4 (c)); a lower Gram bound alone gives only
   Omega(alpha/n). Then (R6) at O(J n^3) per layer: G_MC = Theta(1/J), G_multilevel = O(log^2 n / (J n)).
3. [PROVEN] Next order: tr M_3 = M_1 (the trace sector adds nothing once the mean is matched); the trace sector of a
   cubic tensor carries only 3/(n+2) of the diagonal-skewness energy; mixed cumulants kappa(X_i, X_i, X_j) = a rho_ij +
   O(rho^2) carry Theta(n) total energy at the first layer, so diagonal skewness is not the whole cubic correction.
   [PROVEN UNDER structured cubic dominance] a matrix-cost correction with o(n^-2) one-step defect exists only if a
   low-rank innovation representation can be maintained through gating; [CONJECTURE] that it can. [PROVEN UNDER the
   transfer of ARC's ladder to a radial hierarchy] e(C) ~ C^-gamma_n with gamma_n = log q/log n = 0.25-0.375 at
   n = 256 for q = 4-8: the radius correction improves the starting error, not the precision exponent.
4. [PROVEN UNDER multiplicative scale errors] amplitude tolerance for nMSE eps after L layers: delta <= sqrt(eps/(A L))
   (independent) or (1/L) sqrt(eps/A) (systematic), A = |Y|^2/V; 0.04% and 0.007% at A = 20, L = 32, eps = 1e-4.
   [PROVEN UNDER analytic-strip hypotheses] log-scale sinc quadrature for eq. (40) needs J = O(log^2(C_Q/delta)) nodes;
   no numerical value of J (in particular J = 1-3) follows; "one node = 393 passes" is a HEURISTIC estimate.
5. Corrections accepted from both: E10's first-layer result is an asymptotic lower bound (liminf, absolute squared
   error; normalised error needs division by C_* or E V), not Theta(n^-2); the r2 one-replacement bound is for a
   Gaussianisation immediately after layer 1 (r2 eq. 26), not "anywhere after layer 1"; after radius matching the
   residual includes b_1 |M_1|^2; independent-radius (eq. 40), lognormal and monotone-transport reconstructions are
   different, and the measured monotone-transport errors do not transfer to eq. (40)'s cost without an argument; the
   oracle radial-Gaussian is a specified projection benchmark, not a ceiling for deductive closures; replicate cross
   products remove replicate variance, not finite-sample fitting bias (2^19 samples, batch-2^14 rank transport): the
   full-recursion numbers are finite-sample stochastic-recursion measurements whose convergence is not established;
   E11 "as E10.6 says it must be" -> "consistent with E10.6"; b_0 ~ 0.95 holds for long suffixes (0.82, 0.91, 0.95 at
   t = 8, 16, 31), not every depth; the degree statements of E6/E10.8 are infinite-width (only b_0 was measured at
   finite width); E10.3's "more than the infinite-width table gives" is false at 256 x 32 (the asymptotic cubic bound
   1.1e-4 there is below the infinite-width cubic weight 1.9e-3).

## E13 (corrections from an independent adjudication relayed by main, 10:22Z; applied 10:25-10:30Z)
- E12.2: the step to Theta(L/n^2) assumes sum_l D_l = Theta(L/n^2) with two-sided Gram bounds, which is close to the
  conclusion; it is a consistency decomposition of the measured L/n^2 law, not a proof of it (relabelled CONSISTENCY).
- A2 is a pricing identity, not a theorem about what affordable methods can achieve; "Theorem A" is renamed.
- The radial closure's "~5x gain over MC" in the report charged one order-2 step (393 passes at 256) to a measurement
  that used 2^19 samples per layer (>= 5.2e5 passes per replicate). Costed as run it loses to MC by ~250x at its own
  error; the gain claim is withdrawn and replaced by a break-even cost (a deductive version beats MC at its floor only
  below ~5 order-2 steps per layer, RQMC below 2-3.5).
- H_R / H_{R,s,tau}: one exploratory test on one net did not contradict them; "supported" was too strong.
