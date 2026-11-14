# Co-prover statement, round 1 (lane preint, 2 November 2026): pre-integration of deep ReLU nets and the rate of
# estimating their output means

## Setting
- Net: x in R^d, h_0 = x, h_l = relu(W_l h_{l-1}), l = 1..L, W_l iid N(0, 2/n) entries, square n x n, no biases,
  input dim d = n ("ARC family"; ARC's contest shape is n = 256, L = 32). Output f(x) = h_L(x) in R^n. A second family
  is narrow-deep: n = d = 8, L = 256 (inputs synchronise; all live states share one downstream activation pattern
  from layer 20-48 on, so f = J_c h_c there with J_c of rank 1).
- Estimand: E_{x ~ N(0, I_d)} f(x) (all n coordinates). Score nMSE = |est - E f|^2 / tr Var f; plain MC with N paths
  scores 1/N. Cost in forward passes (2 n^2 L FLOPs each).
- f is continuous, piecewise linear on a finite polyhedral fan (cones through 0), positively homogeneous of degree 1.
- Pre-integration (line + radius). For a unit u, x = rho (yhat + s u) with yhat uniform on the unit sphere of u-perp,
  rho ~ chi_{d-1}, s = t / rho, so E[f | yhat] = int f(yhat + s u) w(s) ds with w(s) = (k / sqrt(2 pi)) (1 + s^2)^{-(k+2)/2},
  k = d - 1. (Classic version: g(y) = int f(y + t u) phi(t) dt on u-perp.) Exact algorithm: carry the vertices of the
  half great circle from -u to +u through the layers; one matvec per vertex per layer; a sign change of a unit inside
  a segment adds a vertex (interpolated, no matvec); the integral is a sum of closed forms. Then RQMC (scrambled
  Sobol) over yhat in d - 1 dims mapped to the sphere.

## Measured facts (this lane and earlier lanes; MEASURED unless stated)
1. Vertices on the half great circle after layer l, ARC family n = 8..256, L <= 64 (random u, yhat): 3 + n l within
   a factor 0.76-1.39 (exactly 3 + n at l = 1). At 256 x 32: 6,686 vertices (a window holding all but 1e-8 of the
   weight: 1,406), cost of one exact line 3,469 passes (window: 752). At 8 x 256 the count saturates at 103-172 by
   depth 16-32 (synchronisation).
2. RQMC (scrambled Sobol, inverse normal, radius not exact; arc-update lane) on the ARC family along L = n/8:
   N * nMSE at N = 2^8, 2^10, 2^12, 2^14 (2^16), median over 5-9 nets: n = 32: 0.29, 0.24, 0.19, 0.19;
   n = 64: 0.39, 0.32, 0.31, 0.35; n = 128: 0.58, 0.50, 0.49, 0.40; n = 256: 0.80, 0.63, 0.52, 0.51 (0.48).
   At 8 x 256 (nd-exact lane) cost x nMSE of RQMC keeps falling over 4 decades (0.4-1.2 -> 0.01-0.1).
3. One exact line + radius integral with random u removes 12% of the variance at 32 x 4 (30% with u = top
   eigenvector of E[J^T J]) and 45% at 8 x 256 (dev nets). On a 32 x 4 dev net, at equal numbers of lines and
   points PI-RQMC is only about as accurate as RQMC (per line vs per point), at 40-65 times the cost.
4. Relevance lane (ARC 256 x 32, at the input): mean Hermite degree of the output 16-30; degree-1 share 0.22;
   99% capture needs all 256 input directions. Arc-update lane: 1 - b_0 ~ 9 pi^2 / (2 t^2), b_1 = Theta(t^{-3}) for
   the depth-t kernel's power-series coefficients (b_d are the coefficients of the dual kernel kappa_t(rho)).

## Questions (label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE; prove PROVEN items at
## the level of every nontrivial step; prefer a correct weaker statement to a strong wrong one)
Q1. Smoothness. What smoothness do g (on u-perp) and E[f | yhat] (on the sphere of u-perp) have, for u not parallel to
    any facet of the fan, and when that fails? Is the monotonicity condition of Gilbert-Kuo-Sloan ("Preintegration is
    not smoothing when monotonicity fails") needed for piecewise-linear f? Give the class (Holder / Sobolev, isotropic
    or mixed) with constants in terms of the fan (angles between u and facets, slope jumps).
Q2. Rates for a fixed net. Asymptotic MSE-vs-N rates of (a) RQMC on f (or radius-exact RQMC on S^{d-1}), (b) RQMC on
    the pre-integrated function on S^{d-2}, (c) an optimal randomized algorithm on each (Bakhvalov / Novak type).
    Does the gain survive in the pre-asymptotic regime, where a quadrature cell contains many kinks (8 x 256 has
    about 10^5 regions in 8 dims; typical distance to a region boundary 0.003-0.006)? A useful model may be a Poisson
    process of kink hyperplanes with random orientations; check whether its spectrum is |xi|^{-(d+3)} for f and what
    it is after integrating along u.
Q3. Cost. Prove or refute: in the wide-net (Gaussian-process) limit, each unit at each layer has on average one sign
    change on a half great circle (Rice's formula, using that the ReLU correlation map has derivative 1 at rho = 1),
    so an exact line costs about n L / 2 passes, and a window of angular half-width psi_0 about (n L / 2)(2 psi_0 / pi).
    With the rates of Q2, at what compute could PI-RQMC overtake RQMC, as a function of d (and n, L)?
Q4. Wide-net limit. The weight-averaged kernel K(x, x') = E_W f(x) . f(x') is exactly |x||x'| kappa(<xhat, xhat'>) at
    every finite width (rotation invariance of W_1, homogeneity). For any rule linear in f (N point evaluations or N
    line + radius integrals, nodes and weights possibly randomised), E_W |E_mu f - nu(f)|^2 = MMD_K^2(mu, nu).
    (a) Is that identity right, and what does it give as a lower bound in terms of the Gegenbauer energies of kappa in
    dimension d? (b) Can one prove that along L = alpha n no such rule achieves MSE <= C N^{-gamma} with gamma > 1
    uniformly in n (for N up to poly(n), or up to exp(o(n)))? Or give a counterexample. (c) Explain or predict the
    RQMC plateau constants of fact 2 from the degree distribution of kappa.
Q5. Better ideas. Is there any estimator from the sampling side (or a modest white-box addition to it) whose MSE
    exponent in compute exceeds 1 and stays above 1 as the width grows along L = alpha n? If you think none exists,
    state the strongest negative you can prove and what kind of ingredient (non-linear in f, adaptive, white-box use
    of the weights) would be required to escape it. Then name the single most promising concrete test.
