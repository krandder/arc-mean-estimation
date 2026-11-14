# randomness lane: pre-registration (written 2 Nov 2026 ~13:58Z, before any evaluation run)

Hashes of this file and of the frozen code are in prereg_hashes.txt (sha256 + UTC time). Dev runs (not scored) used
256 x 32 nets 100, 101, 102 (sigma = 1e-3 truths as approximations) and seed 9500 at n = 32, 64, 128 (runs/dev_*;
logs/dev_struct*.log). Every threshold below was chosen after seeing those dev runs; none of the evaluation nets has
been run by this lane.

## Evaluation nets and truths
- 256 x 32 (ARC's Phase-1 shape): seeds 200-204, anet.make_weights; truths: arc-noisy noiseless 2^26-path files
  (floor 1.5e-8 nMSE).
- Ladder L = n/8: n = 32, 64, 128, seeds 300-307 (8 nets each); truths: arc-update's 2^24-path files (floor 6e-8).
  The fourth rung is the 256 x 32 set.

## Frozen code
lib/rnd.py (nets, designs, Gegenbauer utilities), scratch/structure.py (E1), scratch/combo.py (E2), scratch/noise.py
(E3), scratch/detqmc.py (E4), scratch/score.py (the scorer, rules below), tests/test_rnd.py (passes).

## Runs
- E1 structure.py on every evaluation net: rotation variances of Haar-randomised designs (ONB, simplex, cross-polytope,
  Kerdock and MUB at n = 256; 64 replicates, 12 for Kerdock), antipodal split, multilevel prefix controls, scrambled
  Sobol (RQMC) in the standard, polar and SVD frames of W_1 at 2^10, 2^12, 2^14 (16 replicates), antipodal RQMC,
  polar-aligned Kerdock with random signed permutations, centred Sobol vs truth.
- E2 combo.py on nets 200-204: the registered head-to-head at ARC's budget, N = 2^16, 16 replicates: rqmc_std,
  rqmc_polar, kerdock (66,048 points, one Haar rotation per replicate), mc_pairwise (2 n b random bits), det_std and
  det_polar (zero random bits), all radius exact, errors against the truth.
- E3 noise.py (P = 4096 pairs per delta) on every evaluation net.
- E4 detqmc.py on every evaluation net: centred Sobol (rb, plain, polar), Korobov lattices (centred, baker) at
  N = 2^6..2^16; full k-wise independent designs over GF(q) (q the least prime > n): k <= 4 at n = 32, 64, k <= 3 at
  n = 128, k = 2 at n = 256; unrotated and polar-aligned Kerdock at n = 256. Descriptive extra (not scored): k = 3 at
  256 x 32 on net 200 only.
- Compute: CPU, nice 19, ionice -c3, at most 2 heavy processes, 1 thread each.

## Predictions (scored by scratch/score.py; "median" = median over the nets named)
Spectrum (FORMAL T1; shares relative to the radius-exact variance Lambda):
- PS1 256 x 32: median odd share V_odd / V_rb in [0.45, 0.70] and every net in [0.40, 0.75].
- PS2 256 x 32: median share of harmonic degrees <= 2 (1 - simplex risk relative to RB-MC) in [0.30, 0.65].
- PS3 256 x 32: median even >= 6 share (half the Kerdock risk relative to RB-MC) in [0.08, 0.30].
- PS4 Along L = n/8: the simplex (2-design) gain over MC and the degree-1 share E_1 are lower at n = 256 than at
  n = 32 (medians).
Black-box ceiling (FORMAL T4):
- PB1 Kerdock (Haar, radius exact) gain over MC, 256 x 32: median in [2.0, 5.0], >= 1.5 on 5 of 5 nets.
- PB2 No Haar-randomised design (ONB, simplex, cross-polytope, Kerdock, MUB) gains more than 6 over MC at 256 x 32.
White-box (FORMAL T9, T10):
- PW1 256 x 32, 2^14 points: scrambled Sobol in the polar frame of W_1 gains more over MC than in the standard frame
  on >= 4 of 5 nets, with median ratio >= 1.2.
- PW2 n = 32, 64, 128: the median (over 8 nets) polar/standard ratio at 2^14 lies in [0.8, 1.3] at each width.
- PW3 256 x 32: Kerdock aligned with the polar frame and randomised only by signed permutations is biased:
  mean nMSE x m >= 5 on >= 4 of 5 nets.
- PW4 256 x 32: the best two-level multilevel prefix control gains <= 1.1 over RB-MC on 5 of 5 nets.
Registered combination at ARC's budget (E2):
- PC1 rqmc_polar gains >= 2.0 over MC on >= 4 of 5 nets and >= 1.2 x rqmc_std's gain on >= 4 of 5 nets.
- PC2 Kerdock (Haar) gains >= 1.8 over MC (mean nMSE vs truth) on >= 4 of 5 nets.
- PC3 The best structured sampler per net (max of rqmc_std, rqmc_polar, kerdock) gains between 2 and 8 over MC on
  every net: structure buys a constant, and none reaches 10x.
- PC4 Pairwise-independent MC (2 n b = 16,384 random bits for 2^16 points at b = 32) is MC-accurate: median of
  nMSE x N / (V_rb / V) in [0.6, 1.5].
- PC5 Zero random bits: centred Sobol in the polar frame has median nMSE x N <= 1 (beats plain MC).
Noise sensitivity and GSA (FORMAL T6-T8; GSA pooled over delta = 1e-6, 1e-5, 1e-4 as flips / 2 sqrt(delta/pi)):
- PN1 Layer-1 GSA within +-10% of n / sqrt(2 pi) on every evaluation net at every width (a theorem; validates the
  estimator).
- PN2 256 x 32: every layer's GSA (l >= 2) in [0.5, 1.3] x n / sqrt(2 pi), every net.
- PN3 256 x 32: total partition GSA in [0.6, 1.2] x n L / sqrt(2 pi), every net.
- PN4 256 x 32: NS_out(1e-5) / 1e-5 in [0.4, 1.5] x n / V on every net.
- PN5 256 x 32: P(the gate pattern of some layer changes) at delta = 1e-6 >= 0.8 on every net.
- PN6 Validity of T6: the design-measured tail tau_2 = 1 - (degree <= 2 share) is >= the T6 lower bound computed from
  NS_sph at delta in {0.03, 0.1, 0.3} (exact Gegenbauer a_d, d < 400), with tolerance 0.05, on every 256 net.
Deterministic QMC and bounded independence (E4):
- PQ1 256 x 32: centred Sobol (rb) fitted rate p (nMSE ~ N^-p over N = 2^8..2^16, points above 3x the truth floor):
  median in [0.6, 1.4] (no QMC rate at this dimension; MC has p = 1).
- PQ2 Centred Sobol (rb) median nMSE x N at 2^14 is higher at n = 256 than at n = 32.
- PQ3 Every resolved k-wise design (nMSE >= 3x the truth floor), every width and k: nMSE x N in [0.05, 5]
  (bounded independence is MC-like at its own size; no "fooling" beyond MC).
- PQ4 256 x 32: Korobov lattice (rb) median nMSE x N at 2^14 >= 0.5.

## Rate exponents (for the sibling preint lane)
Reported, not scored: fitted p for every deterministic series (E4), and nMSE x N vs N for the randomised series
(E1 at 2^10, 2^12, 2^14 and E2 at 2^16); plain MC has p = 1 exactly.

## Deviations
Any change after hashing goes to logs/deviations.txt with time and reason; amendments are hashed before their runs.
