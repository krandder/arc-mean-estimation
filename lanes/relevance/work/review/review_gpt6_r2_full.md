The revision’s main results survive. **Six first-round findings are resolved; nine are partly resolved.** Remaining corrections are minor. Checked read-only through 2026-11-01 23:24:53 UTC; document SHA-256 begins `dc1184a6`. No files changed. Running stationary cells are not findings.

For resolved items, severity below retains the original severity; otherwise it grades the remaining work.

1. **Minor — Finding 1 partly resolved: M1 conclusion.**  
   The main conclusion now correctly leaves better projections and integration methods unresolved. However, [Summary 4](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:68) still calls the tested coordinates the “best … input features.”  
   **Exact fix:** Replace “best 16, 64 or 128 input features” with “top 16, 64 or 128 active-subspace features tested.” These measurements do not bound the gains achievable with optimal features.

2. **Major — Finding 2 resolved: theorem scope and free-position comparison.**  
   Angular/frozen-Jacobian restrictions and the heuristic extension are now explicit. Independently recomputing measured/predicted participation ratios gives:

   | ARC seed | Ratios at \(l=4,8,16,24,28,31\) | Within 20% |
   |---|---|---:|
   | 4000 | 1.1302, 1.1877, 1.1890, 1.1193, 1.0282, 0.9433 | 6/6 |
   | 4001 | 1.2790, 1.2606, 1.3071, 1.1033, 1.1930, 1.0564 | 3/6 |
   | 4002 | 1.0107, 1.0555, 1.0370, 0.9286, 0.8569, 0.9625 | 6/6 |
   | 4003 | 1.0269, 0.8612, 0.9046, 0.9157, 0.8760, 0.9510 | 6/6 |

   Total **21/24**, median **1.032596**, range **0.856921–1.307080**: all match. **Exact fix:** None.

3. **Minor — Finding 3 partly resolved: radius versus linear feature.**  
   The principal distinction and Gaussian-replacement caveat are fixed. But [§3](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:123) now says the centered-input radius variation “is degree two.” It has degree two **and higher even degrees**. For \(X\sim N(0,I_{256})\), degree two accounts for approximately **99.9026%**, not 100%, of \(\operatorname{Var}\|X\|\).  
   **Exact fix:** Write “its centered Hermite expansion starts at degree two and contains higher even degrees.”

4. **Minor — Finding 4 partly resolved: degree attribution and uncertainty.**  
   The renamed surrogates, negative values, per-net ranges, and separate-median explanation are correct. I reproduced all seven rows’ measured ranges; for example, the even surrogate ranges are **−0.036335–0.188340** at \(l=16\) and **−0.068180–0.138774** at \(l=31\).  
   Two requested corrections remain: the opening still advertises a split into “single-gate terms,” and between-net ranges do not quantify sampling uncertainty. `mehler_curve` shares draws across correlations, but their covariance is not retained.  
   **Exact fix:** Replace the opening’s gate attribution with “degree 1, an even-degree surrogate, and a remainder.” Either supply joint uncertainty estimates or explicitly state that sampling uncertainty for these combinations was not quantified and the comparison is descriptive.

5. **Major — Finding 5 resolved: advertised accuracy.**  
   Independent recomputation gives **Q1 12/14, Q2 13/14, Q3 11/14**. Maximum errors over all ARC cells are **22.191984%, 0.124508, and 46.118478%**, consistent with the rounded revision.  
   **Exact fix:** None.

6. **Minor — Finding 6 partly resolved: count limitations.**  
   The main document and first-chaos figure legends now state the important limitations. I reproduced omitted mass **0.05468722** and Q4 **14/14 at both tolerances**. However, [§5](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:170) still calls the spectrum estimates “debiased,” despite E12 explaining that the subtraction is not generally valid; `results/report_tables.md` still labels them “lower bound.”  
   **Exact fix:** Use “heuristically noise-corrected, uncertified estimates,” and update the generated table header and its generator. Preserve frozen artifacts.

7. **Minor — Finding 7 partly resolved: stationary gate uncertainty.**  
   The provisional label accurately discloses the missing outer-noise uncertainty. The estimator itself remains unchanged: two shared future-noise realizations and an input-row jackknife.  
   **Exact fix:** Keep these results explicitly provisional and state that re-estimation remains outstanding. Before promoting them to uncertainty-qualified results, use independent outer noise pairs and include denominator uncertainty.

8. **Minor — Finding 8 partly resolved: gate counts and denominators.**  
   The corrected denominator and stationary counts reproduce: **four zeros; nonzero importance-order counts 1, 13, 23, 25**. The remaining ambiguity is ordering: the stationary **109–634** range and Summary’s approximately **1,950–4,900** counts refer specifically to importance ordering. Margin-order stationary counts range **126–771**.  
   **Exact fix:** Name importance ordering beside those ranges. Replace “Each sample flips 5–9%” with “Median per-sample flip fractions across nets range from **5.18% to 8.90%** across the reported layers.”

9. **Minor — Finding 9 partly resolved: stationary interpretation.**  
   The prose now correctly distinguishes medians, per-net spread, observed finite-depth residuals, and the top AS direction. But the regenerated [stationary figure](/home/agent/workspaces/mats/work/relevance/figs/fig3_stationary.png) still labels its curves “best single direction.”  
   **Exact fix:** Change those legends in `scratch/figs_accounting.py` to “top active-subspace direction” and regenerate the figure.

10. **Major — Finding 10 resolved: synchronization thresholds.**  
    Recomputed persistent \(10^{-3}\) crossings are **100, 32, 176, 80**, in the stated net order. Final residuals are **\(9.7228\times10^{-9}\), \(1.0821\times10^{-22}\), \(4.3731\times10^{-15}\), \(1.5948\times10^{-20}\)**. The corrected \(n=32\), seed-301 value at \(4n\) is **\(3.12998\times10^{-5}\)**.  
    **Exact fix:** None to these corrections; see item 16 for another synchronization paragraph.

11. **Minor — Finding 11 partly resolved: estimator claims.**  
    Nominal cost, excluded setup, reference uncertainty, exploratory status, and finite-budget slopes are correctly disclosed. Recomputed median slopes are **1.0277, 1.2729, 1.0261, 1.1913, 0.9935**. Nevertheless, [§9](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:272) still turns approximate synchronization into the exact equality \(a(x)=|h_{32}(x)|g(u^*)\). Repetition-level uncertainty remains unavailable.  
    **Exact fix:** Use \(\approx\), identify this as the truncated estimator’s approximation, and state that stored repetition averages do not support reconstructed confidence intervals. In the Summary, replace “by a constant factor” with “by the measured factors at the reported budget.”

12. **Minor — Finding 12 resolved: direct numerical corrections.**  
    Recomputed gains are **RQMC 10.596461×**, **RAD32 9.695996×**, **RADQ32 113.011529×**, and **RADQ32/RQMC 15.237165×**. The Gaussian-fidelity ratio is **0.506460–362.453232**. Gate-count medians are **4913** and **1952.5**, and the stationary registered-window rate is **0.04711415**.  
    **Exact fix:** None; retain the stated aggregation and median-rounding conventions.

13. **Minor — Finding 13 partly resolved: scorecard completion and provenance.**  
    Q5–Q7 and the corrected P1 miss are now reported. All **18 hashes**, plus the separate frozen v2 theory hash, match. However, the scorecard still lacks the promised per-test completion/seen–prospective breakdown: several pooled rows contain partial prospective stationary data without row-level marking.

    For the saved scorecard snapshot:

    | Test | Completed ARC + \(n\le64\) stationary | Prospective stationary, interim | Pooled |
    |---|---:|---:|---:|
    | P1, \(\varepsilon=0.1\) | 64/80 | 4/6 | 68/86 |
    | P1, \(\varepsilon=0.01\) | 38/80 | 4/6 | 42/86 |
    | P8, \(\varepsilon=0.1\) | 58/80 | 2/6 | 60/86 |

    **Exact fix:** Add these completion splits, distinguish prospectivity relative to each registration, and mark every affected pooled verdict interim. This concerns labeling, not expected changes from running jobs.

14. **Minor — Finding 14 resolved as a provenance disclosure.**  
    The restoration/drop times now match the logs, missing deviations have evidence pointers, and the guessed embedded times are explicitly acknowledged. That explanation is author-reported; it does not independently establish message receipt times.  
    **Exact fix:** None beyond preserving that distinction.

15. **Minor — Finding 15 resolved: technical definitions.**  
    \(J\), \(K\), empirical-input-mean use, normalized kernel shares, the forward-covariance proxy, and P5’s **12/13** are now specified.  
    **Exact fix:** None.

16. **Minor — Additional numerical problem: the near-ray example is wrong.**  
    [§8](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:264) claims angles within 0.014 radians and cosines 0.9997–0.9999 throughout \(l=64–96\). For the net exhibiting the quoted 11–15% residual—\(n=32\), seed 300—the stored mean cosines range **0.997435–0.999966**; \(\arccos(\text{mean cosine})\) ranges **0.008222–0.071641** radians.  
    **Exact fix:** Name seed 300 and replace the ranges accordingly. Call the angular number “arccos of mean pair cosine”; it is neither a maximum pair angle nor necessarily the mean angle.

17. **Minor — Additional provenance problem: future checked-at time.**  
    [§10](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:303) says “checked … at 23:40Z,” although the reviewed document was hashed at 23:21:05Z and this check finished before 23:25Z.  
    **Exact fix:** Replace 23:40Z with the actual verification time and identify the score-file snapshot used. Do not substitute a planned refresh time.

18. **Minor — Two small numerical consistency corrections.**  
    The measured \(l=16\) degree-1 median is **0.77490574**, so §3’s **0.78** should be **0.77**, agreeing with §4. At \(l=0\), the model/measured degree-1 median difference is **0.07102617**, slightly exceeding §4’s literal “within 0.07.”  
    **Exact fix:** Change those to **0.77** and “within **0.072**” respectively.

19. **Minor — Summary assessment: mostly appropriately qualified, but not fully.**  
    The theorem restrictions, prospective scores, tested-subspace qualification, stationary limitations, and unresolved M1 conclusion now match their evidence. The remaining overstatements are the single-gate attribution, “best” input features, and constant-factor wording identified above.  
    **Exact fix:** Open with: “A heuristic accounting predicts variance, linear share, mean Hermite degree, and tested-subspace counts; its registered ARC criteria passed on two prospective nets. The degree-surrogate comparison is exploratory, and better projections or integration methods remain unresolved.”

**Verdict: minor revision.**
117,931
The revision’s main results survive. **Six first-round findings are resolved; nine are partly resolved.** Remaining corrections are minor. Checked read-only through 2026-11-01 23:24:53 UTC; document SHA-256 begins `dc1184a6`. No files changed. Running stationary cells are not findings.

For resolved items, severity below retains the original severity; otherwise it grades the remaining work.

1. **Minor — Finding 1 partly resolved: M1 conclusion.**  
   The main conclusion now correctly leaves better projections and integration methods unresolved. However, [Summary 4](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:68) still calls the tested coordinates the “best … input features.”  
   **Exact fix:** Replace “best 16, 64 or 128 input features” with “top 16, 64 or 128 active-subspace features tested.” These measurements do not bound the gains achievable with optimal features.

2. **Major — Finding 2 resolved: theorem scope and free-position comparison.**  
   Angular/frozen-Jacobian restrictions and the heuristic extension are now explicit. Independently recomputing measured/predicted participation ratios gives:

   | ARC seed | Ratios at \(l=4,8,16,24,28,31\) | Within 20% |
   |---|---|---:|
   | 4000 | 1.1302, 1.1877, 1.1890, 1.1193, 1.0282, 0.9433 | 6/6 |
   | 4001 | 1.2790, 1.2606, 1.3071, 1.1033, 1.1930, 1.0564 | 3/6 |
   | 4002 | 1.0107, 1.0555, 1.0370, 0.9286, 0.8569, 0.9625 | 6/6 |
   | 4003 | 1.0269, 0.8612, 0.9046, 0.9157, 0.8760, 0.9510 | 6/6 |

   Total **21/24**, median **1.032596**, range **0.856921–1.307080**: all match. **Exact fix:** None.

3. **Minor — Finding 3 partly resolved: radius versus linear feature.**  
   The principal distinction and Gaussian-replacement caveat are fixed. But [§3](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:123) now says the centered-input radius variation “is degree two.” It has degree two **and higher even degrees**. For \(X\sim N(0,I_{256})\), degree two accounts for approximately **99.9026%**, not 100%, of \(\operatorname{Var}\|X\|\).  
   **Exact fix:** Write “its centered Hermite expansion starts at degree two and contains higher even degrees.”

4. **Minor — Finding 4 partly resolved: degree attribution and uncertainty.**  
   The renamed surrogates, negative values, per-net ranges, and separate-median explanation are correct. I reproduced all seven rows’ measured ranges; for example, the even surrogate ranges are **−0.036335–0.188340** at \(l=16\) and **−0.068180–0.138774** at \(l=31\).  
   Two requested corrections remain: the opening still advertises a split into “single-gate terms,” and between-net ranges do not quantify sampling uncertainty. `mehler_curve` shares draws across correlations, but their covariance is not retained.  
   **Exact fix:** Replace the opening’s gate attribution with “degree 1, an even-degree surrogate, and a remainder.” Either supply joint uncertainty estimates or explicitly state that sampling uncertainty for these combinations was not quantified and the comparison is descriptive.

5. **Major — Finding 5 resolved: advertised accuracy.**  
   Independent recomputation gives **Q1 12/14, Q2 13/14, Q3 11/14**. Maximum errors over all ARC cells are **22.191984%, 0.124508, and 46.118478%**, consistent with the rounded revision.  
   **Exact fix:** None.

6. **Minor — Finding 6 partly resolved: count limitations.**  
   The main document and first-chaos figure legends now state the important limitations. I reproduced omitted mass **0.05468722** and Q4 **14/14 at both tolerances**. However, [§5](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:170) still calls the spectrum estimates “debiased,” despite E12 explaining that the subtraction is not generally valid; `results/report_tables.md` still labels them “lower bound.”  
   **Exact fix:** Use “heuristically noise-corrected, uncertified estimates,” and update the generated table header and its generator. Preserve frozen artifacts.

7. **Minor — Finding 7 partly resolved: stationary gate uncertainty.**  
   The provisional label accurately discloses the missing outer-noise uncertainty. The estimator itself remains unchanged: two shared future-noise realizations and an input-row jackknife.  
   **Exact fix:** Keep these results explicitly provisional and state that re-estimation remains outstanding. Before promoting them to uncertainty-qualified results, use independent outer noise pairs and include denominator uncertainty.

8. **Minor — Finding 8 partly resolved: gate counts and denominators.**  
   The corrected denominator and stationary counts reproduce: **four zeros; nonzero importance-order counts 1, 13, 23, 25**. The remaining ambiguity is ordering: the stationary **109–634** range and Summary’s approximately **1,950–4,900** counts refer specifically to importance ordering. Margin-order stationary counts range **126–771**.  
   **Exact fix:** Name importance ordering beside those ranges. Replace “Each sample flips 5–9%” with “Median per-sample flip fractions across nets range from **5.18% to 8.90%** across the reported layers.”

9. **Minor — Finding 9 partly resolved: stationary interpretation.**  
   The prose now correctly distinguishes medians, per-net spread, observed finite-depth residuals, and the top AS direction. But the regenerated [stationary figure](/home/agent/workspaces/mats/work/relevance/figs/fig3_stationary.png) still labels its curves “best single direction.”  
   **Exact fix:** Change those legends in `scratch/figs_accounting.py` to “top active-subspace direction” and regenerate the figure.

10. **Major — Finding 10 resolved: synchronization thresholds.**  
    Recomputed persistent \(10^{-3}\) crossings are **100, 32, 176, 80**, in the stated net order. Final residuals are **\(9.7228\times10^{-9}\), \(1.0821\times10^{-22}\), \(4.3731\times10^{-15}\), \(1.5948\times10^{-20}\)**. The corrected \(n=32\), seed-301 value at \(4n\) is **\(3.12998\times10^{-5}\)**.  
    **Exact fix:** None to these corrections; see item 16 for another synchronization paragraph.

11. **Minor — Finding 11 partly resolved: estimator claims.**  
    Nominal cost, excluded setup, reference uncertainty, exploratory status, and finite-budget slopes are correctly disclosed. Recomputed median slopes are **1.0277, 1.2729, 1.0261, 1.1913, 0.9935**. Nevertheless, [§9](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:272) still turns approximate synchronization into the exact equality \(a(x)=|h_{32}(x)|g(u^*)\). Repetition-level uncertainty remains unavailable.  
    **Exact fix:** Use \(\approx\), identify this as the truncated estimator’s approximation, and state that stored repetition averages do not support reconstructed confidence intervals. In the Summary, replace “by a constant factor” with “by the measured factors at the reported budget.”

12. **Minor — Finding 12 resolved: direct numerical corrections.**  
    Recomputed gains are **RQMC 10.596461×**, **RAD32 9.695996×**, **RADQ32 113.011529×**, and **RADQ32/RQMC 15.237165×**. The Gaussian-fidelity ratio is **0.506460–362.453232**. Gate-count medians are **4913** and **1952.5**, and the stationary registered-window rate is **0.04711415**.  
    **Exact fix:** None; retain the stated aggregation and median-rounding conventions.

13. **Minor — Finding 13 partly resolved: scorecard completion and provenance.**  
    Q5–Q7 and the corrected P1 miss are now reported. All **18 hashes**, plus the separate frozen v2 theory hash, match. However, the scorecard still lacks the promised per-test completion/seen–prospective breakdown: several pooled rows contain partial prospective stationary data without row-level marking.

    For the saved scorecard snapshot:

    | Test | Completed ARC + \(n\le64\) stationary | Prospective stationary, interim | Pooled |
    |---|---:|---:|---:|
    | P1, \(\varepsilon=0.1\) | 64/80 | 4/6 | 68/86 |
    | P1, \(\varepsilon=0.01\) | 38/80 | 4/6 | 42/86 |
    | P8, \(\varepsilon=0.1\) | 58/80 | 2/6 | 60/86 |

    **Exact fix:** Add these completion splits, distinguish prospectivity relative to each registration, and mark every affected pooled verdict interim. This concerns labeling, not expected changes from running jobs.

14. **Minor — Finding 14 resolved as a provenance disclosure.**  
    The restoration/drop times now match the logs, missing deviations have evidence pointers, and the guessed embedded times are explicitly acknowledged. That explanation is author-reported; it does not independently establish message receipt times.  
    **Exact fix:** None beyond preserving that distinction.

15. **Minor — Finding 15 resolved: technical definitions.**  
    \(J\), \(K\), empirical-input-mean use, normalized kernel shares, the forward-covariance proxy, and P5’s **12/13** are now specified.  
    **Exact fix:** None.

16. **Minor — Additional numerical problem: the near-ray example is wrong.**  
    [§8](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:264) claims angles within 0.014 radians and cosines 0.9997–0.9999 throughout \(l=64–96\). For the net exhibiting the quoted 11–15% residual—\(n=32\), seed 300—the stored mean cosines range **0.997435–0.999966**; \(\arccos(\text{mean cosine})\) ranges **0.008222–0.071641** radians.  
    **Exact fix:** Name seed 300 and replace the ranges accordingly. Call the angular number “arccos of mean pair cosine”; it is neither a maximum pair angle nor necessarily the mean angle.

17. **Minor — Additional provenance problem: future checked-at time.**  
    [§10](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:303) says “checked … at 23:40Z,” although the reviewed document was hashed at 23:21:05Z and this check finished before 23:25Z.  
    **Exact fix:** Replace 23:40Z with the actual verification time and identify the score-file snapshot used. Do not substitute a planned refresh time.

18. **Minor — Two small numerical consistency corrections.**  
    The measured \(l=16\) degree-1 median is **0.77490574**, so §3’s **0.78** should be **0.77**, agreeing with §4. At \(l=0\), the model/measured degree-1 median difference is **0.07102617**, slightly exceeding §4’s literal “within 0.07.”  
    **Exact fix:** Change those to **0.77** and “within **0.072**” respectively.

19. **Minor — Summary assessment: mostly appropriately qualified, but not fully.**  
    The theorem restrictions, prospective scores, tested-subspace qualification, stationary limitations, and unresolved M1 conclusion now match their evidence. The remaining overstatements are the single-gate attribution, “best” input features, and constant-factor wording identified above.  
    **Exact fix:** Open with: “A heuristic accounting predicts variance, linear share, mean Hermite degree, and tested-subspace counts; its registered ARC criteria passed on two prospective nets. The degree-surrogate comparison is exploratory, and better projections or integration methods remain unresolved.”

**Verdict: minor revision.**
