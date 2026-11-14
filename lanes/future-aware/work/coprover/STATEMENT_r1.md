# Future-aware layer-wise estimators for ARC's random MLPs: statement for the co-prover, round 1 (2 Nov 2026)

You are asked for an independent analysis. The lane's own theory is being written in parallel and will be frozen
before your answer is read. Label every claim PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE, give proofs
at the level of every nontrivial step for PROVEN items, prefer a correct weaker statement to a strong wrong one, and say
where something is not checked.

## Setting (as in the arc-update lane; its report is /home/agent/workspaces/mats/outbox/arc-update-2026-11-02.md)
- Width n, depth L, x ~ N(0, I_n), h_0 = x, h_l = relu(W_l h_{l-1}), W_l iid entries N(0, 2/n), no biases, no noise.
  P_l = law of h_l. Target Y = E h_L in R^n; error nMSE = |est - Y|^2 / tr Var(h_L). ARC's instance: n = 256, L = 32.
  Cost unit: one forward pass = 2 n^2 L flops; a vector-Jacobian product through t layers costs about 2-3 forward
  passes through those t layers.
- Cut at layer l, t = L - l layers to go, future F_l = (W_{l+1}, ..., W_L), future map g_l: R^n -> R^n (positively
  homogeneous, piecewise linear), so Y = int g_l dP_l for every l.
- Deduction-projection estimator: reconstructions Q_l (finite signed measures), Q_0 = P_0, defects
  Delta_l = Q_l - Phi_l Q_{l-1} (Phi_l = push-forward by h -> relu(W_l h)), est = int h dQ_L. Telescoping (PROVEN):
  est - Y = sum_l <g_l, Delta_l>.
- Forward-only = Q_l depends only on W_1..W_l. Theorem A (arc-update, PROVEN at every finite width): for a
  past-measurable defect Delta at layer l,
    E_future |<g_l, Delta>|^2 = sum_{d >= 0} b_d^{(n,t)} || int |h| (h/|h|)^{tensor d} dDelta(h) ||_F^2,
  b_d >= 0, sum_d b_d = 1, from Mehler's formula on the fresh Gaussian layer W_{l+1} and positive homogeneity.
  Infinite-width values: b_0 = 0.32, 0.68, 0.83, 0.93, 0.97 and b_1 = 0.50, 0.14, 0.05, 0.013, 0.003 at t = 1, 4, 8,
  16, 31; finite width n = 256: b_0 = 0.318, 0.677, 0.824, 0.911, 0.948 at t = 1, 4, 8, 16, 31 (measured).
- Relevance lane Theorem 1 (PROVEN): with e = m/|m| (m the past-measurable mean of the layer-l state) and B an
  orthonormal basis of e-perp, write W_{l+1} = g e^T + M B^T; given the past, g and all later layers, M is iid
  N(0, 2/n) and independent of them. So the future's action on the angular part of the state is rotation-invariant
  given the past ("relevant directions are Haar given the past").
- ARC's "mechanistic L^2 sketching" (Hilton et al., "Mechanistic estimation for expectations of random products",
  May 2026): in a deduction-projection estimator for E_x[f(x) g(x)] with g the deduced state and f the random tail
  (future) drawn from a known law, compress g to g~ so as to minimise E_f[(E_x[f g~] - E_x[f g])^2]; the optimum keeps
  the top eigenfunctions of the tail kernel K(x, x') = E_f[f(x) f(x')], and "the maximum mean squared error is then
  determined by the largest unused eigenvalue". There the kernel uses the tail's LAW, not its realisation.

## Measured facts at 256 x 32 (arc-update and relevance lanes; MEASURED unless marked)
- ARC K = 2 ('augment') nMSE 8.4e-4 at ~450 passes; exact Gaussian closure 1.2e-3; radius-corrected Gaussian closure
  run as a full recursion 4.9e-4 (close to L/n^2 at n = 64, 128, 256 along L = n/8); RQMC gain over MC 1.2-2.2 at
  2^8-2^16 points; at the contest budget 6.5e4 passes RQMC is 7-40x better than the best affordable ARC variant.
- About 60% of the K = 2 closure error is made by layer 8 (accumulated); single-cut Gaussian defects ~2e-4 at l = 2-16.
- Third-cumulant participation ratio of the true cloud: 115 (l = 1), 66 (2), 23 (4), 4-10 (8), 1-4 (l >= 12).
- Value function g_l on the Gaussianised layer-l cloud: mean Hermite degree 21, 7.7, 4.1, 1.9, 1.3 at l = 0, 4, 8, 16,
  24; degree-1 share 0.22, 0.48, 0.61, 0.77, 0.92; number of linear projections of the state needed for 99% of its
  variance N(l, 0.01) = 256, 192, 128, 80, 48 (point estimates); the input map's annealed mean degree is n / E_W V
  (PROVEN), ~19 here, growing linearly in n at fixed L/n.

## Questions
Q1 (conditional pricing; ARC's sketching). Let the layer-l projection depend on the future only through a statistic
   S (a sigma-algebra of future quantities). Give the exact pricing E[|<g_l, Delta>|^2 | past, S] and its relation to
   ARC's L^2 sketching with the conditional kernel K_S(h, h') = E[g_l(h) . g_l(h') | past, S]. Identify the annealed
   kernel's eigen-structure (S trivial; it is Theorem A's kernel) and the realised one (S = everything; rank <= n).
   What does ARC's own rule, applied to their own MLP setting with the tail LAW, keep?
Q2 (k-sketch theorem). S = sigma(W_{l+1} V, W_{l+2}, ..., W_L) with V a past-measurable n x k matrix with
   orthonormal columns. Give K_S exactly (Mehler expansion in the complement), the resulting price of a defect, and
   how much of the forward price a k-sketch method can remove at most, as a function of the defect's structure. Is it
   O(k/n) (or O((k/n)^d) at degree d) for defects of high effective rank, and what replaces this for low-rank ones?
Q3 (future-chosen subspaces). Now V may depend on the future (e.g. the top-k eigenvectors of the cloud-averaged
   E[J^T J] of g_l, J the Jacobian, possibly whitened by the cloud covariance). Using Theorem 1, bound in expectation
   the fraction of the realised price |<g_l, Delta>|^2 of a past-measurable defect that a projection exact on a k-dim
   future-chosen subspace (and unchanged elsewhere) can remove. Is there a Haar-overlap bound, and what effective
   dimension enters (the defect's, the cloud's, the future's)?
Q4 (what can be proven, and why not more). Is there a computational model of future-aware layer-wise estimators
   (future access through q vector-Jacobian products, a k-dim sketch, frozen-gate products, ...) in which a lower bound
   is provable and not artificial? State precisely why an unconditional extension of Theorem A to future-aware
   layer-wise estimators cannot exist (or can), with the strongest correct statement.
Q5 (hybrids). For the estimator est = (closure's value of E_Q[c]) + RQMC mean of (h_L(x) - c(h_l(x))), with c a
   surrogate of g_l built from the future (linear and quadratic in a few relevant directions, say), give the error
   decomposition (bias from the closure's E_Q[c], variance of the residual) and the condition under which it beats a
   sampler with gain G over MC at equal cost, counting the closure and the backward pass. What is the best variance
   reduction available from controls whose mean is exactly known (functions of h_1, whose law is explicit), in terms
   of the value function's chaos decomposition?
Q6 (width scaling). Under which conditions could a future-aware closure's gain over MC grow with n along L = alpha n?
   Relate to the input map's mean degree n / E V and to N(l, eps). Give the single strongest defensible negative
   statement for future-aware layer-wise estimators, and the single strongest positive possibility.

You may read /home/agent/workspaces/mats/outbox/arc-update-2026-11-02.md, /home/agent/workspaces/mats/outbox/
relevance-accounting-2026-11-01.md, /home/agent/workspaces/mats/work/arc-update/FORMAL.md and the arc-update and
relevance code. Do NOT read anything under /home/agent/workspaces/mats/work/future-aware/ other than this file.
Write everything to stdout.
