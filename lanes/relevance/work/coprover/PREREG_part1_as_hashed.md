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
