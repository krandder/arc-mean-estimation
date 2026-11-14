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

## Amendment 1 (written 05:31Z; hashed before queue Y, i.e. before any ladder evaluation run at n = 32-128; queue X
## had restarted at 05:30:31Z and was still on the rank controls; no evaluation output had been read)
Motivation (dev, one net per width): the best error over the measured orders at L = n/8 was 2.6e-5, 3.4e-5, 2.0e-4,
3.2e-4 at n = 32, 64, 128, 256: it grew with width. If the hierarchy's attainable precision worsens as width and depth
grow together, "matching sampling with the depth growing linearly in the width" fails for this class at every
precision below that floor. Two more predictions, scored by scratch/score_lad.py tables:
P11 (attainable precision worsens along L = n/8). Let e*(n) = min over variants of the median-over-nets nMSE (variants
   k1..k4f run at that width: K <= 4 at n <= 128, K <= 3 at n = 256). Then e*(256) >= 3 e*(32), and e*(128) >= e*(64).
P12 (each order buys little). e_3/e_2 >= 0.2 at n = 64, 128, 256, where e_K is the median nMSE of the best variant of
   order K (each step from K = 2 to K = 3 divides the error by at most 5). [dev: 0.37, 0.36, 0.52]

## Amendment 2 (radial lead; written 06:16Z at main's request, after seeing eval net 200's oracle radial-Gaussian
## profile; hashed before any attribution run on nets 201-204, which have not started; scored on 201-204 only, net 200
## reported separately as seen)
Object: the "radial lead" = a Gaussian-direction closure whose radius (amplitude) marginal is exact. Its CEILING is
measured by the registered oracle radial-Gaussian model of run_attr.py (true mean and covariance, Gaussian directions,
true radius marginal by monotone transport, exact network after the cut): Gamma_rad(l). Its cost is not measured (no
deductive version is built); the cost model used is that of a K = 2 closure plus a one-dimensional radius law per layer,
i.e. ARC k2 'simple' at 256 x 32 (393 passes) up to the exact Gaussian recursion's ~1.2e3 passes (both measured or
counted in this lane), stated as an assumption.
R1 (the lead is real early). Median over nets 201-204 of Gamma_rad(l)/Gamma*_2(l) <= 0.33 at >= 2 of l = 1, 2, 4.
   [net 200: 0.09, 0.09, 0.03]
R2 (an angular floor remains). Median over nets 201-204 of Z = max_{l in {8, 16, 24}} Gamma_rad(l) >= 5e-5.
   [net 200: 1.4e-4]
R3 (crossover). With RQMC's measured curve on each net, the cost at which RQMC's nMSE equals Z is <= 2e4 passes on
   >= 3 of 4 nets, i.e. below one third of the Phase-1 budget (6.5e4 passes): sampling overtakes even the ideal radial
   closure's single-cut floor well inside ARC's budget. [net 200: ~3e3]
Reporting (not tested): X = (RQMC nMSE at the closure's assumed cost) / Z, the largest factor by which the ideal radial
closure could beat RQMC, and Y = Z, the precision below which it cannot compete; also against MC (1/N), the Kerdock
design (0.40/N, prior lane) and the multilevel sampler (~1.0x radius-exact MC at 256 x 32, prior lanes).

## Amendment 3 (ARC's own law as an error-cost exponent; written 06:20Z, hashed before I looked at any n = 128 ladder
## result (seed 300's n = 128 runs had finished; none read) or at any 256 x 32 result other than net 200's)
Arithmetic (PROVEN under the stated laws): if the order-K error is e_K = c (L/n)^K with c independent of K, and the
order-K cost is C_K ~ n^{K-1} forward passes (basic), then the best order affordable at budget C has error
e(C) ~ c (L/n) C^{-gamma} with gamma = log(n/L)/log n = 1 - log L/log n. So gamma -> 1 at fixed L (ARC's "matching at
fixed depth, large width") and gamma = log(1/alpha)/log n -> 0 at L = alpha n: the hierarchy's error falls with compute
ever more slowly than sampling's (gamma = 1). Predictions on the evaluation nets, with gamma_{2->3} =
ln(e_2/e_3) / ln(C_3/C_2) from the medians of the best variant of each order (errors and costs as in score_lad.py):
P13. gamma_{2->3} < 1 at every n = 32, 64, 128, 256 (L = n/8).
P14. gamma_{2->3} lies within [0.5, 1.5] x log(n/L)/log n (= log 8/log n: 0.60, 0.50, 0.43, 0.375) at n = 128 and 256.
[seen before writing: n = 32: 0.52, n = 64: 0.38 on the eval nets; net 200 alone: 0.48]

## Amendment 4 (width scaling of the radial ceiling; written 06:50Z after reading astra round 3 (FORMAL E10), which
## names this as the discriminating measurement; hashed before any run at n = 32, 64, 128 of the oracle models and
## before any oracle run on nets 201-204; seen before writing: net 200 at 256 x 32 only (E8))
Question: does the single-cut oracle floor of the ideal radial closure (Gaussian directions, exact radius marginal)
decay with width fast enough that its advantage over sampling grows? astra r3: after radius correction the first layer
leaves an n^{-2} angular error (PROVEN UNDER H_shell); in the middle layers H_cap would give n^{-1} (CONJECTURE).
Design: scratch/run_width.py (hashed with this amendment's code hash line, after a dev test on net 9500 only), the
oracle Gaussian and oracle radial-Gaussian of run_attr.py with one change: each push half uses its OWN covariance,
radius quantiles and pilot (independent clouds), so the cross-product b^2 is unbiased to leading order in the cloud
size (run_attr shares them across halves, a bias <= ~1/N_cloud). Nets: n = 32, 64, 128 (L = n/8) seeds 300-307 with
this lane's 2^24-path truths; n = 256 seeds 200-204 with arc-noisy's 2^26-path truths. Cuts: l = 1 and the three
mid cuts l = n/32, n/16, 3n/32 (fixed l/n and t/n). Pushes 2^21 per model and cut at n <= 128, 2^20 at n = 256;
clouds 2^18 per half.
Statistics (medians over nets): G1(n) = Gamma*_2(1); F1(n) = Gamma_rad(1); Zm(n) = mean over the three mid cuts of
Gamma_rad; p(stat) = minus the least-squares slope of ln stat on ln n over n = 64, 128, 256 (n = 32 reported only).
Wr(n) = median over nets of [cost at which that net's RQMC curve reaches its own mid-cut mean Gamma_rad] / [ARC k2
'simple' cost at width n], both in forward passes (RQMC curves and k2 costs from the registered ladder runs).
P15. p(G1) in [0.6, 1.4] (the plain first-cut Gaussian defect is the radius defect, ~1/n).
P16. p(F1) >= p(G1) + 0.4 (the radius correction buys a faster first-cut rate, toward astra's n^{-2}).
P17. p(Zm) in [0.5, 1.5] (the mid-layer angular floor of the ideal radial closure decays like ~1/n, as H_cap would
     give; a value > 1.5 refutes my reading and counts for the positive side).
P18. Wr(256)/Wr(64) <= 2 (the radial closure's window against RQMC does not grow polynomially with width).
Reported, not tested: per-width X(n) = RQMC nMSE at the k2 cost / Zm(n) and Y(n) = Zm(n); the same statistics for
the oracle Gaussian (Z2m); max over the mid cuts (Amendment 2's Z); the cost multiplier J (quadrature nodes) of
astra's implementable closure, which multiplies the closure's cost and divides Wr.

## Amendment 5 (the ideal radial closure as a full recursion; written 07:07Z, hashed before any run of run_ipr.py on
## any net, dev or eval; seen at this time: eval single-cut attribution logs of nets 200-201 at 256 x 32 (201 partly),
## no width-scaling eval output (queue W had not started))
Question: single-cut oracle defects do not bound a full recursion (cancellation, E2; accumulation). So measure the full
recursion of the ideal closures directly: scratch/run_ipr.py runs the moment-matched Gaussian projection (the exact
Gaussian recursion) and the radial-Gaussian projection (Gaussian directions, radius marginal of the exact one-layer
push-forward of the model state, monotone transport) through all L layers, with each layer's moments computed from
2^19 samples of the model state (two independent replicates; b2 = cross product, unbiased for the noise-averaged
closure's squared error). This is the closure's bias with exact per-layer moments, not a cost-competitive method; its
deductive cost model stays astra's O(J n^3) per layer (FORMAL E10.1). Nets: 256 x 32 seeds 200-204; n = 64, 128
(L = n/8) seeds 300-307. Scored by scratch/score_amend5.py.
P19 (method check). On each 256 x 32 net the Gaussian IPR's b2 is within a factor 1.5 of the deductive exact Gaussian
     recursion's total (runs/attr_s{seed}.json).
P20 (the single-cut floor transfers). Median over 256 x 32 nets of the radial IPR's b2 >= 0.5 x Zm(256) (Amendment 4).
P21 (the lead survives the full recursion). Median over 256 x 32 nets of (radial IPR b2)/(Gaussian IPR b2) <= 0.5.
P22 (width). p_full = minus the least-squares slope of ln(median radial IPR b2) on ln n over n = 64, 128, 256 lies in
     [0.5, 1.5].
P23 (ARC's budget). At 256 x 32, RQMC's measured curve reaches the radial IPR's b2 at <= 2e4 passes on >= 4 of 5 nets.
Reported: per width the radial IPR's error E_rad(n), the RQMC cost to reach it, the gain at the k2 cost (J = 1:
X_full(n) = RQMC nMSE at the k2 cost / E_rad(n)); the per-layer mean errors.

## Amendment 6 (the radial full recursion with a rank transport; written 08:25Z after stopping queue V; hashed before
## any run of run_ipr2.py; seen before writing: Amendment 5's results at n = 64 and 128 on all 8 nets, net 200 at
## 256 x 32 (Gaussian IPR 9.8e-4; radial IPR noise-dominated: replicate noise var 1.8e-3, cross product -1.9e-4))
Why: in run_ipr.py the radius transport maps each sample through a fresh 2^16-sample pilot CDF of the Gaussian model;
the pilot's CDF error shifts all radii coherently by ~0.1% per layer, which random-walks through 32 layers and is read
by the future with weight ~0.95 (b_0), so at 256 x 32 the replicate noise (1.8e-3) swamps the closure's bias.
scratch/run_ipr2.py is run_ipr.py with one change: within each batch of 2^14 samples the j-th smallest Gaussian radius
is mapped to the ((j - 1/2)/2^14)-quantile of the previous layer's radii (an exact rank transport; no pilot). Same
closures, sample sizes (2^19 per layer, two replicates) and seeds scheme. Nets: 256 x 32 seeds 200-204 first, then
n = 128 and 64 (seeds 300-307) if time allows. Scored by scratch/score_amend6.py; the same statistics as Amendment 5.
P24 (validity). The median replicate noise var of the radial IPR2 at 256 x 32 is <= 1e-4; if not, P25-P27 are
     reported as undetermined.
P25 (= P20). Median radial IPR2 b2 at 256 x 32 >= 0.5 x Zm(256) (Amendment 4: Zm(256) = 1.4e-4).
P26 (= P21). Median over 256 x 32 nets of (radial IPR2 b2)/(Gaussian IPR2 b2) <= 0.5.
P27 (= P23). RQMC reaches the radial IPR2 b2 at <= 2e4 passes on >= 4 of 5 nets.
P28 (= P22, if n = 64, 128 are run). p_full over n = 64, 128, 256 in [0.5, 1.5].
