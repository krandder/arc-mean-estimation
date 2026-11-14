**Verdict: major revision, concentrated in cost accounting.** The missing H1 cross term is fixed, the reported scores reproduce, and most round-2 corrections are complete. However, the D1 optimistic extraction scenario assumes Cholesky on states that are indefinite, while H1’s “full ledger” still charges per-sample matrix multiplications that v2 eliminates. These affect the headline equal-cost interpretations.

Checked read-only on **2026-11-02**. Report SHA-256: `65b06768a9fff34376fbea28901f8ed98ca2619544ec850a0b428b35a510c09d`. I recomputed from saved runs, regenerated the scoring artifacts entirely in memory, and reran one D1 case with diagnostic instrumentation. No files were modified.

The disposition of the 15 findings carried forward into round 2 is:

| # | Status | Assessment and remaining problem |
|---|---|---|
| 1 | **Resolved** | The predictable radius term, positive-degree restriction, and fixed-defect/additive-correction assumptions remain explicit. |
| 2 | **Resolved** | Failure of annealed-price domination is separated from the open computational lower bound; conditional pricing survives. E15 supersedes the historical overstatement. |
| 3 | **Resolved** | The unsupported \(q\le n/L\) claim is explicitly superseded in E15. The report retains the uniform-law and cost/comparator hypotheses. |
| 4 | **Resolved** | The summary now includes the polynomial-reading qualification and distinguishes the series-free identity. The general mechanism is labelled HEURISTIC and restricted to tested representations. |
| 5 | **Resolved** | T2 now distinguishes raw, literal, and historically floored statistics. Both numerator and denominator receive the literal P3 truth-floor check. |
| 6 | **Partly resolved** | §4.2 correctly gives success counts, successful-case medians, individual variation, and guarded failures. But §6 item 4 still says the half-width median is better than k3 without the survivor qualification; the completed mean-field \(n=256\) median is **0.919652**, below 1. |
| 7 | **Resolved** | Paired ratios and retained factors remain correctly defined and reproducible. |
| 8 | **Partly resolved** | The finite-algorithm target and descriptive three-width interpretation are now clear. Additional particle/pilot replicates and uncertainty estimates remain absent, as §7 acknowledges. |
| 9 | **Resolved** | Diagram costs remain explicitly assumed scenarios, not lower bounds. This does not validate the separate, newly added extraction scenario discussed below. |
| 10 | **Partly resolved** | The ledger is substantially improved, but “full”/“all its work charged” remains unjustified. D1’s Cholesky scenario is inapplicable to observed states, and H1 retains obsolete evaluation charges. |
| 11 | **Resolved** | Direct hybrid estimates are scored against \(Y\), including the formerly omitted cross term. |
| 12 | **Resolved** | Mixture scaling remains unmeasured, uniform control exponents are “not established,” and the unsupported “smaller still” sentence is removed. |
| 13 | **Resolved** | Hybrid extrapolation is eliminated; comparator extrapolation is labelled; sensitivity calculations are supplied and reproduce. One sensitivity-summary range needs a small correction below. |
| 14 | **Resolved for the previously identified corrections** | The earlier cut, particle, order-4, and spectrum corrections remain applied. Further wording/numerical issues are listed below. |
| 15 | **Resolved for the round-2 requirements** | The report separates original, amended, and corrected results and appropriately limits what hashes/timestamps establish. Guarded P7 results should continue to be identified as a changed, post-hoc algorithm. |

The six additional round-2 issues have the following status:

| Round-2 issue | Status | Assessment |
|---|---|---|
| 1. Invalid H1 error sum | **Resolved** | Actual hybrid errors are now stored and scored. Cost interpretation remains a separate problem. |
| 2. Correction scripts overwrite the scorer on import | **Resolved** | They use side-effect-free helpers. In-memory execution attempts only their intended output writes. |
| 3. Conflicting supplementary statistics | **Resolved** | Raw/literal/floored columns and the historical H1 metric are labelled. The numerator-floor omission is fixed. |
| 4. Half-width accuracy overstatement | **Partly resolved** | Corrected in §4.2, but an unqualified version remains in §6 item 4 and conflicts with the completed guarded results. |
| 5. Unsuperseded FORMAL statements | **Resolved** | E15 explicitly supersedes the named unconditional-extension and \(q\le n/L\) statements. |
| 6. Three smaller claims | **Resolved** | The order-4 range, 78–91% retained range, and cost-exponent sentence are corrected. |

The direct H1 scoring is mathematically correct. In [run_hyb_direct.py](/home/agent/workspaces/mats/work/future-aware/scratch/run_hyb_direct.py:159), the quantity squared is precisely
\[
E_Q[c]+\frac1N\sum_i\bigl(h_L(x_i)-c(h_l(x_i))\bigr)-Y.
\]
Across the saved records, I verified
\[
\texttt{dir\_eg}=\texttt{old}+\beta_{\rm eg}+\texttt{cross}
\]
to maximum absolute discrepancy below \(10^{-17}\).

The control construction and seed formulas match `run_hyb.py`. Maximum relative discrepancies across all three widths were approximately \(1.00\times10^{-8}\) for eta, \(2.78\times10^{-9}\) for beta, and \(2.70\times10^{-8}\) for the old residual metric. Thus the report’s \(3\times10^{-8}\) reproduction statement is supported.

V2 is algebraically equivalent to v1: each control is linear in \(h_l\) and, where applicable, its quadratic features. Summing these sufficient statistics before applying the fitted matrices gives the same estimator, up to floating-point rounding. The rewrite fixes evaluation speed without changing the intended estimate.

These independently recomputed §4.3 quantities agree with the report:

| Quantity | \(n=64\) | \(n=128\) | \(n=256\) |
|---|---:|---:|---:|
| First-layer quadratic eta | 0.319 | 0.447 | 0.546 |
| First-layer quadratic hybrid/plain error at \(2^{16}\) | 0.810392 | 0.882151 | 0.965542 |
| Best gain at 10,000 passes, registered ledger, same-scramble curves | 0.845688 | 0.865566 | 0.849640 |
| Best gain at 65,000 passes, registered ledger, same-scramble curves | 0.957423 | 0.979718 | 0.977130 |
| Best gain at 10,000 passes, stated full ledger | 0.840919 | 0.853544 | 0.821300 |
| Best gain at 65,000 passes, stated full ledger | 0.957008 | 0.978309 | 0.973820 |
| Best gain at 65,000 passes against arc-update’s curve | 0.990310 | 0.729092 | 0.999572 |
| Median per-net minimum deeper beta | \(6.82935\times10^{-5}\) | \(8.87498\times10^{-5}\) | \(2.60169\times10^{-4}\) |

The last row takes the minimum across eligible controls/layers **within each net**, then the median across nets. That aggregation reproduces the table.

No hybrid curve is extrapolated: the scorer rejects \(N\) outside its measured interval, and the extended grid reaches \(2^{16}\). The same-run plain comparator also covers both budgets. Arc-update’s 65,000-pass comparisons at \(n=64,128\) still require the disclosed extrapolation. Equal-cost values remain log-log interpolations, rather than simulations performed at those exact budgets; “same scrambles” describes the paired measured endpoints.

The remaining substantive findings are:

1. **D1’s optimistic extraction scenario cannot use ordinary Cholesky on the measured states.**

   [d1_ledger.py](/home/agent/workspaces/mats/work/future-aware/scratch/d1_ledger.py:7) proposes Cholesky whitening plus a randomized range finder at
   \[
   \frac{(L-1)\,[n^3/3+12n^2(k+10)]}{2n^2L}
   \]
   passes. The matrix-product arithmetic is a plausible optimistic starting point **for positive-definite states**, but that condition fails here even at quarter width.

   I reran **\(n=128,L=16,\text{seed}=304,\texttt{futmf2\_32}\)**. Its nMSE reproduced the saved value:
   \[
   0.000377692097065432
   \quad\text{versus}\quad
   0.000377692097065428.
   \]
   Cholesky failed at **every layer from 5 through 15**. Layer 5 had minimum eigenvalue \(-1.22925\times10^{-4}\); layer 13 had **33 nonpositive eigenvalues** and minimum \(-0.00453428\).

   This is a successful quarter-width run used in the proposed window, not merely one of the failed half-width runs. A repair must specify how to handle indefinite \(S\), charge that work, and establish whether the resulting directions preserve the measured accuracy. Ordinary Cholesky of a regularized matrix does not automatically reproduce the current positive-part spectral construction.

   The randomized formula also does not separately enumerate orthogonalization, the reduced eigensolve, or mapping/normalizing the resulting features. Those may fit a deliberately optimistic allowance, but it is not an established accounting of **all** required work.

   The dense \(26n^3\)-per-layer allowance is reasonable as an approximate scenario, not a measured exact flop count. Both scenarios’ reported arithmetic reproduces:

   | \(n\) | Randomized / dense extraction passes | Total cost including pilot, randomized / dense | Gain, randomized / dense |
   |---|---:|---:|---:|
   | 64 | 145.833 / 728 | 525.036 / 1107.203 | 1.285593 / 0.490536 |
   | 128 | 256.250 / 1560 | 1042.852 / 2346.602 | 1.464870 / 0.665280 |
   | 256 | 471.458 / 3224 | 2217.759 / 4970.301 | 1.315338 / 0.534924 |

   **Required correction:** retain these as assumed-cost arithmetic, but withdraw the claim that the optimistic row charges all the work of a currently specified feasible extraction method. Either supply a suitable algorithm and its costs or explicitly add the missing feasibility/accuracy assumptions.

2. **H1’s “full ledger” does not price v2’s evaluation.**

   [score_hyb_direct.py](/home/agent/workspaces/mats/work/future-aware/scratch/score_hyb_direct.py:84) still imports the old per-sample multiplier `a`. For a linear control this is \(1+1/L\), charging an \(n\times n\) matrix-vector multiplication for every sample.

   But [v2](/home/agent/workspaces/mats/work/future-aware/scratch/run_hyb_direct.py:147) accumulates \(h_l\) and applies the matrix once. Its additional evaluation work is approximately \(Nn+2n^2\), rather than \(2Nn^2\). The quadratic version similarly avoids applying the output regression matrix per sample.

   This matters near gain 1. Keeping the report’s entire “full” setup charge unchanged, and changing **only** the first-layer linear evaluation charge to \(Nn+2n^2\), I obtain:

   | Fixed `1/jacmf` control, same interpolation | \(n=64\) | \(n=128\) | \(n=256\) |
   |---|---:|---:|---:|
   | Gain at 10,000 passes | 0.939352 | 0.908284 | 0.841140 |
   | Gain at 65,000 passes | **1.031617** | **1.020054** | 0.997136 |

   These are accounting sensitivities, not statistically established positive results. They do show that “the hybrid loses” is sensitive to a cost that the revised implementation has already eliminated.

   There are smaller ledger inconsistencies too: `jacmf` setup already includes the full Gaussian recursion, yet the scorer adds the layer-\(l\) Gaussian closure cost again; and the `k2` scoring branch uses the same Gaussian-based setup budget regardless of its mean source.

   **Required correction:** preserve the registered ledger as a historical cost model, then add a ledger for the sum-based implementation. Call the present added-cost version an expanded ledger rather than “full” until its allowances, omissions, and reuse assumptions are reconciled.

3. **The closing half-width recommendation conflicts with the newly completed data.**

   [§6 item 4](/home/agent/workspaces/mats/work/future-aware/future-aware.md:555) says the half-width median is slightly better than k3. With guarded failures included, the \(n=256\) medians are **1.045875 for VJP** and **0.919652 for mean-field**. The latter beats k3 on only **2/5 nets**.

   The earlier successful-only mean-field value, 1.19, came from one net. Use the completed results in the recommendation or explicitly say “among the originally successful runs.” The parenthetical PCA result does not qualify a claim about future/mean-field directions.

4. **Several smaller statements need narrower labels or numerical corrections.**

   - §4.3 says the best hybrid at each budget is the first-layer mean-field control. It is the **best fixed control**, but at \(n=256\), seed 202, budget 10,000, the per-net winner is **`2/jacmf`**. The reported best-per-net median is **0.849640**, whereas the best fixed-control median is about **0.840**. Preserve that distinction.
   - §4.4’s sensitivity sentence says implemented D1 “stays 0.035–0.061.” That covers \(n=128,256\); \(n=64\) is **0.120927**, unchanged because it needs no extrapolation.
   - The repeated “5–200×” D1 loss statement should identify an approximate range of **variant medians**, not individual runs. For example, a registered projected run at \(n=64\) loses by only **2.25×**, while another at \(n=128\) loses by **336.69×**.
   - The \(n=64\) mean-field half-width retained median is **1.134661**, so §4.2’s prose should use **1.13**, matching its table, rather than 1.14.
   - For the new order-4 seed-300 run, \(e_3/e_4=\mathbf{1.649152}\); “1.65” avoids the report’s upward double-rounding to 1.7.
   - The six guarded reruns verify agreement on **six sampled registered successes**, not every registered success.

The new guarded results otherwise reproduce: all 12 previously failed records are finite, six successful-case reruns agree within \(4.62\times10^{-14}\) relative error, and the two severe \(n=256\) divergences plus the poor mean-field seed-202 result are disclosed. This supports numerical fragility, not a general accuracy rescue.

The new order-4 comparisons also reproduce. For seeds 300–302, errors relative to full k4 are:

| Projection | Seed 300 | Seed 301 | Seed 302 |
|---|---:|---:|---:|
| Both cores, \(k=16\) | 2.01855 | 9.36150 | 1.11562 |
| Both cores, \(k=32\) | 0.84894 | 2.02410 | 0.76074 |
| Fourth core only, \(k=16\) | 0.28621 | 0.85338 | 0.55361 |
| Third core only, \(k=16\) | 2.99931 | 10.27780 | 1.28733 |

The bottleneck interpretation is supported as an exploratory observation on these three nets. Summary wording should retain that limited scope; a requirement for half the directions is not uniform across these cases.

I regenerated `score_part1`, both correction outputs, `tables_part1`, `hyb_direct`, `d1_ledger`, `extrap_sensitivity`, `guard`, and `comparator_noise` **byte-for-byte in memory**. Thus the outstanding issues are not stale generated artifacts. The comparator-noise calculation reproduces, but its “roughly ±40%” description is not a confidence interval, and paired comparisons do not remove interpolation, finite-truth, or control-selection uncertainty.

The summary now correctly limits the theoretical and width claims, includes the polynomial qualification, and identifies the unbuilt implementations and post-hoc analyses. It still overstates the cost evidence through **“all its work charged,”** treats near-unity H1 losses too definitively, and leaves the half-width survivor qualification out of the closing recommendation. **“No major positive demonstrated over the tested widths” remains supported; the specific all-work D1 window and blanket hybrid-loss claims need revision.**
