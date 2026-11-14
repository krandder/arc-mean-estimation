# Co-prover provenance log (bits-bounds lane)

"Claude" = the bits-bounds lane agent (Claude Opus 5.5); "astra" = gpt-6-astra via codex-any (read-only sandbox, xhigh
effort, nice 19). Model line checked in each raw log header ("model: gpt-6-astra").

## Round 1 (21:06-21:25Z): independent attempts
- Astra got only the lemma-free coprover/STATEMENT_r1.md (sha d559f9cf..., hashed 21:05:59Z) and was told not to read
  other files. Answer: coprover/astra_r1_answer.md (extracted from astra_r1.raw, lines 200-1195).
- Claude wrote FORMAL.md v1 between 21:07 and 21:18Z (sha dbdcb7f7..., notes/formal_hashes.txt; frozen copy
  coprover/FORMAL_v1_as_written.md) before reading anything of astra's answer beyond the header's model line. Astra's
  run ended at 21:25:21Z.
- Found independently by both (same conclusion; proofs differ where noted):
  - a layer-sweep model with M bits of state, bounded passes, charged computation; all four families placed in it;
  - information bounds on unrestricted states are capped by the weights' description length (Claude Prop 3.3; astra
    2.1 "PROVEN limitation" with an explicit operator-norm discretisation);
  - per-sample (trajectory) information is the same at every layer of a noiseless net, so a layer-dependent "bits at
    layer l" needs a restriction (Claude section 5 reading; astra 2.3 warning);
  - only the nonlinear part of the future matters for the mean: a linear future is integrated exactly from the mean
    (astra 2.3 counterexample; Claude notes/N_definition.md Addition 1, written 21:35Z after v1 and before reading astra);
  - forward-only defects are kernel discrepancies under k(h, h') = |h||h'| kappa_{n,t}(cos) (Claude Prop 4.4; astra 5.2,
    with the trajectory-metric formula);
  - a random hash with a known ensemble mean is easy to average (Claude Prop 9.1, partial enumeration >= 4x over MC;
    astra 4.b, the zero estimator on independent Rademacher tables has normalised MSE 1/(K-1));
  - optimal multilevel allocation (sum_j sqrt(v_j c_j))^2 (Claude section 7 cites the standard; astra 3.3 proves it);
  - the bottleneck is computational: no unconditional lower bound for averaging/closure methods (Claude C4; astra
    C_comp).
- New from astra (round 1):
  - A1 (2.1): exact one-pass characterisation of forward-only bits: error >= D_{2^b}(T(A)), the 2^b-point
    quantisation error of the mean-query function T(A) in L^2(future); attained information-theoretically; uniform
    version by packing/covering.
  - A2 (2.5): a worst-case depth-2 ReLU family (diagonal W_1 = diag(1 + u), suffix selects coordinate j) where constant
    precision needs > 0.188 d forward-only bits but O(log d) with a preliminary future-reading pass (INDEX argument).
  - A3 (2.6): value-oracle tables with an unknown common bias (Beta prior): Theta(min(K, eps^{-2})) queries, matched by
    sampling without replacement. This is the precise sense in which a "hash" is hard: the common bias must be
    unknown; with a known bias (A-table of independent signs) the zero estimator wins.
  - A4 (2.3): Gaussian water-filling rate for the trajectory channel with C^{1/2} A^T A C^{1/2} (PROVEN), and
    a finite-bit clipping/rounding construction (3.1).
  - A5 (3.3): dyadic multilevel cost under H_ML: gains L/(log^2 L + n/L) for sqrt(n) < L < n, n/log^2 n at
    L = alpha n, none certified for L < sqrt(n).
  - A6 (5.3, 5.4): annealed tangent-energy preservation E_B J^T J = I (PROVEN); the future-blind subspace theorem
    E_B tr(P_S P_F) = k d/(n-1) for prefix-measurable S in u-perp (the kstar-frames Prop. 2 in exact form).
  - A7 (5.5): in Model S the annealed second moment grows by n sigma^2 per layer; the stationary annealed law exists
    (Doeblin minorisation via the all-negative event), with finite first and infinite second moment.
  - A8 (4): ray counterexample: a cut state on a fixed ray is integrated exactly with one suffix evaluation; parity
    as a maximally non-additive function with a known mean.
  - Heuristics: R_path ~ [n/(8 t ln 2)] log^2(T/D) under a geometric future spectrum; chart count (1 + t/l)^k from cloud
    size ~1/l and frame coherence ~1/t (same structure as Claude's ratio rho_l ~ 4.7 L'/l).
- Not in astra round 1 (Claude only): the measure-propagation class with the telescoping defect identity (Thm 4.2);
  the Euler residual lemma (4.3); the exact one-layer residual law (Thm 5.1); the mean-field frozen/radial recursion,
  the cubic law (4/(3 pi)) L' phi^3 and the crossover near L' phi ~ 2 (Thm 5.2); the cell-class rate-distortion
  bound (Thm 6.1, Cor 6.2) and the unbounded forward-only/two-sided separation for cells (Thm 6.3); the smooth/rough
  regimes and the water-filling heuristic for N_cell.
- Claude's checks of astra round 1 (21:45-21:55Z, by hand): A1 (quantisation inequality: fixing public randomness,
  the suffix output is a function d_s(B) of the message; error >= E min_s ||T(A) - d_s||^2) CONFIRMED; A2 (threshold
  at 3c/2 separates u_j; Fano-type step H(U|S,R) <= d h_2(1/4)) CONFIRMED; A3 (posterior variance computation with
  Beta(s+1, m-s+1): E Var(mu | obs) = u/(6K^2) + u^2/(6K^2(m+2))) re-derived, CONFIRMED; A6 (one-layer
  E[1{w.h>0} w w^T] = I/n by w -> -w) CONFIRMED; A7 second-moment identity CONFIRMED. (The check times above were
  written as 21:45-21:55Z; the actual clock was about 21:26-21:30Z: a typo, nothing depends on it.)

## Round 2 (21:27-21:52Z): lemma exchange and audit of FORMAL v1
- Astra got FORMAL.md v1 (sha dbdcb7f7, verified by astra), its round-1 answer, PROVENANCE.md, lib/meanfield.py,
  lib/chain3.py, notes/N_definition.md and the relevance lane's DEFINITIONS.md and FORMAL.md. Prompt: coprover/prompt_r2.md
  (sha 917ff19d). Answer: coprover/astra_r2_answer.md. Claude's FORMAL v2 sections 0-11 were drafted while round 2 ran
  (from round 1 and the measurements); section 12 and the corrections below were applied after reading round 2.
- Audit verdicts (astra r2, section 1): CORRECT: Thm 3.1 (crossings p + #same-direction neighbours <= 2p - 1),
  Cor 3.2, Thm 4.2, Prop 4.4, Thm 5.1. CORRECT AFTER FIX: Prop 2.2 (mv versus scalar units; cone storage), Prop 3.3
  (annealed criterion, unbounded weights), Def 4.1 (truncated cumulants are not measures), Lemma 4.3 (boundary
  convention; r_j >= 0 componentwise; contributions not orthogonal), Thm 5.2 (see below), Def 5.3 (rename N_cell),
  Thm 6.1 (condition on public randomness), Cor 6.2 (the Euclidean Shannon bound fails for the homogeneous distortion:
  h = 2c has zero residual; quantise directions under the radius-weighted angular law), Prop 6.4-6.6, section 7.
  WRONG: Thm 6.3 as a fixed-net separation (a past-measurable policy may be the constant codebook that happens to be
  optimal for the realised future; the valid statement averages over random futures), Prop 9.1 literally (the
  within-instance variance is s^2(1 - 1/K), so the gain over MC is K(K-1)/(T(K-T)), about 4, exactly 2 at K = 2,
  T = 1). HEURISTIC with corrections: section 8 (PR is not the dimension of fine quantisation; in the noise regime
  2.23 Q^{-2/3} is 1 - cos theta, so theta ~ Q^{-1/3}).
- New from astra (round 2), each re-checked by Claude where marked:
  - B1 closed form of the mean-field frozen recursion: q_t = s r_t + (1 - s^2) P_t, P_t = prod (1 - phi_i/pi),
    equivalently q_t = s C_t(s) + (1 - s^2) C_t'(s). CHECKED numerically against lib/meanfield.py to 7 digits.
  - B2 the cubic law with its next term: D_F = (4t/(3 pi)) phi^3 - (t(t-1)/pi^2) phi^4 + O_t(phi^5). CHECKED (series
    matches the recursion for small t phi).
  - B3 the scaling limit x = t phi/(3 pi): D_F = phi^2 [1 + (1+x)^{-2} - 2 (1+x)^{-3}], D_R = phi^2/(1+x)^2; crossover
    t phi = 3 pi (2^{1/3} - 1) = 2.4497. CHECKED (the number).
  - B4 the finite-width raw residual has cubic coefficient (4/(3 pi)) S_{n,t}, S_{n,t} = sum_{j<t} (1 - 2^{1-n})^j: no
    positive t/n correction. The 1.7-3.3x "enhancement" in Claude's chain3 numbers comes from normalising by the output
    norm |h_t|^2 (an inverse-norm effect; the unregularised ratio has no finite expectation since h_t = 0 with v_t != 0
    is possible); regularised expansion 1 + (5t + 1)/n. Astra's own chain with the scale kept: raw/MF = 0.988, 0.979,
    1.001 at n = 64, 128, 1024. Claude's C1 is withdrawn as stated (see FORMAL v2 section 12).
  - B5 rough regime: 5 - B(cos theta) = 4 theta^2 - (4/3) theta^4 (coefficient 4, not Claude's 2.9; CHECKED at
    theta = 0.1); Var log(|g(h)|/|g(c)|) ~ (6 pi/n) phi x/(1+x), so c = 6 pi for t phi >> 1 (under log regularisation
    and iterated limits); D_R ~ (3 pi/t)^2 + (6 pi/n) phi in the window 1/phi << t << n; reference quantisation
    D(M) ~ M^{-p/d} (p = 3 frozen, p = 1 gain variogram) under a regular d-dimensional source.
  - B6 optimised gains of M-reference merges: C(M) ~ a M + b eps^{-2} M^{-p} gives eps^{-6/(d+3)} (p = 3/d) and
    eps^{-2/(d+1)} (p = 1/d).
  - B7 Gaussian-cloud linear-future feature theorem: forward-only k features leave a sum_{i>k} lambda_i(Lambda);
    future-aware leave sum_{i>k} lambda_i(Lambda^{1/2} A^T A Lambda^{1/2}).
  - B8 corrected Shannon-type cell bound for angular sources: log2 M >= (d/3) log2(E R^2/D) + O(1), d an actual
    source dimension.
  - B9 a K-only bias floor cannot hold for classes containing polynomial Gaussian mixtures (degenerate components
    are particles); for the single-Gaussian recursion a positive annealed floor at L = alpha n is plausible; sufficient
    target C_closure(n, eps = n^{-q/2}) >= n^{max(1, q) - o(1)}; an unbiased cross-product test for closure bias.
  - B10 Minkowski certificate for forward-only closures: sqrt(E|mu^ - mu|^2) <= sum of root-mean-square kernel
    discrepancies of the layer defects.
  - B11 corrections to round 1: crossings (2p - 1)M; one-pass multilevel; the n/log^2 n gain is an attainable upper
    bound, not an optimality theorem. And a small correction to the relevance lane's Cor 1b (average the right side
    over the singular values), to be relayed.

## Round 3 (22:17:59Z-22:32:15Z; prompt_r3.md sha256 bf9107bb..., run_r3.sh eba99b3a..., FORMAL.md at launch
## 27bb1a35...; raw log astra_r3.raw, "model: gpt-6-astra" on line 5; answer astra_r3_answer.md)
Question: a lower bound for the exact single-Gaussian recursion (lib/closure.py) at L = alpha n, of the form
E_W|m_L - mu|^2 >= c E_W V n^{-a}, and what a would mean at the method's cost. Launched at 22:17:59Z, before
Amendment 3's first evaluation run (22:21:02Z); the prompt cites the hardness lane's K = 2 results and my dev checks
(corrected after review 2; an earlier version of this entry said "after Amendment 3's results").
- New from astra (round 3), checks by Claude in `logs/check_r3.log` (scratch/check_r3.py) where marked:
  - C1 exact defect decomposition E|m_L - mu|^2 = sum_l D_l + 2 sum_{l<k} C_lk, each a kernel-tested Gaussianisation
    defect under the exact future; cross terms have no sign. (Follows from FORMAL Thm 4.2 and Prop 4.4.)
  - C2 radius component of the future kernel: E_W g_t(h) = (a_n^{t-1}/sqrt(pi)) |h| u, u = 1/sqrt(n), with
    a_n = E sqrt((2/n) sum (Z_i)_+^2) = 1 - 5/(8n) + O(n^-2), so K_t = (a_n^{2(t-1)}/pi)|h||h'| + PSD part.
    CHECKED: n(1 - a_n) = 0.6366, 0.6278, 0.6257, 0.6252, 0.6250 at n = 16, 64, 256, 1024, 4096 (exact binomial sum).
  - C3 first radius defect E rho_1 = 9/(16 sqrt n) + o(n^-1/2), from E|H|^4 = n^2 + 7n + 10 and E|G|^4 = n^2 + 5n/2 +
    O(1). CHECKED: E|H|^4 by algebra ((n + 2)(n + 5)); (E|H|^4 - E|G|^4)/n = 4.91, 4.60, 4.53 (+- 0.06, 0.03, 0.02) at
    n = 16, 64, 256 (-> 9/2); sqrt(n) E rho_1 = 0.536, 0.556, 0.561 (+- 0.002, 0.001, 0.001) (-> 0.5625), with E|G| by
    the exact Laplace identity (checked against Monte Carlo at n = 16: 4.02353 vs 4.0235 +- 0.0012).
  - C4 UNCONDITIONAL one-defect theorem: Gaussianise once after layer 1 and integrate the true suffix exactly; then
    liminf n E|mu~ - mu|^2 >= (81/(256 pi)) e^{-5 alpha/4} (0.0539 at alpha = 1/2, 0.0289 at alpha = 1). Proof read;
    not re-derived.
  - C5 CONJECTURE (H_R): E_W R(G(T_W # N(m, S))) >= a_n R(N(m, S)) for every m, S (Gaussianisation does not lower the
    mean radius on average over a fresh He layer). PROVEN UNDER (H_R): liminf n E|m_L - mu|^2 >= the same constant,
    and E|m_L - mu|^2 >= c(alpha) E V / n with c(alpha) = 81 e^{-5 alpha/4}/(512 pi C_V), C_V = 1 + 2 sum (1 - c_j).
    CHECKED the constants: C_V = 13.481, c(1/2) = 2.0e-3, c(1) = 1.07e-3 (C_V recomputed by a stable recurrence for
    1 - c_j after review 2: the first version's tail constant was wrong, 281.6 instead of 9 pi^2/2 = 44.41, but
    the value of C_V survives).
  - C6 the pointwise version of (H_R) is false: H_M = ((M + Z)_+, (-Z)_+) has E|G_M| - E|H_M| ~ -1/(2 sqrt(2 pi) M^2).
    CHECKED by quadrature: -1.17e-2, -3.35e-3, -8.16e-4, -1.99e-4 at M = 4, 8, 16, 32 against -1.25e-2, -3.12e-3,
    -7.79e-4, -1.95e-4.
  - C7 if the 1/n floor fails, later radius defects must cancel the first: sum_{l>=2} a_n^{L-l-1} b_l =
    -(9/(16 sqrt n)) a_n^{L-2} + o(n^-1/2) (necessary, not sufficient).
  - C8 a product-law toy for order-K matching: radius exponent a_K = 2 floor(K/2) - 1; transfer to real cumulant
    recursions not proved.
  - C9 ARC's K = 2 'simple' kind truncates the off-diagonal covariance at the linear term: exact Cov(Z+, Z'+) at
    correlation 1/2 is 0.1453439474 against 1/8. CHECKED (closed form; and in kprop_harmonic.py a (1,1) block costs 1
    against a budget of K - 1 = 1, so one covariance block is admitted).
  - C10 the theorem's normalisation is E[err^2]/E[V] (annealed), not the median of per-net nMSE used in Amendment 3.
- Claude's use: FORMAL section 11 (C4) and the report state the conditional floor as PROVEN UNDER (H_R) [A], the
  one-defect theorem as PROVEN [A], and note that the floor's constant (n E[err^2]/E[V] >= 1.1e-3 at alpha = 1) lies
  two to three orders of magnitude below the measured values (0.2-1.0), so under (H_R), at fixed alpha and large n,
  the theorem bounds the closure's annealed gain at its own cost by a constant (about 1/(2 c) ~ 470 at alpha = 1) but
  does not predict where its growth stops.

## Round 4 (23:23:58Z-23:41:03Z; prompt_r4.md sha256 cd6f0ec3..., run_r4.sh 66a54a77..., FORMAL.md at launch
## 5547b83e... (v2.2 with section 6.6, frozen 23:21:12Z); raw astra_r4.raw, "model: gpt-6-astra" on line 5;
## answer astra_r4_answer.md)
Question: Part 1 independent (the log-radius martingale, the radial-merge distortion, the cell lower bound, effective
dimension of an exponential-spectrum cloud, the bits formula), then an audit of FORMAL 6.6. Astra states it did Part 1
before reading 6.6.
- New from astra, checks by Claude where marked:
  - D1 the log-radius process needs a death convention: the stopped (frozen-at-death) log ratio is a martingale with
    Var Z_L = sum_j E[1{tau > j} v_n(theta_j)] exactly, equal to the original except with probability <= 2L 2^-n;
    conditioning on survival to the final depth keeps zero drift but makes the increment variance horizon-dependent
    (explicit n = 2 counterexample; not checked). My 6.6(a) conflated the two: corrected.
  - D2 v_n = b(theta)/n + O(n^-2), b = 3 - [(pi - theta)(1 + 2 cos^2 theta) + 3 sin theta cos theta]/pi
    (= 3 - 2 k2, as in 6.6(a)); b = 2 theta^2 - (2/3) theta^4 + ...; B_inf = 21.301, B_inf/2 = 10.6505; the future share
    F_l = 0.486, 0.325, 0.197, 0.111, 0.0595, 0.0310 at l = 8-256, ~8.34/l. CHECKED: B_inf = 21.3009 (sum to 2e5 plus
    the 18 pi^2/J tail), the F values to 4 digits; my 10.63 and 0.058/0.029 used a truncated sum (to 4096), and my
    5.5/(l + 5.5) had the wrong coefficient; 8.3/(l + 9) is within 3%.
  - D3 rho_{n,t}(phi) = 2(1 - K_{n,t}(cos phi)) exactly (homogeneity, rotation invariance); strict mean field has no
    linear term (rho_inf ~ phi^2/(1 + z)^2, z = t phi/(3 pi)); the finite-width radial part adds
    (6 pi/n) phi z/(1 + z) under a uniform mean-field approximation, justified in the window 1/phi << t << n.
  - D4 no positive global linear minorant exists: rho_{n,t}(phi) <= 2(1 - cos phi) <= phi^2 and rho = phi^2 + o(phi^2)
    at fixed finite n, t (radial merges are locally quadratic). A minorant can hold only on a restricted scale window.
  - D5 the covering lower bound of 6.6(e) is correct as an abstract theorem (with the truncation at phi_0 handled by
    theta <= phi_0, K M >= 1), but the layer-l angular law has atoms (single-neuron input cones map to coordinate rays,
    which keep positive mass if they survive), so a global small-ball bound fails; it can hold only for a bulk part.
  - D6 for a Gaussian cloud with lambda_k ~ exp(-2 beta (k - 1)), beta = l/n: the small-ball exponent grows with
    resolution, d_sb(r) ~ log(sigma/r)/beta; optimal M-point quantisation with distance loss has
    log(D(M)/sigma) = -sqrt(2 beta log M)(1 + o(1)); so a constant d_l is inappropriate at high precision and the rate
    grows like the square of log(C/eps^2). Water-filling proxy: gamma x PR ~ 2/(1 + 2 beta m), no universal constant.
  - D7 the bits formula is a high-resolution law under two-sided regularity (covering and small-ball, upper and lower
    distortion bounds); the measured 1.4 PR and 1.75 PR are fitted exponents of one construction, not source
    dimensions; the p = 3 law belongs to frozen merges, radial merges are p = 2 at small angles.
  - D8 audit numbers: variance_made.md and bits5_posthoc_old.json reproduce; the 88% bit agreement (old nets)
    decomposes into 249/251 censored (> 8 bits), 36/36 zero-bit and 23/64 resolved nonzero cases. CHECKED (same
    decomposition; on the Amendment 5 nets: 63/63 censored, 14/14 zero, 5/13 resolved nonzero, where the formula
    over-predicts by a median factor 1.8).
  - D9 the cell-count inequality is not a necessary condition for beating sampling (cancellation, stratification,
    sampled residuals); multilevel ideal work O(eps^-2 log^2 L) against O(L eps^-2).
  - D10 the attribution of the variance profile to the input-bits lane is correct (B(c) = 4 k2(c) - 1).
- Claude's use: FORMAL 6.6 rewritten (v2.3): (a) stopped martingale; (b) corrected constants; (d) formula labelled
  HEURISTIC with a scale window and the censoring decomposition; (e) kept as an abstract theorem with its failure on
  nets stated; (f) restated as an idealised enumeration comparison; D6 added as the scale-dependent refinement.
