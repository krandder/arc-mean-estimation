# Bits-bounds lane: pre-registration of the measured parts (E1, E2, E3)

Written 21:25-21:32Z on 1 November 2026, before any evaluation run. Dev runs used seeds 9001-9003 only (logs/dev_explore.log,
runs_dev/); evaluation seeds are 100-107 and have not been run. Code: scratch/run_eval.py (as hashed with this file),
lib/bb.py, lib/chain3.py, lib/meanfield.py; tests: tests/test_bb.py (all pass, logs/test_bb.log).

## Nets and configurations
He-ReLU, no bias, W_l iid N(0, 2/n), weights from bb.make_weights(seed, n, L). Unit input directions U (the radius is
exact by homogeneity); output A(U) = h_L(U); V_ang = tr Var_U A per net (on the test split). Configurations
(n, L) and seeds:
- L = n: (32, 32), (64, 64), (128, 128) seeds 100-107; (256, 256) seeds 100-103.
- L = n/2: (64, 32), (128, 64) seeds 100-107; (256, 128) seeds 100-103.
- ARC: (256, 32) seeds 100-107.
- L = 4n: (32, 128) seeds 100-107.
Dead nets (V_ang = 0) are recorded and excluded. Each net: 2048 fit directions and 2048 test directions.

## Measurements (per net)
E1, at layers l in {L/4, L/2, 3L/4, 7L/8} (integer division, l >= 1):
- cloud: angular spectrum (participation ratio PR, log-slope of eigenvalues k = 1..10), median pairwise angle;
- mean-propagation error |E A - g_l(m_l)|^2 / V_ang, m_l the 4096-point cloud mean;
- forward-only references: spherical k-means on the fit split's directions at l, M in {1, 4, 16, 64, 256}; the
  reference state of a cell is its fit member closest to the centre; test points assigned to the nearest centre;
  merges frozen (J_l(c) h), radial ((|h|/|c|) g_l(c)), best (per cell, chosen on the fit split), rule (frozen iff
  L' x the cell's RMS angular spread < 2, past-measurable); residual D = mean |A - G|^2 / V_ang (test) and bias
  |mean(A - G)|^2 / V_ang;
- two-sided references: k-means on trajectory signatures (directions at l, l + L'/2, L), M in {4, 16, 64}; merges F,
  R, best.
E2, at the same layers: 16 reference directions, 7 input angles delta in {1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1}, 16
perturbations each: layer-l angle phi, r_F = |g(h) - J(c) h|^2/|g(h)|^2, r_R = |g(h) - (|h|/|c|) g(c)|^2/|g(h)|^2,
number of future gate disagreements. The exact annealed three-replica chain (lib/chain3.py, 4000 chains) at the same
(n, L', phi) for each qualifying phi bin.
E3, at prefix depths r in {L/8, L/4, L/2}: two-level samplers, level 1 = merge G (cost r/L per sample), level 2 = A - G
(cost 1, plus (L - r)/L per sample in frozen cells); variants: one random reference direction with the radial merge
(the unrestricted lane's sampler), forward-only k-means references M in {1, 16, 64, 256} with the radial merge and with
the rule merge. Ideal ratio = (sqrt(V1 C1) + sqrt(V2 C2))^2 / V_ang (below 1 = gain over radius-exact MC); setup
recorded separately (one future pass and one frozen application per reference, plus the fit-split prefixes).

## Predictions (registered; each with its scoring rule)
P1 (cubic exponent). For each (net, l) with L' >= 8, bin pairs by phi (bins = the delta levels); over bins with
L' phi_median <= 0.3 and >= 20 pairs (at least 3 bins), the log-log slope of the MEAN r_F against phi_median lies in
[2.4, 3.6] on >= 80% of qualifying (net, l) cells.
P2 (coefficient against the exact chain). On the same cells, the ratio of the nets' pooled mean r_F/(L' phi^3) to the
chain's annealed mean at the same (n, L', phi) lies in [1/3, 3] on >= 75% of cells.
P3 (crossover). Median r_F < median r_R in the bins with L' phi <= 0.5, and median r_F > median r_R in the bins with
L' phi >= 5, on >= 80% of the cells where such bins exist.
P4 (rough versus smooth, one reference). D_F(1) > D_R(1) at l = L/4 on >= 90% of nets; D_F(16) < D_R(16) at l = 7L/8 on
>= 80% of nets (all configurations pooled).
P5 (decay with M). The slope gamma of log D_best(M) against log M over M = 4..256 (forward-only) lies in [0.05, 0.4] at
l = L/4 and L/2 and in [0.3, 1.2] at l = 7L/8, on >= 75% of nets per configuration.
P6 (two-sided against forward-only). At M = 64: D_best(two-sided) / D_best(forward-only) <= 0.8 on >= 60% of (net, l)
cells.
P7 (bias far below the RMS residual). For M >= 16, on the (net, l, M) cells where the bias is resolved (bias >
3 D_best / 2048), bias_best <= D_best / 10 on >= 80% of them.
P8 (mean propagation). The mean-propagation error decreases from l = L/4 to l = 7L/8 on >= 80% of nets, and is <= 0.05 at
l = 7L/8 on >= 75% of nets.
P9 (estimators). (a) The random-reference two-level sampler's best ideal ratio over r lies in [0.5, 1.2] on >= 75% of
nets with L <= n. (b) The best multi-reference ideal ratio (over r, M in {16, 64, 256}, radial or rule) is below the
random-reference one on >= 70% of nets, and their ratio (multi / random-reference) is >= 0.6 (gain at most 1.7x) on
>= 80% of nets. (c) The median over nets of that gain does not grow by more than 1.5x from n = 64 to n = 256 at L = n.
P10 (cloud spectrum). The eigenvalue log-slope over k = 1..10 lies in [-0.7, -0.15] on >= 90% of (net, l), and PR
decreases from l = L/4 to l = 7L/8 on >= 80% of nets.
P11 (bits that matter, cell count). N_cell(l, eps) = log2 of the least M on the grid with D_best(M) <= eps^2 (forward
only; "> 8" if none). At L = n: N_cell(L/2, eps^2 = 0.01) > 8 on >= 75% of nets, and N_cell(7L/8, 0.01) <= 6 on >= 75%
of nets.

## Analysis rules
- Scored by scratch/score_prereg.py (to be written before reading the evaluation results, and hashed separately).
- Post-hoc analyses are labelled as such in the report.
- Compute: CPU only, nice -n 19, ionice -c3, single-threaded BLAS, at most 2 processes at a time.

## Amendment 1 (F1; written 21:45Z on 1 November, before any F1 evaluation run)
Disclosure: E1-E3 evaluation results for every configuration except 256 x 256 had been seen (results/tables.md,
results/posthoc.md); the F1 dev check used seed 9004 only.
Purpose: compare full multilevel samplers, not only two-level ones (the brief's "best multilevel sampler").
Runs: scratch/run_ml.py on the same nets as E1-E3 (seeds 100-107; 100-103 at n = 256) for (32, 32), (64, 64),
(128, 128), (256, 256) [L = n], (32, 128), (64, 256) [L = 4n], (256, 32) [ARC].
Samplers: dyadic levels r = L/2, L/4, ... (at most 7), radial merges; "rand" = one random reference trajectory shared by
all levels (the unrestricted lane's sampler); "trajM" (M = 4, 16, 64, 256) = M reference trajectories chosen by k-means
at the deepest level, shared by all levels, each sample merged at each level with its nearest reference state. For each
sampler: the best subset of levels (optimistic: chosen on the test split) and the full dyadic set.
Predictions (medians over nets per configuration unless stated):
A1. rand, best subset: ideal gain over radius-exact MC (1/ratio) in [1.1, 3] at L = n for every n, in [1.5, 8] at
    L = 4n, and in [0.8, 1.3] at 256 x 32.
A2. The rand gain at L = n grows from n = 32 to n = 256 by a factor in [1.0, 2.0] (flat allowed).
A3. trajM does not beat rand: best-subset ratio(trajM)/ratio(rand) >= 0.8 for every M on >= 75% of nets, and the full
    dyadic trajM is worse than the full dyadic rand for every M on >= 75% of nets.
Scoring: scratch/score_ml.py (written before the F1 runs and hashed with this amendment).

## Amendment 2 (C3, rough-gain variogram; written 22:02-22:04Z on 1 November, before any run of scratch/run_gain.py)
Purpose: test astra's round-2 rough-regime law on nets: Var(Delta) ~ (6 pi/n) phi x/(1 + x), x = L' phi/(3 pi), Delta
= log(|g_l(h)|/|h|) - log(|g_l(c)|/|c|) for pairs (h, c) at layer-l angle phi (proved only in the iterated
large-width, small-angle limit; the extension to L' ~ n is not proved).
Runs: scratch/run_gain.py on (64, 64), (128, 128), (256, 256) with seeds 100-103, layers L/4 and L/2; 32 references,
input angles delta in {0.01, 0.03, 0.1, 0.3, 1}, 16 perturbations each.
Prediction G1: in the bins with L' phi_median >= 3 (rough regime), the ratio (second moment of Delta)/(prediction) has a
median over (net, layer, bin) cells in [1/3, 3] for each width, and the median ratio changes by less than 2x from
n = 64 to n = 256. Scored by scratch/score_gain.py (written with this amendment).

## Amendment 3 (C4 cheapest test, the exact single-Gaussian recursion; written 22:18-22:20Z on 1 November, before any
## evaluation run of scratch/run_closure.py; dev checks on seed 9005 only: nMSE 0.018 at 32 x 32, 0.004 at 64 x 32)
Purpose: the cleanest averaging method, lib/closure.py (exact Gaussian ReLU moments, moment matching every layer,
tests/test_closure.py passes), against the truth along L = alpha n, with the closure's squared error estimated without
sampler noise by (a - mu1).(a - mu2) from two independent Monte Carlo estimates (2^16 inputs each for n <= 64, 2^15 at
n = 128).
Runs: scratch/run_closure.py on (16, 8), (32, 16), (64, 32), (128, 64) [alpha = 1/2] and (16, 16), (32, 32), (64, 64),
(128, 128) [alpha = 1], seeds 100-107.
Predictions:
B1. At each alpha the median closure nMSE falls with n with log-log slope in [-1.0, 0.0] (no faster than 1/n).
B2. The gain over MC at the closure's matrix-product cost (2n passes, generous to the closure: (1/2n)/nMSE) has median
    <= 10 at every (n, alpha), and the median gain at n = 128 is at most 2x the median gain at n = 16 for each alpha.
Scored by scratch/score_closure.py (written with this amendment).

## Amendment 4 (the closure at larger width; written 22:27-22:29Z on 1 November, AFTER Amendment 3's results were seen:
## at alpha = 1 the closure's gain at its matrix-product cost rose 0.38, 0.28, 0.63, 3.26 for n = 16-128)
Purpose: decide between H_peak (the exact single-Gaussian recursion is a constant-factor method at L = alpha n: its gain
over MC at its own cost peaks, as ARC's K = 2 did along alpha = 1/2 in the hardness lane) and H_grow (its gain keeps
growing with width at L = n, which would make it a candidate counterexample to C4 for averaging methods).
Runs: scratch/run_closure.py on (192, 192) and (256, 256) [alpha = 1], (256, 128) [alpha = 1/2], seeds 100-103.
Predictions (my expectation is H_peak, about 60%):
B3. The median gain at (256, 256) is at most the median gain at (128, 128) (3.26).
B4. The median gain at (256, 128) is at most 2x the median gain at (128, 64) (0.89).
Scoring: by hand from runs/closure_*.json with the same gain definition as scratch/score_closure.py.

## Amendment 5 (the variance profile and the bits at layer l on new configurations; written 23:12-23:17Z on
## 1 November, before any evaluation run of scratch/run_bits5.py)
Disclosure: all E1-E3, F1, G1 and closure results above have been seen. The bands below were calibrated POST HOC on
the registered E1 data (scratch/score_bits5.py --old, results/bits5_posthoc_old.json) and on dev seed 9006 only
(runs5_dev/, 64 x 64 and 192 x 192). The variance profile itself is the input-bits lane's (outbox/input-bits-2026-10-31.md,
section 2.2: C_L = (1/4) sum_j [5 - B(c_j)]); what is tested here is that profile together with my cloud dimension and
merge exponent as a formula for the bits at layer l.
Purpose: a prediction of the bits that matter at layer l from three factors: the cloud's dimension (PR_l, ~n/l), the
share of the output variance that the future still makes from the layer-l direction (mean field), and the decay of
the merge residual with the number of cells (exponent ~0.72/PR_l in the rough regime).
Runs: scratch/run_bits5.py on new configurations (192, 192), (128, 256) seeds 100-103 and (384, 96), (512, 64)
seeds 100-101 (lib/bb.py with the post-review k-means fix; E1 as in run_eval.py, forward-only references only, cuts
L/8, L/4, L/2, 3L/4).
Predictions (mean-field formulas as in scratch/score_bits5.py; cells pooled over the new configurations):
Q1. The per-net log-radius variance Var_u log|h_l(u)| at l = L/8, L/4, L/2, L lies within [0.5, 1.5] times the
    mean-field (1/2) sum_{j<l} (3 - 2 k2(c_j))/n on >= 75% of (net, l) cells.
Q2. V_ang/E|A|^2 lies within [2/3, 1.5] times the mean-field 1 - c_L exp(-S_0/2) on >= 75% of nets, and every new
    configuration's median ratio lies in [0.8, 1.25].
Q3. The one-reference radial residual D_R(1) at each cut, divided by its future-half prediction (measured M = 1 spread
    and measured V_ang/E|A|^2), has a configuration median in [1/3, 3] for every new configuration.
Q4. In the rough cells (theta_median L'/2 > 2), the median of gamma_R x PR is in [0.45, 1.1] (gamma_R = minus the
    log-log slope of D_R(M) over M = 4..256; post hoc on the old data: 0.72).
Q5. Zero-input prediction in the rough cells: D_R(256) within a factor 3 of D_R^MF(1) x 256^{-0.72/(1.04 n/l + 1.38)}
    (full mean field) on >= 60% of cells (post hoc on the old data: 73%).
Q6. The bits formula in the rough cells: N_l(eps) = (PR_l/0.72) log2(D_R(1)/eps^2) agrees with the measured bits
    (log2 of the least M on the grid with D_R(M) <= eps^2, interpolated; "> 8" if none) for eps^2 in {0.1, 0.03, 0.01}
    on >= 70% of (cell, eps) pairs, agreement meaning both above 8 bits, or the prediction at most 10 bits and within
    2 bits of a measured value (post hoc on the old data: 88%).
Scoring: scratch/score_bits5.py (hashed with this amendment), output results/bits5_scores.json.
