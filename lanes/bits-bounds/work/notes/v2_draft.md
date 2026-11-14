# Draft additions for FORMAL v2 (written 21:40Z, after reading astra round 1, before round 2's answer)

## A. References are samples in disguise (forward-only merges)
Theorem (stratified law; PROVEN for the identity and the bound; cross-term size HEURISTIC, tested by P7). Let cells
C_1..C_M and references c_k be past-measurable and the merge rule m past-measurable; suppose the cell statistics
E[m(h; c_k) 1_{C_k}(h)] are exact. The merged estimate's error is e = sum_k P_k Rbar_k, Rbar_k = E[R(h; c_k) | C_k],
R = A - m. Over the random future (W_{>l}),
    E|e|^2 = sum_k P_k^2 E|Rbar_k|^2 + sum_{k != k'} P_k P_k' E[Rbar_k . Rbar_k'],
    E|Rbar_k|^2 <= D_k := E E[|R|^2 | C_k]   (Jensen),
and for the radial merge E[R(h; c) . R(h'; c')] = |h||h'| [kappa(h^.h'^) - kappa(h^.c'^) - kappa(c^.h'^) + kappa(c^.c'^)]
(kappa = kappa_{n,L'}), a mixed second difference of the back kernel, small when the two cells are far apart compared
with their sizes and the kernel is smooth off the diagonal. With equal-mass cells and negligible cross terms,
E|e|^2 <= D/M: M deterministic references have the error of a stratified sampler with one draw per stratum.
Reading: a deterministic method that evaluates the future at M points cannot average the within-cell (rough) part
better than stratified sampling; its advantage over MC is V/D(M), the variance its cells explain.

## B. Point-evaluation lower bound in terms of the bits that matter (average case)
PROVEN UNDER (G): restricted to the cloud's support, the future (minus its known mean) is a centred Gaussian field whose
covariance has a singular part A |h - h'|^{2H} (isotropic, d-dimensional support carrying P_l with a density bounded
above and below). Then every algorithm using the future only through M (adaptively chosen) evaluations of values and
finitely many derivatives has average error^2 >= c(d, H) A M^{-1 - 2H/d} (average-case information-based complexity
for Gaussian measures: adaption does not help, and the n-th minimal integration error for a field of smoothness
H + d/2 decays like n^{-1/2 - H/d}; Wasilkowski 1986, Traub-Wasilkowski-Wozniakowski 1988, Ritter 2000 - recalled,
hypotheses not checked line by line).
- Below the linearity scale (cells smaller than ~2/L'): H = 3/2 (cubic law), A ~ (4/(3 pi)) L' |g|^2 (mean field).
- Above it: the gains form a rough field, H = 1/2, A ~ c |g|^2 / n (HEURISTIC, astra round 2 to check).
- Bits: to reach eps^2 V a point-evaluation method needs log2 M >= [log2(A/(eps^2 V)) - O(1)] / (1 + 2H/d), against
  log2(1/eps^2) for MC; the advantage exponent is 2H/d: 3/d smooth, 1/d rough. As eps -> 0 at fixed net the cells
  shrink below every axis of the cloud, d -> n - 1, and the exponent tends to 3/(n - 1) (the unrestricted lane's
  partition-cubature exponent [A]).
- (G) is false at finite width with L' ~ n (the future is not Gaussian); the statement is for the surrogate.

## C. The hash proposition, both faces (main's request)
- Average case, random table with KNOWN ensemble mean m (iid values, ARC's averaged criterion): Bayes estimator =
  partial enumeration; gain >= 4x over MC with replacement at every budget, 1/x over sampling without replacement
  (x = T/2^N). The gain comes from the ensemble prior, not from structure in the function.
- Value-oracle access with an UNKNOWN common bias (astra A3): Theta(min(2^N, eps^{-2})) queries, matched by sampling
  without replacement: here a hash is exactly as hard as Kelvin says.
- For the nets: the random future's rough part behaves like the first face for methods that integrate it analytically
  (it self-averages) and like the second face for methods that query it at points (section A: references are
  samples). Which face applies depends on the algorithm's access to the future, not on the net alone.

## E. Cost floor of state-heavy deduction (PROVEN, cost accounting)
A sweep that keeps and updates a dense covariance (or any n x n matrix per layer) spends at least the cost of a
matrix product per layer, n^omega, i.e. n^{omega - 2} single-input passes per layer (n with schoolbook products). An
order-K moment closure spends ~n^{K+1} per layer, n^{K-1} passes. At fixed eps, MC needs 1/eps^2 passes, so for
n^{K-1} > 1/eps^2 the closure is more expensive than MC whatever its accuracy. Measured floors (earlier lanes): K = 2
about 0.12/n nMSE (stationary regime), K = 2 gains of 2-8x over MC at its own cost at widths 32-128, about 1 at 1024.
So a fixed-order closure is a constant-factor method at its own cost: it can beat sampling only in the precision
window eps^2 < n^{-(K-1)}, by the factor (MC cost at that eps)/(closure cost). For "depth growing with width at fixed
eps", only sweeps with O(n^2 polylog) work per layer (a bounded number of vectors: reference trajectories, mean
propagation) can beat sampling by a growing factor.

## F. Mean-estimation version of the linear-feature separation (PROVEN)
For a feature map P and a hybrid that uses the true law of P X and a surrogate conditional law q for the complement,
error = -E_mu[r (dq/dmu - 1)], r = g - E_mu[g | P X], so |error| <= sqrt(E r^2) sqrt(chi^2(q || mu)) (Cauchy-Schwarz;
needs q << mu). Two-sided P (the relevant subspace, residual eps V): the forward model's error is suppressed by
sqrt(eps V). Forward-only P (past-measurable, so by the decoupling theorem it captures relevance only in proportion to
the cloud variance it captures): no suppression unless P holds the cloud's top-N_fwd directions.

## G. The past's dimension law (MEASURED post hoc; HEURISTIC derivation)
PR of the angular cloud = 1.04 (n/l) + 1.33 (R^2 = 0.967, 232 (net, layer) points, all configurations). Derivation
sketch: if the cloud's variance profile follows the rank-conditioned Lyapunov contraction, lambda_k ~ exp(-2 (k-1) l/n),
then PR = coth(l/n) ~ n/l + l/(3n): the n/l term is the Lyapunov count; the measured offset (~1.3) is not explained.
The eigenvalue log-slopes match -2 l/n for l/n <~ 0.2 (128 x 64 at l = 16: -0.25 both; 256 x 32: -0.10/-0.18/-0.20/-0.21
against -0.06/-0.13/-0.19/-0.22) and saturate near -0.4..-0.6 deeper.
At L = alpha n, layer l = lambda L: PR ~ 1/(alpha lambda) + 1.3 and rho = theta_l L'/phi_lin ~ 3.9 (1 - lambda)/lambda,
both independent of n: the bits that matter at a fixed relative depth do not grow with width. The variance, however,
is created in the first O(1) layers (input-bits lane: C_L = 5.5, 7.2, 8.6 of C_inf = 10.65 at L = 8, 16, 32), where
the cloud's dimension n/l is large and the remaining future is long and rough.

## D. From astra round 1 (to integrate, with provenance)
A1 exact forward-only characterisation (quantisation of the mean-query function T(A)); A2 worst-case INDEX family,
Omega(d) forward-only vs O(log d) future-aware bits; A3 table lower bound; A4 Gaussian water-filling for
C^{1/2} A^T A C^{1/2}; A5 dyadic multilevel regimes under H_ML; A6 E_B J^T J = I and the future-blind subspace theorem;
A7 Model S: annealed second moment infinite at stationarity (stationary covariance-based N needs a quenched or
truncated normalisation); A8 ray counterexample.
