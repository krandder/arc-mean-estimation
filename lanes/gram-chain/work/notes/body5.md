## 7. What the chain cannot account for, and how much that is

- Which directions. PROVEN (FORMAL 1.3; relevance lane Theorem 1 is the sharper form): given the past, the joint law of
  the future responses to perturbations of layer l depends on the perturbations only through their Gram relations with
  the replicas (rotations of layer l fixing the replicas leave it unchanged). So the chain, which
  only sees Gram matrices, carries no information about which directions of layer l are relevant; and the frozen
  Jacobian's transverse singular frame is Haar given the past (relevance lane Corollary 1b, PROVEN). That the frame of the
  full nonlinear, cloud-averaged relevance operator is Haar relative to the cloud is HEURISTIC (it is the free-product
  assumption of 3.3). None of this applies to output coordinates (E[h' | h] is along the all-ones vector).
  Size of what is missing (interpretation, not a bound): describing a generic k-dimensional subspace of R^n to precision
  eps takes about k(n - k) log2(1/eps) bits, while the chain supplies O(k) numbers (spectral moments). With k taken of the
  order of the participation ratio, n^{2/3} near the output in the stationary regime, that is of order n^{5/3}
  log2(1/eps) bits per layer. A participation ratio is not the rank needed to capture 1 - eps of the variance (the
  spectrum's tail is not measured here), and nothing here shows that estimating a mean requires encoding that subspace;
  the kstar-frames lane found a polynomial-size learned map recovering 93-99% of the sensitivity weight.
- Per-net ratios. A fixed-weight Sobol index, participation ratio or relevance share is a ratio of noise
  expectations; the chain gives weight averages of numerator and denominator and their joint moments (2r replicas for
  the across-net second moment of an r-replica quantity), not the average of the ratio. Part C shows how far ratios of
  annealed means sit from per-net medians.
- Raw-state second moments: in the stationary regime the annealed second moments of raw-state differences are infinite
  (section 1), so the chain gives no annealed raw-variance quantity; it gives the direction and log-radius versions.
- Rare nets. Annealed tangent means are carried by rare nets (E_W |J v|^2 = |v|^2 while the typical value decays), and
  heavy radius tails make ratio-of-means estimands weight large-cloud nets.
- Conditioning on a replica's radius approximates conditioning on the net's radius (the radius varies by n^{-1/3}
  within a net and by O(1) across nets) but does not keep replicas iid given the weights; radius-binned chain
  statistics in this report are labelled approximate.
- What this means for M1 (interpretation only). The chain says how much of the output's variance each layer's state
  decides, for how long, and with what participation ratio. It says nothing about which directions, and for the frozen
  Jacobian those are Haar given the past apart from the state's own direction (PROVEN). If a method had to encode a
  generic rank-k relevant subspace per layer, that would cost about k(n - k) log2(1/eps) bits; the measured moments do
  not establish the required rank k (a participation ratio is not a rank), and nothing here shows that estimating the
  mean requires encoding any subspace. Whether it does is the bits-bounds lane's question.

## 8. Coordination with the sibling lanes

- Relevance accounting (work/relevance/, quenched forward-backward theory). Their Theorem 1 (rotation invariance about
  the mean direction) is the sharper form of my FORMAL 1.3, and their free-product Corollary 1c is the same formula as
  FORMAL 3.4 / 7.6 (found independently by them, by me and by gpt-6-astra). Two points I sent them
  (`work/gram-chain/notes/for-siblings.md`): their Gaussian-convention quantities (gamma_l = N(m_l, Sigma_l), K_l(rho))
  are not replica quantities, so the chain cannot give their annealed counterparts exactly (it gives the true-law,
  noise-coordinate versions); and the stationary memory share they need a "separate derivation" for is FORMAL 3.2:
  M(t) = 1 - Y((t - 1)/T*), checked here to within 0.003-0.014 at n = 256-1024 (section 3). Their per-net memory shares
  for the raw output at n = 32-64 fit my two-channel form (1 - rho) V_P^dir + rho V_P^log (section 3.2), and their
  quenched counts N(0.1) (12, 12, 8, 6, 2 at t = 1, 2, 4, 8, 16, n = 64) are of the size of my participation ratios
  (15, 12, 8, 5, 3). One nuance: their Corollary 1c says the degree-1 count follows the backward spectrum; with
  PR_rel = n/(n/PR_C + c t) that holds once c t exceeds n/PR_C (about t > 3 at n = 256), while over the last couple of
  layers the cloud's own dimension n^{2/3} is the binding term. Their dev observation that the stationary
  direction channel is degree-1 dominated supports using the linear free-product formula in the stationary regime. No
  disagreement; no duplicated runs (they measure N(l, eps) and Hermite shares on nets; I measure annealed quantities and
  per-net scatter of cloud size, PR and relevance).
- Bits-bounds (work/bits-bounds/, theory). Their forward-only cell count N_fwd is "an exact finite-width chain
  function"; the chain library (`lib/gc2.py`) computes such functions. No overlap in runs.
- Disagreement reported to main: the numerics lane's 1/k cloud spectrum (and with it the (log n)^2 dimension) is
  contradicted by the four-point law PR_C = n theta*/pi and by its radius dependence in the exact chain (section 2.4).
