<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/nd-exact/review/review_gpt6_r1.raw -->

Model: GPT-6 (Codex). **Verdict: major revision.**

The registered CS2 failures are reproducible. The broader conclusion that deterministic estimation cannot beat sampling is unsupported and contradicted by a simple omitted baseline.

Checked 2026-11-02 UTC, read-only: all nine supplied tests pass; both score files reproduce exactly in memory. All frozen-code hashes match. Part 1’s hash matches the first 6,038 bytes of the amended registration. Registration precedes the covered runs: Part 1 at 04:14:52Z versus first CS2 log at 04:15:57Z; Amendment 1 at 04:20:55Z versus first CS2b log at 04:24:56Z.

1. **Critical — An omitted deterministic baseline changes the main answer.**

   [The conclusion](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:302) generalizes from CS2 to deterministic methods. I tested a fixed cubature rule with no RNG or fitted parameters:
   `Sobol(d=8, scramble=False).random_base2(12) + 1/8192`, inverse-normal transform, normalize each vector, integrate the radius analytically, and evaluate through layer 48 with the existing tail-cone check and full-tail fallback.

   Charging **60 mv/node plus CS2’s entire setup**, total cost was approximately 250,000 mv. Results against the stored reference:

   | Seed | Deterministic nMSE | RQMCJ nMSE / deterministic nMSE, fresh equal-cost check |
   |---|---:|---:|
   | 203 | 4.12e-7 | 109.4 |
   | 216 | 9.89e-7 | 17.8 |
   | 217 | 3.88e-6 | 4.91 |
   | 220 | 5.45e-6 | 6.27 |
   | 221 | 6.05e-5 | 0.740 |
   | 223 | 9.05e-5 | 0.182 |

   The fresh comparison used 64 RQMCJ replicates, spending the available budget on 4,508–4,517 points. A separate check using 4,096-point, power-of-two RQMCJ replicates also gave over 3× improvement on the same four nets. Against the report’s existing interpolated curves, the four ratios were 73.7, 20.3, 3.66 and 5.49. Full-depth evaluation confirmed the deterministic tail evaluations within \(3.4\times10^{-14}\) relative discrepancy.

   These are exploratory results; they establish a missing competitive deterministic estimator and require confirmation as such. **Fix:** add this baseline, freeze its configuration, report its complete convergence curve, and rewrite the headline around the tested methods. Exact integration remains a separate question.

2. **Major — T4 measures one truncation strategy; it is not a lower bound for exact methods.**

   [region_code.py:42](/home/agent/workspaces/mats/work/nd-exact/frozen/region_code.py:42) correctly separates discovery/ranking sample A from evaluation sample B. Conditional on A, B estimates the omitted contribution without selection bias. Squaring that estimate introduces positive noise bias, which the resolution filter substantially limits.

   However, [the claimed oracle bracket](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:190) is unjustified: neither the in-sample nor held-out curve is a guaranteed bound on optimal region selection. The experiment also requires dropping every unselected region. It does not cover approximating the remainder, integrating unions, or sharing computations between regions.

   Likewise, **9 mv/region is an assumed generous cost, not a proved universal lower bound**: a rank-one output functional need not require constructing an independent dense map for every region. Finding regions need not require sample A’s particular discovery procedure.

   **Fix:** describe T4 as failure of the *sample-A-ranked, integrate-and-drop strategy under an optimistic assumed cost*. Remove the oracle bracket and universal impossibility inference. The earlier lane explicitly called its orthant-cost extrapolation a heuristic, not a bound.

3. **Major — Global tail exactness and reference accuracy remain conditional.**

   The homogeneity identity and \(E[a]=J_cE[h_c]\) **under the stated single-class premise** are correct. But [RQMCJ](/home/agent/workspaces/mats/work/nd-exact/frozen/baselines.py:75) applies its pilot-derived Jacobian to every state without checking membership or falling back. [Truth](/home/agent/workspaces/mats/work/nd-exact/frozen/truth.py:47) similarly assumes the premise during reference integration.

   Zero exceptions in the census or \(2^{21}\)-point check does not prove absence of rare exceptional regions. The stored reference variances, \(3.01\times10^{-10}\)–\(9.08\times10^{-10}\) nMSE, quantify replicate uncertainty conditional on this truncation; they do not bound truncation bias.

   The choice \(c=48\) also uses the evaluation-net census. Its discovery cost is excluded despite the “every operation” claim; the full-depth census alone costs approximately \(2^{30}\) mv per net before bookkeeping.

   **Fix:** use the existing cone-membership/fallback machinery for RQMCJ and reference evaluations, or prove global containment. Distinguish offline structural information from charged estimator setup. The large CS2 losses survive this qualification.

4. **Medium — “Certified exact” overstates the numerical implementation.**

   I found no algebraic error in the gnomonic interval extrema, factored-map propagation, cone moment formulas, or \(KA\) containment constraints. But [the certifier](/home/agent/workspaces/mats/work/nd-exact/frozen/cs2.py:21) uses ordinary floating-point products and sums, without outward rounding or propagated error bounds. [Moments](/home/agent/workspaces/mats/work/nd-exact/frozen/cubesphere.py:36) use finite quadrature on \([0,9]\).

   The quadrature check reproduces **3.152e-9** worst relative discrepancy for Q=32 on its 200 test cells. That is useful numerical evidence, not a certificate for all cells; [the test only asserts the Q=64 tolerance](/home/agent/workspaces/mats/work/nd-exact/tests/test_cubesphere.py:123). Numerical moments also make UNB’s unbiasedness accurate only to integration error.

   There is additionally a transcription error: [the report’s](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:98) \(E\chi_8=2.7396\) should be **2.741624675377656**. The code uses the correct value.

   **Fix:** distinguish exact real-arithmetic identities from numerical certification. Add rounding/quadrature bounds if rigorous certification is intended; otherwise state numerical tolerances and limitations.

5. **Major — The dimensional explanation establishes a weakness of these cells, not a general integration barrier.**

   [The covering argument](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:256) reverses a geometric implication. Distance \(d\) to the nearest boundary guarantees an inscribed ball of radius \(d\); it does not require every contained cell to have radius below \(d\). Anisotropic or boundary-aligned cells can extend much farther tangentially. Consequently, the \(10^{16}\)–\(10^{18}\) cell estimate cannot constrain arbitrary deterministic methods.

   The one-layer experiment is especially misleading as evidence for a general width-3/4 crossover: **every tested width has the cheap exact answer**
   \[
   E[\operatorname{ReLU}(Wx)]_j=\|w_j\|/\sqrt{2\pi}.
   \]
   It measures CS2’s efficiency, not feasibility of exact integration. Conversely, individual joint gate regions already involve correlated Gaussian orthant probabilities at depth 1, so “region-exact formulas break at depth 2” conflates aggregate means with individual-region integration.

   **Fix:** scope the explanation and crossover to the tested dyadic centroid algorithm. Separate region geometry, certification cost, and integration complexity.

6. **Medium — Amendment 1 does not deliver its stated anti-starvation guarantee.**

   [CS2b initialization](/home/agent/workspaces/mats/work/nd-exact/frozen/cs2b.py:256) still assigns root priorities without the mass floor. The floor appears only when children are inserted. Thus the claim that every positive-mass open cell eventually splits is false for the registered implementation.

   The report discloses the defect, which is good. Its consequences are material: the corrected final errors improve roughly **8× on seed 203** and **6× on 217**. Those registered slopes partly describe starvation, rather than geometric convergence.

   **Fix:** retain the frozen results as historical registered outcomes, but use the corrected implementation for conclusions about the algorithm’s convergence. Explicitly qualify the Amendment 1 guarantee.

7. **Medium — The number of classes is overstated by approximately twofold.**

   [n_cells](/home/agent/workspaces/mats/work/nd-exact/frozen/cs2.py:157) counts every cell ever constructed, including replaced parents. The report treats it as the current number of classes.

   For seed 203 at the final checkpoint, the run records **890,258 constructed nodes but 445,137 open leaves**. Seed 220 records **890,518 versus 445,258**. Since no cells are certified, the leaves are the actual classes.

   **Fix:** use `n_open` for these runs’ class counts and class-error plots. Label `n_cells` as cumulative constructed nodes. This shifts the absolute class count by approximately one bit.

8. **Medium — The slope comparisons use different windows and omit the nominal endpoint.**

   [The scorer](/home/agent/workspaces/mats/work/nd-exact/frozen/score.py:55) filters actual cost at \(2^{24}\). Every nominal \(2^{24}\) CS2 checkpoint slightly overshoots, so none enters the fit. Meanwhile, [report_tables.py](/home/agent/workspaces/mats/work/nd-exact/scratch/report_tables.py:72) uses \(2^{17}\)–\(2^{25}\) for samplers under a heading saying \(2^{18}\)–\(2^{24}\).

   Including the nominal endpoint gives CS2 **3.65–8.75** bits/halving and CS2b **3.31–7.63**, versus the reported 3.57–8.53 and 3.08–7.50. T3/T3b still hold.

   **Fix:** define a common fitting window explicitly, preserve nominal checkpoint labels, and distinguish corrected descriptive fits from frozen scores.

9. **Medium — The cost ledger is approximate, with both omissions and overcharges.**

   Examples:
   - [Moment initialization](/home/agent/workspaces/mats/work/nd-exact/frozen/cubesphere.py:36) computes quadrature nodes and tables before resetting the counter to zero.
   - [The moment counter](/home/agent/workspaces/mats/work/nd-exact/frozen/cubesphere.py:78) charges approximately \(11mQ+4Q\) operations where the displayed arithmetic needs approximately \(8mQ+4Q\): about **5.25 mv extra per width-8, Q=32 cell**.
   - [Tail-Jacobian setup](/home/agent/workspaces/mats/work/nd-exact/frozen/baselines.py:40) performs a forward matvec as well as matrix propagation, while charging eight mv/layer.
   - RADQ’s pilot normal generation and some reductions, Sobol generation/setup, and other bookkeeping are absent or nominal.

   **Fix:** replace “every operation” with an accurately specified nominal model, reconcile these items, and give sensitivity results. These small corrections cannot explain away CS2’s large losses; the region lower-bound and census-accounting issues are more consequential.

10. **Medium — Some numerical and statistical conclusions exceed the recorded evidence.**

   The assertion that no tested method beats MC is directly false under the report’s own accounting. For seed 216, the region code at \(R=131072\) has **1.52e-5 nMSE at 1,179,648 mv**, versus MC’s **2.18e-4**, a **14.3× improvement**. The corresponding gains are 9.1×, 5.6× and 2.5× on seeds 217, 220 and 223.

   Also, T5’s failure to demonstrate a **3×** improvement does not establish that “the cells add nothing.” UNB’s largest-budget relative standard errors are **30–65%** across the six nets. Seed 221’s T6 ratio is only **3.045**, with approximately **50%** relative SE on UNB’s estimated MSE.

   **Fix:** correct the MC claim, report uncertainty, and describe T5/T6 as the observed registered score outcomes. Attribute gains using an ablation with the same cut, radius treatment, and tail checks before concluding that the cells provide no benefit.

The reproducible registered counts remain **T1/T2: 0/6; T3/T4: 6/6; T1b/T2b: 0/6; T3b: 6/6; T5: 0/6; T6: 5/6**. Their interpretation needs the revisions above.
