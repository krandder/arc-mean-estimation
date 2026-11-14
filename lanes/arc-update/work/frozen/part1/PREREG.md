# arc-update pre-registration, Part 1 (written 05:26Z, 2 November 2026; hashed before any evaluation-net run)

Lane: arc-update (bead pool-ttdzrk.13). Theory: FORMAL.md v1 (sha 910255ee, frozen 04:54:16Z). Code frozen by sha256 in
prereg_hashes.txt together with this file: lib/au.py, scratch/{truth,run_lad,run_attr,run_rank,run_rqmc,score_lad,
score_attr}.py. Deviations go to logs/deviations.txt.

## What was seen before registration (development; not scored)
- Dev nets: 256 x 32 seeds 100, 101 (arc-noisy dev weights; their sigma = 0.001 truths, 2^25 paths, used as approximate
  noiseless truths: the noise moves these means by nMSE ~3e-7), and seed 9500 at n = 32, 64, 128 with L = n/8 (2^22-path
  truths computed here). Runs: ARC kprop variants (runs/lad_*_s9500_*, lad_n256_L32_s100_*), RQMC, attribution on 100
  and 101 (2^16 pushes), rank statistics on 100 (N = 2^14; 101 at 2^16 still running at the hash) and the controls
  (rank_control.json, N = 2^14).
- Prior-lane numbers in notes/READING.md (arc-noisy medians at sigma = 0.001 on nets 0-23; not the eval nets).
- Nothing from the evaluation nets below has been run by this lane. The arc-noisy lane ran ARC kprop K = 2 at L = 32 and
  K <= 3 at L = 8 on seeds 200-204 (its noiseless controls); I have not opened those result files.

## Nets
- 256 x 32 (ARC's Phase 1 shape): seeds 200-204, weights anet.make_weights (checksummed in the truth files), truths =
  arc-noisy's noiseless 2^26-path files truth_256_32_s0_seed20?.npz (nMSE floor 1.5e-8).
- Ladder along L = n/8: n = 32 (L = 4), 64 (L = 8), 128 (L = 16), seeds 300-307 (8 nets each); truths 2^24 paths
  computed here (scratch/truth.py; floor 6e-8). Errors below 10x the floor are reported, not scored.

## Methods
- ARC's mlp_kprop (main at 93d091a), sigma = 0, avg_metric = True (ARC's default loop as in arc-noisy), ARC's FLOP counter:
  k1, k2 ('simple'), k2a ('augment'), k3 (basic), k3f (factorised), k3fa (factorised augmented), k4f, and k4 (basic) at
  n <= 64. At 256 x 32: k1, k2, k2a, k3, k3f on all five nets; k3fa on seeds 200 and 201 only (about an hour each).
  Cost in forward passes = ARC flops / (2 n^2 L).
- Exact single-Gaussian recursion (bits-bounds lib/closure.py relu_moments, q = 48) at 256 x 32 (inside run_attr);
  cost = matrix products 4 n^3 L + pairwise moments n^2 x 48 x 28 x L flops.
- RQMC: scrambled Sobol (scipy), inverse normal, N = 2^8, 2^10, 2^12, 2^14 (and 2^16 at 256 x 32), R = 8 replicates
  (mean nMSE over replicates). Plain MC: 1/N exactly. RQMC at other costs: log-log interpolation; beyond the largest
  N, extrapolated with slope -1 (MC rate; conservative for RQMC only if its rate is >= 1, as measured in prior lanes).
- Attribution (FORMAL A6) at 256 x 32, cuts l in {1, 2, 4, 8, 16, 24, 28, 31}, 2^19 pushed samples per (model, cut)
  (dev used 2^16, whose cross-product noise is ~3e-4 in nMSE; 2^19 gives ~5e-5 at b^2 ~ 2e-4):
  ARC k2, the exact Gaussian recursion, the oracle Gaussian (true mean from the truth file, covariance from 2^17 true
  samples) and the oracle radial-Gaussian (oracle Gaussian directions with the true radius marginal by monotone
  transport). Squared norms debiased by independent halves.
- Rank statistics (FORMAL A4, B2-B3) at 256 x 32, layers {1, 2, 4, 8, 12, 16, 20, 24, 28, 31}, N = 2^16 true samples
  (four blocks of 2^14); controls at N = 2^16: Gaussian, planted rank 8 and rank 32.

## Primary quantities
- G_MC = (1/passes)/nMSE and G_RQMC = nMSE_RQMC(passes)/nMSE (gain at own cost; > 1 = the method wins).
- For an order K, G_K = the median over nets of the best variant of that order (K = 2: k2, k2a; K = 3: k3, k3f, k3fa;
  K = 4: k4, k4f).

## Predictions (scored by scratch/score_lad.py and scratch/score_attr.py; a prediction "holds" as stated)
P1 (price ladder, FORMAL C1). a) G_3/G_2 <= 2/L at each width n = 32, 64, 128, 256 (L = n/8). b) G_4/G_3 <= 2/L at
   n = 64 and 128. [dev: G_3/G_2 = 0.18, 0.14, 0.06, 0.015 against 2/L = 0.5, 0.25, 0.125, 0.0625; G_4/G_3 = 0.13, 0.009]
P2 (beyond K = 2 the hierarchy loses). At n = 128 and 256: G_3 < 1 and (n = 128) G_4 < 1 against MC; at n >= 64 the
   best order >= 3 variant has median G_RQMC < 0.5. [dev: 0.22, 0.002, 0.063; G_RQMC 0.30, 0.12, 0.038]
P3 (the K = 2 window is narrow). At 256 x 32, on >= 4 of 5 nets, RQMC reaches the best K = 2 variant's nMSE at a cost of
   at most 4x that variant's cost. [dev: about 2.1x]
P4 (contest budget). At 6.5e4 passes (Phase 1 budget), RQMC's interpolated nMSE is >= 10x below the best ARC variant
   affordable within that budget, on 5 of 5 nets at 256 x 32. [dev: ~35x]
P5 (no width-growing gain along L = n/8). a) G_3 strictly decreases over n = 32, 64, 128, 256 (medians).
   b) G_2 at n = 256 is below G_2 at n = 32. [dev: 1.27, 0.85, 0.22, 0.063; 4.1 vs 7.1]
P6 (attribution, FORMAL A6 and NC), for ARC k2 and the exact Gaussian recursion separately, each on >= 4 of 5 nets:
   a) the past defect at l = 8 carries >= 30% of the total error (b_8^2 >= 0.3 total);
   b) no strong cancellation: total >= 0.4 (a_l^2 + b_l^2) at l = 4, 8, 16.
   c) code check of CHECK-1: |a_31^2| < 1e-5 on every net (the last step is exact given the state). [dev: all hold]
P7 (single-cut Gaussian defect). The median over nets of the oracle Gaussian defect Gamma*_2(l) = b_l^2 is >= 5e-5 at
   each of l = 4, 8, 16, and at l = 16 it is >= 0.2 x the median total error of ARC k2. [dev: 3.6e-4, 2.1e-4, 5.0e-4;
   ratio 0.88]
P8 (where the Gaussian defect lives; radial marginal). Replacing the oracle Gaussian's radius marginal by the true one
   (monotone transport) does not remove the single-cut Gaussian defect: the median over nets of
   Gamma*_radgauss(l) / Gamma*_2(l) is >= 0.5 at >= 2 of the 3 cuts l = 8, 16, 24. [dev 101 at 2^16 pushes, noisy:
   0.14, 2.3, 1.5] So the defect the future sees is not the amplitude marginal alone.
P9 (order-3 structure, FORMAL B2-B3; dev refuted my B2 "rank grows with depth": PR3 falls 115 -> 1.1 from l = 1 to 31).
   a) PR3(l) <= PR_cov(l) at every layer on every net; b) median... every net has PR3(l = 1) >= 40 and PR3 <= 4 at
   every l >= 16; c) the held-out top-32 multilinear capture is <= 0.2 at l = 1 and >= 0.9 at l = 16 on every net;
   d) control: planted rank 32 gives PR3 in [24, 40]. [dev: all hold]
P10 (exact Gaussian closure at 256 x 32). Median nMSE in [2e-4, 2e-3] and median G_RQMC at its full cost <= 1.5.
   [dev: ~6.5e-4; ~0.6]

## Analyses fixed now
- Medians over nets; per-net values reported. Ratios formed per net, then medianed, except P1/P2/P5, which use the
  medians of G as defined.
- FLOPs: ARC's counter for kprop (as published), flopscope-style counts for the exact closure, 2 n^2 L per sample for
  samplers (setup-free; RQMC point generation not charged, which favours RQMC by at most its point-generation cost,
  disclosed).
