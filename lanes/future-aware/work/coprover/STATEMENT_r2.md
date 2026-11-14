# Future-aware layer-wise estimators, co-prover round 2 (2 Nov 2026)

Setting and notation as in STATEMENT_r1.md (read it first) and your round-1 answer (coprover/astra_r1_answer.md, which
you may read). Labels PROVEN / PROVEN UNDER <hypothesis> / HEURISTIC / CONJECTURE; proofs for PROVEN items; prefer a
correct weaker statement. This round is again independent of the lane's own v2 theory (frozen before your answer is
read): do NOT read work/future-aware/FORMAL.md or anything under work/future-aware/ other than coprover/ and the run
files named below.

## New facts (dev measurements, one net per width; L = n/8; MEASURED, not yet the registered evaluation)
(a) Single cut, 256 x 32: replacing the true layer-l law by "k linear features exact (true samples), linear-Gaussian
    conditional complement (mean and covariance exact)": l = 4, 8, 16: plain Gaussian 3.6e-4, 2.0e-4, 4.1e-4 (nMSE);
    features = whitened top-k active subspace of the NONLINEAR part of the future map (E[J^T J] - E[J]^T E[J] whitened
    by the cloud covariance): k = 16: 1.1e-4, 2.1e-5, 4.1e-5; k = 64: 3.1e-6, 5.4e-6, 6.5e-6; cloud-PCA features
    k = 64: 3.1e-5, 1.9e-5, 3.1e-5; random k = 64: 6.3e-5, 1.6e-5, 4.3e-5.
(b) The same projection used at EVERY layer of a recursion (the k-dim law carried by 2^18 particles, the complement
    regenerated each layer from the push's mean and covariance): improvement over the Gaussian closure (error ratio)
    at fixed k = 16: 4.8, 2.1, 1.7 at n = 64, 128, 256; at k = n/4: 4.8, 7.7, 18; at k = n/2: 48, 94 (n = 64, 128).
    PCA features at k = n/4 are 2-7x worse than the future features.
(c) ARC's own K = 3 'simple' cumulant propagation with the third-cumulant tensor projected at every hidden layer onto
    a k-dim span, kappa_3 <- kappa_3 x_1 Pi x_2 Pi x_3 Pi, Pi = S A (A^T S A)^-1 A^T (S = the method's covariance):
    retained fraction R = (e_k2 - e_proj)/(e_k2 - e_k3): future features (VJPs at the method's own Gaussian state)
    k = n/4: 0.98, 0.95, 1.15 at n = 64, 128, 256; k = n/8: 0.82, 0.84, 1.18; PCA k = n/8: 0.62, 0.57, -; at 256 every
    projection with k >= 32 (future, mean-field future, PCA) is better than full k3 (R 1.15-1.23 on one net; on a
    second net (eval net 200, k3 17x better than k2 there): future k = 64: R = 0.96, PCA k = 64: 0.85, k = 16: 0.56
    (future) vs 0.43 (PCA)).
(d) Hybrid: control c(h_l) linear (cloud-averaged Jacobian or least-squares) or linear + quadratic in 16 future
    features, exact mean at l = 1: residual variance share eta = 0.53-0.70 at 256 x 32 (0.29-0.47 at n = 64); but
    scrambled-Sobol RQMC on the residual is no better than RQMC on h_L at 2^14 points (3.4-3.8e-5 vs 3.5e-5) and only
    1.1-1.5x better at 2^10-2^12; deeper controls carry a closure bias beta = 1.4-8.5e-4 at l >= 8.

## Questions
Q1 (future-weighted ladder). Formalise an order-K cumulant hierarchy whose tensors of orders 3..K are restricted at
   every layer to k-dim subspaces. (i) Give a cost model of a DEDICATED implementation per layer (which contractions
   are unavoidable: the linear step, the relu's fresh Gaussian-part cumulants projected onto the new subspace, mixed
   terms), in flops as a function of n, k, K. (ii) Under ARC's per-order error law with ratio q and that cost model,
   what is the error-cost exponent, and what is the exact criterion on (q, k) for matching sampling's rate? Is
   gamma* = log q / log k correct, and does the n^2-type overhead change it? (iii) What does (c) say about q and k at
   order 3, and what would have to hold at order 4 for a window that grows with n along L = alpha n?
Q2 (dimension of the future's nonlinear reading). The linear relevance's participation ratio is ~ n/(2t + 1) (bounded
   at t proportional to n). For the nonlinear part (gate fluctuations), take the mean-field independent-gate recursion
   R_l = W_{l+1}^T [P R_{l+1} P + diag(p (1 - p) diag(R_{l+1}))] W_{l+1}, P = diag(p_{l+1}), R_L = I, and its part
   beyond the linear one. Derive (PROVEN, or PROVEN UNDER free-probability hypotheses) the effective (stable) rank of
   the nonlinear part restricted to the transverse space, as a function of n and t, and say whether it is Theta(n) at
   t = beta n. Relate to (b): a fixed k losing its effect as n grows, k = cn keeping it.
Q3 (why the exact-marginal family cannot be cheap, or can). The family in (a)-(b) needs k proportional to n to reduce
   the closure error by a fixed factor. State precisely what a deterministic representation of the k-dim law would
   need (information-based complexity: worst-case integration of the future's reading over a k-dim non-Gaussian law,
   e.g. Bakhvalov-type lower bounds for Lipschitz or piecewise-linear integrands), and what is NOT implied for this
   specific law. Is there any class of deterministic representations (cumulants of order <= K in the k dims,
   mixtures with M components, lattice rules) whose error on piecewise-linear integrands is provably better than
   M^{-1/k}-type rates?
Q4 (hybrid and RQMC). Explain (d): why a control that removes the linear (and low-order) part of h_L gives almost no
   gain on top of scrambled-Sobol RQMC. State a correct result (e.g. via the ANOVA / Walsh-coefficient description of
   scrambled-net variance, Owen) on the RQMC variance of a function versus that of its residual after subtracting a
   low-order part, and the condition under which control and RQMC gains multiply.
Q5 (strongest statement). Give the single strongest correct statement, with hypotheses, for "future-awareness changes
   the dimension of the hard part (n -> c n), not its nature", and the single strongest positive possibility left.
Write everything to stdout.
