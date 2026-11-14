<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/adaptive-regions/review/astra_review2.raw -->

The main experimental trends reproduce, but several mathematical claims, numerical guarantees, and labels need revision. Checked read-only on **2026-11-03 at 05:12 UTC**.

1. **Major — Numerical integration materially contributes to the “exact-cell” error.**  
   [cones.py:41](/home/agent/workspaces/mats/work/adaptive-regions/lib/cones.py:41) fixes quadrature at 32 nodes without an error estimate. For **5×4, seed 9702**, I changed only eligible Plackett contributions from 32 to 256 nodes, retaining the other cached contributions: nMSE changed from **2.20e-9 to 1.31e-9**. Individual tested orthant probabilities changed by up to **2.53e-6**. This contradicts the claimed approximately 1e-9 agreement and the attribution exclusively to unseen cells in [the report:203](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:203).  
   **Fix:** add quadrature convergence/error checks, recompute affected caches and tables, and distinguish omitted-cell error from numerical integration error.

2. **Major — The cone library has incorrect degeneracy handling.**  
   [cones.py:118](/home/agent/workspaces/mats/work/adaptive-regions/lib/cones.py:118) treats a nearly singular correlation matrix as zero orthant probability. For a 4×4 equicorrelation matrix with correlation **1−1e-13**, it returns **0**, although the probability is near **0.5**. Separately, row-space reduction leaves `y0` in its original coordinates; `measure([[1,0,0],[0,1,0],[1,1,0]])` raises a dimension error instead of returning **0.25** at [cones.py:177](/home/agent/workspaces/mats/work/adaptive-regions/lib/cones.py:177).  
   **Fix:** handle singular Gaussian support correctly and transform/recompute the interior point after dimension reduction. Add deterministic regression cases. These are reproduced library bugs; their contribution to the saved experiments remains unestablished.

3. **Major — The chain’s “exact iff” statement is false.**  
   [pattern_chain.py:13](/home/agent/workspaces/mats/work/adaptive-regions/scratch/pattern_chain.py:13) gives a sufficient condition, not a necessary one. Define
   \[
   \Delta_{st}=E[h_l1_{\{s_l=s,s_{l+1}=t\}}]-T(t\mid s)m_l(s).
   \]
   With exact incoming means, one-step exactness requires **\(D_tW_{l+1}\sum_s\Delta_{st}=0\)** for every \(t\), rather than every \(\Delta_{st}=0\). Masking, null spaces, and cancellation can remove nonzero discrepancies. Pattern Markovness is also distinct from this conditional-mean condition.  
   **Fix:** replace “iff” with “if,” or state the projected aggregate condition precisely.

4. **Major — Failure of the tested representations is overstated as a general limitation.**  
   Summary 0’s “no summary … carries” claim, [D:112](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:112), A’s scaling conclusion, and [C:290](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:290) exceed the experiments. Testing these means/Gaussians, one greedy tree, and unconverged expert fits does not establish that every pattern-indexed representation fails, that merging cannot improve scaling, or that accurate integration requires exact boundaries. Smooth approximation errors can cancel in the mean.  
   **Fix:** restrict conclusions to the tested methods, budgets, widths, and seeds. Keep the proposed mechanisms explicitly heuristic; do not infer an irreducible bias floor from failed convergence checks.

5. **Major — Section C’s reference means and RQMC budgets contradict the stated comparison.**  
   [step4m.py:168](/home/agent/workspaces/mats/work/adaptive-regions/scratch/step4m.py:168) and [step5m.py:293](/home/agent/workspaces/mats/work/adaptive-regions/scratch/step5m.py:293) use **plain-MC truths**, unlike the report’s opening scrambled-Sobol convention. A4 seed 9701 reports truth noise **1.49e-8**, comparable to its alleged RQMC error **1.05e-8**; Section B’s independent, sharper reference gives approximately **2e-11** for the same RQMC sample count. Furthermore, A4 compares **1,560,576 advice paths with 1,048,576 RQMC paths**; A5 compares **1,024,000 with 524,288**. A5 also normalizes by training-mixture variance.  
   **Fix:** use accurate independent references, report reference uncertainty, normalize consistently, and compare explicitly matched budgets. Count additional real-network suffix evaluations during A5 training separately.

6. **Major — A5’s validation and calibration populations participate in training.**  
   Although [step5m.py:194](/home/agent/workspaces/mats/work/adaptive-regions/scratch/step5m.py:194) reserves population indices, the pointwise loss samples from **all** `allH` rows at [step5m.py:216](/home/agent/workspaces/mats/work/adaptive-regions/scratch/step5m.py:216), including validation and calibration populations. These are therefore not wholly held out as claimed. Also, different fitted scales across different K models do not, by themselves, prove covariance *shape* error.  
   **Fix:** split populations before supervised fitting, exclude validation/calibration pairs from every training loss, and rerun stopping/calibration checks. Describe the current coverage results as empirical miscalibration without claiming its cause is identified.

7. **Major — Sampled plateaus do not establish exact ray collapse or complete cell counts.**  
   [Section E:144](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:144) promotes empirical participation ratios and sampled patterns into global geometric statements. In the recorded output, **8×24 seed 9701 still has five patterns and increasing cell counts**. Seed 9702 plateaus at **38,264 cells over depths 17–21**, then grows to **38,840 at depth 22**. Even two patterns can coexist with multiple output directions. Likewise, D’s “ever occur” language is stronger than counting patterns in a finite sample.  
   **Fix:** say “observed prefix-cell plateau” and “near rank-one sampled second moment.” Certify all relevant cone images before claiming exact collapse or identically zero output. Retain \(4^n\) only as a conjecture about the specified quantity.

8. **Minor — “Rank about 3n” means an energy approximation, not matrix rank.**  
   The calculation at [pattern_chain.py:100](/home/agent/workspaces/mats/work/adaptive-regions/scratch/pattern_chain.py:100) correctly measures 99%-energy rank. My reproduction gives **algebraic rank 75 versus energy rank 24** for n=8, seed 9701, and **101 versus 29** for seed 9703; both matrices have full column rank. Similarly, greedy entropy selection measures retained predictive information, not deterministic dependence on a minimal set of parent bits.  
   **Fix:** retain “99%-energy effective rank” in Summary 0, compare against both matrix dimensions, and describe bit counts as in-sample greedy conditional-entropy diagnostics. State that the first-transition non-Markov gap is zero.

9. **Minor — “Irrelevant units” are units freezable to one chosen setting, with a zero-variance failure case.**  
   [pattern_chain.py:277](/home/agent/workspaces/mats/work/adaptive-regions/scratch/pattern_chain.py:277) takes the **minimum** of forcing on/off. For 4×4 seed 9701, one counted unit has zero effect when forced on but **0.215 nMSE** when forced off. Moreover, the dead 4×12 seed-9703 network divides by zero variance and records NaNs and **zero irrelevant units**.  
   **Fix:** call these “empirically freezable gates,” save both intervention effects and uncertainty, and handle zero-variance networks using absolute errors or an explicit undefined-normalization status.

10. **Minor — “Distinct maps” actually counts terminal tree leaves.**  
    [summarize_tree.py:32](/home/agent/workspaces/mats/work/adaptive-regions/scratch/summarize_tree.py:32) prints `final_leaves` as distinct maps. Direct deduplication of cached matrices gives **309 rather than 320** for 5×4 seed 9702, **148 rather than 149** for 4×4 seed 9703, and **2,473 rather than 2,481** for 6×4 seed 9701.  
    **Fix:** count unique cached maps directly, and report terminal leaves separately.

11. **Minor — The tree accuracy threshold and “first point” labels are inaccurate.**  
    [cone_tree.py:179](/home/agent/workspaces/mats/work/adaptive-regions/scratch/cone_tree.py:179) uses **\(2\,err_{\rm exact}+truth\_noise\)**, whereas the tables say “2× exact error.” For 4×4 seed 9703, the saved curve reaches these thresholds at **123 and 126 leaves**, respectively. The curve also omits some intermediate leaf counts, and the threshold is selected using the evaluation truth.  
    **Fix:** print the actual threshold and say “first recorded crossing, selected retrospectively,” or record every split and define an independent stopping rule.

12. **Minor — The hybrid estimator can silently omit a nonempty residual.**  
    At [exact_hybrid.py:100](/home/agent/workspaces/mats/work/adaptive-regions/scratch/exact_hybrid.py:100), residual masks are replaced with zeros whenever a separate finite sample estimates residual mass as zero; the RQMC branch repeats this. Missing a rare residual in that sample does not make it empty, so the advertised unbiased MC correction fails in that case.  
    **Fix:** always evaluate membership on the fresh residual samples. This branch does not invalidate a run whose measured residual mass is positive.

13. **Major — The quoted hybrid experiment is not auditable from the cited outputs.**  
    [Section B:250](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:250) quotes a completed 4×4 seed-9701 hybrid curve, but the reviewed `runs/` and `logs/` contain no corresponding result; the hybrid log present is the interrupted n=6 run. The paragraph also omits the hybrid-RQMC curve needed to support its explanation about lost QMC smoothness. Its comparison charges residual samples while omitting the million-path discovery budget.  
    **Fix:** supply the saved four-way MC/RQMC/hybrid-MC/hybrid-RQMC results and label marginal versus total-budget comparisons explicitly. Until then, mark the quoted experiment unverified.

14. **Minor — Section C omits completed results that qualify its wording.**  
    [step4m seed 9703](/home/agent/workspaces/mats/work/adaptive-regions/runs/step4m_n4_L4_s9703.json) has another checkpoint between MC and RQMC: **K=256, error 1.74e-7**, versus MC **6.40e-7** and IS **3.87e-7**. Thus “once” is false, although its doubling check fails badly. Completed A5 records also include seed-9701 **K=256, error 7.33e-5**, and seed-9702 K=4/16.  
    **Fix:** include all completed results, distinguish completed from interrupted configurations, and conclude “no stable advantage demonstrated.”

15. **Minor — Several descriptive numbers and dimensional statements need correction.**  
    Recomputing [depth_saturation.json](/home/agent/workspaces/mats/work/adaptive-regions/runs/depth_saturation.json) gives geometric means approximately **260, 885, 4,209, 29,457, 60,799**, rather than 257, 873, 4,264, 29,400, 62,600. Tree decision-depth fractions span **25.9–42.8%**, not uniformly 35–45%; moment-check pass rates reach only **93.6%**, not uniformly 95–99%. The cited logs show **879/734 ≈1.20 seconds per cell** at n=5 seed 9701 and **8,847/2,524 ≈3.51 seconds** at n=6 seed 9701. Finally, dropping redundant constraints does not itself reduce orthant dimension as claimed at [B:247](/home/agent/workspaces/mats/work/adaptive-regions/adaptive-regions.md:247); reducing row-space rank does.  
    **Fix:** generate summaries from saved outputs, identify timing conditions, and state the dimensional reduction correctly.

**Verdict:** The observed failure of these chain approximations and the rapid growth of sampled gate-prefix counts are supported; representative order-k calculations reproduced, Gaussian-split resolution checks preserved the failure, and all 18 current cone tests passed. The facet formula is correct with inward unit normals, the Plackett identity and arcsine substitution are correct, and the first-layer \(2^n\) claim holds almost surely for square Gaussian weights. However, the tests do not certify the claimed numerical precision, and the report needs substantial revision before its exact-error attribution, baseline comparisons, saturation mechanism, or broader impossibility claims are reliable. No files were written.
