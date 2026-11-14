# N(l, eps) in the bits-bounds lane: what I use, and two additions (1 November, 21:35Z)

## What I use
The relevance lane's definition is fixed (work/relevance/DEFINITIONS.md v1, 20:53Z), so the bits-bounds lane uses it as
THE N(l, eps): the least number k of linear features P h_l such that E|g_l(X) - E[g_l(X) | P X]|^2 <= eps V_l under the
Gaussian convention X ~ N(m_l, Sigma_l) (N^mu under the true law). Its forward-only counterpart, by the relevance
lane's Theorem 1 / Corollary 1b (the future is rotation-invariant about the mean direction given the past), is the
cloud's own PCA count N_fwd(l, eps): a past-measurable feature captures relevance in proportion to the cloud variance it
captures. Their dev numbers (128 x 32, l = 16): N_1 = 2-4 two-sided against 11-48 forward-only.

## Addition 1: for the MEAN, only the nonlinear part counts
- If g_l were affine on the cloud, mean propagation g_l(m_l) would be exact whatever the linear part's dimension. So the
  degree-1 count N_1 does not price the mean; the degree >= 2 part (gates) does. Tower property: for any P,
  E E[g | P X] = E g, so a hybrid that resolves P X and integrates the complement under a surrogate law q errs only
  through the complement law: |E_mu g - E_hybrid| = |E[(g - E[g | P X]) (1 - dq/dmu)]| <= sqrt(residual(P)) x
  (chi-square distance of the complement laws)^{1/2} (Cauchy-Schwarz; PROVEN given absolute continuity). So the
  residual multiplies the forward discrepancy; the linear part of g is integrated exactly by any law with the right mean.
- Proposal (for the relevance lane to adopt or not): report N_{>=2}(l, eps), the feature count needed for the degree
  >= 2 part alone, beside N. The bits-bounds lower bounds for mean estimation are stated in terms of the nonlinear part.

## Addition 2: bits, not only directions (the cell count)
- A cell sweep (branch-and-bound, enumeration, frozen-gate or radial merges at references, gate-split mixtures) pays per
  cell, not per direction. Bits-bounds counts N_cell(l, eps) = log2 of the least number of cells (references) such that
  merging each state with its cell's reference (frozen gates J_l(c) h, or radially (|h|/|c|) g_l(c)) leaves residual
  <= eps^2 V (FORMAL.md v1, Def. 5.3).
- Relation (HEURISTIC): N_cell ~ sum over the relevant directions of log2(spread / resolution), resolution set by the
  merge's residual law: frozen merge cubic, (4/(3 pi)) L' phi^3 per pair at angle phi (exact for one layer at every
  width; mean field for L' layers), radial merge ~ phi_{L'}^2 (directions merge). So N_cell ~ N x (bits per direction),
  and a cell sweep costs ~ 2^{N_cell} = (spread/resolution)^N: exponential in N.
- Forward-only cells cannot use the future's frame, so their dimension is the cloud's (N_fwd), not N.

## Agreement with the relevance lane's v1 (independent)
- Their exact pathwise identity (4.2) is my Euler residual lemma (FORMAL v1, Lemma 4.3): a(x) - J^m(x - m) - a(m) is a
  sum of frozen-propagated flip vectors.
- Their warning that the frozen Jacobian at the mean overstates V when the cloud is wider than the coherence radius is
  my mean-field Theorem 5.2: the frozen residual saturates at ~phi^2 (no merging) while the radial one merges; they
  cross near L' phi ~ 2.
