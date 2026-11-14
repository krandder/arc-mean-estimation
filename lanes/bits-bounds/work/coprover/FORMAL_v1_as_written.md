# Bits-bounds theory v1 (frozen before reading the co-prover's round-1 answer)

Lane bits-bounds, 1 November 2026, written 21:07-21:18Z by Claude (opus-mats lane agent). Labels: PROVEN, PROVEN UNDER
<hypothesis>, HEURISTIC, CONJECTURE. Provenance in this file: [C] unless marked; results quoted from earlier lanes are
marked (K1)-(K11) as in coprover/STATEMENT_r1.md. Dev calibration (seeds >= 9000, not evidence) is in
logs/dev_explore.log and is marked DEV.

## 0. Claims in one screen

1. Model (section 2): p-pass layer sweeps with M bits or reals of state. All four families fit (Prop 2.2).
2. Information bounds (section 3, PROVEN): a p-pass sweep is a (2p-1)-round protocol across every cut, so
   M >= CC_{2p-1}(eps)/(2p-1). With (K2) this gives (n(n+1)/2) log2(1/eps) - O(1) bits for one forward pass and
   (n log2(1/eps) - O(1))/(2p-1) for p passes. These are capped at (n^2 L + o(1)) log2(1/eps): no information bound on an
   unrestricted state can ever be a count of the input's bits. N(l, eps) can only be a lower-bound parameter for a
   representational class (measure-propagation sweeps, section 4) or for time (out of reach, (K6)).
3. Exact identities (section 4, PROVEN): the error of any measure-propagation sweep is a telescoping sum of closure
   defects tested against the exact future; the linearisation residual of a state h at a reference c is
   (J_l(h) - J_l(c)) h, caused only by the future gates on which the two trajectories disagree.
4. One-layer law (Thm 5.1, PROVEN, every width): E_W |relu(W h) - D(c) W h|^2 = (2|h|^2/pi)(phi - sin phi cos phi)
   ~ (4/(3 pi)) |h|^2 phi^3, phi = angle(h, c); the radial merge has 2|h|^2 (1 - kappa(cos phi)) ~ |h|^2 phi^2.
5. Mean-field law (Thm 5.2, PROVEN UNDER the infinite-width limit at fixed L'): with L' layers to go the frozen-gate
   (linearised) residual is (4/(3 pi)) L' phi^3 (1 + O(L' phi)) and saturates at about phi^2; the radial residual is
   phi_{L'}^2 with 1/phi_{L'} ~ 1/phi + L'/(3 pi). They cross near L' phi ~ 2: below it the future is smooth
   (cubic) on a cell of size phi, above it the future merges directions and only gains differ.
6. Definition (5.3): N(l, eps) = log2 of the least number of cells into which the cloud P_l must be cut so that
   merging each state with its cell's reference (frozen-gate or radial) leaves residual <= eps^2 V. Forward-only
   version N_fwd: cells from the past, residual averaged over the future (an exact finite-width chain function).
   "Bits" = which cell; "matter" = output residual at precision eps; past = the cloud's spread; future = the residual
   law (cubic below the scale 2/L', merging above).
7. Lower bounds (section 6): forward-only cell sweeps need log2 M >= R_rho(eps^2 V), the rate-distortion function of
   the cloud under the future-induced distortion (PROVEN); with a d-dimensional density and cubic distortion,
   N_fwd >= (d/3) log2(1/eps^2) + O(1) (PROVEN UNDER the density and cubic hypotheses). Two-sided cells aligned with
   the actual future's linear regions are exact: N(l, 0) <= log2(#regions met by the cloud). So the forward-only /
   two-sided separation is unbounded as eps -> 0 at a fixed net (PROVEN for this class).
8. Hash (section 9): "a hash over N bits is hard to average" is false: if the per-instance mean is an average of 2^N
   pairwise-uncorrelated values, the ensemble prediction plus partial enumeration beats MC by >= 4x at every budget
   (PROVEN). What survives: resolution methods (cells, enumeration, branch-and-bound) pay 2^{N(l, eps)}, and N(l, eps)
   is large exactly where the cloud is larger than the future's linearity scale (all but the last ~1/6 of the layers
   in the input regime, HEURISTIC). Averaging methods (closures) do not pay N but carry a fixed-order bias (K3).
   Sampling pays only the per-level residual variance (the multilevel sampler of (K5) is a radial-merge sweep).
9. Bottleneck (section 10): whether an averaging (closure-type) sweep can integrate the rough part of the future over
   the cloud without a systematic bias at L = alpha n (conjecture C0* restated in sweep terms).

## 1. Setting and notation

Width n, depth L, W_l iid N(0, 2/n), no bias, x ~ N(0, I_n); h_l = relu(W_l h_{l-1}); a = h_L. Cut at layer l: cloud
P_l = law of h_l(x); future g_l = T_L o ... o T_{l+1}, T_j(h) = relu(W_j h); mu = E_{P_l} g_l. g_l is positively
1-homogeneous and piecewise linear; J_l(h) = D_L(h) W_L ... D_{l+1}(h) W_{l+1}, D_j(h) the gate pattern of h's
trajectory, so g_l(h) = J_l(h) h (Euler). For a reference state c, J_l(c) is the frozen-gate future of c. L' = L - l.
V = tr Var_x a. kappa(t) = (sqrt(1 - t^2) + (pi - arccos t) t)/pi (normalised arc-cosine kernel), so for He rows
E relu(w.h) relu(w.h') summed over n units = |h||h'| kappa(cos angle(h, h')).

## 2. The model

Definition 2.1 (layer sweep). A p-pass sweep processes the layer sequence in p passes; pass k visits all layers in
order 1..L (forward) or L..1 (backward). Between two visits it holds a state s (M bits, or M reals in a stated class).
Visiting layer j it computes s' = U_j(s, W_j, randomness) at cost c_j (in n x n matrix-vector products, "mv"); the
estimate is a function of the final state. Per-layer work poly(n) is the default budget. Two-sided means some
backward pass precedes the forward pass that produces the estimate (the forward state may then depend on a summary of
W_{>l}).

Proposition 2.2 (membership; PROVEN by inspection of each algorithm).
- MC / RQMC / fixed designs: p = 1 forward, M = N n reals (the N states), cost N mv per layer.
- Multilevel shared-trajectory sampler (K5): p = 1 forward. State: the reference state, its running suffix product
  (kept as a running product of norms; s_r = product after r is formed at the end from stored norms, L reals), the
  N_j states of level j until depth r_j, then one scalar |h_{r_j}| per sample (the merge), and the running level
  sums. M = O(n + L + sum_j N_j n) reals, cost sum_j N_j mv per layer up to r_j plus the last level's full passes.
  The merge at r_j replaces the particle h by |h| times the reference direction: a closure (section 4).
- ARC cumulant propagation of order K (K3): p = 1 forward, M = O(n^K) reals, cost O(n^{K+1}) per layer; the
  truncation is the closure.
- Gaussian closure (mean and covariance): p = 1, M = n + n(n+1)/2, cost O(n^3) per layer. With gate splits (a mixture
  of up to M_c Gaussians, splitting a component on chosen straddled units): M = M_c (n + n(n+1)/2); forward-only if
  the split choice uses the past only, two-sided (p = 2) if it uses a backward relevance summary.
- Branch-and-bound over input cones (K6): each refinement round is one forward pass over the current cells (state:
  the cells and their symbolic bounds, M = (#cells) x O(n^2) reals); adaptive over rounds, so p = number of rounds.
  Its centre-point estimate is a frozen-gate merge per cell (section 5).
- Exact enumeration of linear cones: p = 1, M = number of cones carrying mass.

## 3. Information bounds and their cap

Theorem 3.1 (streaming to communication; PROVEN, standard). Fix a cut between layers l and l+1. In a p-pass sweep the
state crosses the cut at most 2p - 1 times (once per pass, plus once between two consecutive passes of the same
direction). So the sweep defines a (2p-1)-round protocol between the holder of W_{<=l} and the holder of W_{>l} in
which every message is a state, and M >= CC^dist_{2p-1}(eps)/(2p - 1), where CC^dist_r(eps) is the r-round
distributional communication complexity of computing mu to the criterion over the weight ensemble.

Corollary 3.2 (PROVEN from (K2), genuine ensemble, fixed (n, l >= 3, L'), eps -> 0). One forward pass:
M >= (n(n+1)/2) log2(1/eps) - O(1) bits. Any p passes: M >= (n log2(1/eps) - O(1))/(2p - 1) bits.

Proposition 3.3 (the cap; PROVEN). A one-pass sweep with M = (n^2 L + o(1)) log2(1/eps) bits that stores the weights
and computes at the end is exact to the criterion (unlimited final computation). So every information lower bound on
an unrestricted state is at most this, a polynomial in n; a lower bound of the form 2^{N(l, eps)} with N a count of the
input's or noise's bits can hold only (a) for a class whose state has a stated meaning (a representation of the
cloud), or (b) as a time bound, which would be a super-linear time lower bound for an explicit distributional problem
(out of reach, (K6)).

## 4. Measure-propagation sweeps (the representational class)

Definition 4.1 (MPS). The state at layer l is a finite signed combination nu_l = sum_i w_i pi_i of components from a
family F of finitely described measures on R^n (Dirac masses, Gaussians, Gaussians restricted to polyhedral cones,
or, for cumulant propagation, quasi-measures given by truncated cumulant sequences). The update is
nu_l = C_l(T_l # nu_{l-1}), where the closure C_l maps the exact push-forward back into F-combinations (identity when
the push-forward is already in F; splits and merges are closures). The estimate is the mean of nu_L. Randomised MPS
may draw components (sampling). C_l is forward-only if it depends on W_{<=l} only, two-sided if it may depend on a
summary of W_{>l}. All families of Prop 2.2 are MPS: MC and designs (Dirac masses, no closure), the multilevel sampler
(a signed combination of Dirac systems at several depths, with the radial merge delta_h -> delta_{|h| c/|c|} as the
closure at r_j), closures and mixtures (Gaussians), branch-and-bound and enumeration (cone-restricted Gaussians, split
closures; the centre-point estimate is a frozen-gate merge), cumulant propagation (quasi-measures, truncation).

Theorem 4.2 (telescoping defect identity; PROVEN). For any MPS,
    est - mu = <nu_0 - gamma, g_0> + sum_{l=1}^{L} <nu_l - T_l # nu_{l-1}, g_l>,   <nu, g> = integral of g d nu.
Proof: g_{l-1} = g_l o T_l gives <T_l # nu_{l-1}, g_l> = <nu_{l-1}, g_{l-1}>; est = <nu_L, g_L> with g_L = id and
mu = <gamma, g_0>; sum the differences. Sampling puts all error in the first term, closures in the defects.

Lemma 4.3 (Euler residual; PROVEN). For any states h, c at layer l,
    g_l(h) - [g_l(c) + J_l(c)(h - c)] = g_l(h) - J_l(c) h = (J_l(h) - J_l(c)) h.
It vanishes when h and c have the same future gate pattern. Layer decomposition: with e_l = 0,
e_j = D_j(c) W_j e_{j-1} + r_j, r_j = (D_j(h) - D_j(c)) W_j h_{j-1}, one has g_l(h) - J_l(c) h = e_L =
sum_{j>l} J_{j->L}(c) r_j, and r_j is supported on the units where the two trajectories' gates disagree.
Proof: induction; h_j = D_j(h) W_j h_{j-1} and the frozen vector v_j = D_j(c) W_j v_{j-1} differ by e_j.

Proposition 4.4 (forward-only defects are kernel discrepancies; PROVEN given (K1)'s kernel identity). If the closure at
layer l does not depend on W_{>l}, then E_{W>l} |<nu_l - T_l # nu_{l-1}, g_l>|^2 = MMD^2 under
K_{L'}(h, h') = |h||h'| kappa_{n,L'}(cos angle(h, h')), the future-averaged back kernel at width n.

## 5. Merges, residual laws, and the definition of N(l, eps)

Two merges of a state h into a reference c (both cost one future evaluation per reference, not per state, when only
the mean is wanted: E[J_l(c) h 1_cell] = J_l(c) E[h 1_cell]):
- frozen-gate (linearised) merge: m_F(h; c) = J_l(c) h;
- radial merge (the multilevel sampler's): m_R(h; c) = (|h|/|c|) g_l(c).

Theorem 5.1 (one future layer, exact at every width; PROVEN). For fixed h, c at angle phi and one layer W with iid
N(0, 2/n) entries:
- E_W |relu(W h) - D(c) W h|^2 = (2|h|^2/pi)(phi - sin phi cos phi) = (4/(3 pi)) |h|^2 phi^3 (1 + O(phi^2));
- E_W #{units whose gates differ} = n phi/pi;
- E_W |relu(W h) - (|h|/|c|) relu(W c)|^2 = 2|h|^2 (1 - kappa(cos phi)) = |h|^2 (phi^2 - (2/(3 pi)) phi^3 + O(phi^4)).
Proof: per unit, with (X, Y) standard bivariate normal of correlation cos phi, the first is
(2|h|^2/n) E[X^2 1{sign X != sign Y}] = (2|h|^2/n)(phi - sin phi cos phi)/pi, using
E[X^2 1{X>0, Y>0}] = (pi - phi + sin phi cos phi)/(2 pi) and E[X^2 1{X>0}] = 1/2; the count is n P(sign X != sign Y)
= n phi/pi; the third expands |relu(Wh)|^2 + (|h|/|c|)^2 |relu(Wc)|^2 - 2 (|h|/|c|) relu(Wh).relu(Wc).

Theorem 5.2 (mean-field law; PROVEN UNDER the infinite-width limit at fixed L', annealed over W_{>l}). Let |h| = |c|,
angle phi. In the limit the true pair keeps equal norms and its angle follows cos phi_{j+1} = kappa(cos phi_j); the
frozen vector v_j keeps |v_j| = |h| and v_j.c_j = h.c (odd symmetry), and psi_j = angle(h_j, v_j) follows the explicit
recursion of lib/meanfield.py (writing Z = a X + b Y + e: cos psi' = 2 [a E X^2 1{X,Y>0} + b E XY 1{X,Y>0}]). Then
- frozen residual E|g_l(h) - J_l(c) h|^2 / |h|^2 -> 2(1 - cos psi_{L'}), which is (4/(3 pi)) L' phi^3 (1 + O(L' phi))
  as L' phi -> 0 (NUMERICAL from the recursion; HEURISTIC argument: the per-layer residuals of Thm 5.1 add, the cross
  term between the carried error and the new disagreement region being of higher order), saturating at
  2(1 - cos phi) ~ phi^2 when L' phi >> 1 (the frozen vector never merges);
- radial residual -> 2(1 - cos phi_{L'}) ~ phi_{L'}^2, 1/phi_{L'} = 1/phi + L'/(3 pi) + o(1) (directions merge).
NUMERICAL (lib/meanfield.py): frozen/(L' phi^3) = 0.4244 at L' = 1; 0.41-0.47 at small L' phi for L' = 4-48; the two
residuals cross near L' phi ~ 2 (L' = 16: between phi = 0.1 and 0.3; L' = 48: near phi = 0.05).
DEV (n = 64, 128, 2 nets): the exponent 3 holds on the nets (log-log slope 2.9 at n = 128, L' = 48, phi = 4e-4 to
5e-3); the per-net coefficient is 2-5x the mean-field one at n = 128 and larger at n = 64; gate disagreements follow
(n/pi) L' phi to within 10-30% until L' phi ~ 1.

Reading. The future has a linearity scale phi_lin(L') ~ 2/L' at remaining depth L'. Below it the future is smooth on a
cell (residual cubic in the cell size, coefficient ~ L', set by the density (n/pi) L' of future kinks per radian and
the phi^2 size of each kink's effect). Above it, the future merges directions (finite-angle contraction) and the
states differ only through gains; with many independent gate flips each moving the gain a little, the gain behaves as
a rough field on the cloud (variogram growing like the distance, HEURISTIC; the input-bits lane's log-gain variance
(2/n)(5 - B(cos theta)) summed along the contracting angles gives a sum linear in phi).

Definition 5.3 (the bits that matter at layer l). Let V be the per-net output variance. A quantiser Q of the state
space at layer l (cells C_1..C_M, references c_k in the support of P_l) and a merge rule m (frozen, radial, or the
better per cell) define the merge residual
    D_l(Q) = E_x |g_l(h_l(x)) - m(h_l(x); c_{Q(x)})|^2.
- Two-sided: N(l, eps) = log2 min{ M : some Q with M cells (which may depend on W_{>l}) has D_l(Q) <= eps^2 V }.
- Forward-only: N_fwd(l, eps) = log2 min{ M : some Q depending on W_{<=l} only has E_{W>l} D_l(Q) <= eps^2 E_{W>l} V }.
  E_{W>l} D_l(Q) = E_x rho_{L'}(h_l(x), c_{Q(x)}) with rho_{L'}(h, c) = E_{W>l}|g_l(h) - m(h; c)|^2, a function of
  (|h|, |c|, angle(h, c)) only (rotation invariance of the future's law), computable exactly at finite width by the
  replica Gram chain of (K11) with three replicas (h, c and the frozen vector) and in the mean-field limit by Thm 5.2.
Why this is the natural count. (i) The bits are the cell index: which class of future gate patterns the state is in.
(ii) They "matter" when merging across them costs output residual above eps^2 V. (iii) The past enters through the
cloud: its spread s_k(l) in each direction (the "Lyapunov covariances"). (iv) The future enters through the residual
law: cubic below phi_lin(L'), merging above, and, two-sided, through where its kinks actually are. (v) N(l, eps) = 0
iff one merge suffices; with the frozen merge at the cloud's mean this is mean propagation from layer l, since
E_x J_l(m_l) h_l(x) = J_l(m_l) m_l = g_l(m_l) (its mean error is at most sqrt(D_l)).

Heuristic formula (HEURISTIC; DEV-calibrated). Cover the cloud by cells of radius phi in each principal direction:
log2 M ~ sum_k log2^+(s_k(l)/phi) (the covering number of the cloud's covariance ellipsoid; the radial direction is
free by homogeneity). In the smooth regime the residual per cell is ~ kappa_3 L' phi^3 |g|^2 (kappa_3 = 4/(3 pi) in mean
field), so
    N(l, eps) ~ sum_k log2^+( s_k(l) / phi_eps ),   phi_eps = ( eps^2 V / (kappa_3 L' |g|^2) )^{1/3},
a reverse water-filling of the cloud's spectrum against the future's eps-linearity radius. With d_eff directions above
phi_eps this is (d_eff/3) log2(1/eps^2) + O(d_eff). DEV: the M-reference residual on the nets falls like M^{-3/d} with
d ~ 5-10 (about twice the angular participation ratio) at l = L/2 and 3L/4; at l <= L/2 one reference leaves a
residual >= V (the cloud is larger than phi_lin). The angular spectrum decays like exp(-(0.27..0.45) k), not at the
Lyapunov rate exp(-2 k l/n): in the input regime the cloud's shape is set by the finite-angle kernel contraction,
not by the infinitesimal Lyapunov spectrum (DEV, 2 nets).

## 6. Lower bounds

Theorem 6.1 (forward-only cell sweeps; PROVEN). Let Q be any M-cell quantiser computed from W_{<=l} (deterministic or
randomised independently of W_{>l}). Then E_{W>l} D_l(Q) >= D_rho(log2 M), where D_rho is the distortion-rate
function of the source P_l under the distortion rho_{L'}. Equivalently N_fwd(l, eps) >= R_rho(eps^2 E V), the
rate-distortion function. Proof: the reconstruction X^ = c_{Q(X)} satisfies I(X; X^) <= H(X^) <= log2 M and achieves
distortion E rho(X, X^) = E_{W>l} D_l(Q); by definition of the distortion-rate function the latter is >= D_rho(I).
Corollary 6.2 (PROVEN UNDER (H1) P_l has a density p on a d-dimensional affine subspace with finite differential
entropy h(p), and (H2) rho_{L'}(h, c) >= a min(|h - c|, r_0)^3 globally; the curved-manifold version is HEURISTIC). Then by the Shannon lower bound for a
power-law difference distortion, R_rho(D) >= h(p) - (d/3) log2(D/a) - C_d for D small enough, so
N_fwd(l, eps) >= (d/3) log2(a / (eps^2 E V)) + h(p) - C_d. In particular N_fwd(l, eps) -> infinity as eps -> 0 and
2^{N_fwd} grows like eps^{-2d/3}: cells chosen from the past beat MC's eps^{-2} only if d < 3.
Theorem 6.3 (two-sided, exact; PROVEN). If every cell of Q lies inside one linear region of g_l, the frozen merge is
exact (Lemma 4.3), so N(l, 0) <= log2 #{linear regions of g_l meeting supp P_l} < infinity, while under (H1)-(H2)
N_fwd(l, eps) -> infinity. Hence knowing the future (one backward pass) removes an unbounded number of bits as
eps -> 0 at a fixed net: the forward-only / two-sided separation in the cell class is unbounded. HEURISTIC size of the
two-sided count: with K future kinks crossing a d-dimensional cloud, at most sum_{i<=d} C(K, i) regions (exact for
hyperplane arrangements; the pulled-back kinks are bent), and K ~ (n/pi) sum_j phi_j (Thm 5.1 per layer).
Proposition 6.4 (exact cell methods; PROVEN). A method that is exact because each cell is linear (branch-and-bound
certified cells, cone enumeration) uses at least as many cells as there are linear regions of the whole net carrying
positive mass.
Proposition 6.5 (averaging methods are outside the cell class; PROVEN by (K3) and example). A Gaussian closure
integrates every kink of the next layer analytically, so it never pays N(l, eps); its error is the closure defect of
Thm 4.2, and ARC's basic order-K truncation has a positive bias floor at every fixed K (K3).
Proposition 6.6 (query access to the future; PROVEN, from the hardness lane's black-box theorems (K6)). If the future is
accessed only through evaluations at chosen states, there are explicit families on which no algorithm beats MC by more
than a small constant. So any gain from relevance must use the future's weights (white box), not only its values.

## 7. Upper bound: the two-sided multilevel merge estimator

Estimator. Choose layers r_1 < ... < r_J, and at each r_j a quantiser Q_j with M_j references and merge m_j. With
G_j(x) = m_j(h_{r_j}(x); c_{Q_j(x)}) and G_{J+1}(x) = a(x),
    mu = E G_1 + sum_{j=1}^{J} E[G_{j+1} - G_j],
estimated with independent samples per level (both terms of a level on the same sample). Unbiased (PROVEN). Costs:
level j's samples cost r_{j+1} mv-layers (the prefix), the merges cost one future evaluation per reference and level
(frozen: J(c_k) applied to the cell's running sum; radial: g(c_k) once), so setup sum_j M_j (L - r_j). Level
variances are at most 2(D_{r_j}(Q_j) + D_{r_{j+1}}(Q_{j+1})) (PROVEN). With M_j = 1 and the radial merge this is the
sampler of (K5), whose residual is O(1/r + n/L^2).
Deterministic version: replace the level means E G_1 and the cell sums by a closure's prediction of the cell
statistics, and drop the correction levels; its bias is the closure defect plus the mean of the residual
(|E R| <= sqrt(D)). Cost ~ 2^{N(l, eps)} future evaluations plus the closure.
When it can win (HEURISTIC). Against the one-reference multilevel sampler the gain of M references is
D_r(1)/D_r(M): about M^{3/d} in the smooth regime and about M^{1/d} in the rough regime (Hölder-1/2 gains), against an
extra setup of M L' mv per level. With d ~ 5-10 (DEV) the gain is a small power of the budget, eps^{-2/(d+1)} at best
when M is optimised against a budget eps^{-2}; it does not grow polynomially in n unless d stays bounded as n grows.
The deterministic version beats sampling at a layer only if 2^{N(l, eps)} < eps^{-2}, i.e. effectively d < 3.

## 8. N(l, eps) for random deep nets (HEURISTIC; DEV-calibrated where marked)

Input regime (sigma = 0). The cloud at layer l has angular size theta_l ~ 3 pi/l (K8), the future's linearity scale is
~ 2/L'. Ratio rho_l = theta_l / phi_lin ~ 4.7 L'/l. Smooth regime iff rho_l < 1, i.e. l >~ 0.82 L (the last ~18% of
layers). There N(l, eps) ~ (d_l/3) log2( kappa_3 L' theta_l^3 / (eps^2 V_rel) ), V_rel = V/|g|^2 ~ 9 pi^2/(2 L^2) +
C_L/n (direction plus amplitude, (K9)). In the rough regime N(l, eps) >~ d_l log2 rho_l (pieces of the rough gain
field) plus the smooth bits inside each piece. d_l ~ 2 x the angular participation ratio, which is 9 -> 5 -> 3 at
l = L/4, L/2, 3L/4 for n = 128, L = 64 (DEV).
Depth regimes. L < sqrt(n): the direction term dominates V; ARC's closure regime (illustrative arithmetic under ARC's
conjectured (L/n)^K law, read as an RMS error: it beats sampling only for L < sqrt(n); cut-rank lane section 10). L ~ alpha n: the amplitude carries V; resolution methods pay 2^{N} with N ~ d log2 rho
at the early layers; the multilevel sampler pays D_r per level and gains n/log^2 n. L >> n: the cloud becomes nearly
radial (K9), d_l and N(l, eps) fall at most layers, and both deduction and the multilevel sampler profit; the
multilevel sampler already captures this (its deep levels are cheap), so no separation is predicted there either.
Noise regime (Model S). The stationary cloud has angle ~ 2.23 Q^{-2/3} ~ 3.2 n^{-2/3} between noise replicas (K10) and
the future is effectively infinite (L' >> n), so rho = cloud/phi_lin is large at every layer except near the output:
the bits that matter are set by the rough regime, d = the cloud's effective dimension (participation ratio growing
like log n for a 1/k spectrum), N ~ d log2 rho with rho ~ n^{1/3} at L' ~ n (HEURISTIC).

## 9. Kelvin's hash argument, revisited

Proposition 9.1 (a hash is easy to average; PROVEN). Suppose the per-instance mean is F = 2^{-N} sum_b H(b) over
N uniform bits, with E H(b) = m known and H(b), H(b') uncorrelated across instances for b != b', Var H(b) = s^2, and the
within-instance variance of H(b) over b equal to s^2 (a hash). Then (i) the prediction m has error s^2 2^{-N}, below
T-sample MC's s^2/T for every T < 2^N; (ii) enumerating T of the 2^N values and predicting the rest by m has error
s^2 2^{-N}(1 - T 2^{-N}) <= s^2/(4T) for every T <= 2^N. So "a hash over N bits cannot be averaged better than by
sampling" is false at every budget; a mean is hard only if it has a component that varies across instances at the SD
scale and is not computable cheaply.
What survives (precise). (S1) Resolution methods (cells, enumeration, branch-and-bound, frozen-gate quantisers) pay
2^{N(l, eps)} at layer l, forward-only methods pay 2^{N_fwd} >= eps^{-2d/3} (Cor 6.2), and N is large wherever the
cloud is larger than the future's linearity scale (HEURISTIC: all but the last ~18% of layers in the input regime).
(S2) Forward computations cannot see the future's frame (K7), and in the cell class this costs an unbounded number of
bits as eps -> 0 (Thm 6.3).
What fails (precise). (F1) The count is not exp(k*): k* (the future's effective rank) does not set the cell count;
the cloud's dimension d_l above phi_eps and the ratio cloud/phi_lin do. (F2) The final layers are the easiest: the
future is smooth on the collapsed cloud for l >~ 0.82 L and N -> 0 at l = L (Thm 5.2). (F3) "Hash implies hard to
average" fails (Prop 9.1): the rough part of the future over many cells self-averages; averaging methods (closures)
evade N altogether and fail for a different reason, a fixed-order bias (K3). (F4) "Nothing beats sampling" depends on
which sampling: the multilevel sampler (a radial-merge MPS) already beats plain MC by n/log^2 n.

## 10. Conjecture ledger and bottleneck

C1 (cubic law at finite width). For n -> infinity with L'/n fixed, E_{W>l}|g_l(h) - J_l(c) h|^2 = k(L'/n) L' |h|^2
phi^3 (1 + o(1)) for L' phi -> 0, with k(0) = 4/(3 pi). DEV: 2-5x at n = 128. Test: the exact three-replica Gram
chain at finite n. Status: new.
C2 (residual decay with references). D_l(M) ~ D_l(1) M^{-3/d_l} (smooth) and ~ M^{-1/d_l} (rough), d_l ~ 2 PR_l.
DEV: M^{-0.3..-0.6}. Test: E1 on fresh nets. New.
C3 (rough regime). For L' phi >> 1 the log-gain difference between two states at angle phi has variance ~ c phi/n
(linear in phi). Test: measure Var log(|g(h)|/|g(c)|) against phi and L'. New (consistent with (K9)'s amplitude law).
C4 (no width-growing gain from relevance at L = alpha n). For every MPS with poly(n) components and per-layer work,
the error is at least c times that of the best multilevel merge sampler at equal cost. This is C0* (K6) restricted to
MPS. BOTTLENECK: it needs a lower bound for averaging methods (closures) at L = alpha n, where N(l, eps) gives none;
the natural target is a positive bias floor of order-K closures uniformly in n at L = alpha n (polynomial-rate version
of (K3)).
C5 (two-sided count). log2 #(future linear regions meeting the cloud) ~ d_l log2( (n/pi) L' theta_l / d_l ). Test:
count distinct future gate patterns on large cloud samples. New.
