# Ambiguities in SPEC-learned-experts.md v1 draft, and where my existing code differs (16:55Z, 2 Nov)

Existing code: lib/gmoe.py (per-layer joint GMM on low-rank coordinates, closed-form push), lib/popmoe.py (torch,
gPoE/mixture fusion of predicted component Gaussians, population loss), scratch/step4g.py, scratch/step4p.py. Both
work entirely in d-dimensional projected coordinates (PCA of the cloud), with the out-of-projection part dropped. Dev
results so far are in runs_dev/ and were relayed; nothing scored has run.

## Ambiguities (each with my proposed default)
1. Projection Pi_l "read by the downstream net (backward passes)": which functional? Proposal: top-32 eigenvectors of
   E[J_l^T J_l], J_l = d h_L / d h_l (trace over all outputs; VJPs with random output vectors), per layer; at the input
   the same (the input is isotropic, so this is the only informative choice).
2. State representation: the spec's maps act on full h (A_e in R^{n x n}) and covariances are "projection plus a
   diagonal remainder". Proposal: components carry a full n-dim mean and covariance Pi S_Pi Pi^T + diag(D) (D the
   per-coordinate residual variance outside the projection), and expert maps A_e = B_{l,s} + U_e V_e^T act on the full
   mean. My code is projection-only; this is a rewrite.
3. Gate covariance C_e: diagonal or full in the projection? Proposal: full in Pi_l (d = 32 is small).
4. Gate-reweighted moments (m_e, S_e) and overlaps w_e under NORMALISED gates have no closed form. Options:
   (a) Monte Carlo inside the component (S draws per component, reparameterised, no net evaluations; exact in
   expectation); (b) my ratio-of-Gaussians closed form (exact at K = 1, approximate otherwise). Proposal: (a) with
   S = 256, (b) as a cheap comparison.
5. What gPoE fuses during propagation: the experts' predicted component Gaussians N(A_e m_e + b_e, A_e S_e A_e^T + R_e)
   (precision-weighted with beta_e = w_e), as my code does? Proposal: yes; it returns the common covariance when the
   experts agree.
6. "Calibration NLL under the model's predicted uncertainty": the fused covariance is the population's spread, not the
   uncertainty of its mean. Proposal: carry a separate mean-uncertainty U per component, U' = A U A^T + (sum_e beta_e
   R_e^{-1})^{-1} / n_eff (the point-fusion confidence), and score m_emp ~ N(m_model, U + Cov_emp / M_b).
7. Size: K = 2^12 experts per (source, target) at every one of 32 source layers x 4 targets with full maps is ~1e10
   parameters at 256 x 32. Proposal: the K curve (metric 2) at the five source layers only (input, L/4, L/2, 3L/4,
   L-1), one target each (s = 1, and s = L - l direct-to-output), with K up to 2^12 there; the full chain with
   K <= 2^8 per (l, s).
8. Compute accounting for metric 3: count sampled paths, EM and gradient-descent flops, and propagation flops, all in
   passes (2 n^2 L flops). Confirm that training flops count (they dominate at small n: 1.7-5.8M passes in dev).
9. "Model's pointwise prediction" for the unbiased variant: proposal: chained point fusion from h_0 = x through the
   chain (and skips), i.e. the propagation of a zero-width population.
10. Dev seeds: fresh seeds 9601, 9602 for 32 x 4 and 64 x 8 (my dev so far used 9500). Scored: 128 x 16 nets 300-302,
   then 256 x 32 nets 200-204 (truths: arc-update 2^24-path, arc-noisy 2^26-path).
11. N(0, I) is in the training populations (the spec includes it): then the estimand's population is not held out.
   Proposal: report m_L(N(0, I)) both with and without the N(0, I) batch in training.
12. GPU: one L4 (cap $5) for the 1M-path data and K-curve fits; GPU-LOG.md; delete after.

## Code that must change for the spec
- full-dimensional component means/covariances (2), shared-base low-rank expert maps (spec 3), backward-pass
  projection (1), MC gate moments (4), route fusion with skips, component split/merge with cap K_pop, calibration
  term (6), known-answer tests T1-T5 (T1, T3 already pass for lib/gmoe.py; T2 needs the n = 4 aligned-gate case,
  T4 and T5 new).
