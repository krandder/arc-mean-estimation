**Verdict: major revision.** The revised numerical comparisons largely reproduce, and the negative conclusion is now substantially better scoped. However, the hybrid estimator’s MSE remains incorrectly scored, incomplete cost accounting still supports headline comparisons, and several qualifications disappear in the summary. “All 15 findings applied” overstates completion.

Checked read-only on **2026-11-02, completed 15:06 UTC**. Report SHA-256: `c461da6c0b2c919ea44d6ddba5a5eb6adc43a49c891b48e9cc9b0609aff5c8ef`. I independently calculated statistics from saved JSON runs; I did not rerun simulations or modify files.

The disposition of each first-round finding is:

| # | Status | Assessment and remaining problem |
|---|---|---|
| 1 | **Resolved in the report** | §2.2, the summary, and §6 now include the predictable radius term and restrict the rank bound to positive degrees. The fixed-defect/additive-correction restriction is explicit. |
| 2 | **Resolved in the report** | §2.4 now distinguishes failure of annealed-price domination from the open computational lower bound. Conditional pricing survives explicitly. |
| 3 | **Resolved in the report** | §2.5 removes the unsupported \(q\le n/L\) assertion, preserves uniform-law hypotheses, and identifies the width criterion as an nMSE statement under specified cost/comparator assumptions. Historical assertions in `FORMAL.md` still need correction pointers; see below. |
| 4 | **Partly resolved** | The overall negative is restricted to tested methods and widths, the general mechanism is HEURISTIC, and alternative representations remain open. But summary item 4 still states exact removal of the future’s modes without the polynomial-reading/\(L^2\)-density qualification that §2.3 correctly supplies. |
| 5 | **Partly resolved** | Literal P1/P3 corrections and the main report’s raw B2 table are correct. However, `results/tables_part1.md` still labels floored values “median b2” and presents floored ratios without identifying them as historical scorer statistics. |
| 6 | **Partly resolved** | The affected success counts are correct: 6/8 at \(n=128\), 1/5 at \(n=256\), for each future half-width variant. But “matched or beat full k3 where it ran” remains false for individual successful runs; successful-case medians do not establish that statement. |
| 7 | **Resolved** | The paired PCA/future ratios and paired retained factors reproduce. The previous ratio-of-medians claims have been replaced in the main report. |
| 8 | **Partly resolved** | The finite-algorithm target and uncertainty limitations are now explicit. No additional particle/pilot replicates or uncertainty estimates were supplied. Moreover, §4.1 still says the benefit of fixed \(k\) “disappears as n grows,” exceeding the explicitly descriptive three-width evidence. |
| 9 | **Resolved** | The diagram-based costs are now explicit scenarios with assumed constants, not computational lower bounds. Cheaper contractions remain allowed. |
| 10 | **Partly resolved** | The extra-k2-pilot gains reproduce, and omitted work is acknowledged. There is still no operation-level ledger, while §3 says “every cost includes” dense linear algebra and §4.3 presents equal-total-cost conclusions. Those claims need narrowing or complete accounting. |
| 11 | **Partly resolved; numerical fix outstanding** | The reference-mean problem is disclosed, but H1 is still scored by the same invalid sum. Neither new correction script rescored actual hybrid estimates. The exploratory analytic-mean runs do not repair the registered H1 results. |
| 12 | **Resolved as an asymptotic exclusion** | Mixture scaling is explicitly unmeasured; a growing window is no longer excluded; uniform positive control exponents are “not established.” One new interpretation of the cost-fit slopes remains unsupported, noted below. |
| 13 | **Partly resolved** | B2 extrapolation and several lower-end window extrapolations are marked. H1’s 65,000-pass row still omits its residual extrapolation, and the requested sensitivity analysis is absent. The plain-MC comparison independently supports the particle implementation’s negative. |
| 14 | **Resolved for the five identified corrections** | The cut count/medians, particle loss factor, development order-4 exception, and spectrum-table alignment are corrected. I found additional small numerical/wording problems below. |
| 15 | **Partly resolved** | Original P7, amended P7, and corrected P8 are clearly distinguished; literal P9(c) reproduces. However, the report still calls hash/file times “authoritative” chronology. They establish artifact identity and recorded timestamps, not independently certified ordering. |

I independently recomputed the following corrected quantities. Values are medians of per-net quantities unless specified otherwise.

| Quantity | \(n=64\) | \(n=128\) | \(n=256\) |
|---|---:|---:|---:|
| Paired PCA/future B2 ratio, \(k=n/4\) | 2.030766 | 2.696448 | 2.872394 |
| Literal P3, \(k=n/4\) | 5.232353 | 9.120564 | 18.832739 |
| Literal P3, \(k=n/2\) | 75.224635 | 139.158074 | 235.576709 |
| Nets retained for half-width P3 | 8 | 8 | 4 |
| Raw median half-width B2 `b2` | \(4.532774\times10^{-5}\) | \(1.308834\times10^{-5}\) | \(4.550445\times10^{-6}\) |
| VJP retained factor \(e_3/e_{\rm proj}\), \(k=n/4\) | 0.862724 | 0.817556 | 0.800430 |
| Mean-field retained factor, \(k=n/4\) | 0.784400 | 0.856185 | 0.907056 |
| Half-width successes, **each** future kind | 8/8 | 6/8 | 1/5 |

These agree with `results/review_recompute.json`.

Literal P1, applying both its PCA threshold and the general truth-floor exclusion, is:

| Cut | Median future/PCA | Eligible nets | Threshold met? |
|---|---:|---:|---|
| 4 | 0.284124 | 5 | Yes |
| 8 | 0.089690 | 3 | Yes |
| 16 | 0.754648 | 3 | No |
| 24 | 0.909130 | 3 | No |

Thus **P1 still fails and P3 still holds**.

The window rows also reproduce:

| Mean-field D1, \(k=n/4\) | \(n=64\) | \(n=128\) | \(n=256\) |
|---|---:|---:|---:|
| Registered hypothetical cost, passes | 273.602 | 585.301 | 1353.150 |
| Median nMSE | \(5.903729\times10^{-4}\) | \(3.063314\times10^{-4}\) | \(2.221407\times10^{-4}\) |
| Gain at hypothetical cost | 2.566478 | 3.007969 | 2.372929 |
| Gain including separate k2 pilot | 1.813317 | 2.178795 | 1.749825 |
| Median window endpoint, passes | 636.189 | 1556.258 | 2789.910 |
| One-diagram scenario gain | 1.907117 | 1.613079 | 0.934346 |
| Three-diagram scenario gain | 1.068221 | 0.778784 | 0.357734 |
| Implemented-cost gain | 0.120927 | 0.056288 | 0.036240 |

Additional checks reproduced:

- Corrected P8: **2.372929** for mean-field and **0.0236403** for VJP.
- Literal P9(c): **0.8319906**, preserving its recorded outcome but not validating the underlying hybrid-MSE calculation.
- \(n=256,l=24,k=64\): future wins **4/5**; raw medians **\(3.879735\times10^{-6}\)** versus **\(5.522283\times10^{-6}\)**.
- Particle implementation losses against plain MC: **82.536×, 32.746×, 20.726×**.
- Corrected \(n=64\) spectrum columns, including first-cut shares **0.382456, 0.797517, 0.958202** and participation ratio **17.464895**.

The remaining substantive and newly identified issues are:

1. **The H1 limitation is still presented as a validated estimator comparison.**  
   [§4.3](/home/agent/workspaces/mats/work/future-aware/future-aware.md:301) and summary item 3 retain the 0.8–1.0× hybrid result. Let
   \[
   x=\widehat E(f-c)-(Y-\widehat E_Pc),\qquad d=E_Qc-\widehat E_Pc.
   \]
   The actual hybrid squared error is \(\|x+d\|^2\). The saved calculation adds \(\|x\|^2+\|d\|^2\), omitting \(2x^\top d\). An estimated reference mean does not make that cross term vanish.

   I reproduced first-layer quadratic `beta_eg` medians of **\(2.0495,1.9683,1.4415\times10^{-6}\)** across the three widths. Calling these smaller than the residual error does not bound the omitted cross term. Score the actual estimates directly, or withdraw the affected claims as validated H1 MSE measurements.

2. **Both new correction scripts rewrite the original score artifact on import.**  
   [review_recompute.py:15](/home/agent/workspaces/mats/work/future-aware/scratch/review_recompute.py:15) and [score_corrections_posthoc.py:8](/home/agent/workspaces/mats/work/future-aware/scratch/score_corrections_posthoc.py:8) import `score_part1`, whose module-level code writes `results/score_part1.json`.

   I verified this with a write-blocking wrapper: each script’s **first attempted write** was the original score file, before its own correction output. No write occurred. With unchanged runs the content may reproduce identically, but this does not implement the stated preservation of original outputs. Use side-effect-free helpers for post-hoc recomputation.

3. **The revised report and supplementary result table still use conflicting statistics under similar labels.**  
   [T2](/home/agent/workspaces/mats/work/future-aware/results/tables_part1.md:123) retains **121** and **204** for half-width gains, and **\(6.70\times10^{-6}\)** as the \(n=256\) “median b2.” The revised report correctly uses **139**, **236**, and **\(4.55\times10^{-6}\)**. Retaining historical results is appropriate, but label their flooring rule and link the corrected table.

   The new P3 “literal” code also checks the denominator’s truth floor but only tests the numerator for truthiness. This does **not** affect these runs—all Gaussian numerators clear the floor—but it incompletely implements the general exclusion rule.

4. **The half-width success qualification still overstates accuracy.**  
   [§4.2](/home/agent/workspaces/mats/work/future-aware/future-aware.md:289) says the projection “matched or beat full k3 where it ran.” At \(n=128\), VJP half-width projection beats k3 on only **3/6 successful nets**; seed 302 has retained factor **0.561083**, meaning approximately **1.78× greater error**. PCA at \(n=256\) beats k3 on **3/5**, despite its median retained factor of 1.120266. Describe successful-case medians and variation explicitly.

5. **Some corrected theory remains contradicted by unsuperseded text in `FORMAL.md`.**  
   [E3](/home/agent/workspaces/mats/work/future-aware/FORMAL.md:166) still asserts \(q\le n/L=8\); [E1](/home/agent/workspaces/mats/work/future-aware/FORMAL.md:134) still concludes that Theorem A has no unconditional future-aware extension. E13–E14 do not explicitly supersede these first-review corrections. Preserve the historical text, but append an authoritative correction identifying these statements.

6. **Three smaller claims need correction.**
   - [§5](/home/agent/workspaces/mats/work/future-aware/future-aware.md:407) says half-width order-4 errors are “3–8× worse than k4.” The actual five ratios span **2.061–7.753×**; seed 300 is also below 3× at **2.610×**.
   - [§6](/home/agent/workspaces/mats/work/future-aware/future-aware.md:478) says quarter-width future projection retains **80–91%**; including mean-field directions, the verified range starts at **78.44%**.
   - After reporting slopes against actual saved construction costs, [§5](/home/agent/workspaces/mats/work/future-aware/future-aware.md:396) says additive setup costs make the effective exponent “smaller still.” That does not follow from those fits; the setup costs are already included. Remove the claim or define and calculate a different exponent.

**The summary is substantially improved, but does not yet stay entirely within what is shown.** Its tested-width restriction, hypothetical-cost labels, numerical-failure disclosure, and open alternative representations are appropriate. It still needs the polynomial/integrability qualification for exact mode removal, an explicit qualification of the uncorrected H1 scores, and consistent separation of descriptive width trends from asymptotic claims.

The remaining major revision is concentrated: correct or withdraw the H1 estimator-MSE claims, reconcile the cost-accounting language, and propagate the existing qualifications consistently into the summary and supporting artifacts. The recomputed paired statistics and hypothetical D1 windows can stand.
