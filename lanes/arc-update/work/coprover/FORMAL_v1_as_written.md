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
