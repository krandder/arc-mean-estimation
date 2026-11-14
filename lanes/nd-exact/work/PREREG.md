# nd-exact pre-registration (Part 1)

Lane nd-exact (target M1), work directory `work/nd-exact/`, bead pool-yode25 under Kelvin's ask pool-e0w4ba. Part 1 is
hashed in `prereg_hashes.txt` before any estimator is run on an evaluation net. Code is frozen by sha256 in the same
file. Deviations go to `logs/deviations.txt` with evidence.

## What was done before registration (development; not scored)
- Region census on the six evaluation nets (descriptive, step 2 of the brief): `scratch/census.py`, `runs/census_s*_n22.json`,
  `results/census_table.md`.
- Reference truths for the six evaluation nets and dev nets 103, 111 (`scratch/truth.py`, `runs/truth_s*.json`).
- Development of the deterministic code on dev nets 103, 111 (`lib/cubesphere.py`, `lib/cs2.py`, `runs/dev_*`), the
  depth-1 rate study (`scratch/depth1_rate.py`, descriptive), and the oracle region code on dev net 103.

## Nets, estimand, truth
- Plain ReLU nets, width 8, depth 256, sigma = 0: `ndx.make_weights(seed)` = `nd.make_weights('plain', seed, 8, 256)`;
  x ~ N(0, I_8); a = h_256. Evaluation seeds 203, 216, 217, 220, 221, 223 (the healthy seeds used by the relevance and
  narrow-deep-m1 lanes).
- nMSE(est) = |est - truth|^2 / tr Var(a).
- Truth (`scratch/truth.py`, c = 64): E[a] = J_64 E[h_64], E[h_64] = E|x| x mean of f_64(x/|x|) over 16 replicates of
  2^22 scrambled-Sobol points; J_64 = Jacobian of layers 65..256 on the downstream class of the replicate mean's
  direction. Checked against plain full-depth MC (2^21 inputs), which also counts inputs outside J_64's class.
  Truth standard error about 1e-9 in nMSE; nMSE values below 1e-8 are reported but not used in any test.

## Cost model
1 mv = 128 FLOPs (an 8 x 8 matrix-vector product with ReLU; flopscope conventions of `work/narrow-deep/lib/nd.py`:
matmul M N (2K - 1), elementwise 1, normal cdf and inverse normal 96, pdf 54, normal draw 16). Every operation is
charged, including setup (tail Jacobians, tail-cone certificates, pilots). Wall-clock is reported but not scored.

## Methods
- MC: full depth, 256 + 1 mv per path; nMSE = 1/N exactly (not simulated).
- RQMC: scrambled Sobol on the 8 inputs (inverse normal), full depth, 256 + 6 mv per point.
- RQMCJ (sampling with the same structure the deterministic code uses): J_48 E|x| mean f_48(x/|x|) over scrambled Sobol
  points, 48 + 7 mv per point, setup (256 - 48) x 8 mv; c = 48 is the smallest cut at which every evaluation net had a
  single live downstream class in the census.
- RADQ (the relevance lane's estimator, setup now charged): g(u*) E|h_32| with scrambled Sobol inputs.
- CS2 (the deterministic code, `lib/cs2.py`), in the framing main relayed from Kelvin (04:10Z):
  - Exact limit: a class is a cell of inputs (a cone over a dyadic box on a face of the cube, exact Gaussian mass and
    conditional mean by a one-dimensional integral); it contributes its mass times the net at its conditional mean,
    which is exact whenever the gates are constant on the cell, and every cell becomes exact as cells shrink.
  - Skips: on a cell whose gates are certified constant (exact interval arithmetic, layer by layer), the layer maps are
    composed exactly (factored once fewer than 8 units are active).
  - Compression: at layer c0 = 32 all certified cells whose image lies in the tail cone K are merged into one class,
    pushed to the output by one exact linear map J (K is a box cone around the synchronised direction on which the
    gates of layers 33..256 are certified constant; setup charged).
  - Refinement: the open cell with the largest surplus (half the change its last split made to the estimate, floored at
    1% of the cell's own contribution) is split first, along the coordinate in which the straddling gates vary most.
  Fixed configuration (chosen on dev nets 103, 111 at 2^22 mv; `runs/dev_cs2_*`): c0 = 32, Q = 32 Gauss-Legendre
  nodes on [0, 9], rule = surplus, floor = 0.01, max tree depth 60. Of the three refinement rules tried (surplus;
  a priori forward-propagated distortion; their maximum) surplus had the lowest nMSE on both dev nets. No random
  numbers; the output is a deterministic function of the net.
- ORACLE (bound, not a method): the top-R regions of layers 1..32 by contribution, each integrated exactly, the rest
  dropped (`scratch/region_code.py`, 2^22 inputs). Charged 9 mv per region (8 mv for its linear map, 1 for its moments),
  a lower bound for any region-by-region exact method; the measured per-region cost of real exact moments is far higher.
- Budgets: 2^12, 2^14, ..., 2^26 mv for the samplers (replicates: 40 up to 2^18, 16 up to 2^22, 8 above); CS2 anytime
  curve at every power of 2 from 2^12 to 2^24 mv (2^25, 2^26 if a net's run finishes within 45 minutes).

## Tests (scored by `scratch/score.py`, frozen with this file)
Equal-cost comparisons interpolate the comparator's nMSE log-log in cost between its measured budgets.
- T1 (the success criterion, M1-type): CS2's nMSE is at most one third of RQMC's at equal cost at some CS2 checkpoint in
  [2^16, 2^24] mv, on at least 4 of the 6 nets. PREDICTION: fails (0 of 6 nets).
- T2: the same against RQMCJ. PREDICTION: fails (0 of 6).
- T3 (slope): CS2's bits per halving of error, b = 2 x d(log2 cost) / d(-log2 nMSE), from a least-squares fit over its
  checkpoints in [2^18, 2^24] mv, exceeds 2 (sampling's value for MC) on at least 4 of 6 nets. PREDICTION: holds.
- T4 (oracle bound): at every R with ORACLE nMSE at least 10 times its MC noise floor, ORACLE's nMSE exceeds RQMCJ's
  nMSE at cost 9 R mv, on at least 5 of the 6 nets. PREDICTION: holds.
A failure of T1 and T2 is the registered negative result; T3 and T4 say why.

## Descriptive (no test)
- The error of the mean against the number of classes (cells) and its slope, for CS2 on the six nets (from the same
  runs).
- One ReLU layer at widths 2, 3, 4, 6, 8 (exact truth |w_j|/sqrt(2 pi)): CS2 (c0 = L = 1) against RQMC, to show how
  the deterministic code's rate depends on the number of angular dimensions (`scratch/depth1_rate2.py`).

## Amendment 1 (registered before any of its runs on an evaluation net; see prereg_hashes.txt)
Motivation, from development only: (i) the registered refinement rule can leave an open cell unrefined forever when its
centroid's output is zero while part of the cell is live (seen on one ReLU layer at width 2: certified mass stuck at
0.75); (ii) main relayed Kelvin's optional unbiased version (an MC correction of the within-class residual).
- CS2b: CS2 with rule surplus_m: priority = max(surplus, 1% of the cell's own contribution, 1% of the cell's mass times
  the current total estimate's norm), so every open cell with mass is eventually split. Everything else as CS2.
  Runs to 2^26 mv on the six nets (`frozen/run_cs2.py SEED 32 26 surplus_m 0.01 32`).
- UNB (`frozen/run_unbiased.py`): D = CS2 (registered config) after 2^20 mv; correction (1/M) sum (f(x) - q(x)) over
  scrambled-Sobol inputs (and plain MC, reported), q = f at the centroid of x's open cell, 0 residual on certified
  cells; M = 2^12, 2^14, 2^16; R = 8 replicates. Cost = D + M x (inputs, lookup, 32 layers, tail).
- Tests (scored by `frozen/score_a1.py`):
  - T1b, T2b, T3b: T1, T2, T3 with CS2b in place of CS2. PREDICTION: T1b, T2b fail; T3b holds.
  - T5: UNB's nMSE is at most one third of RQMCJ's at equal cost at some M, on at least 4 of 6 nets. PREDICTION:
    fails (on the dev nets UNB was 7-14 times worse than RQMCJ: the cells leave 36-73% of the variance).
  - T6: the same against RQMC. PREDICTION: fails.
- Descriptive: the one-layer width study rerun with CS2b (`frozen/depth1_rate3.py`).
