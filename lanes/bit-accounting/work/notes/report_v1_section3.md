### 4.1 Fixed budgets, all nets: without the shortcut early layers need many more bits (MEASURED)
Best local code found for nMSE 0.1 (channel bits, median over nets; results/A1_table.md, S1_best.md):

| net | l = 0 | L/4 | L/2 | 3L/4 | L-1 | output's own count |
|---|---|---|---|---|---|---|
| ARC 256 x 32 (l = 0, 8, 16, 24, 31) | >256 | 135 | 43 | 25 | 24 | 25 |
| narrow-deep 8 x 256 (l = 0, 64, 128, 192, 255) | 15 | 1.6 | 1.7 | 1.6 | 1.7 | 1.7 |
| 16 x 4 | 22 | 15 | 12 | 10 | (= 3L/4) | 10 |
| 32 x 8 | >32 | 21 | 11 | 8 | 8 | 9 |
| 16 x 16 | 27 | 6 | 4 | 3 | 3 | 3 |
| 32 x 32 | >32 | 5 | 2 | 2 | 2 | 2 |

ARC also needs > 256 bits at l = 2 and 4. At 1% error ARC needs > 256 bits at every l <= 8, about 210 at l = 16, 119 at
l = 24, 135 at l = 31; the best codes at l = 24-31 beat the Gaussian bound on the output (median 170), so the output's
own count at 1% is at most about 114-168 bits on these nets; at 0.1% every ARC layer needs > 256 (Gaussian bound
404-500). Narrow-deep: the state is a ray from layer 8-32 on, so the output is one number times a fixed vector: 1.7,
3.3, 5.0 bits for 10%, 1%, 0.1%. An unrestricted encoder (shown the exact output) needs the same bits at every layer
of the small nets up to training (flat curves in figs/bits_by_layer.png; 1500 steps 4.6-5.9, 3000 steps 2.4-3.5 against
the output's 1.9-3.0).
Comparisons asked for in the brief:
- The relevance lane's linear-feature count N(l, 0.1) on ARC (208, 96, 56, 20, 12, 12 at l = 0, 4, 8, 16, 24, 31):
  about 2 bits per direction at l >= 16, many more where linear features are not enough.
- Gaussian reverse water-filling over the output covariance gives the output-space channel count exactly (19-39 bits
  at 10%, four ARC nets; learned output codes within 1-2%, A1.1). Over the true-law gradient-energy spectrum of layer
  l (the local high-resolution price) it predicts the local count within a factor 1.3 at l >= 8 and overprices early
  layers (334-770 bits where the measured count is > 256) (HEURISTIC, FORMAL 4.4). The degree-1 relevance spectrum
  prices only the linear part (FORMAL 4.3).

### 4.2 Were the earlier counts converged? (certificates of the fixed-budget codes)
- Known answers. (i) Output codes against the Gaussian bound: ARC learned output codes match it within 1-2%; the
  small-net learned output codes (no linear start) sit 0.5-2.4 bits above it (training). (ii) Unrestricted against
  the output's count: flat but 1.5-2.5x high at 1500 steps, within 0.5-1 bit at 3000 steps or with the S7 objective.
  (iii) Planted toy (a target that depends on exactly k sign bits): sign-bit training measures 2, 4-6 and 12 bits for
  k = 2, 4, 8 (unrestricted); the one-ReLU-layer encoder, which can represent the answer exactly, plateaus at nMSE
  0.08, 0.17 and 0.61 (S5.1 missed). Sign-bit training has real optimisation overhead.
- Quantiser optimality (S5, l = 0 and 4/8 so far): the per-code centroid improves on the learned decoder by <= 2% on
  97% of points (decoders are optimal for their encoders); one unrestricted Lloyd step cuts the error a lot (by > 20%
  on 93% of points, 6-30x at 8-16 bits), but re-training the local encoder to emit those codes recovers less than half
  of that on 94% of points (S5.5). So at early layers the local count is set by the restriction, not by optimisation.
  Restarts: sign-bit counts vary by more than 1.5 bits between restarts on 3 of 5 cells (dead codes at random rates,
  S5.4 missed).
- Joint quantisation (S6; 2^b-vector codebooks): b_VQ(10%) = 5.6, 7.5, 8.2 (16 x 4), 7.9, 6.7, 8.0 (32 x 8), 3.2
  (16 x 16) against Gaussian bounds 6.3, 12.3, 10.2, 8.7, 7.0, 10.4, 3.0: a joint binary index needs no more bits than
  the Gaussian channel count (below it on 6 of 8 nets; S6.2 missed in that direction). The earlier binary overhead (b/C
  ~1.3-1.4 for per-coordinate codes, 2-3x for learned sign bits) was encoder limitation; reachable codebooks (actual
  outputs as reconstructions) cost < 0.5 bit more on 6 of 8 nets.
- Bounds on the output's own rate (results/bounds_small.json): Shannon-type lower bound from the top 1-3 principal
  projections and the Gaussian upper bound: 16 x 16 1.2-1.4 <= R(10%) <= 1.9-3.4; 32 x 32 1.5-1.6 <= R <= 1.7-2.8;
  16 x 4 1.7-3.0 <= R <= 6.3-12.3; 32 x 8 2.4-3.4 <= R <= 7.0-10.4.

