**Verdict: major revision.** The evidence supports a negative for the tested implementations at the measured widths. It does not establish a negative for future-aware layer-wise estimators as a class. Several headline comparisons also need numerical or methodological correction.

Checked read-only on 2026-11-02 at 14:47 UTC; report SHA-256 prefix `5c4d541d995af411b2`. I recomputed statistics from saved runs, without rerunning the original simulations or modifying files.

1. **Major — the k-sketch conclusion omits the predictable radius term.**  
   The exact residual formula in [§2.2](/home/agent/workspaces/mats/work/future-aware/future-aware.md:92) is correct. The subsequent statement that a sketch removes at most \(k/r\) of the defect’s price needs another hypothesis: \(M_0=\int\|h\|\,d\Delta=0\).

   As the round-1 answer explicitly explains, the \(d=0\) contribution is completely predictable even at \(k=0\), because the interface reveals all later layers. The flattening-rank inequality applies to \(d\ge1\). Ordinary mean/covariance matching does not eliminate \(M_0\).

   **Fix:** State the bound for the positive-degree price, or require radius matching. Otherwise the removable price is bounded by
   \[
   b_0|M_0|^2+\sum_{d\ge1}b_d\min(1,k/r_d)\|M_d\|_F^2.
   \]
   Carry this qualification into the summary and §6.

2. **Major — “no unconditional extension exists” overstates what was proved.**  
   [§2.4](/home/agent/workspaces/mats/work/future-aware/future-aware.md:126) contains a valid counterexample to positive uniform domination of adaptive realised price by annealed price. It does not prove that no other unconditional theorem exists.

   Likewise, reducing an unrestricted layer-wise lower bound to an explicit computational lower bound establishes difficulty, not impossibility. Conditional pricing itself already supplies an unconditional identity once measurability and integrability are specified.

   **Fix:** Separate the claims: “The annealed-price domination fails for adaptive defects” is **PROVEN**; “an unrestricted computational lower bound remains open” is the appropriate status for the broader question.

3. **Major — the ladder arithmetic is valid, but the asserted bound \(q\le n/L\) is unsupported.**  
   The elimination of \(K\) in [§2.5](/home/agent/workspaces/mats/work/future-aware/future-aware.md:134) correctly gives the stated lower envelope under uniform lower error and cost laws. ARC’s conjectured scaling does not establish an upper bound \(q\le8\) on actual order-to-order improvement. This report itself measures median \(e_2/e_3=11.948\) at \(256\times32\).

   The width criterion is also correctly derived only for the specified cost and comparator laws: \(G_nC_ne_n\to0\). For \(C_n=\Theta(n)\) and \(G_n=\Theta(1)\), this becomes \(e_n=o(1/n)\), where \(e_n\) is **nMSE**, not RMS error. The summary’s test for “any layer-wise proposal” drops those restrictions.

   **Fix:** Replace \(q\le n/L\) with an explicit hypothesis, preserve uniformity over orders, and state the general cost–error criterion wherever the conclusion is universal.

4. **Major — the summary converts conditional models into a class-level mechanism.**  
   The summary and §6 say that the future’s reading requires linearly many directions and that retaining the necessary law is the original integration problem. The proofs establish linear participation ratio for an independent-gate model, while the experiments measure a fitted, covariance-whitened statistic under actual gates. Neither establishes the missing connection from derivative energy to integration error.

   The coordinate-permutation experiment establishes sensitivity to dependence in the tested coordinates. It does not establish that the whole joint law must be represented; §5 correctly acknowledges this, but the summary does not.

   **Fix:** Label the proposed mechanism **HEURISTIC**, restrict the negative to tested methods and sizes, and retain the open possibilities of mixed-moment, oblique-feature, and implicit representations in the summary.

5. **Major — the hashed scorer does not implement the written `b2` rules literally.**  
   [The scorer](/home/agent/workspaces/mats/work/future-aware/scratch/score_part1.py:69) replaces recursion `b2` by `max(b2, noise, 1e-7)`. This substitution is absent from the written predictions and deviations. It also propagates into tables labelled “median b2.”

   Concrete effects:

   - At \(n=128\), P3’s half-width improvement is **139.158** using raw `b2`, versus approximately **121** in the scorer.
   - At \(n=256\), the raw median half-width `b2` is **\(4.55045\times10^{-6}\)**, versus approximately **\(6.70\times10^{-6}\)** after flooring.
   - Applying the preregistration’s “below ten times the truth floor: not used in ratios” rule excludes the negative \(n=256\), seed-203 half-width denominator. P3’s resulting median ratio is **235.577**, using four nets.
   - P1 also omits that general truth-floor rule: at \(l=16\), seed 202 has numerator \(5.06\times10^{-8}\). Excluding it changes the median from **0.552** to **0.755**.

   These corrections do not change P1–P4’s pass/fail outcomes.

   **Fix:** Preserve the frozen output, add a literal-wording correction, disclose the conflict, and print raw estimates separately from any explicitly defined conservative statistic.

6. **Major — the strongest projected-k3 comparison hides severe survivor selection.**  
   The \(n=256,\ k=n/2\) future and mean-field entries in [§4.2](/home/agent/workspaces/mats/work/future-aware/future-aware.md:245) each contain **one successful net out of five**, seed 204. The reported factors **14.74** and **14.24** are therefore single-net results, although the table is introduced as medians over nets and supports a general claim of improvement over full k3.

   There are also four failed half-width runs at \(n=128\): `futv64` and `futmf2_64` on seeds 304 and 306. The main failure discussion concentrates on the eight failures at \(n=256\).

   **Fix:** Show successful/attempted counts beside every affected entry, disclose failures at every width, and restrict the “better than k3” claim to successful matched cases. Any rank-guard rerun must remain separately identified as post hoc.

7. **Major — several headline ratios use ratios of medians instead of the registered median of paired ratios.**  
   The reported PCA/future recursion improvements **1.6, 2.8–2.9, 4.8** are ratios of median errors. Recomputing the median per-net PCA/future ratios gives **2.031, 2.696, 2.872**.

   Similarly, “retains 76–115% of k3’s error factor” divides separately computed median factors. The median per-net retained factor
   \[
   q_{\rm projected}/q_3=e_3/e_{\rm projected}
   \]
   is **0.863, 0.818, 0.800** at \(n=64,128,256\). The claimed 115% retention at \(n=64\) does not survive the registered aggregation.

   **Fix:** Use paired ratios throughout, or explicitly label a ratio of medians as a different descriptive quantity. The per-net identity connecting \(R\) and \(q\) is correct; applying it to separately aggregated medians is not.

8. **Major — finite-particle bias and measurement uncertainty remain unresolved.**  
   B2’s cross-product estimates the squared bias of the **noise-averaged finite-particle algorithm**, relative to the stored reference. It does not isolate the infinite-particle closure’s bias. Increasing particle count alone also leaves finite relevance and Jacobian pilots.

   The exploratory \(n=64\) convergence check is useful but insufficient: `futnl32` changes from \(2.94\times10^{-5}\) to \(3.29\times10^{-5}\) between the saved development runs. There is no comparable convergence study for the \(n=256\) errors used in the strongest precision claims.

   Two replicates do not provide a reliable uncertainty estimate for tiny cross-products. `noise` is not their standard error, and 379 share-law cells are clustered within eight networks.

   **Fix:** Report finite-algorithm targets explicitly; add independent particle/pilot replicates and uncertainty for paired differences and width trends. Until then, replace claims of \(o(1/n)\), or its failure, with descriptive observations over the three widths. In particular, \(ne=0.0029,0.0017,0.0017\) does not establish continued decay.

9. **Major — the co-prover’s implementation upper bound is used as a numerical cost restriction.**  
   The round-2 result is an \(O_K(n+k^{K-1})\) **sufficient implementation bound**, conditional on contractible diagrams. It is neither a lower bound nor a fully specified flop count.

   [§4.4](/home/agent/workspaces/mats/work/future-aware/future-aware.md:285) nevertheless assigns one/three-diagram numerical costs and uses gains **0.93/0.36** to conclude that the window disappears “under the co-prover’s explicit bound.” The supplied big-O result does not establish those constants or exclude cheaper contractions.

   **Fix:** Call these additional cost scenarios, state their complete formulas and assumed constants, and remove their use as a lower-bound argument. The registered dedicated-cost model is appropriately called hypothetical elsewhere; apply that standard here too.

10. **Major — the dedicated-cost window omits an unresolved pilot cost, and the implementation ledgers are approximate.**  
    The measured mean-field method first runs a separate k2 trajectory to obtain gate probabilities, then performs projected-k3 propagation. The hypothetical `C_ded` contains one k2 base cost, the backward sweep, and projected-order terms, but does not explain how that separate pilot is absorbed or reused.

    Adding just one additional k2 pilot changes the median hypothetical gains **2.57, 3.01, 2.37** to **1.81, 2.18, 1.75**, before resolving other feature-construction costs.

    Other accounting gaps include:

    - H1 charges regression pilot paths but omits covariance/Gram construction and fitting costs.
    - H1 quadratic feature construction uses a separate \(2^{16}\)-sample cloud, whose construction and matrix work are not fully charged.
    - D1’s VJP ledger does not separately identify Gaussian sample construction and the relevance Gram matrix.
    - Conversely, the three-forward-pass VJP convention is conservative for the explicit fixed-weight input-gradient implementation, which performs one forward and one backward matrix multiplication per layer.

    **Fix:** Supply an operation-level ledger, distinguish conservative allowances from omitted work, and make pilot sharing and feature extraction explicit hypotheses of the dedicated implementation. The existing ledgers do count substantial backward work; the problem is their claim to complete accounting.

11. **Major — H1 adds two quantities that are not the required bias and variance.**  
    [The hybrid runner](/home/agent/workspaces/mats/work/future-aware/scratch/run_hyb.py:111) estimates the quadratic control’s reference mean using `Qtrue` from \(2^{16}\) samples. It then measures residual squared error against that estimated reference and adds a squared closure discrepancy against the same reference.

    If the reference control mean has error \(\delta\), the residual squared error already contains a reference-error contribution. Adding the estimated squared bias does not generally recover the actual hybrid MSE. For an exactly known control mean with true bias zero, this procedure can count approximately \(2\|\delta\|^2/V\) unnecessarily.

    This matters for the “exact means” row: median quadratic `beta_eg` at \(l=1,n=256\) is **\(1.44\times10^{-6}\)** despite the population control mean being analytically available.

    **Fix:** Score each actual hybrid estimate directly:
    \[
    E_Qc+\widehat E_{\rm RQMC}(f-c),
    \]
    against the reference output. Use analytic first-layer moments, as the exploratory `run_cvk.py` already does. Separate residual variance estimation from reference-mean uncertainty.

12. **Major — the exploratory mixture and control results do not support their asymptotic exclusions.**  
    [§5](/home/agent/workspaces/mats/work/future-aware/future-aware.md:327) acknowledges that mixture-component scaling with width is unmeasured, then uses \(M\sim k\) to exclude a growing window. The particle/EM mixture recursion also does not establish the error of a particular deterministic mixture propagation algorithm.

    Similarly, two fitted exponents at one net per width cannot establish that a positive control-construction exponent fails uniformly in width. The inference from an error-versus-\(k\) fit to an error-versus-cost exponent also ignores large additive setup costs. Fitting the saved construction costs directly gives descriptive slopes around **−0.338** and **−0.104**, rather than the claimed bounds on \(\delta\).

    **Fix:** Retain these as exploratory measurements, state the unmeasured scaling assumptions, and replace “cannot”/“does NOT hold uniformly” with “not established by these runs.”

13. **Minor — extrapolation is correctly implemented but incompletely labelled and overinterpreted.**  
    The scorer correctly interpolates log error against log cost and applies slope −1 outside the measured range. B2 comparisons extrapolate approximately **101×, 117×, and 40×** beyond the largest measured RQMC sample counts.

    Those large extrapolations are disclosed in §4.2, but lower-end extrapolations—such as costs 106, 164, 201, and 223—and hybrid residual extrapolations are not consistently marked in §4.4.

    **Fix:** Mark both ends, label the 45–250× RQMC losses as extrapolated estimates, and add a sensitivity analysis. The particle implementation’s negative is already supported by comparison with plain MC’s known \(1/C\) risk, without assuming distant RQMC behaviour.

14. **Minor — several statements disagree with the saved numbers or table layout.**  
    Specific corrections:

    - At \(n=256,l=24,k=64\), future beats PCA on **4/5**, not 5/5 nets. Seed 204 has \(9.999\times10^{-6}\) versus \(9.550\times10^{-6}\).
    - The corresponding medians are **\(3.880\times10^{-6}\)** and **\(5.522\times10^{-6}\)**, not \(3.0\times10^{-6}\) and \(4.5\times10^{-6}\).
    - §6 says the particle closure loses by approximately \(10^3\); the reported median gains imply roughly **45–247×**.
    - “No better than k3” for every listed \(n=32,k=8\) order-4 run is false on development seed 9500: its error improves by about 1.7×, although it loses most of full k4’s factor.
    - The \(n=64\) relevance-spectrum table has six headers but five data cells because duplicate dimension keys collapse. Values appear under incorrect headers.

    **Fix:** Generate these statements and columns from the same paired, explicitly filtered data used for the tables.

15. **Minor — distinguish original registration, post-observation amendments, and scorer corrections more precisely.**  
    The NaN exclusion was documented after failures were observed, even if before scoring. It is a disclosed post-observation amendment, not part of the original frozen P7. Under that amendment, P7 holds; the original universal wording fails.

    P8’s naming correction is transparently disclosed and implements the intended prediction. P9(c), however, requests the cheapest setup of each control kind; the scorer uses each layer’s own setup. Using the minimum setup across layers gives median **0.83199**, versus **0.82959**; its outcome remains unchanged.

    **Fix:** Show original, amended, and corrected outcomes separately, and log the remaining wording/code inconsistencies. Content hashes establish artifact identity, not independently certified chronology.

The principal theorem labels that **survive** are conditional pricing under conditional Fubini/integrability; the rotational-reference harmonic eigenvalues; realised-kernel rank **at most** \(n\); the conditional Mehler expansion and fixed-defect additive-correction identity; the Haar-linear spectral-share result; the series-free projection identity; the conditional isotropic moment-covariance bound, with justified summability; and the independent-gate participation-ratio result. The Hermite expansion’s restriction for singular post-ReLU laws, withdrawal of E12, extra hypotheses for the \(3/7\) constant, and scrambling qualification are appropriate. None supplies the missing computational lower bound for actual future-chosen ReLU closures.

My numerical checks reproduced the stored scorer output, including NaNs, and regenerated **all T1–T4 tables byte-for-byte in memory**. I also checked the paired-cut statistics, share-law fits, projected-k3 factors and windows, hybrid summaries, and the reported \(n=64\) order-4 example. All **20 manifest-listed hashes** matched their appropriate frozen/current artifacts; live Part-1 code matched its frozen copies.

| Prediction | Audit outcome |
|---|---|
| P1 | Fails; literal truth-floor filtering changes the \(l=16\) statistic |
| P2 | Holds: 5.232 → 2.261 → 1.359 |
| P3 | Holds; reported half-width statistics use the undisclosed flooring rule |
| P4 | Holds |
| P5 | Holds under the stated RQMC extrapolation |
| P6 | Holds; \(R\) is correctly defined as retention of the error difference |
| P7 | Original fails; documented NaN amendment holds: 57 finite runs, maximum gain 0.18132 |
| P8 | Frozen scorer fails through naming bug; intended prediction holds: 2.37293 and 0.0236403 |
| P9 | Holds under the recorded scoring calculation; findings 10–11 limit its estimator interpretation |

The hypothetical dedicated windows also reproduce: gains **2.566, 3.008, 2.373**, ending at **636, 1556, 2790 passes**. These are useful conditional projections. They should not be presented as achieved implementations or as bounds on what another implementation could accomplish.
