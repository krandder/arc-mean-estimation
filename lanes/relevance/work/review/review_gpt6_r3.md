codex
The new results reproduce. Remaining corrections concern mathematical scope, scorecard labels, and a few incomplete round-2 edits. Checked read-only through **2026-11-02 02:51:12 UTC**; document SHA-256 `686152e3183687106763dd9e97c2706651970bd91a36d1daf211ecb261228670`. No files changed.

1. **Minor — Most round-2 corrections remain resolved; “all applied” is slightly too strong.**

   The earlier fixes to theorem scope, radius versus linear feature, degree surrogates, uncertainty disclosures, estimator claims, numerical corrections, and figure legends remain in place. I also inspected the regenerated stationary figure.

   Two remnants remain: [§6](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:313) still says “Each sample flips 5–9%,” and §10 supplies only some of the requested P1/P8 group splits.

   **Exact fix:** Replace that sentence with “The layerwise medians of per-sample flip fractions range from 5.18% to 8.90%.” Complete the splits in item 10 below before retaining “all applied.”

2. **Minor — Registration artifacts match; distinguish pre-run registration from author-reported blindness.**

   All **34 entries in `prereg_hashes.txt`** match recoverable artifacts. The amendment checks are:

   | Amendment | Registered | Matching SHA-256 prefixes: registration / theory / scorer | Timing evidence |
   |---|---|---|---|
   | 3A | 00:35:48Z | `a00177f95e16` / `c57c84278705` / `9b02a06e65fa` | First 4004 output born 00:39:37Z; its logged first-cell duration is consistent with starting immediately after registration. |
   | 3B | 01:26:28Z | `ac782abfbd88` / `c1d86a9bed6f` / `f2b67dcbf3ab` | Queue created 01:26:35Z; first outputs born 01:34:28Z, consistent with the reported 01:26:41Z start. Frozen FORMAL also matches `ee05be076a46`. |
   | 3C | 02:03:18Z | `8ee2ffdcdfd0` / `6651cd08c794` / `502489e23a1c` | Partial 4006/4007 outputs already existed. First completed net: 4007 at 02:04:07Z. |

   The co-prover answer hash also matches. Its recorded commands support independence from v3.3 and use of only nets 4000–4005. However, neither hashes nor file times establish that the author had not read partial 4006/4007 outputs. The disclosure in §11 correctly acknowledges this limitation.

   **Exact fix:** Describe 3C consistently as “registered during execution, before output inspection according to the author; reads were not logged.” Preserve 3A’s registration snapshot explicitly: its hash is currently recoverable from the first **12,911 bytes** of the later frozen PREREG files.

3. **Minor — The exact rewriting is correct, but the reported factor uses a different normalization from its physical interpretation.**

   [§3a](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:188) is algebraically correct. For the Gaussian cloud, define
   \[
   q_\gamma=E_\gamma\|X\|^2,\quad q_{a,\gamma}=E_\gamma\|a(X)\|^2,\quad
   R_\gamma=\frac{J_\gamma(1)/\operatorname{tr}\Sigma}{q_{a,\gamma}/q_\gamma}.
   \]
   Then \(D=R_\gamma(\operatorname{tr}\Sigma/q_\gamma)/(V_\gamma/q_{a,\gamma})\).

   But [`measured_R`](/home/agent/workspaces/mats/work/relevance/lib/theory_v33.py:45) uses **`J1_gauss` with `Ea2_true`**. The reported factor is therefore a reference-normalized factor, not exactly the same-cloud tangent-to-forward gain ratio. The co-prover explicitly disclosed this distinction; the main report omits it. The v3.4 predictor additionally uses a separately fitted Gaussian, whereas v3.3 samples true forward trajectories.

   **Exact fix:** Name the scored quantities \(R_{\rm ref}\) and \(b_{\rm ref}=V_\gamma/E_\mu\|a\|^2\). State that their algebraic cancellation remains exact, while identifying \(R_{\rm ref}\) with the same-cloud gain ratio requires a normalization approximation. Preserve registered scores; label any same-law recalculation post hoc.

4. **Minor — The Summary promotes the forward predictor beyond its stated heuristic status.**

   The conditional tangent-energy identity in FORMAL v3.4(b), the coherence identity \(s_1=CD\), and the zero first chaos of the centered-input radius are sound. The distinction between conditional expectation and fixed-net prediction is also correctly stated in §3a.

   However, [Summary 2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:59) says “so R is a product of active-count gains over radial gains.” That is a proxy, not an exact expression for fixed-net \(R\); v3.4 explicitly adds radial transfer. FORMAL v3.5(d)’s “all three factors are forward quantities” similarly conflates exact \(R\), defined through gradient energy, with its forward-only estimate.

   **Exact fix:** Write: “Gate counts and radial gains yield forward-only heuristic estimates of \(R\); the trajectory-conditional version includes radial transfer.” Replace the general forward-predictability conclusion with an empirical statement about these tested cells. Replace FORMAL v3.3(g)’s “One forward pass suffices” with the actual sampling requirements: 1,024 trajectories for v3.3; 16,384 pilot inputs and 4,096 Gaussian trajectories for v3.4, with no pilot fit at the input.

5. **Minor — Two mathematical qualifications were lost in the condensed theory.**

   [FORMAL v3.4(c)](/home/agent/workspaces/mats/work/relevance/FORMAL.md:341) omits the co-prover’s conditioning on survival. With \(K=0\), the displayed logarithmic expressions are undefined. Also, §3a calls the single-ray proxy’s logarithm “log R,” although those are not established moments of the cloud-averaged fixed-net factor.

   FORMAL v3.3(b)’s fluctuation estimate uses ordinary matrix rank. The relevant quantity is an effective rank; an arbitrarily ill-conditioned high-rank tangent matrix does not obtain the stated concentration.

   **Exact fix:** Define \(G_t=\prod_j K_j/S_j\), condition on \(K_j>0\), and assign the displayed log moments to \(G_t\). For the concentration claim, use
   \[
   \mathrm{CV}=\sqrt{\frac{2}{k\,r_{\rm eff}}},\qquad
   r_{\rm eff}=\frac{(\operatorname{tr}A)^2}{\operatorname{tr}(A^2)},
   \]
   for transverse tangent covariance \(A\) and active count \(k\), or remove the unsupported rank-based rate.

6. **Minor — Both registered primary mean-degree tests missed their joint criteria.**

   I recomputed both forward predictors on all 28 fresh cells using the registered seeds. Predictions matched the stored results exactly.

   | Criterion | Recomputed |
   |---|---:|
   | B1, all cells | **21/28** |
   | B1, \(l\le8\) | **6/12** |
   | B2 | **26/28** |
   | C1, all cells | **22/28** |
   | C1, \(l\le8\) | **7/12** |
   | C2 | **22/28** |
   | v2 Q1 / Q2 / Q3 | **19/28 / 26/28 / 25/28** |
   | v2 Q4, \(\varepsilon=0.1/0.01\) | **27/28 / 28/28** |

   PREREG specifies the all-cell **and** early-cell requirements for B1 and C1. Thus C1’s all-cell component passes, but **C1 overall fails**. “Mixed” and “C1 … hit” obscure that distinction.

   **Exact fix:** In the Summary, §10, and FORMAL v3.5, write: “B1 and C1 both missed their registered joint criteria. C1 passed its all-cell component, 22/28, but missed its early-cell component, 7/12.” Retain B2 and C2 as hits.

7. **Minor — Disclose predictions outside the admissible population range.**

   Both new rules predict \(D<1\) on **6/28** fresh cells. Their minima are **0.897047** for v3.3 and **0.889800** for v3.4. Predicted \(s_1>1\) occurs on **4/28** v3.3 cells, maximum **1.047110**, and **1/28** v3.4 cells, maximum **1.009654**.

   Population Gaussian mean degree satisfies \(D\ge1\), and \(0\le s_1\le1\). These violations are model/predictor outputs, distinct from the separately disclosed sampling noise in measured shares.

   **Exact fix:** Add these counts beside the prospective scorecard and identify them as limitations of the approximate predictions. Do not clip the frozen predictions or retroactively change their scores.

8. **Minor — The gain-factor statistics reproduce; specify their conventions and correct one error percentage.**

   Recomputed directly from the raw run records:

   | Seed | Input \(R_{\rm ref}\) |
   |---|---:|
   | 4000 | 1.080116795 |
   | 4001 | 1.619726184 |
   | 4002 | 0.849944061 |
   | 4003 | 1.436187037 |
   | 4004 | 2.131640498 |
   | 4005 | 2.088892954 |

   Their log mean is **0.375376562**, with **sample SD 0.364980357**. Across ten nets these become **0.168720148** and **0.425602961**. E18 and the rounded report values reproduce.

   Fresh-cell gain errors also reproduce: v3.3 median/max **5.0688% / 24.5919%**; v3.4 **3.5407% / 19.0627%**. The latter’s predicted/measured factor range is **[0.9107413, 1.1906274]**.

   The budget correlation and regression slope reproduce as **0.674397** and **0.299734**. But FORMAL v3.5’s “budget error up to 30%” uses measured/model normalization; the registered error convention, model/measured, reaches **42.6077%**.

   **Exact fix:** Specify sample SD, identify the correlation as a post hoc descriptive association across 70 dependent layer cells from ten nets, and replace “error up to 30%” with “measured/model as low as 0.7012, equivalent to 42.6% model-relative-to-measurement error.”

9. **Minor — Stationary table values reproduce, but its count convention differs from the general definition.**

   Independent raw-data recomputation gives:

   | \(n,t\) | Resolved nets | Memory | Degree-1 share | AS direction residual | Radial residual | AS \(N(.1)\) | AS \(N(.01)\) |
   |---|---:|---:|---:|---:|---:|---:|---:|
   | 128,32 | 4 | 0.242962 | 0.998250 | 0.060365 | 0.281440 | 1 | 70 |
   | 256,128 | 2 | 0.363869 | 1.094989 | 0.008846 | 0.082219 | 1 | 6.5 |

   These match §7. However, §1 describes reported counts as the best of three exhibited bases, while §7 uses AS counts. At \(n=256,t=32\), the displayed **132** is the median AS count; the median best-of-three count is **100**.

   **Exact fix:** Label §7’s columns \(N_{\rm AS}\), and explicitly distinguish the registered AS counts from the best-of-three descriptive counts in §5. Retain the registered scores.

10. **Minor — The Part 1 wrapper is faithful; finish the reporting splits.**

   [`score_part1_registered.py`](/home/agent/workspaces/mats/work/relevance/scratch/score_part1_registered.py:14) excludes exactly ARC seeds 4004–4009. It changes no scoring rule. Running it with its output captured entirely in memory reproduced **every stored score and cell record**.

   The final splits are:

   | Test | ARC + stationary \(n\le64\) | Stationary \(n\ge128\) | Pooled |
   |---|---:|---:|---:|
   | P1, \(\varepsilon=.1\) | 64/80 | 23/43 | 87/123 |
   | P1, \(\varepsilon=.01\) | 38/80 | 14/43 | 52/123 |
   | P8, \(\varepsilon=.1\) | 58/80 | 34/43 | 92/123 |
   | P8, \(\varepsilon=.01\) | 57/80 | 24/43 | 81/123 |

   **Exact fix:** Include all four splits. Call these group splits, not an unqualified seen/prospective split: all cells are prospective relative to Part 1, while ARC 4002–4003 inside the 80-cell group are also prospective for v2.

11. **Minor — Pooled Part 3 counts reproduce; one Summary denominator is mis-scoped.**

   Recomputing v2 predictions and comparisons from runs 4002–4009 gives **Q1 45/56, Q2 49/56, Q3 44/56, Q4 55/56 and 56/56**. The disclosure that pooled thresholds were not separately registered is appropriate.

   [Summary 2](/home/agent/workspaces/mats/work/relevance/relevance-accounting.md:65) attaches “25 of 28 there” to nets with \(R<1\). That count covers all four fresh nets. The three nets whose early factors are below one contribute **21/21** Q3 successes.

   **Exact fix:** Write: “v2’s mean-degree prediction passed on 25/28 fresh cells, including 21/21 cells from the three nets whose early-layer factors were below one.”

12. **Minor — A few live statements remain stale or over-rounded.**

   FORMAL E3 still says the free-position comparison holds “at every ARC layer”; E14 still advertises “3–18%” agreement. Those conflict with the expanded evidence. E13 still describes input-radius variation simply as “degree two.” Historical frozen text can remain, but these live errata need pointers to the corrected statements.

   The Summary’s narrow-deep bound “at most \(2\times10^{-2}\)” also rounds downward from §8’s \(2.1\times10^{-2}\). Finally, final Part 3B scoring completed at **02:36:43Z**, whereas Part 3C completed at **02:38:06Z**.

   **Exact fix:** Append corrections identifying **21/24 non-input ARC cells**, replace E14’s obsolete accuracy claim with the applicable scorecards, describe the radius expansion as starting at degree two with higher even degrees, use **\(2.1\times10^{-2}\)** in the Summary, and distinguish the two scoring timestamps.

13. **Minor — Summary assessment: numerically current, with localized overstatements.**

   The Summary’s principal counts, stationary results, gain-factor errors, and estimator gains are current. Its distinction between tested predictive dimension and an unresolved integration-cost lower bound remains appropriate. Post hoc development on 4000–4005 is generally kept separate from testing on 4006–4009.

   **Exact fix:** Apply items 3–6 and 11–12 to the Summary: distinguish the reference-normalized factor from the exact same-law quantity; call the forward rule heuristic; report both primary mean-degree tests as misses; correct the denominator scope and narrow-deep bound. Keep the measured-budget reconstruction explicitly a consequence of factor accuracy, not an additional prospective test.

**Verdict: minor revision.**
