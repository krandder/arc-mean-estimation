# gram-chain lane: notes for the relevance and bits-bounds lanes (1 Nov 2026, 21:30Z; updated as results land)

Read-only for you; I read your DEFINITIONS.md (relevance v1, 21:00Z) and questions.md. Main gets my disagreements.

1. What the chain can give you, exactly (annealed = weight-averaged): any E_W of a fixed-weight quantity that is a noise
   (or input) expectation of a function of a fixed number of replicas' Gram path, for a fixed sharing pattern
   (FORMAL.md 1.1-1.2; lib/gc2.py, tested against explicit nets). In particular your M_l = V_l / V (memory share) is
   annealed-exact with 2 replicas (identical at l, independent future noise); its across-net second moment needs 4.
2. What it cannot give you: your Gaussian-convention quantities (gamma_l = N(m_l, Sigma_l)) are NOT replica quantities:
   sampling X ~ N(m_l, Sigma_l) needs the net's own mean and covariance. The chain gives the true-law versions only, and
   its "Hermite" curves are in the noise coordinates (noise correlation rho per layer), not in layer-l Gaussian
   coordinates. So K_l(rho) in your 4.1 has no exact annealed counterpart; the noise-coordinate analogue does.
3. Integrability warning: E_W of raw-state second moments is infinite in the stationary regime (E Q = inf and the radius
   ratio does not shrink at large Q): annealed versions of tr Cov(h | W), of V_l for raw a, etc. are infinite; use the
   direction u = a/|a| and log|a|, or per-net normalisation. (FORMAL 1.5.)
4. Results you may use (all in FORMAL.md, numbers in results/ and runs/):
   - Stationary closed relevance (your M_l, direction observable), mean field: M(t) = 1 - Y((t-1)/T*), Y' = 1 - Y^{3/2},
     T* = (Q+1) delta*(Q) ~ 2.231 Q^{1/3}; area 0.791 T*; half after ~6 layers at n = 256 (ratio of means over the
     radius law) and ~8 at the median radius. Radius (log|a|) memory is ~n layers. Your Q3/Q5 "separate derivation
     needed" for the stationary regime: this is it (two replicas identical at l, independent future noise: their angle
     grows from 0 to delta*; M = 1 - E f(delta_{t-1}) / E f(delta*)).
   - Free-position dimension formula (linear regime): 1/PR_rel = 1/PR_C + 1/PR_M - 1/n, PR_M = n/(2t+1) for t frozen-gate
     ReLU layers (one ReLU layer has phi(M^2)/phi(M)^2 = 3). Same suspicion as your Q1; my Part B tests it with 4- and
     8-replica chains.
   - Input regime: the angular PR of the input cloud at layer l is a 1/n (four-point vertex) effect: the double
     difference D of four inputs obeys D' = kappa'(c_l) D + zeta_l; PR(l) = 4n(1 - c_l)^2/V_D(l) ~ 1.5 n/l. Exact chain at
     n = 256: 166, 62, 18.8, 12.1, 6.1 at l = 1, 4, 16, 32, 64 (recursion 167, 62, 19, 10.3, 5.3; input-bits nets 159, 57,
     17, 9.6, 6.1).
   - At sigma = 0 the radius |h_l| carries (1/2 + C_l)/(1/2 + C_L) of E_W Var_x(log|a|) (kernel); exact chain at
     256 x 32: 0.19, 0.29, 0.46, 0.64, 0.82, 0.93, 0.99 at l = 1, 2, 4, 8, 16, 24, 31.
   - Across-net CV of the per-net direction-cloud size is ~0.5 at n = 64 and grows toward 0.68 (radius-driven, not
     self-averaging); hypothesis: per-net quantities depend on the net mainly through its radius (Part C tests it).
5. Duplicate-run avoidance: I run per-net V_P(t; W), T_P(t; W), cloud trace and PR on nets n = 8-256 (seeds 5000+,
   Part C). I do NOT measure N(l, eps), Hermite shares in layer-l coordinates, or gate attributions; those are yours.
