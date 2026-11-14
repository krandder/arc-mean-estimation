<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/nd-exact/review/review_gpt6_r2.raw -->

Model: GPT-6. **Verdict: major revision.**

The revision substantially improves the report, and the registered failures remain reproducible. However, the new claim that fixed Sobol “ties sampling” is unsupported, and several qualifications disappear in the summary and section 10.

Checked **2026-11-02, 05:34 UTC**, read-only: both score files reproduce; `results/tables.md` regenerates exactly; frozen-code hashes match; all nine tests pass using the project environment where needed. I independently reproduced all 66 deterministic Sobol errors and all 18 paired-ablation means. Full-depth evaluation of every deterministic point set agreed with its shortcut estimate within \(7.1\times10^{-14}\) relative discrepancy. I inspected CS2c’s implementation and stored curves without rerunning its full refinements.

Numbering below follows the ten round-1 findings.

1. **Major — Partially addressed: the deterministic baseline is included, but its statistical dismissal is unjustified.**

   [Section 8](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:312) correctly reports **42/66 wins against mean scrambled nMSE, 32/66 against the median, and mean rank share 0.505682**. The code correctly computes
   \[
   \hat p=\frac1{64}\sum_r\mathbf1\{e_r<e_{\rm fixed}\}.
   \]

   The interpretation is the problem:

   - Conditional on this fixed rule, its expected share is \(p=F(e_{\rm fixed})\), **not automatically 0.5**.
   - A uniform rank follows if the comparator is itself an independent, exchangeable draw from the scrambled-error distribution. That assumption is not established for the selected unscrambled rule.
   - **0.036 is mathematically correct for 66 independent uniform ranks**: with 64 comparison runs, the variance of one normalized rank is \(66/(12\cdot64)\). But these are eleven configurations of the same deterministic rule on each of six nets; the report supplies no justification for treating their ranks as independent uniform draws. As an illustration of sensitivity, the six net-average ranks have a descriptive SE of **0.0666**.
   - Randomness from the 64 comparison scrambles is a different uncertainty: conditional on the fixed tasks, the estimated SE of the average share is about **0.0061**.

   A mean rank near one-half establishes neither a uniform rank distribution nor equality of MSE. “Statistically one RQMC run with the randomness fixed,” “the wins are luck,” and “ties … on average” therefore overreach. The mean/median ratios also demonstrate skewness, not necessarily heavy tails.

   **Fix:** retain the descriptive results and say: “The fixed rule is competitive but inconsistent across nets and budgets; this experiment establishes neither systematic superiority nor equivalence.” Remove the asserted statistical identity and the unsupported equivalence conclusion from the summary and section 10.

2. **Resolved in the main analysis; minor residual overstatement — T4 is now appropriately scoped.**

   [Section 5](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:187) explicitly identifies sample-ranked integrate-and-drop, assumed cost, uncharged discovery, and alternatives it does not cover. The oracle bracket is removed. This addresses the substantive round-1 objection.

   However, [section 3](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:162) still says exact integration “is governed by coverage, not entropy” and that a region code “must find and integrate enough” regions. That remains broader than the demonstrated strategy.

   **Fix:** qualify those sentences with “for this integrate-and-drop strategy.” No new experiment is needed.

3. **Major — Partially addressed: conditional tail exactness is disclosed, then overstated again.**

   [Section 2](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:117) now distinguishes the identity from its sampled premise and names the uncharged census. But the summary still says “Past layer 20–48 the problem is exactly linear,” and [section 10](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:380) calls the benefit “the exact zero-bit tail” without qualification.

   The new exception calculation also conflates checks: the additional \(2^{21}\) full-depth inputs were checked at **cut 64**, as recorded in every truth file and implemented in [truth.py](/home/agent/workspaces/mats/work/nd-exact/scratch/truth.py:71). They do not independently establish absence of exceptions at cut 48. Pooling them with the census to claim \(5\times10^{-7}\) at both cuts is unsupported; the census-only zero-event benchmark at cut 48 is approximately \(7.1\times10^{-7}\), subject to selection qualifications.

   Further, small exceptional probability alone does not bound truncation bias: the needed quantity is the exceptional contribution of \(a-J_ch_c\). “Typical-sized outputs” is an additional assumption.

   **Fix:** carry the conditional wording into the summary and section 10; separate evidence by cut. Label the nMSE estimate as a sensitivity calculation under an amplitude assumption. The deterministic full-depth checks I reproduced are reassuring, but do not validate every scrambled/reference evaluation.

4. **Mostly addressed; minor residual — Numerical certification is now disclosed, but “exact” and “unbiased” need consistent qualification.**

   [Section 6](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:222) correctly states finite quadrature, double precision, and no outward rounding. The reproduced quadrature discrepancy is **\(3.1521\times10^{-9}\)**. The corrected chi-mean value is numerically right.

   Remaining issues: the summary still calls computed masses “exact,” and section 9 does not explain that numerical moment error makes UNB unbiased only up to integration error. Also, \(2.741625\) is a rounded value, not an exact equality.

   **Fix:** use “numerically certified,” distinguish exact identities from their numerical evaluation, and add the quadrature qualification to UNB.

5. **Medium — Partially addressed: the width study is correctly scoped, but the geometric implication remains wrong.**

   The one-layer closed-form mean and algorithm-specific crossover are now explicitly acknowledged. That resolves the main experimental interpretation problem.

   However, [section 7](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:286) still says a box-like cell is certifiable “only if it fits within distance \(d\).” Distance to the nearest boundary provides an inscribed-ball radius; it does not impose that circumradius on a contained box. Even boxes can extend farther tangentially. Calling the subsequent count heuristic does not repair this necessary-condition statement.

   **Fix:** describe \(h\sim d\) as a rough isotropic-resolution model, not a containment requirement or lower bound. Keep the measured CS2c slopes separate from the heuristic explanation.

6. **Medium — Implementation addressed; attribution and headline slopes remain inconsistent.**

   [The root-floor implementation](/home/agent/workspaces/mats/work/nd-exact/lib/cs2.py:261) gives every open root positive priority on these six nets. The stored CS2c curves yield **3.305–4.308 bits per halving**, supporting the reported 3.3–4.3 range.

   But CS2c uses **`surplus_m`**, so comparison against original CS2 combines the child mass-floor change with the root fix. To isolate the root fix, compare against CS2b: final error improves approximately **6.72× on 203** and **3.74× on 217**. The other four CS2c curves match CS2b exactly apart from timing.

   Despite saying convergence conclusions use CS2c, [section 10](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:371) still uses **3.3–8.8**, mixing corrected and defective implementations.

   **Fix:** identify CS2c as CS2b plus root flooring; use 3.3–4.3 for conclusions about corrected convergence, retaining older slopes as registered historical results.

7. **Medium — Leaf counts corrected, but “nothing certified” is false.**

   The main class counts now use open leaves, addressing the factor-of-two error. However, the repeated assertions of zero certified cells contradict the runs:

   - `cs2_s220.json`: **9 certified cells**, certified probability mass **\(5.788711\times10^{-6}\)** at the final checkpoint.
   - CS2b and CS2c on 220: **4 certified cells**, mass **\(3.209396\times10^{-6}\)**.

   The [section 6 table](/home/agent/workspaces/mats/work/nd-exact/nd-exact.md:251) incorrectly reports zero. Four-decimal formatting in `tables.md` conceals the nonzero mass. This also corrects the corresponding blanket statement inherited from round 1.

   **Fix:** say certification covered *negligible mass*, report the actual counts, and label cumulative constructed nodes separately from open leaves.

8. **Medium — Descriptive refits are correct, but the supporting table remains inconsistent.**

   The report’s nominal-checkpoint ranges reproduce: **CS2 3.649–8.746**, **CS2b 3.305–7.631**. The sampler ranges also reproduce.

   However, [results/tables.md](/home/agent/workspaces/mats/work/nd-exact/results/tables.md:53) still presents the older CS2/CS2b fits under the same window heading. Its [generator](/home/agent/workspaces/mats/work/nd-exact/scratch/report_tables.py:80) still excludes the overshooting nominal endpoint.

   Other numerical corrections:

   - Section 6, seed 223 at \(2^{24}\): RQMC is **\(4.87\times10^{-7}\)**, not \(1.6\times10^{-7}\); RQMCJ is **\(7.38\times10^{-8}\)**, not \(7.7\times10^{-8}\).
   - The largest adjacent-budget change in stored deterministic Sobol error is approximately **1,130×**, not 2,000×.
   - Section 7’s width-study numbers reproduce at the **last stored CS checkpoint within RQMC’s measured range**; specify that convention.

   **Fix:** regenerate clearly labelled descriptive-fit tables and correct these values.

9. **Mostly addressed; minor accounting gap — The nominal-cost qualification is appropriate.**

   The revised ledger names the important omissions, including census cost. This substantially resolves the original “every operation” overclaim.

   Two qualifications remain: “each is under 10%” is asserted without a supporting reconciliation, and [the ablation](/home/agent/workspaces/mats/work/nd-exact/scratch/posthoc_unb_ablation.py:45) assigns NOCELL only point costs while reusing the tail cone/Jacobian constructed through `est.setup()`.

   **Fix:** charge NOCELL its necessary tail setup, and either substantiate the 10% bounds or remove them. These corrections are unlikely to reverse the large CS2 losses.

10. **Medium — The paired ablation supports the direction of the conclusion, but does not “settle” it.**

   The experiment correctly pairs inputs and holds the cut, radius treatment, and tail checks fixed. All **18 stored means reproduce**, and NOCELL has lower estimated MSE in every comparison. At \(2^{16}\) points, the reported **1.6–3.3×** ratios are correct.

   The displayed standard errors are valid **marginal mean-error SEs**, not uncertainty for the paired contrast. Reconstructing the pairs gives these approximate, unadjusted 95% t-intervals for **UNB minus NOCELL nMSE**:

   | Net | Mean difference | Paired 95% interval |
   |---|---:|---:|
   | 203 | \(8.96\times10^{-7}\) | \([-2.52\times10^{-7},\,2.04\times10^{-6}]\) |
   | 221 | \(1.00\times10^{-6}\) | \([-2.34\times10^{-8},\,2.03\times10^{-6}]\) |

   Thus “lower estimated MSE on every net” is supported; statistically established improvement on every net is not. The boundary-jump explanation is plausible, but the ablation does not isolate that mechanism.

   The MC correction also needs one detail: seed 223’s **2.5×** gain occurs at **125,293 regions**, not \(2^{17}\); that run contains fewer than \(2^{17}\) discovered regions.

   **Fix:** report paired uncertainty and preserve per-replicate errors. Say the ablation supports tail-shortcut computation as sufficient for the observed gain, with no demonstrated benefit from this cell correction; label the jump explanation as a hypothesis.
