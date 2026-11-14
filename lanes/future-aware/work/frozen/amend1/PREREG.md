# future-aware pre-registration, Part 1 (written 11:09-11:22Z, 2 November 2026; hashed before any evaluation-net run)

Lane: future-aware (bead pool-ttdzrk.14). Theory: FORMAL.md v1 (sha 171b2d39, frozen 10:39:14Z) and the co-prover's
round 1 (coprover/astra_r1_answer.md). Code frozen by sha256 in prereg_hashes.txt with this file: lib/fa.py,
lib/fa_kprop.py, scratch/{run_cut, run_rec, run_k3p, run_hyb, score_part1}.py, the eval queue scripts, and the imported
read-only work/arc-update/lib/au.py. Deviations go to logs/deviations.txt.

## What was seen before registration (development; not scored)
- Dev nets: n = 64 (L = 8) and n = 128 (L = 16) seed 9500 (arc-update's 2^22-path dev truths); 256 x 32 seed 100
  (arc-noisy's sigma = 0.001 truth, 2^25 paths, an approximate noiseless truth). Runs: runs/*_dev*.json, logs/dev_*.log.
- Prior-lane numbers on the evaluation nets (arc-update's registered results: ARC kprop variants, RQMC curves, the
  radius-corrected recursion) are known to me; they are comparators here, not predictions.
- Nothing of this lane's methods has been run on the evaluation nets 200-204 (256 x 32) or 300-307 (n = 64, 128).
- At the hash time some dev runs on net 100 (256 x 32) were still running (the l = 24 single cut, two recursion
  variants, the remaining k3p variants and the hybrid); their outputs are dev data and change nothing registered here.
- Dev values used for the thresholds (net 100 at 256 x 32 unless stated): single cut l = 4: gauss 3.6e-4, cond_futnl64
  3.1e-6, cond_pca64 3.1e-5; l = 16: 4.1e-4, 6.5e-6, 3.1e-5; recursion (b2): gauss 9.3e-4, futnl16 5.5e-4, futnl64
  5.1e-5; n = 128 (net 9500): gauss 1.6e-3, futnl16 7.5e-4, futnl32 2.1e-4, futnl64 1.7e-5, pca32 6.6e-4; n = 64:
  1.4e-3, futnl16 2.9e-4, futnl32 2.9e-5, pca16 5.4e-4. k3p (nMSE): 256: k2 6.2e-4, k3 3.2e-4, futv64 2.8e-4, pca64
  2.5e-4; 128: k2 1.8e-3, k3 3.7e-4, futv16 6.0e-4, pca16 9.8e-4, futv32 4.4e-4, pca32 4.1e-4, futmf2_32 5.2e-4;
  64: k2 1.7e-3, k3 3.8e-4, futv8 6.2e-4, pca8 8.9e-4, futv16 4.1e-4, pca16 6.1e-4, futmf2_16 4.6e-4. Hybrid (n = 64):
  eta at l = 1: 0.29-0.47; beta_eg at l = 4: 2.1-5.3e-4; residual RQMC 1.1-1.3x below plain RQMC at N = 2^12.

## Nets
256 x 32: seeds 200-204 (truths: arc-noisy noiseless 2^26 paths, nMSE floor 1.5e-8). Along L = n/8: n = 64 (L = 8)
and n = 128 (L = 16), seeds 300-307 (truths: arc-update 2^24 paths, floor 6e-8). Values below 10x the floor are
reported, not used in ratios.

## What is run, and what each thing is
Cost unit: one forward pass = 2 n^2 L flops ("pass"). Every cost below includes the backward work used to find the
future-relevant directions (VJPs: 3 x 2 n^2 t flops per sample through t layers; basis VJPs for E[J]: n per sample;
mean-field backward sweeps: 2-4 n^3 per layer) and the dense linear algebra (counted analytically).
Feature kinds (lib/fa.py): futnl = whitened top-k active subspace of the NONLINEAR part of the future map g_l (VJPs
J^T v at 2^12 samples of the cloud, E[J] from 64-128 samples); fut = the same for the whole g_l; pca = top-k cloud
covariance axes (past-measurable); rand = Haar frame; futv = whitened active subspace from VJPs at samples of a
method's OWN Gaussian state; futmf2 = deductive mean-field E[J^T J] with independent gates (lib/fa_kprop.py).

B1. Single-cut BENCHMARK (scratch/run_cut.py; not an estimator; true samples carry the kept law). At cut l the true
    law is replaced by a projection and pushed through the exact rest of the net; b2 is unbiased for the squared
    single-cut defect (two halves, common random numbers across variants). Variants: gauss, radg (arc-update's radial
    transport), cond_<kind><k> (k features exact, linear-Gaussian conditional complement; mean and covariance exact),
    radg_<kind><k> (cond, then radial transport), edge_<kind><k> (oracle Gaussian x order-3 Gram-Charlier weight with
    the k features' TRUE third cumulant: future-weighted cumulant truncation (b), as a benchmark). 2^18 pushes (two
    halves of 2^17; dev noise check: the 'true' variant's |b2| <= 3e-6). n = 256: cuts l = 1, 4, 8, 16, 24; cond
    futnl, pca, rand at k in {4, 16, 64, 128}; radg futnl, pca, rand at k in {16, 64}; edge futnl, pca at k in
    {4, 16}. n = 128: cuts 1, 2, 4, 8, 12; cond fut, futnl, pca, rand at k in {4, 16, 32, 64}; radg at {16, 32}.
    n = 64: cuts 1, 2, 4, 6; cond fut, futnl, pca, rand at k in {4, 16, 32}; radg at {16}. (Queue A.)
B2. Full-recursion BENCHMARK, the future-aware closure "keep k future-relevant directions exact, Gaussian elsewhere"
    run as a finite-sample recursion that carries the k-dim law by N = 2^18 particles (scratch/run_rec.py; two
    replicates, b2 = cross product). It measures the family's bias. It is ALSO scored as an estimator at its honest
    cost (passes_per_rep: flop count of one replicate incl. the per-layer backward work), because carrying a k-dim
    law by particles is a hybrid sampler. Variants: gauss, radg, futnl{16, n/4, n/2}, pca{n/4}; pca{n/2}, rand{n/4}
    at n = 64, 128 only (time). (Queues B, C.)
D1. Deductive members (b) and (a): ARC's K = 3 'simple' propagation with the third cumulant restricted at every hidden
    layer to k feature directions, kappa_3 <- kappa_3 x Pi x Pi x Pi, Pi = S A (A^T S A)^-1 A^T (scratch/run_k3p.py):
    "third cumulant only in the future-relevant subspace, Gaussian elsewhere". Kinds: futv (2^11 VJPs per layer at
    samples of the method's own Gaussian state), futmf2 (deductive), pca; k in {16, n/4, n/2}; 'none' = ARC k3.
    Run with ARC's factorised representation (factor = True, 'simple'), whose third cumulant Sym(sum_r a_r b_r c_r) is
    projected factor by factor (Pi a_r, Pi b_r, Pi c_r); this equals projecting the dense tensor (dev n = 64: dense and
    factorised runs agree to all printed digits on 4 variants; ARC's k3 and k3f give the same nMSE). Cost of THIS
    implementation = ARC's flop counter (k3f) + the projection (6 n^2 R per layer, R = number of factors) + backward.
    A best-case cost for a dedicated k-dim implementation (HEURISTIC, fixed now so it can be scored):
    C_ded(k) = C(k2) + k + 1.5 k^4 / n^2 + C_back, with C_back = 2^11 x 3 x (L - 1)/2 passes (futv) or the mean-field
    sweeps 4 n^3 L / (2 n^2 L) = 2 n passes (futmf2).
H1. Hybrid (c) (scratch/run_hyb.py): control c(h_l) = jac (E[J] by basis VJPs), jacmf (mean-field Jacobian,
    deductive), reg (least-squares linear fit on a 2^15-sample pilot), regq16 (reg + quadratics in the top-16 futnl
    features), at l in {1, 2, 4, 8, 16, 24} (n = 256; {1, 2, 4, 8, 12} at 128; {1, 2, 4, 6} at 64), with E_Q[c] from
    the exact Gaussian recursion (eg; exact at l = 1) or ARC k2; eta = residual variance share on independent samples;
    beta = |E_Q[c] - E_P[c]|^2 / V; RQMC (8 scrambles, N = 2^8..2^14, the same points for plain h_L and every residual)
    gives G_R. Equal-cost criterion (astra r1 Q5): error(C) = beta + eta / (N G_R(N)) with N = (C - B)/a, B = setup
    (closure + backward + pilot), a = per-sample cost.
Comparators: RQMC curves of arc-update (runs/rqmc_*.json, mean over 8 scrambles at N = 2^8..2^16 (256) or 2^14,
log-log interpolation; below the smallest N extrapolated with slope -1, labelled); plain MC 1/N; ARC k2, k2a, k3 from
arc-update runs/lad_*.json; the multilevel shared-trajectory sampler ~1.0x MC at 256 x 32 [prior, not rerun].

## Primary quantities
For an estimator with error e (nMSE; per-replicate nMSE for B2 as an estimator) at cost C (passes):
G_RQMC = e_RQMC(C) / e (its gain at own cost; > 1 means it wins), C* = the cost at which RQMC reaches e (the end of
its window). "Beats RQMC by X up to precision Y" = X = median G_RQMC, Y = median e, per width. Ratios per net, then
medians over nets.

## Predictions (scored by scratch/score_part1.py; dev values in brackets)
P1 (future-aware beats past-measurable selection; B1). At n = 256, median over nets of b2(cond_futnl64) /
   b2(cond_pca64) <= 0.5 at >= 3 of the 4 cuts l = 4, 8, 16, 24 (cells with b2(cond_pca64) < 5e-6 excluded).
   [dev net 100, l = 4: 0.10; dev n = 64/128 at k = n/4..n/2: 0.14-0.44]
P2 (fixed k loses its effect with width; B2). The median improvement I_16(n) = b2(gauss) / b2(futnl16) satisfies
   I_16(256) < I_16(64). [dev: 4.8, 2.1, 1.7 at n = 64, 128, 256]
P3 (k proportional to n is needed; B2). At every width: median b2(gauss)/b2(futnl{n/4}) >= 2, and
   median b2(gauss)/b2(futnl{n/2}) >= 10. [dev: n/4: 4.8, 7.7; n/2: 48, 94 at n = 64, 128]
P4 (future beats PCA in the recursion; B2). At every width: median b2(futnl{n/4}) < median b2(pca{n/4}).
   [dev: 2.9e-4 vs 5.4e-4 (64), 2.1e-4 vs 6.6e-4 (128, k = 32)]
P5 (B2 as an estimator loses). For futnl{n/2} at its honest per-replicate cost, G_RQMC < 0.5 on every net at every
   width.
P6 (D1, future-weighted truncation keeps k3's gain; future directions matter at small k). Retained fraction
   R = (e_k2 - e_k3p) / (e_k2 - e_k3) (ARC 'simple' k2 and k3 on the same net; R > 1 is possible): (a) median
   R(futv, n/4) >= 0.7 at every width; (b) median R(pca, n/8) < median R(futv, n/8) at every width.
   [dev: R(futv, n/4) = 0.98 (64), 0.95 (128); R(futv, n/8) = 0.82, 0.84 vs R(pca, n/8) = 0.62, 0.58;
   at k = n/4 pca is as good as futv at n = 128 (0.97 vs 0.95), so (b) is registered at n/8]
P7 (D1 opens no window as implemented). At 256 x 32, G_RQMC of every D1 variant at its cost (this implementation)
   < 0.2 on 5 of 5 nets.
P8 (D1 best case). At 256 x 32, with the registered best-case cost C_ded, median G_RQMC of k3p(futmf2, 64) and of
   k3p(futv, 64) <= 3.
P9 (hybrid). (a) At l = 1 (exact means) the best control has median eta >= 0.25; (b) at l >= 8 every control's median
   beta_eg >= 1e-4 at n = 256; (c) the best hybrid's equal-cost gain over RQMC at 6.5e4 passes (registered formula,
   with the setup of the cheapest-setup control of each kind) is <= 2 at n = 256 (median).
   [dev n = 64: eta(l = 1) = 0.29-0.47; beta(l = 4) = 2-6e-4; residual RQMC 1.1-1.3x below plain RQMC at 2^12]

## Analyses fixed now
- Medians over nets; per-net values reported; ratios per net. Width trends over n = 64, 128, 256 are descriptive slopes
  except where registered above.
- The single-cut and recursion benchmarks bound the family's bias for the stated projections; they are not ceilings
  for every member of the family and not estimators (B2 is also scored as one at its own cost).
- Exploratory analyses (post hoc) are labelled as such.

## Amendment 1 (width extension to n = 512, L = 64; written and hashed before any run at that width)
Nets: seeds 500, 501, 502 at n = 512, L = 64 (fresh; truths: 2^22 paths in two halves, nMSE floor ~2.4e-7, computed by
scratch/run_w512.py). Runs per net: the truth, scrambled-Sobol RQMC (8 replicates at N = 2^8, 2^10, 2^12, 2^14), ARC k2
'simple', k3f ('none') and D1 variants futmf2_{128, 64, 16}, pca_{128, 64, 16} with the unchanged lib/fa_kprop.py.
Predictions (scored by scratch/score_amend1.py; 256 x 32 values are the Part 1 medians over nets 200-204):
P10 (ARC's order-3 error does not fall with width at fixed L/n): median k3f nMSE at 512 x 64 in [1e-4, 4e-4].
P11 (future-weighted truncation needs k ~ n): median over nets of q_proj(futmf2, n/4) / q_3 >= 0.6 at 512, and median
    q_proj(futmf2, 16) at 512 < its 256 median (q_proj = e_k2 / e_k3p, q_3 = e_k2 / e_k3).
P12 (no growing window): median G_RQMC of k3p(futmf2, n/4) at the registered best-case cost C_ded (PREREG D1) at 512 <=
    its 256 median.
P13 (ARC K = 2 loses ground): median G_RQMC of ARC k2 'simple' at its own cost at 512 < its 256 median.
