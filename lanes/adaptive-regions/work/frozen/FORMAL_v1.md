# adaptive-regions FORMAL v1 (written 15:15-15:45Z, 2 Nov 2026, before any scored run and before reading the co-prover's round-1 answer)

Labels: PROVEN, PROVEN UNDER <hypothesis>, NUMERICAL, HEURISTIC, CONJECTURE. [C] = this lane; [prior: lane] = a sibling
lane's FORMAL or report. v1 is frozen by sha256 (notes/formal_hashes.txt); later additions are appended as E1, E2, ...

## S0. Setting and notation
f(x) = h_L(x) in R^n, h_0 = x ~ gamma = N(0, I_n), h_l = relu(W_l h_{l-1}), W_l iid N(0, 2/n), no biases. f is
continuous, piecewise linear on polyhedral cones (activation regions), positively homogeneous: f(x) = r g(u), r = |x|,
u = x/r, m_n = E r. mu = E f; V = tr Var f; nMSE = |est - mu|^2 / V (MC: 1/N). A partition P = {R_1..R_K} of R^n
(measurable, p_k = gamma(R_k) > 0); mu_k = E[f | R_k]; sigma_k^2 = tr Var(f | R_k). Cost unit: one forward pass,
2 n^2 L flops. The idea under test: a tree of regions in which some regions are "understood" (a local model with an
exactly known region mean) and the others are "sampled more" (Neyman or bandit allocation).

## S1. Bookkeeping (PROVEN, elementary)
(a) Stratified estimator, N_k iid draws from gamma restricted to R_k: muhat = sum_k p_k fbar_k, unbiased,
    E|muhat - mu|^2 = sum_k p_k^2 sigma_k^2 / N_k. Over sum N_k = N the minimum is (sum_k p_k sigma_k)^2 / N, at
    N_k proportional to p_k sigma_k (Neyman; Cauchy-Schwarz). Proportional allocation N_k = p_k N gives
    sum_k p_k sigma_k^2 / N = E tr Var(f | P) / N. Gains over MC: G_N = V / (sum p_k sigma_k)^2 >= G_P = V / sum p_k sigma_k^2
    >= 1, and G_N / G_P = 1 + CV_p(sigma)^2 (p-weighted coefficient of variation of sigma_k). Integer constraints
    (N_k >= 1) cost at most a factor N / (N - K).
(b) Post-stratification. With exact p_k and N plain MC draws, sum_k p_k (mean of the draws falling in R_k) has
    variance sum_k p_k sigma_k^2 / N + O(K/N^2) (Cochran). So G_P is available at MC cost plus routing (finding a
    point's cell: D dot products of length n for a depth-D tree, D/(2nL) passes) and the cost of the p_k.
(c) Exponent bookkeeping. If, along a nested family, (sum p_k sigma_k)^2 / V <= C K^-beta for all K, then K = N^a
    (a < 1) gives nMSE <= C N^{-(1 + a beta)} (1 + o(1)), plus the costs of p_k, routing and allocation. To beat
    RQMC's fitted exponent p_R (1.05-1.12 on the ladder, arc-update runs), a beta > (p_R - 1)/a is needed, holding as
    n grows; to beat RQMC by a constant growing with n, G(K) / G_RQMC must grow with n at affordable K.
(d) Allocation rules (MISER, VEGAS+, MC-UCB) choose N_k from pilot or running estimates of sigma_k; for a given
    partition none can beat oracle Neyman, so the oracle gains G_N, G_P measured on held-out samples are upper bounds
    on what any allocation rule achieves on that partition. (For MC-UCB the excess over the oracle is of lower order
    when K = N^a, a < 1: Carpentier and Munos 2011, memory; it does not matter for the ceilings below.)

## S2. Ceilings on the gain of a K-region partition
### S2.1 Partitions chosen without the net: a per-net harmonic rank ceiling (PROVEN [C])
Harmonic decomposition: g = sum_{d>=0} g_d with g_d in H_d (degree-d spherical harmonics, dim N_d; N_0 = 1, N_1 = n,
N_2 = n(n+1)/2 - 1, N_d ~ n^d/d!) componentwise. Then mu = m_n g_0 and the centred f is
f~ = (r - m_n) g_0 + sum_{d>=1} r g_d, an orthogonal sum in L^2(gamma) (different degrees are orthogonal on the
sphere, and the degree-0 term has zero spherical mean against every Y in H_d, d >= 1). Put E_0 = Var(r) |g_0|^2,
E_d = E r^2 E_u |g_d(u)|^2 (d >= 1), so V = sum_d E_d, e_d = E_d / V.

Theorem 1. Let P be any fixed partition into K cells and Q Haar-distributed on O(n), P_Q = {Q R_k}. For every net,
  E_Q [ sum_k p_k sigma_k(P_Q)^2 ] >= V - sum_{d>=0} min(1, (K-1)/N_d) E_d,
so the proportional-allocation gain, in the sense V / E_Q[within], is at most 1 / (1 - sum_d e_d min(1, (K-1)/N_d)).
The same holds averaged over random nets for a FIXED partition (W_1 -> W_1 Q preserves the law of the net).
Proof. Between-cell variance = |Pi' f~|^2 with Pi' the L^2(gamma) projector onto span{1_{R_k} - p_k} (rank K - 1;
f~ has mean 0). For the rotated partition this is |Pi' R_Q^{-1} f~|^2 with (R_Q phi)(x) = phi(Q^T x). T = E_Q R_Q Pi' R_Q^{-1}
commutes with every rotation (Haar invariance). V_d = {r Y(u) : Y in H_d} (d >= 1) and V_0 = span{r - m_n} are
invariant subspaces carrying inequivalent irreducible representations (H_d, n >= 3), so Pi_{V_d} T Pi_{V_d'} = 0 for
d != d' (Schur) and Pi_{V_d} T Pi_{V_d} = c_d I with c_d = tr(Pi_{V_d} T)/N_d = tr(Pi_{V_d} Pi')/N_d (the trace is
rotation invariant because V_d is). tr(Pi_{V_d} Pi') <= min(rank Pi', dim V_d) = min(K - 1, N_d). Hence
E_Q |Pi' R_Q^{-1} f~|^2 = sum_d c_d E_d <= sum_d min(1, (K-1)/N_d) E_d (componentwise, summed over outputs). QED.
Reading. A K-cell partition that does not look at the net explains at most (K-1)/N_d of the degree-d energy:
degree 1 needs K ~ n cells, degree 2 K ~ n^2/2, degree 3 K ~ n^3/6, whatever the shape of the cells (boxes, cones,
trees, Voronoi cells). With the spectrum along L = alpha n [prior: randomness E2.4: degree 1 ~0.29, degree 2 ~0.21 of
the angular variance in the limit, the rest at degree >= 3; measured at 256 x 32: degrees <= 2 carry 0.47], every
weight-blind partition with K <= n^2/2 has G_P <= 1/(e_2 (1 - (K-1)/N_2) + e_{>=3} (1 - 3/n)) ~ 1/e_{>=3} ~ 2 (1.9 with
the 256 x 32 shares): a ceiling that does not grow with n, so no beta > 0 can persist over K <= poly(n) uniformly in
width (beta_eff -> 0). With Neyman allocation (which looks at f through sigma_k) the gain
can exceed this by the factor 1 + CV_p(sigma)^2 of S1(a), which Theorem 1 does not control; S2.4 and the diagnostic
address it. Fixed strata with fixed allocation are also linear rules with weight-independent nodes, so the ensemble
barriers of [prior: preint F7; randomness T4, E1.1] apply to them as well (positive weights: every even power from
degree 6 on paid in full for N <= ~5.7e5 at n = 256).

### S2.2 Partitions chosen with the net: the subspace ceiling (PROVEN [C])
Proposition 2. If every cell is measurable with respect to x_S = Pi_S x for a subspace S (e.g. a tree whose split
hyperplanes all have normals in S, any thresholds, any depth, chosen with full knowledge of W), then with
tau_S(x) = tr Var(f | x_S):
  sum_k p_k sigma_k^2 >= E tau_S = V (1 - Sbar_S),   (sum_k p_k sigma_k)^2 >= (E sqrt(tau_S))^2,
where Sbar_S = tr Var(E[f | x_S]) / V is the closed Sobol index of the subspace. Proof: law of total variance inside
each cell (R_k is x_S-measurable), sigma_k^2 = E[tau_S | R_k] + tr Var(E[f|x_S] | R_k) >= E[tau_S | R_k]; then
sqrt(E[tau_S | R_k]) >= E[sqrt(tau_S) | R_k] (Jensen) and sum over k. QED.
Reading. The best any tree can do with splits along s fixed directions, however many cells it uses, is the
infinitely fine stratification of those s coordinates: G_P <= 1/(1 - Sbar_S), G_N <= V/(E sqrt tau_S)^2. A beta > 0
that persists needs Sbar_S -> 1 along a sequence of subspaces whose dimension the cell budget can follow. The
Gaussian Poincare inequality gives 1 - Sbar_S <= tr(Pi_{S-perp} E[J^T J]) / V, and E|J|_F^2 = n on average over nets
(criticality [prior: gram-chain]) against V ~ 11-20 [prior: randomness E2.3], so this upper bound is vacuous until S
holds all but ~V/n of the gradient energy; the future-aware lane measured that energy spread over PR ~ n/4 directions
at the first layer [prior: future-aware]. Sbar_S for the top-s directions of each frame is measured directly
(pick-freeze), which gives the ceiling of every tree that splits only along them.

### S2.3 An information ceiling (PROVEN [C]); where it is weak
Proposition 3. For ANY partition into K cells (white-box, adaptive, any cell shapes) and every r <= n and every
r-dimensional orthogonal projection P_r of the output space for which y = P_r f(x) has a density,
  (sum_k p_k sigma_k)^2 >= r N(y) K^{-2/r},   N(y) = exp(2 h(y)/r) / (2 pi e)   (entropy power of y).
Proof. sigma_k^2 >= tr Var(y | R_k) >= (r / (2 pi e)) exp(2 h(y | R_k)/r) (the Gaussian maximises entropy at given
covariance; AM-GM on its eigenvalues). So sum p_k sigma_k >= sqrt(r/(2 pi e)) sum_k p_k exp(h(y|R_k)/r)
>= sqrt(r/(2 pi e)) exp(sum_k p_k h(y|R_k) / r) (Jensen) and sum_k p_k h(y | R_k) = h(y | cell) = h(y) - I(y; cell)
>= h(y) - log K. QED.
Corollary (linear f). If f = A x and A^T A has eigenvalues lambda_1 >= ... >= lambda_n, take y = the top-r part: any
K-cell partition has G_N <= K^{2/r} V / (r lambda_r). For a flat rank-r spectrum, G_N <= K^{2/r}: beta <= 2/r. A
K-cell partition carries at most log K nats about x, and cutting the variance of an r-dimensional Gaussian signal by
a factor G needs (r/2) log G nats.
Where it is weak. At depth the output law is nearly one-dimensional (final-layer covariance PR 1.9 at 256 x 32 [prior:
arc-update P9]), so with r = 1 or 2 the bound allows beta up to 1-2: the output side does not forbid a gain. The
obstruction is on the input side: the cells must be sets in x whose probabilities are computable, and the amplitude
that carries the variance is a function of x of high degree spread over ~n directions (S2.1, S2.2). The ideal
partition (level sets of the amplitude) would need the law of f(x), which is the problem itself.

### S2.4 Neyman's extra factor (identity PROVEN; magnitude HEURISTIC)
G_N / G_P = 1 + CV_p(sigma)^2. It is large only if the local standard deviation is very uneven across regions: a small
probability carrying a large share of sum p_k sigma_k. Under the Gaussian surrogate prior with a rotation-invariant
kernel the local roughness is the same in every direction and adaption gains nothing on average
(Wasilkowski-Wozniakowski 1984 [prior: preint E1]); so any gain beyond Theorem 1 must come from non-Gaussian, per-net
unevenness of the local roughness. Homogeneity fixes the radial part: sigma(cell) scales with the radius, and Neyman
over radial shells gains E r^2 / (E r)^2 = n / m_n^2 = 1 + 1/(2n) + O(n^-2) (negligible). The angular part: the
net's local amplitude |h_L(x)| / |x| fluctuates over directions with log-variance ~ 5L/n [prior: preint E1(d), E3(c):
0.54-0.73 at L = n/8]. HEURISTIC: if sigma_k tracks a lognormal amplitude with log-variance v (of the squared amplitude),
1 + CV^2 -> exp(v/4) ~ 1.15-1.2 at L = n/8, a constant in n (v is set by L/n). A gain from Neyman that grows with K
would need rare high-variance regions; the diagnostic measures the share of sum p_k sigma_k carried by the top q of
regions.

## S3. "Understanding" a region (PROVEN facts; HEURISTIC counts)
(a) On a full activation region C (every gate of every layer fixed) f(x) = A_C x exactly, A_C = D_L W_L ... D_1 W_1,
    and C is a polyhedral cone. So E[f 1_C] = A_C E[x 1_C] = A_C p_C c_C: the linear map is cheap (one Jacobian, n
    vector-Jacobian products or one product chain), and the region's Gaussian probability p_C and centroid c_C carry
    all the difficulty.
(b) Count. W_1 is invertible almost surely, so all 2^n first-layer sign patterns have positive probability (PROVEN):
    every full region lies inside one of 2^n first-layer cones, and full regions refine them. So covering mass
    1 - eta with full regions needs at least (1 - eta) / max_C p_C regions, and max_C p_C <= max over first-layer
    patterns of an orthant probability of N(0, W_1 W_1^T). HEURISTIC: the first-layer signs are nearly independent fair
    coins (pairwise correlations O(n^-1/2)), so the first-layer pattern has entropy ~ n bits and full patterns more;
    the diagnostic measures the effective number of patterns through layer l by a collision (birthday) estimate.
(c) Cost of p_C and c_C. C has up to nL facets in R^n. Its Gaussian measure is an orthant probability of a correlated
    Gaussian vector of dimension (number of facets); exact volume of polytopes is #P-hard (Dyer-Frieze 1988, memory);
    randomised approximation to relative error eps costs poly(n)/eps^2 oracle calls (memory). Either way one region
    costs far more than one pass and carries mass 2^{-Theta(n)} (HEURISTIC, from (b)).
(d) No region family has both cheap (p, c) and near-linearity (HEURISTIC with a PROVEN core). Cheap families have few
    facets: boxes in an orthonormal frame (p and c exact in product form), cones of k first-layer gate signs (k-dim
    orthant probabilities; centroid E[x | cone] = W_S^T (W_S W_S^T)^{-1} E[z_S | signs], z_S = W_S x, a k-dim
    truncated-normal mean). f is linear on a cell only if no gate boundary crosses it; the expected Gaussian perimeter of
    the gate partition is ~ nL/sqrt(2 pi) [prior: randomness T7, E1.2], so a cell of Gaussian mass p and diameter
    rho (at radius ~ sqrt n) is crossed by ~ 0.8 n^{3/2} L (rho / sqrt n) boundaries (S5(c)). A cell with few facets and
    mass >> 2^-n has diameter of order sqrt n, hence ~ nL boundaries inside: f is far from linear there.
(e) A local linear control variate on a coarse cell (fit B_k on independent samples; exact cell centroid) removes only
    the part of f that is linear inside the cell. For K = 1 that is the degree-1 energy E_1 (gain 1/(1 - e_1),
    ~1.3-1.4 from the shares in S2.1). Whether it grows with K is measured (diagnostic (iii)).

## S4. Branch similarity (PROVEN identity; HEURISTIC scaling)
(a) Two inputs whose layer-(l-1) states have cosine rho: the expected number of layer-l gates that disagree, over
    the layer-l weights, is n arccos(rho)/pi (each unit's two pre-activations are jointly Gaussian with correlation
    rho; [prior: gram-chain]). The ReLU kernel map preserves small angles to first order (kappa'(1) = 1), so for input
    angle theta the expected disagreements total ~ nL theta/pi over the net (theta small), and for two random inputs
    the per-layer disagreeing fraction arccos(rho_{l-1})/pi decays only like ~3/l (infinite-width kernel).
(b) Prediction error of one region's linear map (HEURISTIC). f(x') - A(x) x' is a sum over the gates that differ
    between x and x' (same radius sqrt n, angle theta, random direction of motion) of (pre-activation overshoot) x
    (downstream Jacobian column). By (a) about nL theta/pi gates differ; a flipped unit's overshoot is of order its
    pre-activation change, ~ theta (the motion's component along one normal is ~ theta/sqrt n of the unit sphere,
    times |x| ~ sqrt n), and downstream columns have squared norm ~1 (E_W |J u|^2 = |u|^2 [prior: gram-chain]), so
    E|f(x') - A(x) x'|^2 ~ c nL theta^3. This is the kink term delta^{3/2} of the noise-sensitivity expansion
    [prior: randomness E1.3] with delta = 1 - cos theta. Two transfer radii follow: relative to the local change
    |A(x)(x' - x)|^2 ~ |A|_F^2 theta^2 ~ n theta^2, the relative error is ~ c L theta (transfer over theta << 1/L);
    relative to the total variance V (~11-20), theta* ~ (V/(c nL))^{1/3} ~ n^{-2/3} at L = alpha n. Either way,
    covering the sphere with caps of the transfer radius takes ~ (C L)^{n-1} or ~ (C n^{2/3})^{n-1} "similar branches":
    shared structure transfers between branches only over small angles. For a CELL (a cap of angular radius delta)
    the count is different: a cap reaches every hyperplane within angle delta of its centre, so ~ 0.8 n^{3/2} L delta
    boundaries cross it (S3(d)), sqrt(n) times more than a pair at the same angle crosses.
    Measured: relative prediction error and per-layer disagreements vs theta.

## S5. Settling a region (MCTS-Solver analogue)
(a) Criterion (PROVEN, triangle inequality). If certified intervals [l_k, u_k] contain mu_k for k in a set S of
    regions with exact p_k, the estimator that uses midpoints on S and unbiased sampling elsewhere has
    |bias| <= sum_{k in S} p_k |u_k - l_k|/2. With half-widths |u_k - l_k|/2 <= tau = sqrt(eps V) (Euclidean norm over
    outputs), the settled part adds at most eps V p_S <= eps V to the squared error: a region settles at level eps when
    its certified half-width is <= sqrt(eps V). Settled mass at level eps = sum of p_k over such regions.
(b) Homogeneity (PROVEN). For a cone C, mu_C = m_n E[g(u) | u in C], so certifying g on the section C cap S^{n-1}
    (enclosed in a box) suffices; cells split at threshold 0 in a frame, or by gate signs, are cones.
(c) Bound growth (HEURISTIC). Interval bound propagation (IBP) maps half-width vectors by |W_l| (and halves straddling
    units at most); an input box of half-width delta gives pre-activation half-widths ~ delta sqrt(4n/pi) after one
    layer and grows by a factor ~ c sqrt(n) per layer while units straddle 0: (c sqrt n)^L overall. CROWN (backward
    linear relaxation from the actual weights) is exact when no unit straddles 0 on the cell and loses roughly in
    proportion to the straddling units' ranges; at radius sqrt(n) a cap of angular radius delta has ~ 0.8 n^{3/2} L delta
    straddling units (S3(d)), so CROWN is near-exact only for delta << 1/(n^{3/2} L) (7.6e-6 at 256 x 32), which needs
    ~ (1/delta)^{n-1} cells. The certified branch-and-bound [prior: unrestricted] lost 1e3-1e6x from width 4 to 32 and
    certified nothing from width 6 on; at n >= 32 I expect zero settled mass at every affordable K.
(d) Settling at depth (PROVEN, elementary). Cells B_k of the layer-l state can be bounded through only L - l layers,
    and the deep state is concentrated (covariance PR 4-12 at l = 16-24 at 256 x 32 [prior: arc-update]), so bounds
    there are far tighter. But p_k = P(h_l in B_k) is the layer-l law. If it is estimated from N inputs pushed to
    layer l (frequencies phat_k), the estimator sum_k phat_k m_k (m_k = certified midpoint) has variance
    Var(m_{k(x)})/N, which tends to V/N as the cells shrink: the MC rate, saving only the tail layers' cost per sample
    (at most a factor L/l in passes) and adding the certification bias. A rate gain from deep settling needs p_k
    computed without sampling, i.e. the layer law itself: ARC's closure problem, which arc-update measured on the
    error-cost ladder. The diagnostic reports, per layer l, the radius at which CROWN certifies a box around a layer-l
    state to each eps and the implied covering number of the layer-l cloud.

## S6. What a gain would have to come from (summary, HEURISTIC with the PROVEN pieces above)
- Weight-blind regions: capped by Theorem 1 (proportional) and by the linear-rule barriers (fixed allocation).
- Any regions along s fixed directions: capped by the closed Sobol index of those directions (Proposition 2).
- Under the Gaussian surrogate prior adaption gains nothing (W-W 1984). So a gain must come from (i) white-box
  structure that puts most of the variance into few directions or few cells (Sbar_S -> 1 at small s; measured),
  (ii) non-Gaussian unevenness of local variance (Neyman's 1 + CV^2; measured), or (iii) local models whose region
  means are exact (S3: cheap only on cells where f is far from linear).
- For beta > 0 uniform in width one of these must hold with constants that do not degrade as n grows along
  L = n/8. Prediction (to be registered with numbers after dev calibration): none does; beta_eff falls with n and the
  gain at fixed K falls with n for every family, and no cell is ever settled at n >= 32.
