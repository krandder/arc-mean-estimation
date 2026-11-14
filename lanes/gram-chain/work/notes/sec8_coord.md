## 8. Coordination with the sibling lanes

- Relevance accounting (work/relevance/, quenched forward-backward theory). Their Theorem 1 (rotation invariance about
  the mean direction) is the sharper form of my FORMAL 1.3, and their free-product Corollary 1c is the same formula as
  FORMAL 3.4 / 7.6 (found independently by them, by me and by gpt-6-astra). Two points I sent them
  (`work/gram-chain/notes/for-siblings.md`): their Gaussian-convention quantities (gamma_l = N(m_l, Sigma_l), K_l(rho))
  are not replica quantities, so the chain cannot give their annealed counterparts exactly (it gives the true-law,
  noise-coordinate versions); and the stationary memory share they need a "separate derivation" for is FORMAL 3.2:
  M(t) = 1 - Y((t - 1)/T*), checked here to within 0.01-0.05 (section 3). Their dev observation that the stationary
  direction channel is degree-1 dominated supports using the linear free-product formula in the stationary regime. No
  disagreement; no duplicated runs (they measure N(l, eps) and Hermite shares on nets; I measure annealed quantities and
  per-net scatter of cloud size, PR and relevance).
- Bits-bounds (work/bits-bounds/, theory). Their forward-only cell count N_fwd is "an exact finite-width chain
  function"; the chain library (`lib/gc2.py`) computes such functions. No overlap in runs.
- Disagreement reported to main: the numerics lane's 1/k cloud spectrum (and with it the (log n)^2 dimension) is
  contradicted by the four-point law PR_C = n theta*/pi and by its radius dependence in the exact chain (section 2.4).
