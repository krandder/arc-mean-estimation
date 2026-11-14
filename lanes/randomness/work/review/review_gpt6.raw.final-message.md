<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/randomness/review/review_gpt6.raw -->

**Needs revision before Kelvin. No critical numerical corruption found, but several major claims exceed the theory or data.** Checked 2026-11-02 at 16:00 UTC; no files modified. I reproduced the scorers, rates, tables, and tradeoff results in memory from `runs/`; they match the saved outputs.

1. **MAJOR — The verdict turns an optimal-rate bound and particular design limits into universal claims.**  
   [randomness.md:27](/home/agent/workspaces/mats/work/randomness/randomness.md:27): “any point set … has exponent in [1 + 2/(n-1), 1 + 3/(n-1)].”  
   [randomness.md:59](/home/agent/workspaces/mats/work/randomness/randomness.md:59): “proven cap … constant ~3.”

   FORMAL E2.2 bounds the **optimal** exponent among positive, weight-independent spherical rules. Individual rules can have exponent 1, or worse. Likewise, 3.15 is Kerdock’s limiting ensemble gain, not an upper bound for all rules. E2.4 excludes gains diverging with width at a **fixed polynomial budget exponent**; it does not establish a universal constant of three. Its ensemble ratios also are not medians of per-net ratios.

   **Fix:** State the optimal exponent window with its hypotheses; say “best measured median gain: 2.89x; Kerdock’s numerically evaluated ensemble limit: 3.15x.” Restrict “exponent exactly 1” to independent rotations of a **fixed** base design. Separate fixed-width, increasing-budget asymptotics from the joint width/depth limit.

2. **MAJOR — “Proven ceiling 9.6–18.8x” is an uncertain plug-in estimate.**  
   [randomness.md:321](/home/agent/workspaces/mats/work/randomness/randomness.md:321): “The proven black-box ceiling … 9.6–18.8x.”

   [report_tables.py:44](/home/agent/workspaces/mats/work/randomness/scratch/report_tables.py:44) estimates the even-degree tail as half Kerdock’s normalized rotation variance. Consequently, every displayed ceiling is **exactly four times the measured E1 Kerdock gain**, by construction. These are 12-rotation estimates; their stored relative standard errors are approximately 8–18%.

   Moreover, the spectral proxy is not exact. Recomputing the stated Kerdock aliasing formula gives \(NB_6/2=1.031018\), rather than 1. FORMAL E2.1 explicitly acknowledges aliasing errors and requires summing qualifying degrees; numerical minima for degrees 4, 6, and 8 alone do not certify the entire infinite tail.

   **Fix:** Label these “estimated ceilings from spectral proxies,” with uncertainty and aliasing corrections. A certified numerical ceiling requires a lower confidence bound on the actual qualifying spectral energy. Retain the distinction between ensemble guarantees and per-net guarantees averaged over Haar rotations.

3. **MAJOR — The exponent interpretation contradicts the reported intervals.**  
   [randomness.md:535](/home/agent/workspaces/mats/work/randomness/randomness.md:535): “no measured exponent differs from 1.”  
   [randomness.md:233](/home/agent/workspaces/mats/work/randomness/randomness.md:233): “No structured sampler beats RQMC’s exponent.”

   The reproduced intervals for standard RQMC, `[1.031, 1.076]`, and polar RQMC, `[1.008, 1.075]`, exclude 1. Several deterministic point estimates exceed RQMC’s; overlapping intervals do not establish equality or an ordering. The paired polar-minus-standard interval supports **no detected difference**, not proof of no effect. These are finite-range fits, not established asymptotic exponents.

   **Fix:** Report “small positive finite-range excess over MC; no demonstrated substantial exponent improvement from alignment.” Label the broader no-improvement claim CONJECTURE. Describe the bootstrap as uncertainty across five fitted net estimates; avoid treating it as an equivalence test.

4. **MAJOR — The zero-randomness conclusion drops essential qualifications.**  
   [randomness.md:32](/home/agent/workspaces/mats/work/randomness/randomness.md:32): “Proven: … seeds read off the weights simulate any randomised estimator.”  
   [randomness.md:511](/home/agent/workspaces/mats/work/randomness/randomness.md:511): “It takes ‘derandomisation’ off the table (PROVEN).”

   T3 is an existential ensemble-risk result; it supplies neither an efficient construction nor a short description. Simulation from weights is **PROVEN UNDER exact factorisation, probability-transform, and digit-splitting primitives**. The co-prover explicitly excludes unlimited bit extraction from finite-precision weights. An unbiased replicate variance also does not automatically supply a confidence interval with reliable coverage.

   Additionally, “a fixed point set is as good as its randomised version (T2)” at line 272 applies to **Haar rotation**, not arbitrary Sobol scrambling or weight-dependent alignment.

   **Fix:** Keep those qualifications in the summary and verdict. Replace the categorical dismissal with “runtime randomness alone does not distinguish these estimators under the ensemble-risk model.” Distinguish support-index length, runtime random bits, construction cost, and uncertainty estimation.

5. **MAJOR — Two white-box exclusions retain corrections the co-prover explicitly rejected.**  
   [randomness.md:52](/home/agent/workspaces/mats/work/randomness/randomness.md:52): “first-layer controls repeat what a 2-design does; no exact linear tail exists (every input flips some last-layer gate).”

   FORMAL E2.1 says exact control redundancy is wrong: \(|z_i|\), ReLU, \(z_i|z_i|\), and activation-norm features have higher harmonics. Section 4.6 nevertheless says “all of it” is degree 1–2 and “Redundant with designs.”

   The tail claim also contradicts `runs/tail_check_n256_L32.json`: net 200 has last-layer majority-mask agreement on **16/4,096 inputs**. No sampled input matches the majority mask across the last **two** layers. That test concerns one common mask, not every possible algebraic tail simplification.

   **Fix:** Label control near-redundancy HEURISTIC, based on one development net. Replace the tail assertion with the exact sampled observation and its limited scope.

6. **MAJOR — The bounded-independence conclusion overgeneralizes the experiment, and Table E hides severe censoring.**  
   [randomness.md:404](/home/agent/workspaces/mats/work/randomness/randomness.md:404): “how fast do k-wise designs fool the nets as k grows … they do not start to.”

   The experiment tests particular finite-level polynomial-hash constructions. Their marginals are not exactly Gaussian; the radius-normalized variants reported in Table E no longer preserve coordinate-wise independence. The 127-wise counterexample is a **worst-case network**, not a lower bound for random Gaussian weights.

   [report_tables.py:123](/home/agent/workspaces/mats/work/randomness/scratch/report_tables.py:123) removes observations below three times the truth floor before computing medians. Thus Table E’s **4.90 at \(n=64,k=4\)** is one surviving net out of eight; **0.51 at \(n=32,k=4\)** uses two out of eight. These cannot establish the claimed behavior with increasing \(k\). The “114 (net, k) points” also counts plain and radius-normalized variants separately.

   **Fix:** Limit the conclusion to the tested constructions and resolved budgets. Show retained/total counts in Table E and mark the high-\(k\) comparisons unresolved. Preserve PQ3’s registered outcome, but do not turn its broad pass band into an asymptotic conclusion.

7. **MAJOR — The summary’s fourfold ceiling is directly false.**  
   [randomness.md:31](/home/agent/workspaces/mats/work/randomness/randomness.md:31): “Nothing reaches 4x on any net.” Repeated at line 267.

   Recomputed E2 gains include **5.54775x** for fixed Sobol on net 202 and **4.35069x** for fixed polar Sobol on net 203. Both already appear in Table C.

   **Fix:** “None of the three randomized structured methods in PC3 reaches 4x in E2; fixed rules exceed 4x on individual nets. Kerdock has the highest measured median gain.”

8. **MINOR — Registration is substantially supported, but Amendment 1 was partially unblinded.**  
   [PREREG.md:82](/home/agent/workspaces/mats/work/randomness/PREREG.md:82): “hashed before any evaluation result was read.”

   All recorded frozen hashes match, and current generating/scoring code matches the frozen copies. The timeline is:

   | Registration | Hash time | Relevant execution |
   |---|---|---|
   | Part 1 | 13:45:49 | Queues A/B start 13:46:12 |
   | Amendment 1 | 13:50:47 | E5 starts 14:58:48; E1 already running |
   | Amendment 2 | 15:00:43 | First structure run starts approximately 15:00:45.9, from mtime minus recorded duration |

   `logs/deviations.txt` expressly records seeing net 200’s SVD gains before Amendment 1. Thus its blanket “before any evaluation result” wording is false, although it preceded E5 and the exposure was disclosed.

   **Fix:** Say “registered before E5, after limited E1 progress exposure.” I found no evidence of post-result threshold changes. **32 predictions, 25 holds, and seven failures reproduce correctly**, including all four Amendment 2 failures.

9. **MINOR — Correct these remaining numerical and labeling errors.**

   | Location / wording | Correction |
   |---|---|
   | §4.5: fixed Kerdock “0.11–0.68” | **0.1084–0.7952**, approximately 0.11–0.80 |
   | §4.6: fixed aligned Kerdock “97–204” | **53.03–204.00** |
   | §4.7: “four of five … 0.6–0.7 x MC” | Three; plain-MC-normalized values are **0.588, 0.654, 0.622, 2.522, 1.056** |
   | §4.6: multilevel “never exceeds” 1 | Net 202 reaches **1.0302**; the median is below 1 |
   | Summary: output slope “n/V, ~19” | Per-net slope is **D(W)/V(W)**. Measured median: **18.6**; median \(n/V\): **21.6**; \(n/\mathrm{mean}(V)\): **17.3** |
   | §4.1 gains 1.93 and 1.62 | Standard at \(2^{12}\): **1.9358 → 1.94**; polar at \(2^8\): **1.6142 → 1.61** |
   | §4.1 polar ladder exponent at \(n=128\): 1.04 | **1.03479 → 1.03** |
   | §4.4 median V at \(n=32\): 10.8 | **10.7463 → 10.7** |
   | §7: \(512\times64\) “needs” testing | Already completed; replace with additional nets/widths |
   | §7: descriptive \(k=3\) run “was queued” | Explicitly say it was stopped and remains incomplete |

10. **MINOR — Bit accounting and literature rates need their assumptions restored.**  
    The reported **135,168** Sobol bits assume 32-bit scrambling; `lib/rnd.py` leaves SciPy’s `bits` unset, and the installed default is **30**. The pairwise implementation draws 53-bit floating uniforms, rather than implementing the stated 32-bit construction. Exact continuous unbiasedness/pairwise independence does not follow literally for the finite-grid implementation.

    **Fix:** Label the counts as idealized 32-bit accounting, distinct from implementation entropy and discretization. The continuous pairwise theorem gives radius-exact MC risk \(V_{\rm rb}/N\).

    The cited He–Wang excess \(1/(4d-2)\) is an **RMSE** exponent; in this report’s MSE convention it doubles to \(1/(2d-1)\), approximately **0.00196** at \(d=256\), subject to the theorem’s integrand assumptions. Also replace “none exists” for full-net PRGs with “none was found in the cited search”; a circuit-lower-bound implication is not a nonexistence theorem.
