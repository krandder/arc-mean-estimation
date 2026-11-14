<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/scale-mode/review/review_gpt6.raw -->

**Verdict: major revision.** The numerical work is reproducible and largely faithful to the implementations. The main problems are stronger conclusions than the measurements establish, an ambiguous Phase 2 verdict, and insufficient uncertainty reporting.

Checked against the supplied files on 2026-11-02. I modified no files. All 27 manifest entries verified against their applicable frozen/current copies; the scorer’s only change was the disclosed expansion of two cell counts from four to eight. Re-executing its calculations in memory reproduced `results/score.json` exactly after JSON serialization. Both GPU parity gates passed, and all 237 evaluated GPU output files matched their copies in `runs/`.

Independent arithmetic checks included:

| Check | Recomputed result |
|---|---:|
| Author’s 64×16 reproduction, aggregating `runs_dev/claimB.json` | Mean nMSE **0.001516668**; **39,643,382** mean FLOPs; author-accounting MC gain **2.31621** |
| E1 LVTV2, recomputed from estimates and truth files | Median nMSE **0.000363302**, **687.7106** passes |
| E3 1024×256 LVTV2, recomputed using cross-half errors | Median nMSE **0.0001086514**, **2232.7814** passes |
| E4 COV, recomputed from public truths | Mean raw MSE **4.4715848e-6** |
| E4 ARC-k3f, six public nets | Mean raw MSE **3.9509717e-8** |

The reported **40 holds / 5 failures**, plus failed **D1, D2 and D**, are correct. **N2 holds, 12/12**, under the registered extrapolation convention.

1. **Major — Section 4 does not establish that scale separation cannot change the exponent.**  
   [The cited Theorem 3](/home/agent/workspaces/mats/work/scale-mode/thirdparty/scale-separation/extensions/THEOREM.md) assumes **zero Gaussian mean** for its standardized scale-cumulant formula. Its dilution comparison separately assumes **independent coordinates and balanced readouts**. Those assumptions are not established for the de-scaled, fixed-weight network states. Neither result supplies a lower bound on their remaining estimation error.

   Furthermore, ARC’s conjectured upper error law does not imply the asserted limitation. The companion report explicitly requires error and cost **lower bounds uniform over orders**, and over width for width-asymptotic conclusions. Calling this section “HEURISTIC” does not justify the repeated “must,” “cannot,” and “changes the constants, not the exponent.”

   **Fix:** State those assumptions explicitly and present the exponent argument as conditional. Remove claims that the third-party theorem establishes them or rules out a better exponent.

2. **Major — Failed escape criteria are being promoted into an asymptotic negative.**  
   D1 and D2 are correctly scored, but they are operational success criteria, not necessary conditions for every possible escape. A method could fail at small widths and improve asymptotically, or improve at orders not tested here.

   The measured `gamma_SL` is a slope between **two implementations**, LVTV2 and SL3, rather than an established all-order convergence exponent. Also, “no steeper than ARC’s” is false across much of the displayed ladder: at widths 32, 64 and 128, the reported slopes are approximately **1.00 versus 0.54**, **0.72 versus 0.37**, and **0.52 versus 0.28**. They become similar at 256. No new SL4 evaluation tests the author’s distinctive K3→K4 inversion-repair result.

   **Fix:** Conclude: “Neither registered escape criterion was met; the tested levels retain a limited winning window.” Restrict equality with ARC’s slope to 256×32 and leave higher-order and asymptotic behavior open.

3. **Major — The headline Phase 2 conclusion does not cleanly report the registered N2 outcome.**  
   [PREREG §6](/home/agent/workspaces/mats/work/scale-mode/PREREG.md) explicitly defines “our negative applies at Phase 2” through N2. N2 passes on **12/12** nets. Yet the summary says the negative “does not apply here.”

   The broader distinction is reasonable: the measured affordable implementations lose in raw accuracy, while external contest entries demonstrate successful engineered deduction. But those are different evidence sets. The present ARC-k3f implementation exceeds the budget, and the public-board evidence does not demonstrate that this exact implementation can retain its error after being engineered into budget.

   **Fix:** Put both conclusions in the summary: “N2 holds for the implementations tested under ARC accounting. This does not establish a general Phase 2 negative; public contest results support successful deductive methods.” Label the latter as external evidence.

4. **Major — Uncertainty is too large to support several unqualified win/loss and trend statements.**  
   Eight RQMC replicates can be noisy on these deep nets. From the saved replicate estimates, the relative standard error of mean RQMC error at the nearest measured budget ranges approximately **18–45%** across E3 widths 64–512, and **30–70%** at width 1024. The width bootstrap resamples nets but does not separately propagate scramble uncertainty or truth uncertainty.

   Cross-half scoring removes the additive truth-noise bias in the squared-error numerator; it does not remove noise. For net 645 at 1024×256, scoring against each truth half gives about **1.44e-4** and **8.67e-5**, versus cross-half **1.10e-4**. The normalized ratio also uses an estimated variance denominator.

   The 512-cell failure of C1 is a valid registered point-estimate failure, but weak population evidence against MC superiority: my bootstrap using the author-style cell statistic gives approximately **[0.57, 1.63]**, around the reported **0.889**. Likewise, removing the largest width changes the diagonal RQMC-gain slope from **+0.188 to −0.197**.

   **Fix:** Add uncertainty for gains and crossovers, truth-half sensitivity, and leave-one-width-out slopes. Preserve the registered verdicts, but distinguish threshold failures from statistically resolved failures of the underlying claim.

5. **Minor — Some “claim transfers” strengthen or change the author’s actual statements.**  
   The author’s ladder comparisons concern cell-mean errors. C2 introduces a new requirement that SL3 improve on **at least 80% of individual nets**. At 128×32, C2 fails at 6/8, but mean error still improves from **0.00180592 to 0.00149732**. Thus this failure does not refute the author’s mean-error improvement claim.

   C6 likewise changes the author’s ratio-of-means statistic to median gain; C1 additionally extends the claim beyond its original diagonal. These are legitimate registered tests, but not literal reproductions of the original assertions.

   **Fix:** Call them “our operationalized transfer predictions.” Report the author-matched mean statistics alongside them, and explicitly note that the mean ladder improvement survives at 128×32.

6. **Minor — Extrapolation flags disappear from the report’s main tables.**  
   The scorer records them, and `results/tables.md` displays them, but the report tables omit them. Examples include LVTV2 at 32×4, SL3 at 128×32, and SL3 at 256×64. The last comparison extrapolates RQMC from **16,384 samples to roughly 124,095 passes**, approximately **7.6×** beyond the measured range. E4 SL3 comparisons also extrapolate beyond 65,536.

   Half the Phase 2 full-budget comparisons are projections from 16,384 samples. For `p2_07`, the reported ARC-k2a/RQMC ratio is only **1.064**; a replicate-only bootstrap already spans roughly **0.98–1.14**, before uncertainty in extrapolation.

   **Fix:** Mark every extrapolated table entry and state the measured range and imposed slope. Use measured cheaper-sampler comparisons to establish robust losses where possible; measure the missing full-budget Phase 2 points before calling all 12 comparisons directly observed.

7. **Minor — The explanation of the contest’s 10% floor reverses its effect.**  
   “Wins … only because cheap methods are scored as if they used 10%” is misleading. The **compute adjustment** rewards efficiency; the **floor penalizes especially cheap methods** relative to charging their actual utilization.

   For COV, actual utilization is about 0.0235. Without the floor, its adjusted score would be about **1.05e-7**, better than its floored **4.47e-7**. Its efficiency advantage is therefore not created by the floor. Topic 18198 explicitly discusses adjusted leaderboard scores, so the report confirms its stated claim; full-budget raw accuracy answers an additional question.

   **Fix:** Say that COV wins under the contest’s compute-adjusted metric despite the floor, while full-budget sampling achieves lower raw MSE.

8. **Minor — The claimed identification with the companion’s radius-corrected closure is unproved.**  
   LVTV2 carries a Gamma scale approximation and a matched fourth-moment update. The companion’s finite-sample radial transport propagates a different model construction. Exact homogeneity within the scale-mixture model does not establish that the network’s full radius law is correct, or that this implements the companion’s closure.

   The third-party theory explicitly leaves the exact deep Gamma law and fixed-network error bounds unproved. Consequently, “the first deductive version” and “break-even arithmetic … confirmed” overstate the mechanistic connection.

   **Fix:** Describe LVTV2 as a related deductive scale-mixture approach whose observed cost and error are consistent with the companion’s proposed budget window. Establish equivalence separately before claiming it.

9. **Minor — Reproduction and provenance language needs narrower precision.**  
   The implementation comparison is reassuring: `smlib.py` preserves the author’s R=24, b=6.5, `v2f` rule, Gamma moments and FLOP additions; `run_cell.sh` confirms R=24 despite `lv2.py`’s older default/docstring. The SL3 loop matches the supplied hook, with the justified metric change for the different initialization.

   However, the 1024×256 check establishes agreement with the author’s **printed four-decimal** variance, `0.0284`, and rounded FLOP count—not exact equality of full predictions or reproduction of its error. Likewise, hashes establish content integrity, not independently authenticated chronology. The queue timestamps are consistent with the disclosed registration sequence; I found no additional undisclosed methodological change.

   **Fix:** Replace “exactly” with “to the published precision” for that identity check. Retain the disclosed amendments and distinguish hash verification from timestamp evidence. Also label the table’s bracketed minima/maxima as **ranges**, not confidence intervals, and keep the special-function repricing explicitly identified as a partial sensitivity calculation rather than full flopscope metering.
