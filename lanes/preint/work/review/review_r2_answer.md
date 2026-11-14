codex
**Verdict: major revision.** The measured compute disadvantage remains supported, and the generated report reproduces exactly. However, registered MLMC scoring is wrong, several headline claims still exceed the theory or statistical evidence, and some claimed fixes remain incomplete.

Checked at **2026-11-02 16:49 UTC**. I made no file changes; all generated writes were intercepted in memory.

I reran `score.py`, `posthoc_matched.py` with the three requested patterns, `report_tables.py`, `cost_sensitivity.py`, and `assemble_report.py`. All six generated outputs, including `preint.md`, were **byte-identical** to the saved files. I also regenerated `degree_table.md` in memory; it matched. Reproduction therefore confirms the assembly, but also reproduces the scoring and labeling errors below.

All nine tests passed, with stdout matching `logs/test_line.log`, including the four additions. All 11 hashes in `prereg_hashes.txt` match. The recorded chronology is consistent:

| Event | Evidence |
|---|---|
| Initial registration, 14:03:47Z | Earliest scored-file creation: 14:04:10Z. |
| Amendment 1, 15:08:43Z | Net 202 file created at 15:08:47Z; nets 203–204 started later. |
| Amendment 2, 15:34:02Z | Net 201’s completed 64-line active result was written at 15:33:58Z; termination logged at 15:34:03Z; continuation file created at 15:34:22Z. |
| Completion | Net 201 has active budgets through 64 lines and random through 32; nets 202–204 have both through 32. Last completion: net 203 at 16:38:10Z. |

These are matching hashes and consistent local timestamps, not independent timestamp attestations. Amendment 2 followed observed partial results, as its text acknowledges. The registered methods and endpoints are present; the extra MLMC budgets are an unreported deviation.

The disposition of each round-1 finding is:

| R1 | Status | Evidence |
|---|---|---|
| 1. Conclusion exceeds scope | **Partly** | [Section 5](/home/agent/workspaces/mats/work/preint/preint.md:230) now distinguishes absolute ensemble error, normalized ensemble error, and excluded algorithms. The [opening paragraph](/home/agent/workspaces/mats/work/preint/preint.md:23) still combines point and line polynomial-window claims and asserts no measurable exponent change. |
| 2. Point corollary extended to lines | **Partly** | [Lines 245–251](/home/agent/workspaces/mats/work/preint/preint.md:245) correctly restrict the corollary to points and retain degree-dependent line ranks. The opening summary still omits that distinction. |
| 3. Uncertified spectral barrier/design ceiling | **Partly** | [The degree discussion](/home/agent/workspaces/mats/work/preint/preint.md:270) explicitly disclaims a certificate, and the fourfold ceiling is withdrawn. But [section 6](/home/agent/workspaces/mats/work/preint/preint.md:303) still says an outer design changes only the constant. |
| 4. Quantitative Gaussian extension | **Resolved** | [Lines 277–285](/home/agent/workspaces/mats/work/preint/preint.md:277) separate Gaussian optimality from the missing output-channel bounds and leave the actual prior’s adaptive/nonlinear case open. |
| 5. Inconsistent compute ledger | **Partly** | [Setup](/home/agent/workspaces/mats/work/preint/preint.md:75) discloses omissions and adds sensitivity analysis. That analysis is incomplete, and several numerical summaries contradict its own output. |
| 6. Missing matched 256 × 32 comparison | **Resolved** | Four `posthoc_smallN_n256_L32_s*.json` files provide 16-replicate references at N = 2–64. The requested rerun reproduces eight matched comparisons at width 256 and 56 comparisons overall. |
| 7. Final verdicts on incomplete experiments | **Partly** | [The scorer](/home/agent/workspaces/mats/work/preint/scratch/score.py:54) checks method endpoints, but not complete budget grids, replicate counts, or four valid fit observations. Some missing methods cause exceptions before the pending gate. |
| 8. Slopes treated as equivalence/asymptotics | **Partly** | [Section 4.3](/home/agent/workspaces/mats/work/preint/preint.md:212) preserves failures and says “not an equivalence test.” Regression SEs were added, but no uncertainty for slope differences; the headline and conclusion still claim no measurable change. |
| 9. Window-tail MC floor | **Partly** | The eventual \(1/N\) floor is acknowledged at [lines 87–90](/home/agent/workspaces/mats/work/preint/preint.md:87). The claimed normalized contribution of approximately \(10^{-16}\) per line is not quantified by an artifact or bound. |
| 10. Constructive rates attributed to implemented methods | **Partly** | [Section 3](/home/agent/workspaces/mats/work/preint/preint.md:134) correctly identifies another algorithm. The table still labels its rates “asymptotic RB / PI,” and “only \(o(1/N)\) is [proven]” remains unsupported for the implementation. |
| 11. Bias/MSE validation | **Partly** | [Setup](/home/agent/workspaces/mats/work/preint/preint.md:70) admits omitted truth noise, uncalibrated diagnostics, and the empirical tail premise. The \(t_7\) interpretation remains unjustified for the general statistic; no independent full-network tail validation was added. |
| 12. Downward-biased line-variance statistic | **Resolved** | [The scorer](/home/agent/workspaces/mats/work/preint/scratch/score.py:121) adds replicate estimator variance, preserves the frozen statistic for P2, and the report distinguishes them. The stated maximum correction, 0.035 rounded, reproduces. |
| 13. Live dependencies in frozen execution | **Partly** | Current `line.py` and `nets.py` match frozen copies; the estimator diff is only the unused `jac` option. The external MLMC hash matches the logged prefix. [Execution still imports live dependencies](/home/agent/workspaces/mats/work/preint/frozen/curves.py:21), without per-run loaded-module hashes. |
| 14. Implementation cost promoted to necessity | **Resolved for the report’s scope** | [Lines 121–123](/home/agent/workspaces/mats/work/preint/preint.md:121) explicitly distinguish retained vertices from minimal integration complexity. Tail-map hoisting and the prefix-targeted pilot remain unimplemented but disclosed. |
| 15. Mathematical labels and numerical wording | **Partly** | Degree-estimator qualification, squared-hinge restriction, kurtosis comment, slope counts, and pass sizes were corrected. The surrogate improvement condition \(b>\gamma\) is still absent, and other stale numbers remain. |
| 16. Missing targeted tests | **Partly** | [The added tests](/home/agent/workspaces/mats/work/preint/tests/test_line.py:178) pass and improve coverage. The FLOP test verifies the nominal formula, not actual operation counts; tail-map linearity does not validate the narrow-deep tail premise. |

The remaining findings, with severity and required fixes, are:

1. **Major — The summary still merges distinct theorems and excludes untested possibilities.**  
   **Evidence:** [The opening](/home/agent/workspaces/mats/work/preint/preint.md:27) puts points and exact lines under a spectral-share-dependent \(c/N\) statement over polynomially growing windows. Section 5 correctly supplies a normalized polynomial-window corollary only for points; lines retain their LP certificate and the absolute low-budget bound. The measured aggregate energy is not the required ensemble certificate. [“An outer design changes only … the constant”](/home/agent/workspaces/mats/work/preint/preint.md:304) is also unproved.

   **Fix:** Make the summary preserve those distinctions and normalizations. Remove the constant-only claim about designs. State that the implemented methods lost over the tested compute budgets; broader asymptotic possibilities remain open.

2. **Major — P8 is not scored over its registered budgets. Newly detected.**  
   **Evidence:** [PREREG](/home/agent/workspaces/mats/work/preint/PREREG.md:30) specifies S3 MLMC budgets \(p=8,\ldots,14\). Every S3 MLMC artifact instead includes \(p=6,\ldots,14\), and [the scorer](/home/agent/workspaces/mats/work/preint/scratch/score.py:223) fits all rows. This changes the top-60% fit window from \(p=10\ldots14\) to \(p=9\ldots14\). Filtering to the registered range gives **P8: 11/19**, rather than **7/19**; the overall verdict still fails. For example, 32×4 seed 302 changes from **1.324932 to 1.155927**. Registered-only validity counts become **3/888**, rather than 3/914. [The deviations log](/home/agent/workspaces/mats/work/preint/logs/deviations.txt:12) incorrectly says these fits were scored as registered.

   **Fix:** Filter registered scoring and associated tables to the specified ranges. Retain extra budgets as explicitly post-hoc data, regenerate the report, and document the deviation.

3. **Major — The exponent conclusion remains stronger than its analysis, and the promised failure follow-up is missing.**  
   **Evidence:** [The headline](/home/agent/workspaces/mats/work/preint/preint.md:26) and [section 6](/home/agent/workspaces/mats/work/preint/preint.md:290) claim no measurable exponent change. [The new SEs](/home/agent/workspaces/mats/work/preint/scratch/posthoc_matched.py:16) come from regression residuals; there are no slope-difference intervals, equivalence margins, or saved replicate estimate vectors. Mixed signs alone establish neither equivalence nor absence of a meaningful gain. Furthermore, [PREREG’s explicit response to P3b failure](/home/agent/workspaces/mats/work/preint/PREREG.md:69) was larger-N runs at width 128. P3b now fails, but those runs and an explanation for departing from that commitment are absent.

   **Fix:** Describe finite-window slope estimates as inconclusive about equivalence and asymptotic exponents. Either perform the promised follow-up or record its deferral and the resulting limitation. Stronger statistical claims require uncertainty for differences and a specified meaningful effect size.

4. **Major — The new cost sensitivity does not support its advertised completeness or several quoted numbers.**  
   **Evidence:** [The script](/home/agent/workspaces/mats/work/preint/scratch/cost_sensitivity.py:26) adds a per-vertex allowance, rather than instrumenting actual work. It produces **55 of 56** PI records: net 201’s random variant is skipped because its separate file lacks a reference method. Despite its docstring, it never adjusts MLMC. It also omits the SVD correction and uses RQMCRB for S3 sensitivity, whereas P3a uses RQMC.

   Its reproduced output contradicts [the report’s summary](/home/agent/workspaces/mats/work/preint/preint.md:78):
   - Maximum exponent movement is **0.016887** in scenario A and **0.026326** in B, not at most 0.01.
   - Width-64 cost increases are **1.35–1.43%** in A, not under 1%.
   - One minimum comparison improves numerically: narrow-deep seed 203, PIJ_as, **14.6226 → 14.3820** in A. It still loses, but “every comparison moves against PI” is false.
   - The response’s “under 5%” SVD statement is also incorrect: replacing \(4dP^2\) by the corresponding thin-matrix \(4Pd^2\) model removes 960 passes at \(d=4\), **7.5–8.1%** of the smallest fitted budgets.

   **Fix:** Merge split run files before sensitivity analysis; use the registered comparators; include the stated corrections or explicitly delimit the scenarios. Generate maxima and ranges from the results. The evidence still supports a substantial PI disadvantage, but not the claimed complete accounting.

5. **Major — The remaining Sobol guarantee is not established by the supplied proof.**  
   **Evidence:** [Line 136](/home/agent/workspaces/mats/work/preint/preint.md:136) asserts \(o(1/N)\) is proven for scrambled Sobol. [The co-prover’s audit](/home/agent/workspaces/mats/work/preint/coprover/astra_r2_answer.md:193) expressly requires a corresponding theorem for SciPy LMS scrambling plus digital shift. Moreover, the implemented fixed-window estimator generally has a nonzero \(C_\epsilon/N\) contribution. The [small-net table header](/home/agent/workspaces/mats/work/preint/preint.md:152) still calls another algorithm’s constructive rates “asymptotic RB / PI.”

   **Fix:** State the scrambling assumptions and supply the applicable result, or mark the guarantee unestablished here. Separate deterministic exact-line integration from the window estimator. Rename the table column “constructive cubature upper-bound exponents.”

6. **Minor — Completeness checks and new tests leave their advertised guarantees only partly covered.**  
   **Evidence:** In-memory probes showed `complete()` returns true with **one replicate** or **only each method’s final row**. Removing S1’s RQMCRB or S2’s PIJ_as causes `KeyError` before the pending check. Four rows with only three valid variances still produce an exponent through [the frozen fitter](/home/agent/workspaces/mats/work/preint/frozen/fit.py:15). All current scored rows are finite and the recorded replicate counts agree, so these probes do not invalidate the completed PI results.

   [The FLOP test](/home/agent/workspaces/mats/work/preint/tests/test_line.py:232) recomputes the same nominal charge formula. The arbitrary linear-map test does not establish that a fitted tail map equals the actual downstream network.

   **Fix:** Validate grids, replicates, metadata, and valid fit observations before scoring. Test incomplete inputs directly. Use instrumented operation counts for accounting validation and an independent full-network residual check for the tail premise.

7. **Minor — Bias calibration and the numerical tail-floor claim remain unsupported.**  
   **Evidence:** [The bias paragraph](/home/agent/workspaces/mats/work/preint/preint.md:70) now acknowledges important limitations, but \(t_7\) calibration applies to a rank-one Gaussian special case, not generally to this vector trace-variance ratio. Adding the supplied truth uncertainty leaves all three current flags above threshold; that does not calibrate them.

   Likewise, [the \(10^{-16}\) claim](/home/agent/workspaces/mats/work/preint/preint.md:88) cannot be obtained from \(\epsilon^2\) alone. The normalized tail contribution also depends on the squared total weight and conditional tail-output variance. Neither is measured in the saved sensitivity results.

   **Fix:** Label the \(t_7\) comparison as illustrative, or provide justified calibration. Quantify the tail coefficient or label its stated magnitude heuristic. Keep PIJ/RQMCJ results conditional and replace “exact tail map” in the section heading with that qualification.

8. **Minor — Frozen execution provenance is documented retrospectively, not repaired.**  
   **Evidence:** Current byte comparisons and the MLMC hash support the author’s explanation; I found no demonstrated scored-behavior change. Nevertheless, [the frozen runner](/home/agent/workspaces/mats/work/preint/frozen/curves.py:21) still imports live code, and the run artifacts lack loaded dependency paths, hashes, and versions.

   **Fix:** Preserve the honest retrospective qualification for these runs. For future registered execution, freeze the dependency graph and record what each process actually loads. Current file equality cannot establish historical loaded contents.

9. **Minor — Several labels, numbers, and response claims still need correction.**  
   **Evidence and fix:** [The surrogate paragraph](/home/agent/workspaces/mats/work/preint/preint.md:294) needs **\(b>\gamma\)** for an exponent above one, despite RESPONSE claiming this was added. [The 256×32 random-line cost range](/home/agent/workspaces/mats/work/preint/preint.md:120) is **836–984**, not 836–924. The equivalent-point quantities in [the summary](/home/agent/workspaces/mats/work/preint/preint.md:37) and section 5 use **RQMCRB**, not RQMC, as their reference. The two rate comparisons displayed in [section 3](/home/agent/workspaces/mats/work/preint/preint.md:135) give leading gains approximately **\(2/d\)** and **\(1/d\)**, not “2/d to 4/d.” Finally, replace [“all addressed”](/home/agent/workspaces/mats/work/preint/preint.md:344) with an accurate distinction between resolved issues, disclosed limitations, and unfinished fixes.
