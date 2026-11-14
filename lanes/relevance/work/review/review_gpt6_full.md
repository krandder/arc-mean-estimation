The draft needs major revision. Its strongest results are useful measurements and conditional theory; they do not establish the claimed M1 blocker. Checked against the supplied files on 2026-11-01, approximately 23:12–23:18 UTC, using read-only, single-threaded computations. No files changed.

1. **Major — The headline M1 conclusion exceeds the evidence.**  
   The [Summary](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:18) says the accounting “closes at every layer” and explains why sampling cannot be beaten; §9 says ARC “offers no small description” and a better basis could do “somewhat” better. Exhibited subspaces give upper bounds on optimal dimension, not evidence limiting how much better another basis could be. The nonlinear lower bound assumes properties not established for these networks. The distinction between predictive dimension and integration cost is correctly acknowledged, but contradicted by these stronger statements.

   **Exact fix:** Replace the headline and concluding claim with: “The tested subspaces require many coordinates for 99% predictive capture under fitted Gaussian clouds at ARC’s shape. Whether better future-informed projections or integration methods beat sampling remains unresolved. The missing result is a certified nonlinear lower bound for these networks, followed by an appropriate computational-cost argument.”

2. **Major — The Summary promotes a heuristic free-product model into the theorem.**  
   [Summary 1](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:22) extends equal expected amplification to “every past-measurable direction” and calls the free product “the right object.” The theorem concerns angular directions and the **frozen Jacobian at a nonzero mean**. Its extension to the cloud-averaged Jacobian is HEURISTIC. The quoted participation-ratio agreement concerns six cuts of the first ARC net, not every layer of all four nets.

   **Exact fix:** State the angular/frozen-Jacobian restriction in the Summary; label the averaged-Jacobian free-product model HEURISTIC. Replace “within 20% at every layer” with “within 20% at the six reported non-input cuts of seed 4000; 37/53 cells within 1.5× in the reported broader comparison.”

3. **Major — Radius, a linear radial feature, and Gaussian first chaos are conflated.**  
   [Summary 2 and §3](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:31) still say radius is “one direction, linear,” despite errata E7/E13. Actual radius \(\|X\|\) is nonlinear; at the centered Gaussian input its variation is not first chaos. The measured “radial share” uses conditioning on \(e^\top X\), not radius itself. Also, only the **true-law** noiseless output variance must be cut-independent; the tabulated Gaussianized variance need not be.

   **Exact fix:** Name the measured feature \(e^\top X\), distinguish it from \(\|X\|\), and restrict their approximate equivalence to thin clouds or synchronized rays. Replace “flat … as it must be” with “approximately flat empirically under Gaussian replacement.” Describe the channel decomposition as nonorthogonal and heuristic.

4. **Major — Hermite degrees do not identify gate interactions, and their uncertainty is substantial.**  
   [§4](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:146) labels the rows “single gates” and “interactions.” Higher degrees also contain single-gate tails; degree two contains cross-gate contributions. The Mehler combination estimates an upper surrogate for degree two, not a confidence upper bound. Raw estimates include \(s_{2,u}=-0.06347\) at seed 4003, \(l=24\), and \(-0.06818\) at seed 4002, \(l=31\). Separately taking medians also makes the displayed shares sum to 1.05 at \(l=24\).

   **Exact fix:** Rename the rows “degree 1,” “even-degree surrogate \(s_2+s_4/4+\cdots\),” and “lower surrogate for degree ≥3.” Remove “interactions dominate” as a measured attribution. Supply uncertainty accounting for covariance between Mehler measurements, per-net values, and the separate-median explanation.

5. **Major — The accuracy advertised in the Summary is stronger than the actual validation.**  
   [Summary 2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:36) promises approximately 10% budget error, 0.07 linear-share error, and 20% degree error “at every layer.” Across the 28 ARC cells, the maximum errors are **22.19%, 0.12451, and 46.12%**, respectively. Even the median degree predictions at \(l=0,4\) underestimate by approximately 24.5% and 25.9%.

   **Exact fix:** Replace that sentence with the registered prospective results and their actual bands: budget **12/14 within 20%**, linear share **13/14 within 0.08**, and degree **11/14 within [0.75, 1.33]**. Keep the first-net examples explicitly scoped to that net.

6. **Major — The count presentation still conceals important estimator and model limitations.**  
   [§5](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:158) correctly calls first-chaos estimates uncertified, but the figure-generation code labels them “lower bound.” Part 1 counts use point-estimated residual thresholds, so they are not confidence-certified upper bounds either. The “7–30” first-chaos counts use a tail tolerance of \(0.01V\), not \(0.01V_1\). Moreover, v2 discards **0.0546872 of predicted total variance** above degree 60 at ARC seed 4000’s input, exceeding the 1% target.

   **Exact fix:** Label measured counts “point-estimated counts for exhibited subspaces,” and every numerical first-chaos curve “uncertified first-chaos estimate.” State the normalization \( \sum_{j>k}\lambda_j(C_1)\le\varepsilon V\). Explicitly disclose the omitted chaos mass and incompatible subspace allocations from E17 beside the v2 count results; preserve frozen scores and label any repaired prediction post hoc.

7. **Major — Amendment 2A did not fix stationary gate-count uncertainty.**  
   In [gate_count](/home/agent/workspaces/mats/work/relevance/lib/gates.py:114), only two future-noise realizations are sampled, each shared across all evaluation inputs. The jackknife varies input rows while holding those realizations fixed. It therefore omits outer future-noise variation, precisely the issue identified in co-prover round 2, T2. Adding twice this SE does not provide the claimed uncertainty protection for the noise-averaged gate residual.

   **Exact fix:** Mark stationary gate counts provisional with incomplete uncertainty. Re-estimate using independent outer noise pairs and an uncertainty calculation covering that dimension; include denominator uncertainty if making confidence claims. Keep the corrected cross-realization subtraction, which addresses a separate problem.

8. **Major — Several gate conclusions are false or use the wrong denominator.**  
   [§6](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:197) says every stationary cell needs zero gates at \(\varepsilon=0.1\). Raw amended-rule counts are nonzero in **4/8 cells**: **1, 25, 13, 23**. The “24–56 directions at 90%” claim also misreads \(N_{\ge2}(0.1)\): its residual threshold is \(0.1V\), not 10% of nonlinear variance. Finally, tested prefixes of two orderings do not establish how many gates “must” switch under optimal selection, nor the rank of their normals.

   **Exact fix:** Report zero-gate success as **4/8**, with the other counts. Say “nonlinear residual ≤10% of total relevant variance.” Describe \(G\) as the smallest **tested prefix count for the specified ordering**, and remove inferred necessity and normal-span claims unless separately measured.

9. **Major — Stationary summaries hide spread and overstate a finite-depth observation as a floor.**  
   [Summary 3 and §7](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:214) give residual ranges resembling medians over nets without saying so. Across resolved \(n=32,64\), \(t=16,32\) cells, the top-AS-direction residual ranges from **0.01014 to 0.25008**, and the radial-feature residual from **0.10340 to 0.85300**. A finite-depth residual does not establish an asymptotic floor, and the selected AS direction is not proven optimal or identified as a particular slow response.

   **Exact fix:** Label median ranges explicitly and give per-net ranges. Replace “floor” with “observed residual at these depths,” and “best single direction” with “top active-subspace direction.” Report PS1 as **13/16 already-seen eligible cells passing at 10%, 0/8 at 1%**, with prospective results separate.

10. **Major — The synchronization conclusion contradicts its own runs.**  
    [§8](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:236) claims \(10^{-3}\) accuracy from roughly \(2–4n\), then \(10^{-20}\) a few widths later. Persistent \(10^{-3}\) crossings occur at **\(l=100=6.25n\)** for \(n=16\), seed 300, and **\(l=176=5.5n\)** for \(n=32\), seed 300. Those nets end at residuals **\(9.72\times10^{-9}\)** and **\(4.37\times10^{-15}\)**, respectively, never reaching \(10^{-20}\) on the measured grid. The \(n=32\), seed 301 table entry at \(4n\) is **\(3.13\times10^{-5}\)**, not \(<10^{-5}\).

    **Exact fix:** Report the four measured threshold-crossing depths and retain PS2(a)’s actual supported conclusion: residual ≤0.05 from \(4n\). Remove universal exact-collapse language and correct the table entry. In the Summary, say the six \(n=8\) nets reach \(10^{-5}\) by \(l=32\), rather than suggesting this holds from \(l\approx16\).

11. **Major — The narrow-deep experiment supports a finite-budget gain, not all the estimator claims.**  
    [§9](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:248) calls the comparison equal-compute, but `est_nd.py` excludes 64 pilot paths and the shared tail pass: **2,272 additional layer-matvecs** at \(l=32\). This is small at \(2^{20}\), substantial at \(2^{12}\). Its “bias” estimate compares two finite Monte Carlo means and cannot isolate deterministic bias. Repetition-level errors are discarded. “Every method” having rate \(1/\text{compute}\) is also too categorical: fitted median exponents over the stored budgets are approximately **1.27 for RQMC** and **1.19 for RADQ32**.

    **Exact fix:** Call the current comparison equal **nominal sampling cost**, disclose setup cost and reference uncertainty, and label the bias column “squared discrepancy between finite-sample estimates.” Retain repetition-level outputs for intervals in a follow-up. Report finite-budget slopes without an asymptotic rate claim. Explicitly label this estimator experiment exploratory/post hoc; Parts 1–3 do not register it.

12. **Minor — Independently recomputed numbers identify several direct corrections.**  
    These checks used the raw runs, not just copied report tables:

    | Quantity | Recomputed | Assessment / exact fix |
    |---|---:|---|
    | ARC \(l=0\), median \(V^\gamma/E_\mu\|a\|^2\) | 0.05714942 | Matches 0.0571 |
    | ARC \(l=8\), median linear share | 0.61447633 | Matches 0.61 |
    | ARC \(l=16\), median radial-feature share | 0.44569804 | Matches 0.45 |
    | ARC \(l=24\), degree-two surrogate | 0.05806195 | Matches 0.06; uncertainty issue remains |
    | Narrow-deep RAD32 gain | 9.695996× | Matches 9.7× |
    | Narrow-deep RADQ32 gain | 113.011529× | Matches 113× |
    | Narrow-deep RQMC median per-net gain | **10.596461×** | Replace **7.8×**; that uses a different aggregation |
    | Stationary \(n=64\), registered-window median decay rate | **0.04711415** | Replace §7’s **0.040**; §10 is correct |
    | Part 2, \(l=8\), median importance \(G(0.01)\) | **4913** | Matches |
    | Part 2, \(l=16\), median importance \(G(0.01)\) | **1952.5** | Matches rounded 1952; identify medians as possibly non-grid values |
    | Gate-flip percentages, \(l=8,16,24,31\) | **8.90%, 6.99%, 5.68%, 5.18%** | Replace “about 2%” |
    | ARC input AS-control gains, \(k=16,64,128\) | **1.3283, 1.7959, 3.1058×** | Replace Summary’s interim 1.3, 1.9, 3.3 with §9’s values |

    Additionally, §8’s unspecified Gaussian-fidelity ratio “0.01–1.9” does not reproduce. Across narrow-deep cells with \(l\ge32\), **\(V^\gamma/V^\mu=0.50646–362.45323\)**; the reciprocal is **0.002759–1.97449**. Specify the ratio orientation and report the corresponding range.

13. **Major — Preregistration artifacts are intact, but the reporting of prospective results is incomplete.**  
    All **18 recorded preregistration hashes** matched their frozen artifacts; the separately frozen v2 theory also matched. The live Part 1 analysis differs only by the disclosed angular-spectrum field. The draft reports the main registered misses and acknowledges the design changes, biased \(N_1\), and Amendment 2A.

    However, [§10](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:284) pools partial prospective stationary cells into Part 1 percentages while broadly marking larger widths pending. The saved Part 3 scores already contain **Q6 = 1/2**, below its 75% target, albeit interim; that should appear alongside the other interim results. “69% with the unbiased U-statistic count” is also misleading: the thresholded count is not unbiased, and **59/86 = 68.60% still misses P1’s 75% target**.

    **Exact fix:** Add a checked-at completion manifest and report numerator/denominator, seen/prospective status, and complete/interim status for each test. Include Q5–Q7 explicitly, without treating interim failures as final. Call corrected P1 a post hoc alternative count and explicitly retain its miss.

14. **Minor — The process chronology needs reconciliation.**  
    The stationary restoration and final drop are logged at **21:50:32Z** and **22:53:08Z**, versus 21:52 and 22:55 in the document. `logs/deviations.txt` does not contain every deviation claimed to be there. More substantially, the frozen Part 2 text attributed to **21:36:43Z** mentions requests at **21:40Z and 21:45Z**. Hash agreement establishes artifact consistency, not the chronology of those embedded timestamps.

    **Exact fix:** Correct times against primary logs, link evidence for each deviation, and reconcile the internally inconsistent Part 2 timestamps. Say “before any Part 2 measurement,” not “before any run.” This is a provenance ambiguity, not evidence by itself of retrospective registration.

15. **Minor — Several technical descriptions need precise replacements.**  
    In [§2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:93), define \(J\) as the frozen Jacobian and define \(K\); explain that the exact input mean is zero, where this linearization is generally unavailable. The reported input calculation uses an empirical mean. In §4, normalized kernel shares require the coefficient normalization by \(1-\kappa^{(t)}(c_l)\). In §2, “cloud axes need 163–253 directions for degree-one variance” is not what `N1_free_product` computes: its PCA comparator counts **cloud covariance variance**.

    **Exact fix:** Make these substitutions explicitly; label the PCA number a forward-covariance proxy unless actual first-chaos capture in that basis is measured. Replace §2’s unexplained “P5: 7/7” with the applicable registered result, **12/13**, or identify the different subset.

The population projection bounds, several prospective ARC predictions, and the narrow-deep finite-budget gains survive review. The claimed fundamental obstruction does not.

**Verdict: major revision.**
137,910
The draft needs major revision. Its strongest results are useful measurements and conditional theory; they do not establish the claimed M1 blocker. Checked against the supplied files on 2026-11-01, approximately 23:12–23:18 UTC, using read-only, single-threaded computations. No files changed.

1. **Major — The headline M1 conclusion exceeds the evidence.**  
   The [Summary](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:18) says the accounting “closes at every layer” and explains why sampling cannot be beaten; §9 says ARC “offers no small description” and a better basis could do “somewhat” better. Exhibited subspaces give upper bounds on optimal dimension, not evidence limiting how much better another basis could be. The nonlinear lower bound assumes properties not established for these networks. The distinction between predictive dimension and integration cost is correctly acknowledged, but contradicted by these stronger statements.

   **Exact fix:** Replace the headline and concluding claim with: “The tested subspaces require many coordinates for 99% predictive capture under fitted Gaussian clouds at ARC’s shape. Whether better future-informed projections or integration methods beat sampling remains unresolved. The missing result is a certified nonlinear lower bound for these networks, followed by an appropriate computational-cost argument.”

2. **Major — The Summary promotes a heuristic free-product model into the theorem.**  
   [Summary 1](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:22) extends equal expected amplification to “every past-measurable direction” and calls the free product “the right object.” The theorem concerns angular directions and the **frozen Jacobian at a nonzero mean**. Its extension to the cloud-averaged Jacobian is HEURISTIC. The quoted participation-ratio agreement concerns six cuts of the first ARC net, not every layer of all four nets.

   **Exact fix:** State the angular/frozen-Jacobian restriction in the Summary; label the averaged-Jacobian free-product model HEURISTIC. Replace “within 20% at every layer” with “within 20% at the six reported non-input cuts of seed 4000; 37/53 cells within 1.5× in the reported broader comparison.”

3. **Major — Radius, a linear radial feature, and Gaussian first chaos are conflated.**  
   [Summary 2 and §3](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:31) still say radius is “one direction, linear,” despite errata E7/E13. Actual radius \(\|X\|\) is nonlinear; at the centered Gaussian input its variation is not first chaos. The measured “radial share” uses conditioning on \(e^\top X\), not radius itself. Also, only the **true-law** noiseless output variance must be cut-independent; the tabulated Gaussianized variance need not be.

   **Exact fix:** Name the measured feature \(e^\top X\), distinguish it from \(\|X\|\), and restrict their approximate equivalence to thin clouds or synchronized rays. Replace “flat … as it must be” with “approximately flat empirically under Gaussian replacement.” Describe the channel decomposition as nonorthogonal and heuristic.

4. **Major — Hermite degrees do not identify gate interactions, and their uncertainty is substantial.**  
   [§4](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:146) labels the rows “single gates” and “interactions.” Higher degrees also contain single-gate tails; degree two contains cross-gate contributions. The Mehler combination estimates an upper surrogate for degree two, not a confidence upper bound. Raw estimates include \(s_{2,u}=-0.06347\) at seed 4003, \(l=24\), and \(-0.06818\) at seed 4002, \(l=31\). Separately taking medians also makes the displayed shares sum to 1.05 at \(l=24\).

   **Exact fix:** Rename the rows “degree 1,” “even-degree surrogate \(s_2+s_4/4+\cdots\),” and “lower surrogate for degree ≥3.” Remove “interactions dominate” as a measured attribution. Supply uncertainty accounting for covariance between Mehler measurements, per-net values, and the separate-median explanation.

5. **Major — The accuracy advertised in the Summary is stronger than the actual validation.**  
   [Summary 2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:36) promises approximately 10% budget error, 0.07 linear-share error, and 20% degree error “at every layer.” Across the 28 ARC cells, the maximum errors are **22.19%, 0.12451, and 46.12%**, respectively. Even the median degree predictions at \(l=0,4\) underestimate by approximately 24.5% and 25.9%.

   **Exact fix:** Replace that sentence with the registered prospective results and their actual bands: budget **12/14 within 20%**, linear share **13/14 within 0.08**, and degree **11/14 within [0.75, 1.33]**. Keep the first-net examples explicitly scoped to that net.

6. **Major — The count presentation still conceals important estimator and model limitations.**  
   [§5](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:158) correctly calls first-chaos estimates uncertified, but the figure-generation code labels them “lower bound.” Part 1 counts use point-estimated residual thresholds, so they are not confidence-certified upper bounds either. The “7–30” first-chaos counts use a tail tolerance of \(0.01V\), not \(0.01V_1\). Moreover, v2 discards **0.0546872 of predicted total variance** above degree 60 at ARC seed 4000’s input, exceeding the 1% target.

   **Exact fix:** Label measured counts “point-estimated counts for exhibited subspaces,” and every numerical first-chaos curve “uncertified first-chaos estimate.” State the normalization \( \sum_{j>k}\lambda_j(C_1)\le\varepsilon V\). Explicitly disclose the omitted chaos mass and incompatible subspace allocations from E17 beside the v2 count results; preserve frozen scores and label any repaired prediction post hoc.

7. **Major — Amendment 2A did not fix stationary gate-count uncertainty.**  
   In [gate_count](/home/agent/workspaces/mats/work/relevance/lib/gates.py:114), only two future-noise realizations are sampled, each shared across all evaluation inputs. The jackknife varies input rows while holding those realizations fixed. It therefore omits outer future-noise variation, precisely the issue identified in co-prover round 2, T2. Adding twice this SE does not provide the claimed uncertainty protection for the noise-averaged gate residual.

   **Exact fix:** Mark stationary gate counts provisional with incomplete uncertainty. Re-estimate using independent outer noise pairs and an uncertainty calculation covering that dimension; include denominator uncertainty if making confidence claims. Keep the corrected cross-realization subtraction, which addresses a separate problem.

8. **Major — Several gate conclusions are false or use the wrong denominator.**  
   [§6](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:197) says every stationary cell needs zero gates at \(\varepsilon=0.1\). Raw amended-rule counts are nonzero in **4/8 cells**: **1, 25, 13, 23**. The “24–56 directions at 90%” claim also misreads \(N_{\ge2}(0.1)\): its residual threshold is \(0.1V\), not 10% of nonlinear variance. Finally, tested prefixes of two orderings do not establish how many gates “must” switch under optimal selection, nor the rank of their normals.

   **Exact fix:** Report zero-gate success as **4/8**, with the other counts. Say “nonlinear residual ≤10% of total relevant variance.” Describe \(G\) as the smallest **tested prefix count for the specified ordering**, and remove inferred necessity and normal-span claims unless separately measured.

9. **Major — Stationary summaries hide spread and overstate a finite-depth observation as a floor.**  
   [Summary 3 and §7](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:214) give residual ranges resembling medians over nets without saying so. Across resolved \(n=32,64\), \(t=16,32\) cells, the top-AS-direction residual ranges from **0.01014 to 0.25008**, and the radial-feature residual from **0.10340 to 0.85300**. A finite-depth residual does not establish an asymptotic floor, and the selected AS direction is not proven optimal or identified as a particular slow response.

   **Exact fix:** Label median ranges explicitly and give per-net ranges. Replace “floor” with “observed residual at these depths,” and “best single direction” with “top active-subspace direction.” Report PS1 as **13/16 already-seen eligible cells passing at 10%, 0/8 at 1%**, with prospective results separate.

10. **Major — The synchronization conclusion contradicts its own runs.**  
    [§8](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:236) claims \(10^{-3}\) accuracy from roughly \(2–4n\), then \(10^{-20}\) a few widths later. Persistent \(10^{-3}\) crossings occur at **\(l=100=6.25n\)** for \(n=16\), seed 300, and **\(l=176=5.5n\)** for \(n=32\), seed 300. Those nets end at residuals **\(9.72\times10^{-9}\)** and **\(4.37\times10^{-15}\)**, respectively, never reaching \(10^{-20}\) on the measured grid. The \(n=32\), seed 301 table entry at \(4n\) is **\(3.13\times10^{-5}\)**, not \(<10^{-5}\).

    **Exact fix:** Report the four measured threshold-crossing depths and retain PS2(a)’s actual supported conclusion: residual ≤0.05 from \(4n\). Remove universal exact-collapse language and correct the table entry. In the Summary, say the six \(n=8\) nets reach \(10^{-5}\) by \(l=32\), rather than suggesting this holds from \(l\approx16\).

11. **Major — The narrow-deep experiment supports a finite-budget gain, not all the estimator claims.**  
    [§9](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:248) calls the comparison equal-compute, but `est_nd.py` excludes 64 pilot paths and the shared tail pass: **2,272 additional layer-matvecs** at \(l=32\). This is small at \(2^{20}\), substantial at \(2^{12}\). Its “bias” estimate compares two finite Monte Carlo means and cannot isolate deterministic bias. Repetition-level errors are discarded. “Every method” having rate \(1/\text{compute}\) is also too categorical: fitted median exponents over the stored budgets are approximately **1.27 for RQMC** and **1.19 for RADQ32**.

    **Exact fix:** Call the current comparison equal **nominal sampling cost**, disclose setup cost and reference uncertainty, and label the bias column “squared discrepancy between finite-sample estimates.” Retain repetition-level outputs for intervals in a follow-up. Report finite-budget slopes without an asymptotic rate claim. Explicitly label this estimator experiment exploratory/post hoc; Parts 1–3 do not register it.

12. **Minor — Independently recomputed numbers identify several direct corrections.**  
    These checks used the raw runs, not just copied report tables:

    | Quantity | Recomputed | Assessment / exact fix |
    |---|---:|---|
    | ARC \(l=0\), median \(V^\gamma/E_\mu\|a\|^2\) | 0.05714942 | Matches 0.0571 |
    | ARC \(l=8\), median linear share | 0.61447633 | Matches 0.61 |
    | ARC \(l=16\), median radial-feature share | 0.44569804 | Matches 0.45 |
    | ARC \(l=24\), degree-two surrogate | 0.05806195 | Matches 0.06; uncertainty issue remains |
    | Narrow-deep RAD32 gain | 9.695996× | Matches 9.7× |
    | Narrow-deep RADQ32 gain | 113.011529× | Matches 113× |
    | Narrow-deep RQMC median per-net gain | **10.596461×** | Replace **7.8×**; that uses a different aggregation |
    | Stationary \(n=64\), registered-window median decay rate | **0.04711415** | Replace §7’s **0.040**; §10 is correct |
    | Part 2, \(l=8\), median importance \(G(0.01)\) | **4913** | Matches |
    | Part 2, \(l=16\), median importance \(G(0.01)\) | **1952.5** | Matches rounded 1952; identify medians as possibly non-grid values |
    | Gate-flip percentages, \(l=8,16,24,31\) | **8.90%, 6.99%, 5.68%, 5.18%** | Replace “about 2%” |
    | ARC input AS-control gains, \(k=16,64,128\) | **1.3283, 1.7959, 3.1058×** | Replace Summary’s interim 1.3, 1.9, 3.3 with §9’s values |

    Additionally, §8’s unspecified Gaussian-fidelity ratio “0.01–1.9” does not reproduce. Across narrow-deep cells with \(l\ge32\), **\(V^\gamma/V^\mu=0.50646–362.45323\)**; the reciprocal is **0.002759–1.97449**. Specify the ratio orientation and report the corresponding range.

13. **Major — Preregistration artifacts are intact, but the reporting of prospective results is incomplete.**  
    All **18 recorded preregistration hashes** matched their frozen artifacts; the separately frozen v2 theory also matched. The live Part 1 analysis differs only by the disclosed angular-spectrum field. The draft reports the main registered misses and acknowledges the design changes, biased \(N_1\), and Amendment 2A.

    However, [§10](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:284) pools partial prospective stationary cells into Part 1 percentages while broadly marking larger widths pending. The saved Part 3 scores already contain **Q6 = 1/2**, below its 75% target, albeit interim; that should appear alongside the other interim results. “69% with the unbiased U-statistic count” is also misleading: the thresholded count is not unbiased, and **59/86 = 68.60% still misses P1’s 75% target**.

    **Exact fix:** Add a checked-at completion manifest and report numerator/denominator, seen/prospective status, and complete/interim status for each test. Include Q5–Q7 explicitly, without treating interim failures as final. Call corrected P1 a post hoc alternative count and explicitly retain its miss.

14. **Minor — The process chronology needs reconciliation.**  
    The stationary restoration and final drop are logged at **21:50:32Z** and **22:53:08Z**, versus 21:52 and 22:55 in the document. `logs/deviations.txt` does not contain every deviation claimed to be there. More substantially, the frozen Part 2 text attributed to **21:36:43Z** mentions requests at **21:40Z and 21:45Z**. Hash agreement establishes artifact consistency, not the chronology of those embedded timestamps.

    **Exact fix:** Correct times against primary logs, link evidence for each deviation, and reconcile the internally inconsistent Part 2 timestamps. Say “before any Part 2 measurement,” not “before any run.” This is a provenance ambiguity, not evidence by itself of retrospective registration.

15. **Minor — Several technical descriptions need precise replacements.**  
    In [§2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:93), define \(J\) as the frozen Jacobian and define \(K\); explain that the exact input mean is zero, where this linearization is generally unavailable. The reported input calculation uses an empirical mean. In §4, normalized kernel shares require the coefficient normalization by \(1-\kappa^{(t)}(c_l)\). In §2, “cloud axes need 163–253 directions for degree-one variance” is not what `N1_free_product` computes: its PCA comparator counts **cloud covariance variance**.

    **Exact fix:** Make these substitutions explicitly; label the PCA number a forward-covariance proxy unless actual first-chaos capture in that basis is measured. Replace §2’s unexplained “P5: 7/7” with the applicable registered result, **12/13**, or identify the different subset.

The population projection bounds, several prospective ARC predictions, and the narrow-deep finite-budget gains survive review. The claimed fundamental obstruction does not.

**Verdict: major revision.**
