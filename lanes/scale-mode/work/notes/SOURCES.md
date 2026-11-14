# Sources for the scale-mode lane (fetched 2 November 2026, 10:26-10:45Z)

Raw downloads (untrusted data, never executed) are under `downloads/` (forum/, pdf/, gh/, hf/, kit/, lb/). Older ARC
sources (paper, blog posts, rules) were verified verbatim this morning by the arc-update lane
(work/arc-update/notes/ARC_SOURCES.md, 93 quotes, 04:41-05:05Z); I re-fetched only what this lane needs.

## 1. The two public counter-claims, verbatim

### 1a. Topic 18298 (pranav_viswanath)
URL https://discourse.aicrowd.com/t/18298 . Title "[Phase 2 Algorithmic Contribution] Addressing cumulant propagation's
depth problem with scale separation". Topic created 2026-10-28T23:57:09Z (two minutes before the 28 Oct 23:59Z write-up
deadline); post #1 at version 8, last edited 2026-10-30T16:51:45Z (the date the brief cites); 1 post, 29 views at 10:26Z.
> In a nutshell: when depth grows with width, a collective scale mode builds up that poisons the order-by-order expansion.
> Separating it out exactly via ReLU homogeneity and carrying it as a one-parameter law restores convergence and beats
> sampling at every width tested on across networks of various sizes (64x16 through 1024x256, including improving ARC's
> MSE on the competition's own 1024x16, beating both sampling and existing kappa methods with no fitted constants).
Attachment "Pranav Viswanath ARC Writeup.pdf" (786,829 bytes, sha256 d7f1c06d..., PDF created 2026-10-29 16:07Z) and repo
https://github.com/PranavViswanath/scale-separation (created 2026-10-28T23:50:33Z, HEAD bfeab38 2026-10-30T17:01Z).
- "64x16 through 1024x256" is width x depth on the diagonal L = n/4 (64x16, 128x32, 256x64, 512x128, 1024x256; 10 nets
  per cell), not L = n/8. "Beats sampling" means naive Monte Carlo at equal FLOPs (ARC's counter + 1 flop per ndtr),
  charging MC 2 n^2 (L + 1) per sample (an output layer the estimand does not need).
- The claim's numbers (repo README and WRITEUP.md): margin over naive MC 2.31, 1.57, 1.53, 1.42, 1.21 at 64x16 ... 1024x256;
  nMSE 1.52e-3, 1.51e-3, 9.53e-4, 5.88e-4, 3.73e-4; "1.3x to 4.1x more accurate than ARC's best estimate at my compute";
  the scale-law ladder: K3 9.2e-4 (128x32) and 5.4e-4 (256x64), "about 5x better than the best ARC's ladder reaches",
  but "they sit above the sampling line at their FLOPs". Since 30 Oct the repo also says: "The margin narrows with
  width: ... exponent ... -0.20 (95% bootstrap CI [-0.38, -0.04]) ... at 1024x256 the margin's interval is [0.89, 1.83]
  with 6 of 10 nets ahead of sampling" and "The pre-registered width test failed". The attached PDF does not contain
  these sentences (it says "This note answers it on ARC's own criterion"); see notes/AUDIT.md.
- At 1024x16 (Phase 2 shape) the claim's own K2-cost estimator is 1.09-1.76x WORSE than ARC's AUGMENT K2 on 12/12 nets
  (docs/PREREG.md C1-Q1); the 1.25x / 1.44x gains are the scale hook inside ARC's factored K3, and the graded entry's
  1.73x is inside a fitted engine (504aldo V29 with ridge-fitted tables).
- Nothing in topic 18298 compares with RQMC or any other sampler than naive MC (antithetic and radial-exact MC at 64x16
  only).

### 1b. Topic 18198 (keenanpepper)
URL https://discourse.aicrowd.com/t/18198 , "Covariance propagation baseline scores 3.93e-7/3.93e-6", post #1
2026-08-24T19:49:39Z (unedited), replies 2026-09-03 and 2026-09-04 (no data).
> This should be pretty easy to figure out, but the six current leaderboard submissions that are tied at 3.93e-7 adj /
> 3.93e-6 MSE are probably all the plain & simple covariance propagation baseline. Which decisively beats sampling in
> Phase 2. Exciting!
- The baseline is the starter kit's examples/03_covariance_propagation.py (exact per-neuron Gaussian mean and variance,
  off-diagonal covariance scaled by Phi(a_i) Phi(a_j)); its README lists 51,709,240,799 flopscope FLOPs (2.351% of 2^41)
  and final-layer MSE ~4.2e-6 at the n = 100k check. On Phase 2 dev MLP 12 it reproduces ARC's K2 'simple' to 4 digits
  (3.896e-6 both; runs_dev). "adj" = MSE x max(0.1, C/B) = 0.1 x MSE here, because it uses 2.35% of the budget.

### 1c. Topic 18147 (jonah_butterbaugh), the Phase 1 numbers in the brief
URL https://discourse.aicrowd.com/t/18147 , "[Phase 1 write-up] The non-Gaussianity wall at depth 32, measured with
certificates ..." 2026-08-10T20:32:05Z, unedited, 323 views:
> - diagonal Gaussian closure: 7.18e-4 bias MSE
> - exact full-covariance Gaussian closure: 9.61e-5
> - a budget-matched sampling estimator: ~2.5e-7
> Making the covariance exact buys ~7.5x over the diagonal closure; the remaining ~340x is third-and-higher-cumulant
> structure that no Gaussian-moment closure can represent at any compute multiplier.
Against "400k-sample Monte-Carlo truth", at Phase 1's 256 x 32. This supports the negative at Phase 1 (the full Gaussian
closure is ~400x behind a budget-matched sampler); it is consistent with arc-update's exact Gaussian recursion
(nMSE 1.0-2.0e-3, i.e. raw MSE ~2e-5 to 2.4e-4 with per-neuron variance 0.02-0.12).

### 1d. Related participant material read today (titles and openings only; UNVERIFIED claims)
- 18282 (megan_park, 2026-10-24): "It never samples ... Its public score is 1.918e-9, and its final-layer MSE is 84x below
  full-budget Monte Carlo at 14 % of the budget." "The remaining engine is still 330x better than Monte Carlo at equal
  compute; ARC's reference chain is 118x." (Phase 2, 1024 x 16.)
- 18248 (2026-10-15): "Removing the global scale mode makes a carried kappa4 core pay: extraction on/off x0.380 on the
  grader inside e30_a" (an earlier scale-mode result at 1024 x 16). 18254 (2026-10-18): "Zero-Sample K=4 via Factored
  n^3-Memory Transport at 1024 x 16: 11.8x below augmented K=3". About 25 Phase 2 write-ups (18246-18307), all
  deductive cumulant chains at 1024 x 16.

## 2. The contest's specification (re-fetched today)
Sources: Phase 1 launch https://discourse.aicrowd.com/t/18026 (mohanty, 2026-06-17); Phase 2 launch
https://discourse.aicrowd.com/t/18197 (mohanty, 2026-08-23 23:50Z); update https://discourse.aicrowd.com/t/18251
(2026-10-17); starter kit (AIcrowd/whest-starterkit main = 96e308c, 2026-10-17; README head identical to the live copy
fetched 10:41Z; docs/reference/rounds.md); dataset card https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026
(revision v2-phase2, sha aa99830f, 2026-08-30); Rules (verified 05:00Z by arc-update, ARC_SOURCES 4.4).

| | Phase 1 (`v1-phase1`) | Phase 2 (`v2-phase2`) |
|---|---|---|
| shape (width x hidden layers) | 256 x 32 (L/n = 1/8) | 1,024 x 16 (L/n = 1/64) |
| dates | 18 Jun - 10 Aug 2026 | 22/23 Aug - 21 Oct 2026 (extended from 17 Oct) |
| weights | i.i.d. N(0, 2/width) every layer (He), no biases, no output layer: h_l = relu(h_{l-1} W_l) | same |
| input law | x ~ N(0, I_width) | same |
| estimand | per-neuron E h_l for every layer (predict() returns (depth, width)); scored on the final layer only | same |
| truth | Monte Carlo, N = 1e9 per MLP, float64 sums | same |
| score | s_m = MSE_final,m x max(0.1, C_m / B_m); leaderboard = suite mean ("adjusted"); raw MSE also shown | same |
| FLOP counter | flopscope (v0.8.0rc1 at launch); C = F + lambda R, residual wall time priced at lambda = 1e11 | flopscope 0.12.3; C = F (lambda = 0), residual capped at 0.4 s; computation outside flopscope prohibited |
| budget per MLP | 2.72e11 FLOPs = 64,850 forward passes (2 d w^2 = 4.19e6) | 2^41 = 2.199e12 = 65,536 passes (3.36e7) |
| graded suite | 100 MLPs (hidden) | 100 MLPs (hidden) |
| public data | mini 100 + full 1,000 MLPs with truths | same (`avg_variance` column = final-layer mean per-neuron variance) |

- "adj" vs raw: the 0.1 floor means any method using under 10% of the budget is scored as if it used 10%. Naive MC with
  N samples has raw MSE avg_variance / N and adjusted score avg_variance / (B/pass) for any N >= 0.1 B: on the 12 public
  Phase 2 MLPs 0-11, avg_variance = 0.061-0.096 (mean 0.080), so full-budget MC has raw MSE 1.22e-6 on average.
- Organisers on the shape change: "The best-performing methods in Phase 1 tended to be based on variations of sampling.
  We have made the network wider and shallower for Phase 2, to make cumulant-propagation-style methods more competitive."
  (18197). Starter kit rounds.md: "Brute-force Monte Carlo has been held at roughly the same 65k samples per MLP in every
  round, and in every round that is far short of what a competitive score needs."

## 3. State of the art (public boards, fetched 10:38Z; not the prize ranking, which comes from private re-evaluations;
winners "tentatively on or about November 15, 2026"; no official results published)
- Phase 2 (1024 x 16): #1 marius_binner and oliver_chen, adjusted 1.3e-9, final-layer MSE 1.10e-8, utilisation 0.122;
  #3 J2W and mliston 1.4e-9 (MSE 1.32-1.36e-8). Full-budget MC on these nets would score ~1.2e-6 raw: the best public
  entries are ~100x below it, at 12% of the budget, with deductive cumulant chains (write-ups 18246-18307).
- Phase 1 (256 x 32): #1 ednacob adjusted 1.84e-8, final-layer MSE 3.63e-8 at utilisation 0.508; #2 J2W 2.78e-7;
  #3 dstepanov 2.20e-7. The organisers say Phase 1's best methods were variations of sampling.
- ARC's own published state of the art is unchanged: arXiv:2605.05179 v2 (cumulant propagation, experiments to 12
  hidden layers; ARC_SOURCES 1); no ARC post on depth or on contest results after 9 June 2026 (ARC_SOURCES 9).

## 4. Which phase our nets match
- Our five eval nets 200-204 are Phase 1's setting exactly in law and shape: 256 x 32, W_l i.i.d. N(0, 2/n) every layer,
  no bias, no output layer, x ~ N(0, I), estimand the final-layer per-neuron means (arc-noisy's weight stream; 2^26-path
  noiseless truths). Differences from the contest: our error unit is nMSE = |est - Y|^2 / tr Var (MC with N samples
  scores 1/N) rather than raw MSE x max(0.1, C/B), and cost is ARC's NamedFlopCounter, not flopscope.
- The arc-update ladder (n = 32, 64, 128 at L = n/8) extends Phase 1's ratio L/n = 1/8. Phase 2 (L/n = 1/64) differs, so
  this lane measures it separately on the public Phase 2 MLPs 0-11 with their 1e9-sample truths.
