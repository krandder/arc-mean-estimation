# adaptive-regions: prior-lane facts and literature (written 15:12Z, 2 Nov 2026)

Labels are the source lanes' own. [prior: lane] = an earlier lane's report or FORMAL; "memory" = cited from memory,
not re-checked today.

## Prior-lane facts used here
- Ensemble kernel and linear-rule barrier [prior: preint F7, E3a; randomness T1-T4, E1.1, E2.2-E2.4]. For a rule chosen
  independently of W (fixed or randomised; weighted points, line integrals) the weight-averaged MSE is the kernel
  discrepancy (PROVEN). Positive-weight rules pay every even power from degree 6 on in full for N <= ~5.7e5 at n = 256
  (power form, E2.2), so their gain over radius-exact MC is <= ~2 Lambda / Lambda_{even >= 6}; shares at 256 x 32
  (medians, 5 nets): odd 0.56, even 0.43, degrees <= 2 0.47, even >= 6 0.17 (MEASURED); limits as n grows along
  L = alpha n: degree 1 0.29, degree 2 0.21, even >= 6 0.166 (PROVEN formulas, values numerical). Per net, the same
  holds for Haar-rotated rules with the net's own energies (PROVEN). At fixed n the black-box exponent lies in
  [1 + 2/(n-1), 1 + 3/(n-1)] (PROVEN [A]); "stratifying the sphere into N equal cells attains N^{-1-2/(n-1)}".
  Stratified sampling with weight-independent strata and allocation is such a rule (positive weights).
- Adaption under a Gaussian surrogate [prior: preint E1]: Wasilkowski-Wozniakowski 1984 (orthogonally invariant
  measures), Traub-Wasilkowski-Wozniakowski 1984, Wasilkowski 1986/1989 (abstracts checked by preint). Real prior: unit
  output excess kurtosis 6.9-9.1 at L = n/8, one-point error divided by the net's RMS 5.7-8.8 (MEASURED, post hoc);
  identifiability after ~nL evaluations (so any separation beyond N ~ nL is computational).
- Surrogate route [prior: preint E2(g), A]: surrogates p_q with exact integral at cost q^a and residual trVar <= C q^-b
  uniformly in width give MSE T^{-1-b/a}; a single fixed control changes only the constant. First-layer controls are
  mostly degree <= 2 and redundant with a 2-design (randomness T10, HEURISTIC).
- Finite-width variance mechanism [prior: randomness E2.3, A, PROVEN]: persistent activation-norm differences
  accumulated over the first layers (each O(1/n), summing to O(1)); E V -> 11.15 along L = alpha n.
- Output and input geometry at 256 x 32 [prior: arc-update, future-aware, relevance]: final-layer covariance PR 1.9
  (net 200), so the variance is mostly one amplitude times a nearly fixed direction (MEASURED); the future's reading of
  the first layer has PR 17.5, 33.3, 67 at n = 64, 128, 256 and 16 directions capture 0.80, 0.59, 0.39 of it
  (MEASURED); 99% of the value function's variance needs 256 projections at l = 0 (MEASURED point estimates);
  5-9% of gates switch per sample against the mean path (MEASURED); mean Hermite degree 21 at l = 0 (MEASURED).
- Gate geometry [prior: randomness T7, E1.2; gram-chain]: expected Gaussian perimeter per neuron
  (1 - 2^-n)^{l-1}/sqrt(2 pi) (PROVEN [A]), total ~ nL/sqrt(2 pi); some gate changes with probability 0.93-0.98 at
  correlation 1 - 1e-6 (MEASURED); expected layer-l gate disagreements between replicas with layer-(l-1) cosine rho:
  n arccos(rho)/pi (PROVEN, replica chain); an exact line has ~nL vertices (preint F3, PROVEN in expectation [A]).
- Certified branch-and-bound [prior: unrestricted-estimators 2026-10-31]: cones over cube faces, exact Gaussian cell
  moments, symbolic linear bounds; certifies 93-99% of the mass at width 3, < 1% at width 4-8, nothing at 16-32;
  certificate nMSE 1e16-1e34 at depth 32-64 (symbolic bounds through unstable units compound with depth); 33x-2e5x
  worse than RQMC at width 4, 1e4-1e6x at 6-8, 1e5-1e6x at 16-32 (MEASURED, registered). A cell costs 46-170 passes.
- RQMC baselines (arc-update runs/rqmc_*.json; my fit today over N = 2^8..2^14 or 2^16, 8 scrambles): median fitted
  exponent 1.05, 1.06, 1.12, 1.09 at n = 32, 64, 128, 256; gains over MC 3-7 (32 x 4), 2-4 (64 x 8), 1-3.8
  (128 x 16), 0.7-2.6 (256 x 32).
- Deep-state dimension [prior: arc-update P9]: third-cumulant PR 115, 66, 23, 4.0, 4.1, 1.6, 1.1 and covariance PR
  165, 106, 57, 21, 11.5, 4.1, 1.9 at l = 1, 2, 4, 8, 16, 24, 31 (net 200, MEASURED registered).

## Literature (adaptive stratification and adaption)
- Neyman (1934): optimal allocation N_k proportional to p_k sigma_k; variance (sum p_k sigma_k)^2 / N. Standard.
- MISER (Press and Farrar 1990): recursive stratified sampling; bisect along the coordinate whose split most reduces
  the estimated sum of sub-region standard deviations, allocation proportional to sigma (memory).
- VEGAS (Lepage 1978) adaptive separable importance sampling on a product grid; VEGAS+ (Lepage 2021) adds adaptive
  stratification (memory). Both assume most variance lives in low-order (axis-separable) structure.
- MC-UCB (Carpentier and Munos, NIPS 2011): online allocation over K strata, pseudo-regret relative to oracle Neyman
  of order K^{1/3} N^{-4/3} (up to logs) (memory); Etore and Jourdain (2010) adaptive optimal allocation (memory);
  Carpentier and Munos (NIPS 2012) on choosing the number of strata for differentiable functions (memory).
- Rates: for Lipschitz (or piecewise-smooth) f in d dimensions, stratification into N equal cells gives
  MSE ~ N^{-1-2/d} (Haber 1966; Bakhvalov; Novak 1988, memory): exponent gains ~2/d, i.e. ~1/128 at n = 256.
- Adaption: for linear problems on convex symmetric classes, adaption does not help in the worst case (Bakhvalov 1971;
  Gal-Micchelli 1980; Traub-Wozniakowski, memory); on average under Gaussian measures it does not help either
  (Wasilkowski-Wozniakowski 1984). Novak (1996, "On the power of adaption") surveys when it does: non-convex or
  non-symmetric classes, e.g. functions with a few localised singularities (memory).
- Effective dimension (Caflisch, Morokoff, Owen 1997): QMC and stratification gain when the low-order ANOVA part
  dominates (memory).
- Linear regions of random ReLU nets (Hanin and Rolnick 2019): the expected number of regions meeting a d-dimensional
  input set grows like (#neurons x volume scale)^d / d!, not exponentially in depth (memory); here d = n, so the count
  is astronomical anyway.
- Gaussian rate-distortion (Cover and Thomas, Thm 10.3.3): reverse water-filling; for a description of rate R nats of
  N(0, Sigma), the error covariance D satisfies (1/2) log det(Sigma D^-1) <= R (standard).
- Certified bounds: interval bound propagation (Gowal et al. 2018), CROWN backward linear relaxation (Zhang et al.
  2018), DeepPoly (Singh et al. 2019), symbolic intervals (ReluVal, Wang et al. 2018) (memory). Implemented here from
  scratch, per main's instruction.
- Polytope volume: exact volume is #P-hard (Dyer and Frieze 1988); randomised approximation in polynomial time
  (Dyer-Frieze-Kannan 1991; Lovasz-Vempala O*(n^4) oracle calls) (memory). Genz (1992) for low-dimensional
  multivariate normal probabilities.
- MCTS-Solver (Winands, Bjornsson, Saito 2008): proven node values propagate up the tree; the analogue here is a
  region whose contribution is certified (memory).

## Choices made from this reading
- Region families: (i) frame splits (exact product-form p_k, trivial within-cell sampling); (ii) first-layer gate-sign
  cones (orthant probabilities; cheap k-dimensional sampling for p_k); (iii) greedy CART with candidates from both,
  plus quantile thresholds; local linear control variates per cell (regression on train; white-box Jacobian variant).
- Allocation: oracle Neyman and proportional (post-stratification) gains on held-out samples; the bandit regret is a
  correction that only lowers them (FORMAL).
- Settling: cone cells (sign splits at 0 keep cells conical, so homogeneity reduces bounds to the unit sphere) with own
  IBP and CROWN; boxes around layer-l states for the depth question.
