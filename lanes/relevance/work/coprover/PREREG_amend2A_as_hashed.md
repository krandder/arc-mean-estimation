# Relevance lane: pre-registration

## Part 1 (accounting table predictions, both regimes)

Registered before any evaluation run. The hash and time of this part are in prereg_hashes.txt. Theory: FORMAL.md v1
(frozen 21:17:35Z, sha 23ab1bb1...). Prediction code lib/theory_v1.py; measurement code lib/rel.py, lib/accounting.py;
runner scratch/eval_part1.py; scorer scratch/score_part1.py (all hashed with this part; the scorer implements the
rules below and was tested on dev/smoke data only). Definitions: DEFINITIONS.md v1.

### Evaluation nets (none used in development; dev nets had seeds >= 9100, and narrow-deep dev seed 111)
- E-ARC (input regime, sigma = 0): n = 256, L = 32, seeds 4000-4003 (the stationary lane's weight stream, layers 1..32;
  the input-bits lane's Part 1-2 nets). Layers l = 0, 4, 8, 16, 24, 28, 31. P = 4096.
- E-ND (input regime, sigma = 0): narrow-deep plain 8 x 256 (nd.make_weights), seeds 203, 216, 217, 220, 221, 223
  (the narrow-deep lane's registered healthy nets). Layers 0, 2, 4, 8, 16, 32, 64, 128, 192, 255. P = 8192.
- E-ST (noise-stationary, sigma = 1): stationary-lane stream st.W_layer, seeds 1000-1003 at n = 32, 64, 128 and
  1000-1001 at n = 256. State h_{-s} (t = s + 1 weight layers to go, output relu(W_1 h_0)):
  t in {1, 2, 4, 8, 16, 32, 64, 128} with t <= n, plus t = 2n for n <= 64, plus t = 256 at n = 256.
  P = 4096 (n <= 128), 2048 (n = 256). Clouds: 4P stationary paths per net, burn-in 8n layers before the deepest state.

### Measurements (lib/accounting.analyse_layer)
As DEFINITIONS.md section 5. Measured N(l, eps): the smallest k on the grid {0,1,2,3,4,6,8,12,16,24,32,48,64,96,128,
160,192,224,256} with residual(top-k active-subspace directions, Gaussian convention, point estimate) <= eps V_gauss;
N_lo = the previous grid value; the true N of that basis lies in (N_lo, N]. Same for the scalar readout r.a (fixed
seeded random unit r) on its own active subspace. N_1(eps): from the eigenvalues of B~^T B~ (degree-1 relevance
spectrum), cumulative share of V_1. s_1 = V_1/V (Stein, Gaussian), D = J(1)/V. A cell is resolved if V_gauss > 3 SE and,
in E-ST, the memory share M = V_true / tr Var(a) >= 0.02; unresolved cells are listed and not scored.

### Predictions (theory v1 unless marked DEV = read off the dev nets, a weaker kind of prediction)
- P1 (decoupling; degree-1 count). The free-product prediction of N_1 (measured cloud spectrum, half-width Gaussian
  backward model, Haar orientation) is within a factor 2 (or within 1) of the measured N_1 on >= 75% of resolved
  E-ARC + E-ST cells, separately for eps = 0.1 and 0.01. The forward-only count (PCA of the cloud) is >= 3 times the
  measured N_1 at eps = 0.01 on >= 75% of resolved cells with t >= 4.
- P2 (degree-1 share). |s_1 - s_1(v1)| <= 0.12 on >= 75% of resolved cells, separately E-ARC and E-ST (E-ND reported,
  not scored: the Gaussian convention is not valid there, see P10b).
- P3 (mean degree). D(v1)/D in [2/3, 3/2] on >= 60% of resolved E-ARC cells (DEV suggests v1 underpredicts D at
  mid depth: a miss is expected and will be reported).
- P4 (stationary degree-1 dominance). s_1 >= 0.85 on >= 90% of resolved E-ST cells.
- P5 (frozen-at-mean overstatement). Variance of the frozen part J^m (x - m) over V in [D/2, 2D] on >= 75% of resolved
  E-ARC cells with D >= 2, and >= 1.5 on all of them.
- P6 (generic capture). |PCA-basis residual/V - generic prediction (v1 s_d)| <= 0.10 at k = 1, 4, 16 on >= 75% of
  resolved E-ARC cells with l >= 4 and E-ST cells.
- P7 (N, vector output). v1 rule 4c within a factor 2 of the measured interval (N_lo, N] (or within 2 of N) on >= 70%
  of resolved E-ARC + E-ST cells, separately eps = 0.1 and 0.01; eps = 0.001 reported.
- P8 (N, scalar readout). Same with rule 4d.
- P9 (structure).
  (a) E-ARC: N_vec(l, 0.01) >= 64 at every l <= 8 on all four nets (theory 4c + DEV).
  (b) E-ARC: N_vec(l, 0.01) >= 16 at every layer on >= 3 of 4 nets (DEV).
  (c) E-ARC: N_sc(31, 0.01) <= 4 on >= 3 of 4 nets (theory 4d + DEV).
  (d) E-ND: the true-law projection residual of the radial direction is <= 0.01 V at every l >= 16 on >= 5 of 6 nets
      (theory section 5: synchronisation, N = 1 under the true law).
  (e) E-ST: N_vec(0.1) <= 2 at t = 16 and 32 for n in {64, 128, 256} on >= 75% of resolved (net, t) cells (DEV).
- P10 (Gaussian convention). (a) E-ST: V_true/V_gauss in [0.8, 1.25] at t <= 8 for n >= 64 on >= 75% of cells.
  (b) E-ND: |V_gauss/V_true - 1| > 0.2 at some l >= 32 on >= 4 of 6 nets.
- P11 (stationary memory). (a) V_true(t) does not increase by more than 3 SE between consecutive t (fraction of steps
  reported, >= 90% expected). (b) The log-linear decay rate of V_true over resolved t in [n/4, n], median over nets, is
  within a factor 1.6 of 5/n for each n in {64, 128, 256} (theory 3b).

### Outputs
results/part1_scores.json (scores and per-cell records), results/part1_tables.md (accounting tables per layer: shares
by degree and by channel, measured and predicted N at eps = 0.1, 0.01, 0.001). Every miss is reported with its cells.

## Part 2 (gate counts, the mean-relevant count N_>=2, the gram-chain stationary prediction, synchronisation depth)

Registered after Part 1 runs had started (seen before this registration: E-ND all six nets; E-ST n = 32 all four nets
and n = 64 seed 1000; E-ARC seed 4000 layer 0; dev gate counts on dev net 9103 at 64 x 16). Not yet produced: E-ST
n = 128 and 256, E-ARC except seed 4000 layer 0, every Part 2 measurement on evaluation nets. Runner
scratch/eval_part2.py, library lib/gates.py (hashed with this part). Scorer: written before the Part 2 runs finish,
hashed separately.

### Measurements
- G(l, eps) (main's request, 21:40Z): the smallest number of future gates, switched in decreasing order of first-order
  importance I = |u|^2 s^2 psi(tau) (all other gates frozen at the mean point's pattern, same future noise), with
  V_{>=2}(g - g_G) <= eps V_l (Gaussian convention); also with margin order (tau ascending). G^(1)(eps): the count at
  which the sorted importances leave a tail <= eps of their total (the first-order, no-interaction prediction).
  Grid: 0, then 40 geometric values to n t (all future gates). Cells: E-ARC seeds 4000-4003 at l = 8, 16, 24, 31;
  E-ST seeds 1000-1001 at n = 64, 128 with t = 4, 16. P = 2048.
- N_>=2(l, eps): residual of the degree >= 2 part, r_tot(P_k) - (V_1 - captured_1(P_k)), along the active subspace of
  the nonlinear part g - B~ Z; resolved only where residual + 2 SE <= eps V (eps = 0.01 is expected to be SE-limited).
- N_1 unbiased (split sample).
- Synchronisation (input regime, sigma = 0, L >> n): nets st.W_layer seeds 300, 301 at n = 16 (L = 256) and n = 32
  (L = 512); per layer l on the grid {1, 2, 4} and n/2 .. L step n/4: the true-law projection residual of the radial
  direction (relative to V_true), the cosine between independent cloud points, the gate Hamming distance at layer l+1.

### Predictions
- PG1 (many gates). G(l, 0.01) >= n at every E-ARC layer with t >= 8 (l <= 24) on >= 3 of 4 nets, and
  G(l, 0.01) >= 0.25 n t at l <= 16 on >= 3 of 4 nets (theory: about n T theta_l / sqrt(pi) gates per future layer lie
  within T cloud spreads of their boundary, theta_l ~ 3 pi/(l + 6); DEV 64 x 16: 648 of 768 at t = 12).
- PG2 (first order). G^(1)(0.1) within a factor 2 of G(l, 0.1) on >= 70% of cells (both orders reported).
- PG3 (gates per direction). G(l, 0.1) >= 3 N(l, 0.1) on >= 75% of E-ARC cells (the gates' normals overlap: many
  gates, fewer directions).
- PS1 (gram-chain's stationary prediction, main 21:45Z: the direction stops mattering after ~2 n^{1/3} layers, the
  radius after ~n, so N -> 1 once t >> 2 n^{1/3} ln(1/eps)). Tested on E-ST cells with t >= t_x(eps) = 2 n^{1/3}
  ln(1/eps) and M >= 0.02:
  (a) one direction suffices: residual(top-1 AS) <= eps V, eps = 0.1 and 0.01, on >= 75% of such cells;
  (b) the radius suffices: residual of the radial feature e.X alone <= eps V on >= 75% of such cells.
  My expectation (DEV and Part 1 at n <= 64 already seen, so for n <= 64 this is post hoc; n = 128, 256 prospective):
  (a) holds at eps = 0.1 and fails at eps = 0.01; (b) fails at both (the top direction is the future's slowest mode,
  overlap with e about 0.6-0.95, not the radius itself).
- PS2 (synchronisation depth). The true-law radial residual at l >= 4n is <= 0.05 on all four sync nets, and between
  l = 4n and the first l where it is <= 1e-3 its log decays at a rate within a factor 2 of 2/n per layer (Lyapunov gap,
  after the kernel contraction has brought the angle to ~pi/n near l ~ 3n).

## Part 3 (prospective test of theory v2)

Registered before any prospective cell exists. Theory v2 frozen 21:48:41Z (FORMAL.md v2 sections, lib/theory_v2.py,
sha c57c8427 and a5021b99 in logs/freeze_times.txt). Prospective cells: E-ARC seeds 4002, 4003 (all seven layers);
E-ST n = 128 (seeds 1000-1003) and n = 256 (seeds 1000-1001), every resolved t. Same measurements as Part 1 (same runner
and analysis code; the extra stored field cloud_evals_perp supplies the angular spectrum). Scorer: scratch/score_part3.py,
hashed before its first run on prospective cells.
- Q1 (variance budget, ARC). Predicted V/E|a|^2 (v2.2 with the measured c_0 and radial variance) within 20% of the
  measured value on >= 12 of 14 prospective ARC cells.
- Q2 (linear share). |s_1 - s_1(v2)| <= 0.08 on >= 11 of 14 prospective ARC cells; <= 0.12 on >= 75% of resolved
  prospective E-ST cells.
- Q3 (mean degree, ARC). D(v2 identity)/D in [0.75, 1.33] on >= 11 of 14 prospective ARC cells.
- Q4 (N, ARC, v2.7 rule). Within a factor 2 of the measured grid interval (or within 2) on >= 11 of 14 cells at each of
  eps = 0.1 and 0.01; and the debiased first-chaos lower bound is <= the measured count on every cell (a consistency
  check of the bracket).
- Q5 (N, stationary n >= 128, v2.7 rule). Within a factor 2 on >= 60% of resolved prospective cells at eps = 0.1
  (eps = 0.01 reported; expected to be SE-limited at small memory share).
- Q6 (one direction beyond t_1, v2.8). On resolved prospective E-ST cells with t >= t_1(0.1) = ln(9)/Delta,
  Delta = 0.672 Q^{-1/3} + 1/Q - 5/n with Q the cell's measured mean radius: the residual after the best single
  direction (active-subspace basis) is <= 0.1 V on >= 75% of them; the radial feature alone is not (residual > 0.1 V on
  >= 50% of them).
- Q7 (slow-mode memory, reported as a measurement). The late decay rate of V_true over resolved t in [n/8, n] for
  n = 128, 256, compared with 5/n (v1) and 5/(2n) + 1/Q (astra round 1); no band (v2 has no committed value).

## Amendment 2A (estimator and scorer corrections from gpt-6-astra's round-2 audit; before any Part 2 output)

Registered before any runs/p2_* file exists. Changes (lib/gates.py, scratch/score_part2.py; hashes below):
1. Gate counts, sigma > 0: the first-chaos subtraction now uses a cross-realisation U-statistic (each realisation
   centred by its own mean, centring factor divided out) instead of averaging the two realisations first, which biased
   the nonlinear residual downward even as P grows (audit T2). sigma = 0 is unaffected in expectation.
2. Gate spreads, margins and importances are computed on independent training inputs, not on the evaluation inputs.
3. Every gate-curve and N_>=2 entry stores a jackknife SE; G(l, eps) and N_>=2(l, eps) use "residual + 2 SE <= eps V"
   (the registered rule, which the first scorer did not apply). They are tested counts on the grid, not brackets.
4. N_>=2: the degree-1 complement |B~(I - P_k)|^2 is estimated directly on the holdout sample (exactly 0 at k = n).
5. Scorer: PG1 uses only nets with all four registered layers present; PG2 keeps G = 0 cells (within 2 counts as
   agreement) and reports their number; PS1 reports seen (n <= 64) and prospective (n >= 128) cells separately; PS2 fits
   from l = 4n up to the first crossing below 1e-3 and reports "unresolved" when fewer than two points remain.
Not changed: the registered importance formula |u|^2 s^2 psi(tau) (an uncentred hinge second moment, as written in
Part 2); the grid; the cells; the predictions and bands.
