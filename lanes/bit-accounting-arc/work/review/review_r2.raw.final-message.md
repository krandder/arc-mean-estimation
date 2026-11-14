<!-- Extracted: the reviewer/co-prover model's final message only. The full session dump (prompt echo, tool calls, intermediate output) is not in this repo. Source file: work/bit-accounting-arc/review/review_r2.raw -->

**Verdict: fixable issues.** The headline counts are largely reproducible, but the report does not establish that they are network-limited. Several convergence and comparison claims need correction.

Checked 2026-11-02, approximately 13:10 UTC: 418 deduplicated runs, generated tables, scoring code, hashes, and worker timestamps. Thirty headline counts and their ranges reproduce correctly, including ARC layers 0/2/8/16: **629/1138/1624**, **357/849/1302**, **111/410/768**, **39/205/469**. Duplicate filenames had identical contents. No files changed; pending results are excluded from this verdict.

1. **Major — A18’s checker can certify the wrong configuration.**  
   **Where:** `scratch/conv_subset.py:87–121`; report §4.1 and summary 6.  
   It accepts doublings elsewhere in the winning start’s family. Layer-31 local’s winning depth-6/48k run is declared converged at 10%, using a **depth-3** 24k→48k steps comparison. Layer-0’s winning 24k look-ahead run uses the depth comparison at **12k**. Also, `ch <= -0.03` rejects improvements only; an increase exceeding 3% passes despite the registered “changes by <3%” rule.  
   **Fix:** require matched-axis comparisons for the winning configuration, use absolute changes, and mark missing comparisons unverified.

2. **Major — equal reported nMSE does not mean equal distortion across layers.**  
   **Where:** `gpu_src/lib/vrlib.py:131`, `:878`; all cross-layer envelopes and consistency checks.  
   `pilot_stats` seeds its sample by layer, giving each layer a different estimate of output variance. ARC-4000 uses **31.9453** at layer 31 versus **31.6226** at the output; ND-216 differs by **−3.59%** at layer 16. These differences matter against 1–3% agreement thresholds.  
   **Fix:** rescale existing distortions by `V_layer / V_common`, using one common normalization per net, then regenerate comparisons.

3. **Major — the information inequality is correct; the claimed unrestricted equalities need additional assumptions.**  
   **Where:** report §1, §4.3; `scratch/consistency.py`.  
   Population rate ≥ \(I(h_l;z)\) ≥ \(I(a;z)\) correctly makes each measured code an upper bound on \(R_a(D)\). However, equality with \(R_a\), and the asserted ordering between implemented unrestricted cells, do not follow when reconstruction must pass through the remaining network. Its image can be nonconvex, excluding an optimal output reconstruction; a finite MLP and Gaussian-channel family impose further restrictions.  
   **Fix:** retain the lower-bound argument. State equality under an unrestricted output decoder or an established reconstruction-lifting assumption; label observed gaps as potentially structural, capacity-, prior-, or optimization-limited.

4. **Major — “the output’s curve” denotes three different quantities.**  
   **Where:** `scratch/report_tables.py::best_out`, `scratch/consistency.py`, `scratch/score_P1_v2.py`; report §4.8.  
   Main tables minimize over base/h1 curves; consistency includes additional variants; C1 uses the output cell’s base curve. For ARC-4000 at 1%/0.1%, the table envelope is approximately **84/260**, whereas additional runs reach **78/225**. Layer-31 unrestricted base is consequently **13%/21% above** the latter, contradicting unqualified “within 1%.” Including each local curve in its own denominator also makes local/output ≥1 automatic.  
   **Fix:** name these three baselines separately. Preserve registered C1, and report the stronger envelope comparison independently; agreement with a selected envelope is not independent optimality evidence.

5. **Major — C7’s interpolation misses cheaper achievable mixtures.**  
   **Where:** `lib/vrb.py::R_lin`; report §4.5.  
   Interpolating adjacent Pareto points is achievable, but it is not the lowest time-sharing curve. Using all two-point mixtures changes reference-start VR at the dedicated \(t=-2\) distortion from **117 to 42.85 bits**; that failure remains. But reference \(t=-2.5\) changes **138.44→76.23**, below the dedicated **120.86**, and look-ahead \(t=-2.5\) changes **91.68→65.55**, below **66.27**: both reported failures disappear.  
   **Fix:** show the registered interpolation result separately from the lower convex hull. Describe \(t=-2\) as a reference-start failure; the look-ahead VR curve already beats that dedicated point. The 48k-versus-12k comparison also needs its unequal training budget stated in the headline.

6. **Major — “best found” and “one encoder” are stronger than the reported aggregation.**  
   **Where:** report summaries 1/4; `report_tables.py::best_local`; `export_curves.py`; amendments A13/A15/A17.  
   Tables correctly implement their stated **better-of-two-starts** rule, but later amendments require improvements from other starts to lower the count. ND-217 layer 0 at 10% has a random-start run at **2.54 bits**, versus the reported two-start minimum **5.04**. Exported “best known” values average variant restarts and omit dedicated models. Moreover, selecting different starts by accuracy—and time-sharing points—is not one deployed encoder covering the entire reported curve.  
   **Fix:** distinguish the frozen two-start baseline, best individual run, and each single model’s curve; identify the winner and switching policy.

7. **Major — the amended prediction scorer still ignores the amended local count.**  
   **Where:** `scratch/score_P1_v2.py::Rm` and prediction section.  
   Predictions read `mean`, not `R_class`; h1-only cells are treated as missing. Thus P1.2 reports **0 evaluated nets** despite four measured h1 layer-4 cells. Cut cells become `hit:false` in P1.4/P1.5/P1.10, conflating incomplete coverage with a measured miss. P1.5 also checks one 0.01→0.001 secant rather than all registered high-precision intervals.  
   **Fix:** retain the original scorer as historical output, correct the amended scorer, and distinguish pass/fail/not evaluable. Explicitly report the genuine **P1.8 miss (0/4 near-reference matches)** and **P1.12 random-start toy failure**.

8. **Major — certification scope exceeds the checks performed.**  
   **Where:** title, summaries 1/7, report §3.  
   “Every layer” means ten sampled internal ARC layers and eight narrow-deep layers. ARC layer 4 currently has only h1; layers 16/20/24 have h1 only on net 4000. “Local layers 24–31; output: within 3%” pools cells without matching depth/steps checks, including checks explicitly cut by A18. Narrow-deep “every class, start and restart” similarly includes unrun combinations. Local `--depth` increases the decoder, **not the one-ReLU encoder**.  
   **Fix:** publish coverage by net/layer/start/accuracy and say “all measured combinations.” Describe passing checks as stability within the tested model class, not certification against low encoder capacity or intrinsic network limits.

9. **Major — the exported certification state omits applicable later evidence.**  
   **Where:** `scratch/export_curves.py:105–145`; `results/certified_curves.json`.  
   Certification ignores C7 and A18/A19 outcomes. ND-216 layer-0 unrestricted is exported as certified while the consistency table flags it approximately **4% above the envelope**. The code can also remove missing C3 checks using another net’s passes.  
   **Fix:** export separate, accuracy-specific statuses for registered certificates, A18 convergence, and A19 consistency. Proxy evidence must remain explicitly untested on the recipient net.

10. **Minor — backward initialization approximately copies the code, including a small gain-copy bug.**  
    **Where:** `gpu_src/scripts/run_vr.py::bwd_init`; report §4.2.  
    Source-frame reconstruction and prior copying are consistent with the current local setup. However, gains depend on `Vb`, which is **not copied**: source/target variances are 31.9453/31.6746. Thus copying `ev` and `c` does not copy the gain function exactly. Distillation R² is measured on its fitting sample and only at anchors; the source is also still unconverged at 1%.  
    **Fix:** preserve the source gain normalization, validate between anchors on fresh inputs, and call this an approximate projected warm start. Its failure cannot rule out an exact curriculum from converged later codes.

11. **Major — explanatory claims outrun the diagnostics.**  
    **Where:** summaries 2/3; report §2 and §4.9.  
    The slope formula is correct, but \(256/\alpha\) assumes a particular state-error/rate relationship. Isotropic perturbations do not establish the learned decoder’s anisotropic, biased error scaling, nor exclude optimization and prior overhead. The spectrum comparison is also a heuristic prediction, not evidence that the spectrum uniquely determines the optimum.  
    **Fix:** label both explanations HEURISTIC. Correct summary 2’s reversed ratio: **learned/water-filling**, not water-filling/learned, is 0.70–0.95 on net 4000; across available nets it is approximately **0.69–1.01** at 1%.

12. **Major — the relevance comparison changes both distribution and quantity.**  
    **Where:** report §5; `scratch/relevance_compare.py`; `report_tables.py::n_dirs`.  
    Imported \(N(l,\epsilon)\) uses the **Gaussian state convention**, whereas these codes use the true propagated distribution. Active latents above 0.05 bit are also not a count of noiseless linear features; the table uses reference-start latents even when another start supplies the headline bits. Sibling channel-capacity counts and learned-prior rates are different upper bounds, so their ratio does not isolate encoder improvement.  
    **Fix:** present these as contextual comparisons with explicit definitions. The output Gaussian bound is a valid upper benchmark, not an optimality certificate; the realized analytic reference is a useful baseline, not a matched estimator/decoder ablation.

13. **Minor — preregistration chronology needs a narrower claim.**  
    **Where:** report §7; A19; worker records.  
    Current registered-file hashes match, and checked production launches follow their amendments. However, A19’s two tests on evaluation net 4000 produced held-out curves at **12:19:28** and **12:24:06**, before its **12:25:27** hash. They are disclosed as smoke tests, but “not results” does not mean evaluation data were unseen.  
    **Fix:** say A19 preceded full production runs but followed these pilot evaluations, and preserve their outputs as disclosed development evidence.

14. **Minor — several residual numerical statements need correction.**  
    **Where:** report §3, §4.3, §4.8, §5.  
    The consistency table says **+37%**, not +35%, for ARC-4000 output at 0.1%. Narrow-deep layer 32 rounds to **4.6**, not 4.5 bits. “465/467 C6 passes” covers core accuracies, but its three-exception list additionally includes 0.005. The quoted direction-count ratio reaches **1.6** (32/20), exceeding “0.9–1.5.”  
    **Fix:** generate these sentences from the same scoped tables and retain the scope labels.
