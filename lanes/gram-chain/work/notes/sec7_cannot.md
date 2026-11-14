## 7. What the chain cannot account for, and how much that is

- Which directions (PROVEN, FORMAL 1.3; relevance lane Theorem 1). Given the past, the future is invariant under
  rotations of layer l that fix the replicas (sharper: fix the cloud's mean direction), so every annealed relevance
  quantity is the same for every direction outside the replicas' span. The relevant k-frame at layer l is Haar-random
  relative to everything past-measurable except the state's own direction (the kstar-frames lane's Proposition 2 is the
  same fact seen from the past). Specifying a k-dimensional subspace of R^n to precision eps takes about
  k(n - k) log2(1/eps) bits; the chain supplies O(k) numbers (the spectrum's moments). In the stationary regime,
  k ~ n/(tau + 2t) ~ n^{2/3} near the output, so about n^{5/3} log2(1/eps) bits per layer are per-net information that no
  annealed theory and no forward-only computation can supply; only a backward pass through the specific weights (or a
  learned map, which the kstar-frames lane found recovers 93-99% of the sensitivity weight) can.
- Per-net ratios. A fixed-weight Sobol index, participation ratio or relevance share is a ratio of noise
  expectations; the chain gives weight averages of numerator and denominator and their joint moments (2r replicas for
  the across-net second moment of an r-replica quantity), not the average of the ratio. Part C shows how far ratios of
  annealed means sit from per-net medians.
- Raw-state moments in the stationary regime are infinite (section 1); annealed raw quantities do not exist.
- Rare nets. Annealed tangent means are carried by rare nets (E_W |J v|^2 = |v|^2 while the typical value decays), and
  heavy radius tails make ratio-of-means estimands weight large-cloud nets.
- Conditioning on a replica's radius approximates conditioning on the net's radius (the radius varies by n^{-1/3}
  within a net and by O(1) across nets) but does not keep replicas iid given the weights; radius-binned chain
  statistics in this report are labelled approximate.
