# preint: prior-lane facts, literature, and the design choices (leaf pool-ttdzrk.17.2, 2 Nov 2026)

Labels as in earlier lanes: PROVEN, MEASURED, HEURISTIC. [prior: lane] = an earlier lane's report.

## Prior-lane facts used here

1. RQMC at the ladder and at 256 x 32 [prior: arc-update, runs/rqmc_*.json; MEASURED; scrambled Sobol, inverse
   normal, radius not exact, 8 replicates, 2^24/2^26-path truths]. N * nMSE (= RQMC / MC at equal N), median over
   nets, N = 2^8, 2^10, 2^12, 2^14 (2^16):
   n=32 L=4: 0.29 0.24 0.19 0.19; n=64 L=8: 0.39 0.32 0.31 0.35; n=128 L=16: 0.58 0.50 0.49 0.40;
   n=256 L=32: 0.80 0.63 0.52 0.51 (0.48). Slopes over the window 0.97-1.18, but the last points are flat:
   a plateau c(n)/N with c growing with width. (My reading, notes/QUESTIONS.md A4.)
2. 8 x 256 narrow-deep, input dim 8 [prior: nd-exact, runs/baselines_s*.json; MEASURED, 40/16/8 replicates]:
   cost (passes) x nMSE falls over 4 decades for RQMC (radius exact, 262 mv/pt): 0.4-1.2 at 8 passes ->
   0.009-0.11 at 1.3e5 passes. RQMCJ (Sobol + tail map J_48, 55 mv/pt + 1,664 mv setup): 0.03-0.06 -> 0.01-0.02,
   noisy. Bits per halving of RMSE: RQMC 1.44-2.06, RQMCJ 1.31-1.86 (MSE exponents 0.97-1.39 and 1.08-1.53).
   Tail identity E[a] = J_c E[h_c] (one downstream class from c = 20-48; premise MEASURED on samples).
   Line crossings: a random line crosses a median 103 regions of layers 1..48 within |t| <= 4 (dev net 103; grid
   count, a lower bound) -> nd-exact's estimate "about 10^4 mv per exact line, 180 RQMCJ points" (not tried there).
   Typical distance to the nearest region boundary 0.003-0.006 (sine) at depth 32: regions are thin.
3. Multilevel shared-trajectory sampler [prior: unrestricted, lib/mlmc.py; astra r3]: control
   G_r(U) = m_n s_r |h_r(U)| q_L from one reference path; risk (sum_j sqrt(V_j C_j))^2 / T; about break-even with
   radius-exact MC at L <= n/4 (incl. 256 x 32), 15x at 8 x 256. A variance-constant method (exponent 1).
4. Relevance lane [prior: relevance-accounting, MEASURED on ARC 256 x 32]: at the input the output's mean Hermite
   degree is 16-30, degree-1 share 0.22, even surrogate 0.21, remainder 0.57; 99% capture needs all 256 input
   directions; an exact conditional-mean control on the top 16/64/128 active-subspace features gains 1.33/1.80/3.11x.
   So one input direction carries a few percent of the variance at most.

## Literature (checked 2 Nov 2026 by search; abstracts read, full texts not)

- Griebel, Kuo, Sloan, "The smoothing effect of integration in R^d and the ANOVA decomposition", Math. Comp. 82
  (2013) 383-400 (and the 2010 J. Complexity paper on the ANOVA decomposition; 2017 Math. Comp. note): integrating
  out one variable smooths a kink max(phi, 0) when phi is strictly monotone in that variable.
- Griewank, Kuo, Leovey, Sloan, "High dimensional integration of kinks and jumps - smoothing by preintegration",
  J. Comput. Appl. Math. 344 (2018) 259-274 (arXiv:1712.00920): under monotonicity the preintegrated function lies in
  mixed Sobolev spaces, so QMC / sparse grids can reach near-optimal rates.
- Gilbert, Kuo, Sloan, "Preintegration is not smoothing when monotonicity fails", in Advances in Modeling and
  Simulation (Springer 2022) 169-191 (arXiv:2112.11621): without monotonicity, square-root or other singularities
  remain. Companion: "Analysis of preintegration followed by QMC for distribution functions and densities", SIAM J.
  Numer. Anal. 61 (2023) (arXiv:2112.10308).
- He, "On the error rate of conditional quasi-Monte Carlo for discontinuous functions", SIAM J. Numer. Anal. 57
  (2019) 854-874: O(n^{-1+eps}) mean error when discontinuities are QMC-friendly (axis-parallel) after conditioning.
- He, Wang, SIAM J. Numer. Anal. 53 (2015) 2488-2503: RQMC RMSE O(n^{-1/2 - 1/(4d-2) + eps}) for certain
  discontinuous integrands in d dims (the d-dependence that kills the gain as d grows).
- Liu, Owen, "Pre-integration via active subspaces" (arXiv:2202.02682; SIAM J. Numer. Anal.): for Gaussian inputs
  any linear combination can be pre-integrated; choose the top eigenvector of E[grad grad^T]; under MC and under
  scrambled nets pre-integration can reduce but not increase the variance.
- Background (not re-checked today): Owen 1997 (scrambled nets, smooth integrands, variance O(N^-3 log^{d-1} N));
  Bakhvalov 1959 / Novak 1988 (optimal randomized error N^{-1/2 - s/d} on C^s or W^s); Novak and Wozniakowski,
  Tractability of Multivariate Problems (curse of dimensionality for unweighted isotropic classes).

What the literature does not cover: deep piecewise-linear integrands with 10^3-10^5 kinks per line, bent kink
surfaces, and the cost of finding all breakpoints. Monotonicity in the sense of Gilbert-Kuo-Sloan fails for deep
nets (a line can cross a bent kink surface twice), but the folds are piecewise linear, where crossings merge
linearly, not as a square root; whether that keeps C^{1,1} is FORMAL's first question.

## Design choices (options considered, choice, reason)

D1. What is integrated exactly.
  (a) The Gaussian line y + t u, t ~ N(0, 1), y on u-perp: g(y) = int f(y + t u) phi(t) dt (classic preintegration).
  (b) Line + radius: by positive homogeneity f(rho (yhat + s u)) = rho f(yhat + s u), so
      E[f | yhat] = int f(yhat + s u) w(s) ds, w(s) = (k / sqrt(2 pi)) (1 + s^2)^{-(k+2)/2}, k = d - 1
      (a scaled Student-t density with k+1 degrees of freedom; int w = E chi_k). Same breakpoints, same cost as (a).
  Choice (b): it conditions on less (yhat instead of y), so its variance is never larger (Rao-Blackwell), at equal
  cost; the outer integral runs on the sphere S^{d-2} of u-perp.
D2. Unbounded line.
  (a) Truncate |s| <= S with an MC tail; (b) exact: homogeneous vertices. Treat the line as the half great circle
      from -u to +u through yhat; vertices are vectors in span(yhat, u); between consecutive vertices the net is
      linear on the cone they span, the ends +-u give the asymptotic slopes f(+-u) (shared by all lines).
  Choice (b): exact, no tuning, and f(+-u) costs one pass per direction u. (a) is kept in reserve for 256 x 32 if the
  full half circle is much more expensive than the window that carries the weight (Rice estimate: about 6x).
D3. Direction u.
  (a) random, fresh per replicate (unbiased over u as well); (b) top eigenvector of E[J^T J] (Liu-Owen active
  subspace; J = Jacobian of the output, summed over output coordinates); (c) top right singular vector of the
  cloud-averaged Jacobian E[J] (main's "top future-relevant direction"). (b) and (c) need a pilot, which is charged.
  Choice: (a) and (b) in the scored runs; (c) on dev nets only unless it beats (b) there.
D4. Outer rule. Scrambled Sobol in d-1 dims (scipy LMS + digital shift, as au.rqmc), inverse normal, normalised to the
  sphere of u-perp (the nd-exact sphere convention). MC outer rule for the conditional-MC comparison.
D5. Combinations. PI-RQMCJ at 8 x 256: lines through layers 1..c only, then J_c (exact under the tail premise
  that RQMCJ also uses). Multilevel: only if a level difference is line-integrable more cheaply than the full net.
  Randomness lane's designs: combine with its best registered design once it exists (coordination with main).
