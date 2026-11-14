# scale-mode lane pre-registration (written 10:55-11:25Z, 2 November 2026; hashed before any evaluation-net run)

Lane: scale-mode (bead pool-ttdzrk.15). Question: do the two public counter-claims to arc-update's negative (forum topic
18298's "scale mode" law; topic 18198's "covariance propagation decisively beats sampling in Phase 2") escape the
error-cost ladder measured there (gamma = log(n/L)/log n = 0.375 at 256 x 32; sampling has 1)?
Code frozen by sha256 in prereg_hashes.txt together with this file: scripts/{smlib,run_cell,score,score_predictions}.py,
scripts/iso.sh, the eval queues scripts/evalq_{A,B}.sh, and the two third-party files that run
(thirdparty/scale-separation at bfeab38: estimator/lvlib.py, arc_ladder/descale_fac_src.py). Deviations go to
logs/deviations.txt. Sources: notes/SOURCES.md; audit of the third-party code: notes/AUDIT.md.

## 1. What was seen before registration (development; not scored)
- Dev net 9500 at n = 32, 64, 128 (L = n/8; arc-update's dev truths, ARC runs and RQMC): logs/dev_devlad.log. LVTV2 nMSE
  7.9e-4, 6.8e-4, 6.1e-4 at 200, 287, 426 passes (G_MC 6.3, 5.1, 3.8; G_RQ about 2.0, 2.4, 2.6 by my arithmetic);
  SL3 6.3e-5, 8.5e-5, 2.1e-4 at 1.6e3, 6.1e3, 1.9e4 passes; gamma_SL = 1.2, 0.68, 0.28; ARC k3f 9.5e-4, 3.8e-4, 3.7e-4.
- Gate: SL3 with the hook switched off reproduces arc-update's ARC k3f on net 9500 (n = 64) to 6.7e-16 with identical
  FLOPs (runs_dev/gate.json). Timing net (seed 99, 256 x 32, no truth): LVTV2 688 passes (1,325 with flopscope prices for
  ndtr and exp), SL3 83,186 passes.
- The claim's own cell B (64 x 16, its seeds 7064160 + t, rebuilt with ARC's MLP class; my 2^24-path truths):
  logs/dev_claimB.log. My adapter reproduces the claim's FLOP count (3.964e7 vs its 3.96e7) and its headline number:
  10-net mean nMSE 1.517e-3 and MC/x 2.32 in the claim's L+1 accounting (claim: 1.52e-3, 2.31); per net 0.37-3.2e-3.
- Phase 2 public MLP 12 (not in the scored set 0-11): logs/devq_p2.log. ARC k2 = the starter kit's covariance
  propagation to 2.7e-15 (identical estimates); raw final MSE 3.9e-6 (k2, COV), 1.0e-6 (k2a), 1.22e-6 (LVTV2); RQMC
  gain over MC 1.3-1.6 at 2^8-2^16; full-budget RQMC 6.5e-7, MC 1.04e-6.
- DIAG-DEV (logs/devq_diag.log; the claim's cell B nets 0-1 with my truths and RQMC; our dev net 699 at 128 x 32 and
  256 x 64): see section 5.3. K3 at 1024 x 16 on MLP 12: ARC k3f 3.56e-8 raw at 96,968 passes (1.48x the budget in ARC's
  counter; flopscope's 2.24x per the graded entry's docstring); SL3 3.16e-8 at 212,483 passes.
- Identity check on the claim's own cell I net 0 (1024 x 256, seed 8026560): my run of LVTV2 gives V_L = 0.0284 and
  1.199e12 FLOPs; the claim's log has 0.0284 for that net and 1.20e12 (mean); 454 s on 4 threads here.
- Nothing from the evaluation nets below has been run by this lane. Arc-update's results on nets 200-204 and 300-307
  (ARC variants, RQMC) are known to me from its report; those numbers are inputs here, not predictions.

## 2. Evaluation sets
- E1 (Phase 1 shape): 256 x 32, seeds 200-204 (arc-noisy weight stream), truths = arc-noisy's noiseless 2^26-path files.
- E2 (arc-update's ladder along L = n/8): n = 32 (L = 4), 64 (8), 128 (16), seeds 300-307, arc-update's 2^24-path truths.
- E3 (the claim's diagonal L = n/4, fresh nets, our weight stream): 64 x 16 seeds 600-607, 128 x 32 seeds 610-617,
  256 x 64 seeds 620-627, 512 x 128 seeds 630-633, 1024 x 256 seeds 640-643. Truths computed here in two independent
  halves: 2^22, 2^22, 2^20, 2^18, 2^17 paths. Cross-half scoring removes the truth's bias (1/N); what remains is the
  cross term 2 (est - Y).xi, relative SD 2/sqrt(e n_eff N) per net, from ~1% (n_eff = n) to ~14% (n_eff = 4, a deep
  cloud's participation ratio) at 1024 x 256 and e = 3.7e-4 (CPU throughput here is ~50 GFLOP/s per process under the
  machine's load, so larger truths at 512 and 1024 would take hours). RQMC sizes: 2^8-2^14 (n <= 256), 2^8-2^13 (512),
  2^8-2^12 (1024; the claim's cost there is ~2,200 passes). Queue B runs 512 x 128 then 1024 x 256 (net 643 last); a cell or net not finished when the report is
  written is reported as missing (statistics on the nets that finished; a cell with < 3 nets is not scored).
- E4 (Phase 2 shape): the WhestBench public v2-phase2 'mini' MLPs 0-11 (the claim's own challenge nets), 1024 x 16, with
  the dataset's 1e9-sample truths (parquet sha256 7da858bc..., matching Hugging Face's LFS oid). RQMC at 2^16 points
  (the full budget) on MLPs 0-5; on 6-11 up to 2^14, extrapolated to 2^16 with slope -1 (flagged; on dev MLP 12 this
  understates RQMC's measured 2^16 gain, 1.61 against 1.47 at 2^14, i.e. it favours deduction).

## 3. Quantities (score.py)
- nMSE e = |est - Y|^2 / tr Var (E1, E2, E4 against the full truth; E3 cross-half). E4 also raw final-layer MSE
  |est - Y|^2 / n (the contest's metric) and tr Var = n x avg_variance from the dataset.
- Cost C in passes = flops / (2 n^2 L), ARC's NamedFlopCounter; the claim's arms add 1 flop per ndtr element and its hand
  count of scalar special functions (the claim's own accounting). Also recorded: C with flopscope prices for ndtr (96)
  and exp (16) (passes_fs), a sensitivity column only.
- MC at cost C: 1/C. RQMC (scrambled Sobol, 8 replicates; E1/E2: arc-update's runs; E3/E4: N = 2^8, 2^10, 2^12, 2^14,
  and 2^16 on E4): log-log interpolation, slope -1 outside the measured range (flagged).
- G_MC = 1/(C e), G_RQ = RQMC(C)/e (> 1 = the method beats the sampler at its own cost); X_RQ = N at which RQMC reaches e,
  divided by C (the window closes at X_RQ times the method's cost).
- R_ARC = (min e over ARC variants with cost <= C on the same net) / e.
- gamma_{2->3} = log(e2/e3) / log(C3/C2) per net (median over nets): scale-law ladder LVTV2 -> SL3; ARC k2a -> best of
  k3f, k3fa, k3. The uniform-law value is log(n/L)/log n; sampling's is 1.
- Width exponents: slope of log(median over nets) on log n, 95% bootstrap over nets within each width (2000 resamples).
- The multilevel shared-trajectory sampler is not re-run: prior measurements put it at 0.99-1.06x radius-exact MC at
  256 x 32 and at break-even for L <= n/4 (bits-bounds, unrestricted; ideal, setup excluded), so at these shapes it adds
  nothing over MC, and RQMC is the stronger sampler comparator.

## 4. Methods (all CPU, float64 for deduction, float32 forwards for sampling)
- The claim's estimator, run through scripts/smlib.py (lvlib.lvt2_chain unchanged, the claim's frozen numerics R = 24,
  b = 6.5): LVTV2 (exact V rule with the feasibility cap, Gamma s_k: the scored estimator of the claim), LVT (leading-order
  V rule), LVTV2f1 (first-order s_k), LVT0 (V = 0: exact-pair Gaussian closure).
- SL3: ARC's factored K3 SIMPLE (unmodified, 93d091a) with the claim's factored de-scaling hook and the exact Gamma law,
  V from the carried kappa4 trace (sl_fac.py's loop), average metric 2 (our nets are N(0, 2/n) in every layer).
- COV: the starter kit's covariance propagation (example 03), same math in torch. (Dev: identical to ARC k2.)
- ARC variants: arc-update's lad runs on E1/E2 (k1, k2, k2a, k3, k3f, k3fa where present, k4, k4f); here: k2, k2a on E3 and
  E4, k3f on E3 n <= 256 and on E4 MLPs 0-5.
- SL3 runs on E1, E2, E3 n <= 256 and E4 MLPs 0-5. LVTV2 (with its three controls) everywhere; COV on E1 and E4.

## 5. Predictions (scored by scripts/score_predictions.py; each "holds" exactly as stated there)

### 5.1 The claim's own predictions, transferred to our sets (C)
The claim (18298, README/WRITEUP at bfeab38) asserts, on L = n/4: a fit-free K2-cost estimator beats naive sampling at
equal FLOPs at every width; the scale-law ladder improves with order where ARC's inverts; the scale law improves ARC's
factored K3; the estimator beats ARC's best at its compute; the margin narrows with width; and (its own scope note) at
1024 x 16 it is worse than ARC's AUGMENT K2. Registered transfers:
- C1: LVTV2 beats naive MC at its own FLOPs, MC/(mean nMSE) > 1, in every cell of each of: L = n/8 (E1, E2 n = 32, 64,
  128), L = n/4 (every E3 cell run), 1024 x 16 (E4).
- C2: SL3 < LVTV2 on >= 80% of nets, in every set where SL3 runs (E1, E2, E3 n <= 256, E4 MLPs 0-5).
- C3: SL3 < ARC k3f on >= 80% of nets in the same sets.
- C4: on every E3 cell, median R_ARC(LVTV2) > 1 (more accurate than the best ARC variant at <= its cost).
- C5: at 1024 x 16, LVTV2 worse than ARC k2a on >= 9 of 12 MLPs.
- C6: on E3, the width exponent of median G_MC(LVTV2) is < 0 (needs >= 3 widths).

### 5.2 Ours at L = n/8 (P1-P6), calibrated on dev net 9500 (section 1) and arc-update's ladder
- P1a: on E1 (256 x 32), LVTV2 beats RQMC at its own cost (G_RQ > 1) on >= 4 of 5 nets. [dev G_RQ 2.0-2.6 at n <= 128]
- P1b: on E1, RQMC reaches LVTV2's error at <= 5x LVTV2's cost (X_RQ <= 5) on >= 4 of 5 nets: a K = 2-type budget window,
  as arc-update found for ARC k2a (1.6-3.9x). [dev X_RQ 1.8, 2.2, 3.7]
- P2: on E1, at the Phase 1 budget (64,850 passes) RQMC's error is >= 20x below the best scale-law method affordable
  within it (LVTV2, LVT, LVTV2f1; SL3 costs ~83,000 passes) on 5 of 5 nets.
- P3: the scale-law ladder exponent gamma_SL (LVTV2 -> SL3, median over nets) is < 1 at n = 64, 128 and 256, and < 0.6
  at n = 256. [dev: 0.68 (64), 0.28 (128); 1.2 at n = 32, not registered]
- P4: along L = n/8 (n = 32, 64, 128, 256) the width exponent of median G_MC(LVTV2) is < 0. [dev -0.36]
- P5: along L = n/8 the width exponent of median G_RQ(LVTV2) is < 0.5. [dev +0.19]
- P6: SL3 loses to RQMC at its own cost (G_RQ < 1) on >= 4 of 5 E1 nets and >= 6 of 8 nets at n = 128.
  [dev: G_RQ 0.65 at n = 64, 0.13 at n = 128]

### 5.3 Ours on the claim's diagonal L = n/4 (P7), calibrated on the claim's cell B nets 0-1 and our dev net 699
Dev (section 1, DIAG-DEV): RQMC's gain over MC on L = n/4 nets is 1.7-2.6 (64 x 16) and 2.3-2.5 (128 x 32, net 699) at
2^8-2^14 points: a stronger comparator than at 256 x 32. LVTV2's G_RQ at its own cost: 1.2 and 4.7 (claim B nets 0, 1),
0.57 (699 at 128 x 32, where the old rule LVT did 4.5x better than LVTV2); SL3 at 128 x 32: G_RQ 0.044; gamma_SL 0.44.
256 x 64 (net 699, 2^22-path truth): LVTV2 8.3e-4 at 695 passes, G_MC 1.73, G_RQ 1.27, X_RQ 1.25; RQMC gain over MC 1.23,
1.41, 1.44, 2.6 at 2^8, 2^10, 2^12, 2^14; ARC k2 3.8e-3, k2a 4.5e-2 (AUGMENT diverging, as the claim reports at 256 x 64).
- P7a: the claim's margin over naive MC replicates within a factor 2 at every E3 width run (median G_MC(LVTV2) in
  [0.5x, 2x] of the claim's 2.17, 1.52, 1.51, 1.41, 1.21 at 64, 128, 256, 512, 1024, converted to our L-layer pass).
- P7b: against RQMC the margin is at most marginal at n >= 256: median G_RQ(LVTV2) < 1.5 at every E3 width >= 256.
- P7c: the width exponent of median G_RQ(LVTV2) along L = n/4 is < 0.25 (point estimate; >= 3 widths).
- P7d: SL3 loses to RQMC at its own cost on >= 75% of nets at 128 x 32 and at 256 x 64.

### 5.4 Ours at the Phase 2 shape, 1024 x 16 (P8), calibrated on public MLP 12
- P8a: COV and ARC k2 give the same error (to 1e-6 relative) on 12 of 12 MLPs ("plain covariance propagation" is ARC's
  K2 'simple'). [dev: identical estimates to 2.7e-15]
- P8b: COV's mean raw final-layer MSE over the 12 MLPs is in [3.0e-6, 5.5e-6]. [dev 3.9e-6; README ~4.2e-6]
- P8c: COV beats RQMC at its own cost by >= 3x (G_RQ >= 3) on 12 of 12. [dev 6.1]
- P8d: at the full budget (2^16 points) RQMC has a lower raw MSE than COV on 12 of 12, and than ARC k2a on >= 9 of 12.
  [dev: RQMC 6.5e-7, k2a 1.0e-6, COV 3.9e-6]
- P8e: claim (b) holds in the contest's metric: COV's adjusted score (0.1 x raw, its utilisation being 2.35% in
  flopscope) is below full-budget MC's adjusted score (avg_variance / 65,536) on >= 11 of 12. [dev 3.9e-7 vs 1.04e-6]
- P8f: ARC k3f on MLPs 0-5: raw MSE <= 1e-7, >= 5x below full-budget RQMC, and costs > 65,536 passes in ARC's counter
  (unengineered K3 does not fit the budget), on 6 of 6. [dev: 3.6e-8, 18x, 96,968 passes]
- P8g: gamma_ARC (k2a -> k3f), median over MLPs 0-5, is in [0.6, 1.0] (uniform law log 64 / log 1024 = 0.6; arc-update
  measured 0.30 at 256 x 32). [dev 0.81]
- C2/C3 at E4 use SL3 on MLPs 0-5. [dev: SL3 3.2e-8 vs k3f 3.6e-8 raw, at 2.2x k3f's cost]

## 6. Decision rule for the verdict (registered; D in score_predictions.py)
The claim escapes the ladder (major positive) if either
- D1: the scale-law ladder pushes precision about as efficiently as sampling and beats the best sampler beyond the K = 2
  window: gamma_SL median >= 0.9 at n = 128 (E2) and at n = 256 (E1), AND SL3 beats RQMC at its own cost on >= 4 of 5 E1
  nets; or
- D2: on the claim's own diagonal L = n/4, LVTV2 beats RQMC at its own cost (median G_RQ > 1) at every E3 width run
  (>= 3 widths), AND the width exponent of median G_RQ(LVTV2) has a bootstrap 95% lower bound > 0.
Otherwise it does not escape: a K = 2-cost constant factor (a budget window) and a ladder no steeper than ARC's.
If both routes are undetermined (missing runs), the verdict is UNDETERMINED; one false and one undetermined is reported
as "not shown" with the missing part named.
For claim (b): "our negative applies at Phase 2" if full-budget RQMC beats every deductive method run here that fits the
budget in ARC's counter (COV, k2, k2a, LVTV2 family) on >= 10 of 12 MLPs (verdict N2); the K3 rows (P8f, P8g) say what
happens once K3 is engineered into the budget, which the public board shows participants did.
