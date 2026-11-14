Checked **2026-11-02 01:45 UTC**, read-only, against the revised report, frozen registrations, scorers, logs and NPZ files. Items 1–14 correspond to round-1 findings.

1. **Partly resolved; minor residual — Integrability.** §1 now correctly identifies regularized log moments and the different floors. The direction convention remains incomplete: Part C sets \(u(0)=0\), while Part B computes squared distance as \(2(1-\cos)\), which is incorrect when either output is zero. Explicitly qualify those direction estimators on extinction events. This does not affect runs without extinction.

2. **Resolved — Input vertex recursion.** The quadrature implementation and saved results correct the interpolation error. At \(n=256\), corrected PRs are **10.168, 5.410, 2.821, 1.448** at depths **32, 64, 128, 256**, consistent with round 1. The report preserves registered PB6 targets and separates the numerical error from remaining finite-width discrepancies.

3. **Partly resolved; minor residual — PB1 and totals.** The scorecard correctly reports **15 hits, 7 misses, 2 pending** with revised PB1, versus **14 hits, 8 misses, 2 pending** under its original analysis. Both post-data changes are disclosed. However, summary item 4 and §3.1 still say “PB1, PB2 hit” without identifying PB1 as revised-analysis-only.

4. **Resolved — Amendment A1 chronology.** §§2.4 and 10 correctly distinguish registration after the \(n=256\) run started from prospective \(n=512/1024\) testing. All five archived registration hashes reproduce. The assertion that no output had been inspected remains an author declaration, not something these artifacts independently establish.

5. **Resolved — Registration deviations.** Shortened sharing runs, omitted sharing levels, reduced six-replica budgets and the original baseline substitution are disclosed. The current scorer uses the registered A-r2 baseline. I independently checked all **9/9** PA5 clauses at \(n=64\) and **10/10** at \(n=256\).

6. **Partly resolved; minor residual — Direction theorem.** §7 correctly distinguishes the proven transverse frozen-Jacobian statement from the nonlinear cloud-frame heuristic and excludes output coordinates. Propagate that distinction into the summary and §3.3, which still assert random/Haar relative position directly. Also remove “or the mean direction” from the matched-replica invariance statement: fixing the mean alone need not preserve every replica’s Gram relations.

7. **Partly resolved; major residual — Orientation bits.** The caveats now acknowledge that PR does not determine approximation rank and that description length is not an estimator lower bound. Nevertheless, [§7’s M1 conclusion](/home/agent/workspaces/mats/outbox/gram-chain-2026-11-01.md:467) still substitutes PR for \(k\), reports \(n^{5/3}\log(1/\epsilon)\) bits, and says an estimator “would need” directional information. The measured moments establish neither the required approximation rank nor that computational necessity. Present the bit count strictly conditionally—*if a generic rank-\(k\) subspace must be encoded*—and remove its asserted implication for estimator limitations.

8. **Resolved — Tangent spectrum claim.** §3.3 and FORMAL §7.13(c) now describe a single moment-ratio check, with finite-dimensional and averaging qualifications. That is supported; identification of the whole spectral law is no longer claimed there.

9. **Partly resolved; minor residual — Estimands.** Full-state copying, annealed PR weighting and the radial proxy are now explained. But §3’s definition still says the direction-based \(V_P\) explains “\(E[a]\)”; it concerns the conditional mean of **\(u\)**. §3.5 also reverts to an unqualified raw-output “share”; retain the small-fluctuation qualification there.

10. **Partly resolved; minor residual — Precision and scaling.** PA9 now materially strengthens the width evidence, and the finite-\(Q\) product correction is stated correctly. “Relevance curves to within a few percent” remains too broad: at \(n=1024,t=32\), **0.089 versus 0.075** differs by about **19% relatively**. State the tested range and absolute error, rather than conflating percentage points with relative percentages.

11. **Resolved — Scatter statistic.** Direct recomputation gives squared-CV reductions **87.11%, 88.80%, 96.75%**, and prediction \(R^2\) values **0.88088, 0.92171, 0.93393**. The revision reports these correctly.

12. **Resolved — Descriptive corrections.** The 168-net count, coefficient range, PB4 failure locations, missing log-channel errors, four-survivor conditioning, late \(n=8\) PR rebound and scaled vertex normalization are corrected.

13. **Partly resolved; minor residual — Pending coverage.** The report correctly keeps PA5 pending, limits PA7 because two registered widths were dropped, and treats PA8 as irreversibly missed on its PR clause. The scorer requires all seven PA7 widths and all twelve PA8 clauses for a hit. However, JSON represents **PA7 as `hit:false` with no rows**, conflating pending with failed; use an explicit pending/incomplete state. No completed r3/r6 artifacts were present at this check.

14. **Resolved/reconfirmed — Core measurements and tests.** All **19 library checks pass** again. Four-replica endpoint measurements reproduce directly, and the PB5 score artifact remains **98/100 clauses**. No regression found in these checks.

15. **Informational — PA9 is scored correctly and reproduces.** From the NPZ files,
    \[
    PR_w=\frac{\sum x_{11}x_{22}}{\sum x_{12}^2}
    \]
    gives **48.96096779** at \(n=256\) and **114.74168603** at \(n=1024\); the slope is **0.61434282**. Reproducing the scorer’s random-number sequence gives its exact 200-bootstrap 90% interval **[0.59902640, 0.62885170]**. An independent 10,000-resample chain bootstrap gives **[0.59873597, 0.62981351]**. Both registered thresholds pass. The report’s numerical result and restricted “favoured over this range” conclusion are correct.

16. **Informational — PA5 remains incomplete, with available clauses passing.** Using \(E\delta_0=0.03506313933\), coordinate values are **0.15553, 0.35883, 0.59064**; correlation values are **0.15823, 0.34546, 0.58810**. All six available clauses pass. The newly logged block value at \(t=0.25\), **0.17218**, also passes. Remaining block and antithetic clauses are unavailable; no overall hit is justified.

17. **Minor — Baseline revision was incompletely propagated.** The \(n=256\) mean-order column still shows **4.10 / 4.11 / 3.38**, from the old baseline. Registered-baseline values are **4.0594 / 4.0620 / 3.3432**. Update repeated values and the stale opening status that still lists PA9 and completed PB5 work as pending.

**Verdict: major revision.**
