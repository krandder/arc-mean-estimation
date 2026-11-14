<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/arc-update/review/review_gpt6.raw -->

**Verdict: major revision.** The corrected finite-width pricing identities are defensible, and the principal numerical results reproduce. The report repeatedly turns those identities and measurements into broader lower bounds, ceilings, and asymptotic conclusions that they do not establish.

Read-only audit completed on 2026-11-02 at 09:36 UTC. I checked the report, FORMAL additions, three co-prover answers, source quotations, preregistrations, measurement code, scorers, and selected underlying results. No files were modified.

1. **Major — Sections 6–7 overstate the negative conclusion.**  
   Theorem A prices a specified model discrepancy; it does not establish that every affordable representation has a large discrepancy. A4 bounds approximation error under a rank constraint, not storage or computational cost. A5 avoids a cancellation hypothesis only by examining the final model, whose discrepancy still needs a lower bound. Consequently, “must reproduce, at every early layer,” “every family loses,” and “keeping the MSP … requires naming a non-layer-wise mechanism” do not follow. Forward-only estimators can have cancelling defects, and implicit representations need not store dense tensors.

   **Fix:** Restrict the conclusion to the tested implementations and the explicitly conditional separation results. Preserve future-aware, implicit, alternative-projection, and other untested layer-wise methods as unresolved possibilities.

2. **Major — The uniform-law argument is valid conditionally, but is not implied by ARC’s conjecture.**  
   [Section 2.5](/home/agent/workspaces/mats/work/arc-update/arc-update.md:178) correctly introduces additional lower bounds. ARC supplies **upper** error and runtime bounds with order-dependent constants. Neither supplies uniform positive lower bounds on error or cost. Measurements at orders 2–4 cannot establish uniformity over the growing orders needed for an all-precision conclusion.

   The displayed budget inequality also requires \(n>1\) and \(0<L/n<1\); its monotonicity argument does not extend unchanged to \(L>n\). It proves an error lower bound, not the equality suggested by “falls like \(C^{-\gamma}\).”

   **Fix:** Say “under an additional uniform lower error-and-cost law, the hierarchy cannot decay faster than this bound.” State the domain, applicable variants, and uniformity in both order and width where width-asymptotic conclusions are drawn. Replace “ARC’s own law already implies it” throughout.

3. **Major — The degree-42 mechanism is transferred from infinite width without justification.**  
   The infinite-width table and corrected mean-degree identity reproduce. Its \(t^{-2}\), \(t^{-3}\), and conditional-mean-degree asymptotics are consistent with the cited derivation. However, the summary and sections 5–7 describe degree \(\sim40\) as a property of the actual \(256\times32\) future. Only finite-width \(b_0\) was measured; finite-width \(b_1\), quantiles, and conditional mean degree were not.

   The difference is material: \(b_0^{(256,31)}=0.94817\), versus \(0.97342\) at infinite width. Moreover, the asymptotic cubic lower-bound expression at \(n=256,\beta=1/8\) is \(0.00011284\), while the infinite-width cubic coefficient at \(t=31\) is \(0.00194148\). Thus “more than the infinite-width table gives” is not established at this architecture by that bound.

   **Fix:** Label degree 42 and \(t^2\) growth as infinite-width results everywhere. Measure the finite-width spectrum before assigning those numbers to ARC’s instance. Distinguish coefficient weights from actual error contributions \(b_d\|M_d(\Delta)\|^2\).

4. **Major — Section 2.4 strengthens several conditional/asymptotic results beyond their proofs.**  
   [The one-replacement claim](/home/agent/workspaces/mats/work/arc-update/arc-update.md:155) says Gaussianisation “anywhere after layer 1.” Round 2, equation (26), proves replacement **immediately after the first layer**, followed by an arbitrary-depth exact suffix. It does not prove the same constant for replacement at any later cut.

   Likewise, round 3 proves
   \[
   b_3^{(n,t)}\ge\frac{e^{-5\beta/4}+o(1)}{3\pi^2n},
   \qquad
   \liminf n^2\,\mathbb E\|e\|^2
   \ge\frac{e^{-5\beta/4}\gamma_3^2}{3\pi^2}.
   \]
   The report drops the asymptotic qualifications. The latter constant is for **absolute squared error**; transferring it to annealed normalized error requires a variance bound, such as division by \(C_*\). The lognormal \(O(n^{-3/2})\) radius claim additionally requires radial extensivity and Taylor-remainder control, omitted from the report’s local statement.

   **Fix:** Restore the precise cut, liminf/\(o(1)\), normalization, and hypotheses. Keep the first-layer shell result conditional; retain the separate full-recursion transfer hypothesis and the full \(H_{\rm cap}\), including its kernel convergence and positive limiting discrepancy.

5. **Major — The declared theorem coverage still conflicts with the corrected reconstruction result.**  
   Section 2.1 says the model contains ARC’s cumulant propagation “of every order and variant” through a Gram–Charlier reconstruction. Section 2.2 correctly says the default averaged-metric `augment` and higher-order implementations lack that reconstruction.

   My inspection agrees with the narrower result: A2 is sound for integrable signed measures; A4 is sound for symmetric tensor reconstructions; A5 is sound for an exact model-based final step. Averaged-metric corrections generally violate the positive homogeneity required of a fixed-measure ReLU expectation. The variance floor also prevents a globally exact identity for actual `simple`, although its effect here is tiny.

   **Fix:** Separate coverage by the broad state-update model from coverage by the signed-measure pricing theorem. State the last-row certificate separately; its existence does not establish a substantial error floor.

6. **Major — The cell-count argument confuses representation distortion with mean-estimation error.**  
   [Section 2.6](/home/agent/workspaces/mats/work/arc-update/arc-update.md:196) compares \(2^{45}\) cells with roughly ten samples. The cited bits-bounds report explicitly qualifies those results: the 224/112/45-bit figures are model-based estimates, the geometric lower-bound hypotheses are not established globally for these networks, and the cell theorem is a representation separation, **not a mean-estimation separation**.

   Section 5’s own tower-property observation explains the problem: exact conditional means make every partition mean-exact, including a one-cell partition.

   **Fix:** Remove the cell-count-versus-sample-count inference about estimating the mean. Retain the figures only as representation diagnostics, unless an integration lower bound with controlled cross-cell cancellation is proved.

7. **Major — The oracle radial-Gaussian is not a ceiling on deductive closures.**  
   [Section 4.4](/home/agent/workspaces/mats/work/arc-update/arc-update.md:385) says the measurements “bound what any version can do.” They evaluate particular projections, not the infimum over Gaussian-direction models, radial couplings, or deductive estimators. Exact input moments do not guarantee that a moment-matched projection minimizes output error. Radial transport also changes mean and covariance.

   Further, the implementable \(O(Jn^3)\) construction uses an **independent** lognormal radius and Gaussian direction. The measured monotone transport preserves a different radius–direction coupling. Its measured error cannot simply be paired with the independent-radius construction’s cost.

   **Fix:** Call these “specified oracle-projection benchmarks,” not ceilings or universal floors. Separate the two model definitions and charge an implemented, accuracy-controlled update before claiming an achievable gain.

8. **Major — The full-recursion experiments do not measure exact-moment closure bias.**  
   [The report](/home/agent/workspaces/mats/work/arc-update/arc-update.md:417) upgrades the scripts’ more careful “noise-averaged closure” target to “exact per-layer moments.” For independent stochastic recursions,
   \[
   \mathbb E[(\widehat\mu_A-Y)\cdot(\widehat\mu_B-Y)]
   =\|\mathbb E\widehat\mu-Y\|^2.
   \]
   This does not equal the squared error of the deterministic infinite-sample recursion: nonlinear updates can introduce systematic finite-sample bias.

   Amendment 6 adds another approximation. [Its transport](/home/agent/workspaces/mats/work/arc-update/scratch/run_ipr2.py:49) uses ranks within fixed batches of \(2^{14}\). Increasing total samples while keeping that batch size fixed does not recover the population monotone transport automatically.

   **Fix:** Relabel the results as finite-sample stochastic-recursion measurements. Establish convergence in both total samples and transport batch size, with multiple independent repeats, before claiming exact-moment closure errors.

9. **Major — The width exponents do not support the asserted asymptotic conclusions.**  
   At three geometrically spaced widths, the fitted log–log slope is determined by the two endpoints. The measured \(p(Z_m)=0.673\) does not establish decay slower than \(1/n\). A descriptive bootstrap over the existing networks gives an approximate 95% interval of **0.60–1.23**, even before accounting for each network’s integration noise.

   Normalization also matters. Replacing medians of per-net nMSE with the empirical annealed ratio changes the first-cut radial exponent from **2.477 to 1.781**; its \(n=256\) value changes from \(3.29\times10^{-6}\) to \(1.02\times10^{-5}\). Agreement between normalizations for two Gaussian recursions does not establish agreement for this measurement.

   Finally, \(W_r(256)/W_r(64)=1.402\) is compatible with positive polynomial growth; P18’s threshold of 2 permits an exponent of \(1/2\).

   **Fix:** Report finite-range descriptive slopes with uncertainty and both normalizations. Delete “neither grows polynomially” and claims that these fits establish \(H_{\rm cap}\) or a width-independent advantage.

10. **Major — Amendment 5’s replacement is disclosed, but the scorecard and combined inference mishandle it.**  
    The stopped run is documented honestly: net 200 has radial cross-product \(-1.915\times10^{-4}\) and estimated replicate noise \(1.827\times10^{-3}\). Amendment 6 was registered before its runs. However:

    - P19 is marked HOLDS after only one of five registered networks.
    - P20–P23 show mechanical pass/fail labels despite being undetermined.
    - P24–P26 are marked HOLDS from three of five networks in the saved score snapshot.
    - P27–P28 show FAILS when the necessary runs were incomplete.
    - The scorecard ignores Amendment 6’s `valid` flag when displaying conclusions.
    - The \(1/n\) full-recursion trend combines Amendment 5 at widths 64/128 with Amendment 6 at 256.

    **Fix:** Use explicit pending/undetermined states and sample counts; enforce validity gates. Finish the same transport at all widths before fitting its scaling. Recompute the “30 of 34” tally accordingly. Net 203 completed during this review, so subsequent summaries should identify their input snapshot.

11. **Minor — P1/P5 aggregation and P3 scoring differ from the preregistered wording.**  
    [PREREG’s definition](/home/agent/workspaces/mats/work/arc-update/PREREG.md:41) naturally specifies the median of each network’s best variant. [The scorer](/home/agent/workspaces/mats/work/arc-update/scratch/score_prereg.py:25) computes the best variant’s median instead. For \(G_2\), the former gives **8.805, 5.056, 4.648, 2.979**, rather than **8.060, 4.791, 3.940, 2.630**.

    P3 requires a crossover-cost ratio; the scorer uses gain at the method’s own cost. Direct inversion of the registered RQMC curves gives **1.869, 1.663, 3.913, 1.621, 1.907**. Thus P3 holds on **five of five**, rather than four under the proxy. These corrections do not reverse the main prediction outcomes.

    **Fix:** Implement the literal registered statistics and retain the old outputs as a documented scoring correction. Also enforce the registered resolution filter; all 209 existing ladder rows currently pass it.

12. **Major — The oracle-defect uncertainty is understated.**  
    `run_attr.py` shares estimated covariance, target radius quantiles, and the pilot Gaussian CDF between push halves. Its cross-product removes independent push noise, but retains shared-model estimation error. Amendment 4 improves independence, yet neither procedure establishes the exact oracle target without a convergence analysis.

    At width 256, the first-cut radial cross-products are approximately **20.18, 9.45, 3.29, −1.85, 1.08**, in units of \(10^{-6}\). Corresponding half-difference-based noise estimates are **0.70, 2.73, 0.94, 8.94, 4.76** in the same units. Several observations are therefore poorly resolved. Taking a maximum across noisy cuts, as in R2/R3, also introduces selection bias relative to the maximum of the underlying defects.

    **Fix:** Add independent cloud/pilot replicates and uncertainty intervals. Distinguish push-noise debiasing from projection-estimation bias. Describe radial transport’s effect as a before/after intervention, not an orthogonal “radial share” of error.

13. **Minor — Rank and capture statistics support descriptive structure, not certified compression costs.**  
    The split-block construction in [au.py](/home/agent/workspaces/mats/work/arc-update/lib/au.py:205) provides useful held-out numerators. Its PR numerator is upward biased; replacing it by the independent trace product does not make the resulting ratio unbiased. Capture ratios are likewise biased, and the shared estimated truth mean is not exact centering.

    The supplied correction barely changes net 200’s layer-16 PR: **4.050819 → 4.050158**. P9b therefore still fails mechanically, but the narrow threshold crossing has no uncertainty assessment. High flattening PR does not imply expensive implicit representation; low PR alone does not establish cheap accurate propagation.

    **Fix:** Keep both PR versions, add repeat-based uncertainty, label P9a/P9c partial until their registered sample is complete, and remove computational conclusions drawn from PR alone.

14. **Minor — “Best attainable precision” and pending higher-order claims exceed the tested coverage.**  
    P11 compares different order caps: \(K\le4\) below width 256, but \(K\le3\) at width 256. The registered `k3fa` runs at 256 were also missing. The statement that they could improve precision “but not the order-3 gains” is unsupported: sufficiently improved accuracy could compensate for greater cost.

    **Fix:** Say “smallest error among completed variants.” Report a common-order comparison across widths and leave gains involving unfinished variants unresolved.

15. **Minor — Some RQMC comparisons labelled MEASURED are extrapolations outside the measured range.**  
    RQMC was measured from 256 samples upward. [The scorer](/home/agent/workspaces/mats/work/arc-update/scratch/score_lad.py:40) extends a \(1/N\) curve downward to approximately one pass for `k1` and to several small-width closure budgets. PREREG explicitly specifies extrapolation beyond the **largest** sample size, not this downward extension.

    At one scrambled-Sobol point, the input has the Gaussian marginal and expected normalized error is 1. The extrapolated curves instead imply values around 0.62–1.03. Thus the means-only “16–90× over RQMC” comparison is not directly measured.

    **Fix:** Label extrapolated comparisons and register the extension, or measure the small budgets. Keep the contest-budget comparison, which lies within the measured range.

16. **Minor — ARC quotations are largely fair, but the interpretation omits relevant qualifications and alternatives.**  
    The quoted depth limitation, open problem, upper-bound conjecture, and sampling-based Phase 1 observation match `ARC_SOURCES.md`. However, that source also records ARC’s expectation of improvements beyond basic cumulant propagation and an unverified participant claim of a scale-mode correction tested at depth proportional to width. The latter need not be believed, but it is directly relevant to an assertion that every promising family has been exhausted.

    The contest’s official score also includes a compute-utilization multiplier. Converting the public board’s raw MSE using this report’s different networks gives a rough comparison, not a paired benchmark; the organizer’s aggregate description does not identify the winning entry’s method.

    **Fix:** Preserve ARC’s uncertainty and distinguish tested methods from surveyed proposals. Mention directly relevant unverified alternatives, and label leaderboard comparisons as approximate.

17. **Minor — Preregistration provenance is mostly reproducible, but the summary overstates its independence.**  
    All **25 latest manifest-listed file hashes** matched. Frozen files matched recorded hashes, and the successive preregistration prefixes reproduce recorded hashes after restoring their terminating newline. FORMAL’s frozen-v1 and final hashes also match.

    Nevertheless, Amendment 3 explicitly used already-seen width-32/64 results, so those P13 checks are descriptive rather than fresh predictions. The blanket claim that every prediction preceded its evaluation runs is therefore inaccurate. The claimed pre-scoring P12 calibration disclosure is not in the cited `logs/deviations.txt`. The report’s “every constant rechecked” statement also exceeds PROVENANCE’s explicit list of unchecked calculations/remainders.

    **Fix:** Give each prediction a seen/unseen evaluation subset, correct the disclosure references, and distinguish content-hash verification from independent evidence of chronology. I found no hash mismatch suggesting undisclosed replacement of the frozen code.

The numerical checks support a narrower empirical report. I reran **all seven scorers to stdout**, reproducing their saved JSON outputs before the newly completed net-203 run, and independently recomputed:

| Quantity | Recomputed value |
|---|---:|
| 256×32 median k2 nMSE / cost | \(0.00122204\) / 393.150 passes |
| 256×32 median k2a nMSE / cost | \(0.000841677\) / 451.704 passes |
| 256×32 median k3f nMSE / cost | \(0.000201479\) / 49,097.169 passes |
| P4 RQMC advantage, nets 200–204 | 6.706, 39.772, 17.824, 34.144, 21.633 |
| Infinite-width conditional mean degrees, \(t=1,4,8,16,31\) | 2.752, 4.837, 8.220, 17.242, 42.271 |
| Corresponding FFT median/90% degrees | 2/4, 3/8, 4/14, 6/30, 10/74 |
| Ensemble variance bounds at 256×32 | 0.49951077 to 20.13890814 |
| P15–P17 fitted exponents | 0.948983, 2.476533, 0.672987 |
| Saved three-net Amendment 6 radial median | \(0.000457230\) |

I also reproduced the attribution medians, R1–R3, P13–P14, RQMC gains, and the reported Gaussian annealed/median comparison. These substantiate the tested methods’ performance. They do not substantiate the report’s claimed ceilings or its exclusion of further layer-wise deductive progress.
