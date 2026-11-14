# preint PREREG (Part 1), written 14:15-14:30Z, 2 November 2026, before any scored run

Lane preint (bead pool-ttdzrk.17). Question: does exact pre-integration (line + radius, lib/line.py) followed by RQMC
give an MSE-vs-compute exponent above RQMC's, and does any gain hold as width grows? Development used only dev nets
(arc stream seeds 1 and 9500, narrow-deep 103 and 111 were reserved; 111 unused); scored nets below were not run by
any estimator of this lane before this file was hashed (the pieces counts of results/pieces.md used nets 200, 300,
301, 203, 216, 221 for vertex counting only; P1 below is therefore scored only on nets not in that set).

## Estimators (lib/est.py, scratch/curves.py; code frozen in frozen/ with sha256 in prereg_hashes.txt)
- RQMC: scrambled Sobol (scipy LMS + digital shift), inverse normal, f(x). RQMCRB: the same mapped to the sphere,
  E chi_d f(xhat). RQMCJ (8 x 256 only): RQMCRB through layers 1..48 then nd-exact's tail map J_48 along u*, u* from 64
  separate charged pilot points. MLMC_r: two-level shared-trajectory sampler (unrestricted lib/mlmc.py), levels [0, r],
  256-direction pilot charged.
- PI_as / PI_rand: line + radius integral (F1, exact algorithm F2) on 2^p lines, bases from scrambled Sobol in d - 1
  dims; u = top eigenvector of a 64-point pilot estimate of E[J^T J] (charged: 2 x 64 passes + SVD) or uniform random;
  suffix _w: window mode eps = 1e-8 (exact on the window, one-pass unbiased tail estimate). PIJ_* (8 x 256): lines
  through layers 1..48 then J_48 (same setup as RQMCJ, charged).
- Costs: counted FLOPs / (2 n^2 L) (all matvecs, sign tests, interpolations, cdf evaluations, inverse normals,
  pilots, bases); MC would be 1 pass per point plus draws.
- Score: nMSE by replicate variance (sum over outputs of the across-replicate variance / tr Var f); all estimators are
  unbiased (RQMCJ and PIJ under nd-exact's tail premise), and every run also reports the error against the truth and
  a bias ratio |mean - truth|^2 / (replicate variance / R) (validity flag if > 16, i.e. |z| > 4).

## Scored runs
S1 small nets (asymptotic check): arc stream, (n, L) = (4, 2), (6, 3), (8, 4); seeds: the first three of 11, 12,
   13, ... whose 2^16-path tr Var f is positive (dead nets skipped and listed). RQMC, RQMCRB: 2^6..2^18 points;
   PI_rand, PI_as: 2^2..2^14 lines (n = 8: 2^2..2^13). R = 16. tr Var from 2^16 MC paths (no truth).
S2 narrow-deep 8 x 256, seeds 203, 216, 217, 220, 221, 223: RQMC, RQMCRB, RQMCJ: 2^6..2^16 points; PIJ_as, PIJ_rand:
   2^2..2^11 lines; MLMC_32: 2^8..2^16 passes. R = 8. Truth: nd-exact runs/truth_s*.json.
S3 ladder (32, 4), (64, 8), (128, 16), seeds 302, 303, 304 (arc-update truths, 2^24 paths) and ARC 256 x 32 nets
   201, 202, 203, 204 (arc-noisy truths, 2^26 paths; net 200 was used for vertex counts): RQMC, RQMCRB: 2^6..2^14
   points; PI_as_w, PI_rand_w: 2^2..2^11 lines (n = 32), 2^2..2^9 (64), 2^2..2^8 (128), 2^1..2^7 (256); MLMC_{L/2}:
   2^8..2^14 passes. R = 8.
Order: S2 and S1 first (cheap), then S3 by width. CPU only, at most two processes at nice 19, ionice idle.

## Fit protocol (scratch/fit.py, frozen)
Exponent alpha = minus the least-squares slope of log nMSE (replicate variance) on log cost over the top 60% of a
curve's budgets (at least 4 points). Equal-cost comparison: log-log interpolation of each curve at the RQMC (or
RQMCJ) curve's cost points inside the other curve's cost range. "PI best" = the better of PI_as and PI_rand at that
comparison (by exponent for exponent tests, by nMSE for equal-cost tests).

## Predictions (my expectations, with pass rules)
P1 (cost law, F3). Final window vertices per line (mean over lines) within [0.6, 1.5] x (3 + n L (2 psi0 / pi)) on
   every S3 net whose vertex count was not used before (ladder 302-304, ARC 201-204: 13 nets). Expect: holds 13 of 13.
P2 (value of a line, F6). Line variance ratio (window, random u) >= 0.8 at n >= 64 on all 10 such S3 nets; with the
   active-subspace u >= 0.6. Expect: holds.
P3a (equal cost, wide). On every S3 net, PI best is at least 10x worse than RQMC at every common cost.
   Expect: holds on all 13.
P3b (exponent, n >= 128). PI best's alpha <= RQMC's alpha + 0.15 on at least 5 of the 7 nets with n >= 128.
   Expect: holds (F7: N << dim of degree-4 harmonics there).
P3c (exponent, n = 32 and 64; dev showed PI steeper at 32). PI_as's alpha > RQMC's alpha + 0.1 on at least 2 of 3
   nets at n = 32, and on at most 1 of 3 at n = 64. Expect: holds (uncertain at 64).
P4 (small nets, F5). PI_as's alpha > RQMCRB's alpha + 0.1 on at least 6 of the 9 S1 nets. Expect: holds.
   Descriptive: the fitted alphas against F5's asymptotic values (RQMCRB 1 + 3/(d-1), PI 1 + 4/(d-2)).
P5a (narrow-deep, equal cost). On at least 5 of 6 nets, PIJ best is worse than RQMCJ at every common cost.
   Expect: holds.
P5b (narrow-deep, exponent). |alpha(PIJ best) - alpha(RQMCJ)| < 0.3 on at least 4 of 6. Expect: holds (pre-asymptotic:
   10^5 regions; uncertain).
P6 (F7 consistency). RQMC's N x nMSE >= the NNGP-proxy bound of results/kernel_bound.json at every scored N on every
   ladder and ARC net (interpolating the bound in log2 N). Expect: holds (a weight-averaged bound with a proxy kernel,
   so a failure on one net would not refute the theorem but would show the proxy is too high).
P7 (RQMC plateau, A4). RQMC's local exponent over its last three budgets (2^12..2^14) is <= 1.3 on at least 10 of
   the 13 S3 nets. Expect: holds.
P8 (multilevel). MLMC alpha in [0.8, 1.2] on every net where it runs (S2, S3). Expect: holds.
Validity: bias flags (|z| > 4) are reported; a method with flags on more than 10% of its (net, budget) cells is
reported as suspect.

## What would change the conclusion
- If P3b fails (PI steeper by > 0.15 at n >= 128 on 3+ nets) the wide-net negative weakens and the window of N used
  is pre-asymptotic in a way F7 does not capture; I would then run larger N at n = 128.
- If P4 fails, pre-integration does not even help the exponent in low dimension for these nets, and F5 is wrong.
